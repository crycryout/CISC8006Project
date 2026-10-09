#!/usr/bin/env python3
"""Review a complete job matrix; execute only with evidence, approvals and budget."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import datetime
import fcntl
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import yaml

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.approvals import ceiling, require_approval
from src.config import DEFAULTS, validate
from src.io_utils import file_hash, now, object_hash, write_json
from src.run_store import numerical_source, spent, states
from src.hardware import active_pids


def resolve(matrix):
    if set(matrix)-{"matrix_id","protocol_id","phase","split","methods","seeds","cap","estimated_predictions_per_second","setup_seconds","selected_gpu","preconditions","config_overrides","seed_devices","max_parallel"}: raise ValueError("unknown matrix key")
    manifest=json.loads((ROOT/"data/assets_manifest.json").read_text())
    rows=manifest[matrix["split"]+"_books"]
    predictions=sum(min(row["full_token_length"],matrix["cap"])-1 for row in rows)
    if matrix["estimated_predictions_per_second"]<=0: raise ValueError("invalid throughput estimate")
    expected=predictions/matrix["estimated_predictions_per_second"]+matrix.get("setup_seconds",60)
    jobs=[]
    for seed in matrix["seeds"]:
        for method,settings in matrix["methods"].items():
            rid=f'{matrix["matrix_id"]}-{method}-s{seed}'
            cfg=dict(DEFAULTS,run_id=rid,method=method,phase=matrix["phase"],protocol_id=matrix["protocol_id"],manifest_split=matrix["split"],book_files=[str(Path("data/pg19")/row["file"]) for row in rows],max_tokens_per_book=matrix["cap"],seed=seed,max_gpu_seconds=math.ceil(expected*1.25+120))
            cfg.update(matrix.get("config_overrides",{})); cfg.update(settings); validate(cfg)
            path=ROOT/"runs"/rid
            status=states().get(rid,{}).get("status","not_registered")
            reusable=False
            if path.exists() and status=="completed" and (path/"result.json").exists():
                stored=json.loads((path/"config_used.json").read_text())
                result=json.loads((path/"result.json").read_text())
                reusable=stored==cfg and result.get("contract",{}).get("numerical_source_sha256")==numerical_source()[0]
            selected=str(matrix.get("seed_devices",{}).get(seed,matrix["selected_gpu"]))
            if not selected or "," in selected: raise ValueError("one CUDA device per seed required")
            jobs.append(dict(run_id=rid,config=cfg,output_path=str(path.relative_to(ROOT)),existing_status=status,reusable=reusable,estimated_gpu_hours=expected/3600,config_sha256=object_hash(cfg),selected_device=selected))
    return jobs


def check_window(seconds,gpu):
    # The host's actual root cron toggles GPU0 at 01:30. Never run across it.
    if str(gpu)!="0": return
    current=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
    boundary=current.replace(hour=1,minute=20,second=0,microsecond=0)
    if current.hour>=9: boundary+=datetime.timedelta(days=1)
    elif current>=boundary: raise ValueError("GPU0 scheduled MIG window; wait until 09:00 Asia/Macao")
    if (boundary-current).total_seconds()<seconds: raise ValueError("job crosses GPU0 scheduled MIG change; resume during available window")


def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("--matrix",required=True)
    mode=p.add_mutually_exclusive_group(required=True); mode.add_argument("--dry-run",action="store_true"); mode.add_argument("--execute",action="store_true")
    args=p.parse_args(); matrix=yaml.safe_load(Path(args.matrix).read_text()); jobs=resolve(matrix)
    estimated=sum(j["estimated_gpu_hours"] for j in jobs if not j["reusable"])
    budget=spent(); approval="approved"
    try:
        for j in jobs: require_approval(j["config"]["phase"],j["config"]["method"])
    except ValueError as error: approval=str(error)
    review=dict(matrix_id=matrix["matrix_id"],matrix_sha256=file_hash(args.matrix),jobs=jobs,spent_or_reserved_gpu_hours=budget,estimated_new_gpu_hours=estimated,ceiling_gpu_hours=ceiling(),approval=approval,selected_gpu=matrix["selected_gpu"],seed_devices=matrix.get("seed_devices",{}),max_parallel=matrix.get("max_parallel",1),dry_run=not args.execute)
    print(json.dumps(review,indent=2))
    if args.dry_run: return
    if approval!="approved": p.error(approval)
    limit=ceiling()
    if limit is not None and budget+estimated>limit: p.error("predicted work exceeds actually approved GPU ceiling; a concrete decision is required")
    for condition in matrix.get("preconditions",[]):
        if not (ROOT/condition).exists(): p.error(f"prerequisite evidence missing: {condition}")
    source=numerical_source()[0]
    groups={}
    for job in jobs: groups.setdefault(job["selected_device"],[]).append(job)
    parallel=matrix.get("max_parallel",1)
    if type(parallel) is not int or not 1<=parallel<=len(groups): p.error("invalid device parallelism")

    def worker(device,assigned):
        lease_dir=ROOT/"experiments/device_leases"; lease_dir.mkdir(parents=True,exist_ok=True)
        with open(lease_dir/(device+".lock"),"a") as lease:
            fcntl.flock(lease,fcntl.LOCK_EX|fcntl.LOCK_NB)
            for job in assigned:
                if numerical_source()[0]!=source: raise ValueError("numerical source changed during matrix execution")
                if job["reusable"]:
                    from scripts.validate_runs import validate_run
                    validate_run(ROOT/job["output_path"])
                    continue
                if (ROOT/job["output_path"]).exists(): raise ValueError(f"ID exists; retry requires a new ID: {job['run_id']}")
                check_window(job["config"]["max_gpu_seconds"],device)
                if active_pids(device): raise ValueError(f"CUDA device {device} has active workloads; no process stopped")
                plan_dir=ROOT/"experiments/plans"/job["run_id"]; plan_dir.mkdir(parents=True,exist_ok=False)
                config_path=plan_dir/"config.yaml"; config_path.write_text(yaml.safe_dump(job["config"],sort_keys=True))
                command=[sys.executable,str(ROOT/"scripts/eval_ppl.py"),"--config",str(config_path)]
                write_json(plan_dir/"launch.json",dict(registered_at=now(),matrix_sha256=review["matrix_sha256"],command=command,selected_device=device,numerical_source_sha256=source))
                print(json.dumps(dict(event="launch",run_id=job["run_id"],device=device)),flush=True)
                with open(plan_dir/"driver.log","x") as log:
                    code=subprocess.call(command,cwd=ROOT,env=dict(os.environ,CUDA_VISIBLE_DEVICES=device),stdout=log,stderr=subprocess.STDOUT)
                print(json.dumps(dict(event="finished",run_id=job["run_id"],exit_code=code)),flush=True)
                if code: return code
        return 0

    with ThreadPoolExecutor(max_workers=parallel) as pool:
        futures=[pool.submit(worker,device,assigned) for device,assigned in groups.items()]
        codes=[future.result() for future in futures]
    if any(codes): sys.exit(1)


if __name__=="__main__": main()
