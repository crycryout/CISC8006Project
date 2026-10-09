import pytest
from src import approvals


def test_unlimited_needs_explicit_user_record(monkeypatch):
    record=dict(status="authorized_by_user",reviewer="fixture user",evidence="fixture conversation",approved_ceiling_gpu_hours=None,unlimited_resources=True)
    monkeypatch.setattr(approvals,"budget_decision",lambda:record)
    assert approvals.ceiling() is None
    record["evidence"]=None
    assert approvals.ceiling()==20.0


def test_unlimited_does_not_waive_model_seeds(monkeypatch):
    monkeypatch.setattr(approvals,"budget_decision",lambda:dict(status="authorized_by_user",reviewer="fixture user",evidence="fixture",approved_ceiling_gpu_hours=None,unlimited_resources=True,deterministic_single_pass_exemption=False))
    assert not approvals.single_pass_allowed()


def test_seed_device_pairing_is_preserved():
    from scripts.run_matrix import resolve
    import yaml
    from pathlib import Path
    matrix=yaml.safe_load(Path("configs/reproduction_matrix.yaml").read_text())
    matrix.update(seed_devices={0:"MIG-fixture-a",1:"MIG-fixture-b",2:"MIG-fixture-c"},max_parallel=3)
    jobs=resolve(matrix)
    for seed in (0,1,2):
        pair=[job for job in jobs if job["config"]["seed"]==seed]
        assert len(pair)==2 and len({job["selected_device"] for job in pair})==1
        assert {job["config"]["method"] for job in pair}=={"window","streaming"}
