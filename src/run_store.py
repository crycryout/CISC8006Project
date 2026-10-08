"""Exclusive run directories, launch-time provenance, append-only state and budget."""
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from src.io_utils import file_hash, now, object_hash, write_json

ROOT=Path(__file__).resolve().parents[1]
REGISTRY=ROOT/"experiments/registry.jsonl"


def states(registry=REGISTRY):
    latest={}
    if Path(registry).exists():
        for line in Path(registry).read_text().splitlines():
            row=json.loads(line); latest[row["run_id"]]=row
    return latest


def spent(registry=REGISTRY):
    rows=states(registry).values()
    return 0.25+sum(r.get("gpu_hours") or (r.get("reserved_gpu_hours",0) if r["status"] in {"planned","running"} else 0) for r in rows)


def event(row,registry=REGISTRY):
    registry=Path(registry); registry.parent.mkdir(parents=True,exist_ok=True)
    with open(registry,"a") as stream:
        fcntl.flock(stream,fcntl.LOCK_EX)
        stream.write(json.dumps(row,sort_keys=True,allow_nan=False)+"\n"); stream.flush(); os.fsync(stream.fileno())


def numerical_source():
    paths=list((ROOT/"src").glob("*.py"))+[ROOT/"scripts/eval_ppl.py",ROOT/"third_party/streaming-llm/streaming_llm/pos_shift/modify_gpt_neox.py",ROOT/"third_party/streaming-llm/streaming_llm/kv_cache.py"]
    hashes={str(p.relative_to(ROOT)):file_hash(p) for p in sorted(paths)}
    return object_hash(hashes),hashes


def git_snapshot():
    commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
    diff=subprocess.check_output(["git","diff","HEAD","--binary"],cwd=ROOT)
    dirty=bool(subprocess.check_output(["git","status","--porcelain"],cwd=ROOT,text=True).strip())
    import hashlib
    return dict(git_commit=commit,git_dirty=dirty,tracked_diff_sha256=hashlib.sha256(diff).hexdigest())


class Tee:
    def __init__(self,original,path): self.original=original; self.stream=open(path,"x",buffering=1)
    def write(self,text): self.original.write(text); self.stream.write(text); return len(text)
    def flush(self): self.original.flush(); self.stream.flush()
    def isatty(self): return False


class RunStore:
    def __init__(self,cfg,hardware=None,registry=REGISTRY):
        self.cfg=cfg; self.registry=registry; self.directory=Path(cfg.get("output_dir") or ROOT/"runs"/cfg["run_id"])
        self.directory.mkdir(parents=True,exist_ok=False)
        self.t0=time.perf_counter()
        src_hash,src_files=numerical_source()
        self.row=dict(run_id=cfg["run_id"],phase=cfg["phase"],status="planned",registered_at=now(),
            protocol_id=cfg["protocol_id"],config_sha256=object_hash(cfg),data_manifest_sha256=file_hash(cfg["assets_manifest"]),
            model_revision=cfg["model_revision"],seed=cfg["seed"],hardware=hardware or {},
            gpu_uuid=(hardware or {}).get("uuid"),environment_id=cfg["environment_id"],command=[sys.executable]+sys.argv,
            runtime_seconds=None,gpu_hours=None,reserved_gpu_hours=cfg["max_gpu_seconds"]/3600 if cfg["device"]=="cuda" else 0,
            cost="not separately metered; allocated one device times wall seconds",artifact_path=str(self.directory.relative_to(ROOT)) if self.directory.is_relative_to(ROOT) else str(self.directory),
            parent_run_id=cfg["parent_run_id"],exit_code=None,numerical_source_sha256=src_hash,numerical_files_sha256=src_files,**git_snapshot())
        write_json(self.directory/"config_used.json",cfg)
        write_json(self.directory/"registration.json",self.row)
        # A task-local lock serializes budget reservations; never changes another user's GPU state.
        self.registry.parent.mkdir(parents=True,exist_ok=True)
        with open(self.registry.with_suffix(".lock"),"a") as lock:
            fcntl.flock(lock,fcntl.LOCK_EX)
            if cfg["run_id"] in states(self.registry): raise ValueError("run ID already registered")
            if spent(self.registry)+self.row["reserved_gpu_hours"]>20:
                self.row.update(status="failed",exit_code=2,runtime_seconds=0,gpu_hours=0,error="20 GPU-h reservation exceeded")
                write_json(self.directory/"metadata.json",self.row); event(self.row,self.registry)
                raise ValueError("20 GPU-h reservation exceeded")
            event(self.row,self.registry)
        self.row.update(status="running",started_at=now())
        write_json(self.directory/"metadata.json",self.row); event(self.row,self.registry)

    def finish(self,code,error=None):
        seconds=time.perf_counter()-self.t0
        self.row.update(status="completed" if code==0 else "failed",exit_code=code,ended_at=now(),runtime_seconds=seconds,
                        gpu_hours=seconds/3600 if self.cfg["device"]=="cuda" else 0,error=error)
        write_json(self.directory/"metadata.json",self.row); event(self.row,self.registry)
        files=sorted(p for p in self.directory.rglob("*") if p.is_file() and p.name!="checksums.sha256")
        (self.directory/"checksums.sha256").write_text("".join(f"{file_hash(p)}  {p.relative_to(self.directory)}\n" for p in files))
        return self.row
