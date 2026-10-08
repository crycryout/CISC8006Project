import json
from pathlib import Path
import pytest
from src.config import DEFAULTS
from src.io_utils import write_json
from src.run_store import RunStore, states


def fixture_cfg(tmp_path,run_id="cpu-fixture"):
    manifest=tmp_path/"assets.json"; write_json(manifest,{"fixture":True})
    return dict(DEFAULTS,run_id=run_id,method="window",phase="smoke",device="cpu",output_dir=str(tmp_path/run_id),assets_manifest=str(manifest))


def test_exclusive_run_and_failure_partial(tmp_path):
    registry=tmp_path/"registry.jsonl"; cfg=fixture_cfg(tmp_path)
    store=RunStore(cfg,registry=registry)
    write_json(store.directory/"books/A/metrics.json",{"known_complete":True})
    store.finish(1,"second book error")
    assert states(registry)[cfg["run_id"]]["status"]=="failed"
    assert (store.directory/"books/A/metrics.json").exists()
    assert 'books/A/metrics.json' in (store.directory/"checksums.sha256").read_text()
    with pytest.raises(FileExistsError): RunStore(cfg,registry=registry)


def test_launch_snapshot_does_not_follow_later_head(tmp_path,monkeypatch):
    import src.run_store as module
    monkeypatch.setattr(module,"git_snapshot",lambda:dict(git_commit="launch",git_dirty=False,tracked_diff_sha256="d"))
    store=RunStore(fixture_cfg(tmp_path),registry=tmp_path/"registry.jsonl")
    monkeypatch.setattr(module,"git_snapshot",lambda:dict(git_commit="later",git_dirty=False,tracked_diff_sha256="d"))
    assert store.finish(0)["git_commit"]=="launch"


def test_budget_rejects_without_loading_model(tmp_path):
    cfg=fixture_cfg(tmp_path); cfg.update(device="cuda",max_gpu_seconds=72000)
    registry=tmp_path/"registry.jsonl"
    with pytest.raises(ValueError,match="20 GPU-h"): RunStore(cfg,registry=registry)
    assert states(registry)[cfg["run_id"]]["status"]=="failed"
    assert states(registry)[cfg["run_id"]]["gpu_hours"]==0
