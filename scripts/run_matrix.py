#!/usr/bin/env python3
"""Review a complete job matrix; execute only with evidence, approvals and budget."""
import argparse
import datetime
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


def resolve(matrix):
    if set(matrix)-{"matrix_id","protocol_id","phase","split","methods","seeds","cap","estimated_predictions_per_second","setup_seconds","selected_gpu","preconditions","config_overrides"}: raise ValueError("unknown matrix key")
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
            jobs.append(dict(run_id=rid,config=cfg,output_path=str(path.relative_to(ROOT)),existing_status=status,reusable=reusable,estimated_gpu_hours=expected/3600,config_sha256=object_hash(cfg)))
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
    review=dict(matrix_id=matrix["matrix_id"],matrix_sha256=file_hash(args.matrix),jobs=jobs,spent_or_reserved_gpu_hours=budget,estimated_new_gpu_hours=estimated,ceiling_gpu_hours=ceiling(),approval=approval,selected_gpu=matrix["selected_gpu"],dry_run=not args.execute)
    print(json.dumps(review,indent=2))
    if args.dry_run: return
    if approval!="approved": p.error(approval)
    if budget+estimated>ceiling(): p.error("predicted work exceeds actually approved GPU ceiling; a concrete decision is required")
    for condition in matrix.get("preconditions",[]):
        if not (ROOT/condition).exists(): p.error(f"prerequisite evidence missing: {condition}")
    for job in jobs:
        if job["reusable"]:
            from scripts.validate_runs import validate_run
            validate_run(ROOT/job["output_path"])
            continue
        if (ROOT/job["output_path"]).exists(): p.error(f"ID exists; retry requires new matrix/run ID: {job['run_id']}")
        check_window(job["config"]["max_gpu_seconds"],matrix["selected_gpu"])
        processes=subprocess.check_output(["nvidia-smi","-i",str(matrix["selected_gpu"]),"--query-compute-apps=pid","--format=csv,noheader"],text=True).strip()
        if processes: p.error("selected GPU has active compute workloads; no processes will be stopped")
        # Register exact config in an immutable, separate plan directory.
        plan_dir=ROOT/"experiments/plans"/job["run_id"]; plan_dir.mkdir(parents=True,exist_ok=False)
        config_path=plan_dir/"config.yaml"; config_path.write_text(yaml.safe_dump(job["config"],sort_keys=True))
        command=[sys.executable,str(ROOT/"scripts/eval_ppl.py"),"--config",str(config_path)]
        write_json(plan_dir/"launch.json",dict(registered_at=now(),matrix_sha256=review["matrix_sha256"],command=command))
        code=subprocess.call(command,cwd=ROOT,env=dict(os.environ,CUDA_VISIBLE_DEVICES=str(matrix["selected_gpu"])))
        if code: sys.exit(code)


if __name__=="__main__": main()
