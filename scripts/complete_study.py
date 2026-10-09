#!/usr/bin/env python3
"""Run the authorized preregistered study, preserving every real attempt."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
import yaml
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.io_utils import file_hash,now,write_json
from src.run_store import event,numerical_source,states,spent
from src.approvals import authorized
from scripts.run_matrix import resolve
from scripts.validate_runs import validate_run


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--attach-reproduction",action="store_true")
    parser.add_argument("--study-id",default="owner-h800-20261009")
    args=parser.parse_args()
    directory=ROOT/"experiments/studies"/args.study_id
    directory.mkdir(parents=True,exist_ok=False)
    frozen_source=numerical_source()[0]
    lifecycle=ROOT/"experiments/study_events.jsonl"
    completed=[]

    def checkpoint(stage,status,**extra):
        value=dict(at=now(),study_id=args.study_id,stage=stage,status=status,numerical_source_sha256=frozen_source,completed_stages=list(completed),device_instance_hours=spent(),**extra)
        write_json(directory/"state.json",value)
        event(value,lifecycle)
        print(json.dumps(value),flush=True)

    def unchanged():
        if numerical_source()[0]!=frozen_source: raise ValueError("inference source changed after registration; preserve runs and stop")

    def command(stage,argv):
        unchanged()
        path=directory/(stage+".log")
        with open(path,"x") as log:
            code=subprocess.call([sys.executable]+argv,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
        if code: raise RuntimeError(f"{stage} exited {code}; see {path.relative_to(ROOT)}")

    def wait_matrix(stage,matrix_path):
        jobs=resolve(yaml.safe_load((ROOT/matrix_path).read_text()))
        while True:
            unchanged(); observed=states(); complete=[]; waiting=[]
            for job in jobs:
                row=observed.get(job["run_id"],{})
                if row.get("status")=="failed": raise RuntimeError(f"failed immutable attempt: {job['run_id']}; retry must use a new ID")
                artifact=ROOT/job["output_path"]
                if row.get("status")=="completed" and (artifact/"checksums.sha256").exists():
                    complete.append(job["run_id"])
                else: waiting.append(dict(run_id=job["run_id"],status=row.get("status","not_started")))
            if not waiting:
                for job in jobs: validate_run(ROOT/job["output_path"])
                return
            checkpoint(stage,"running",completed_runs=complete,waiting_runs=waiting)
            time.sleep(30)

    def matrix(stage,path,attach=False):
        checkpoint(stage,"running",matrix_path=path,matrix_sha256=file_hash(ROOT/path),attached=attach)
        if not attach: command(stage,["scripts/run_matrix.py","--matrix",path,"--execute"])
        wait_matrix(stage,path)
        completed.append(stage); checkpoint(stage,"completed")

    try:
        matrix("reproduction","configs/reproduction_matrix.yaml",args.attach_reproduction)
        command("build_reproduction",["scripts/build_results.py"])
        matrix("pilots","configs/pilot_matrix.yaml")
        command("build_pilots",["scripts/build_results.py"])
        proposal=json.loads((ROOT/"results/pilots/selection_proposal.json").read_text())
        selected=proposal["nominated_method"]
        if selected not in {"h1_adaptive_sink","h2_sink_selection"}: raise ValueError("unregistered pilot selection")
        approval_path=ROOT/"docs/approval_decisions.json"
        decisions=json.loads(approval_path.read_text()); decision=decisions["selected_improvement"]
        if not authorized(decision) or decision.get("selection_delegated") is not True: raise ValueError("selection is not actually delegated by owner")
        decision.update(method=selected,selected_at=now(),selection_actor="agent applying the frozen owner-authorized pilot rule",selection_evidence="results/pilots/selection_proposal.json",selection_evidence_sha256=file_hash(ROOT/"results/pilots/selection_proposal.json"))
        write_json(approval_path,decisions)
        family="h1" if selected=="h1_adaptive_sink" else "h2"
        inputs_path=ROOT/"results/final_input_manifest.json"
        inputs=json.loads(inputs_path.read_text())
        write_json(directory/"preselection_input_manifest.json",inputs)
        inputs["improvement"]=dict(baseline=inputs["reproduction"]["candidate"],candidate=[f"runs/I-{family}-v2-mig-20261009-{selected}-s{seed}/result.json" for seed in (0,1,2)],split="test")
        inputs["ablations"]={key:value for key,value in inputs["ablations"].items() if key.startswith(family+"_")}
        write_json(inputs_path,inputs)
        checkpoint("selection","completed",selected_method=selected,rule="frozen quality/cost ranking with H1 negative-result fallback",proposal_sha256=file_hash(ROOT/"results/pilots/selection_proposal.json"))
        matrix("improvement",f"configs/improvement_matrix_{family}.yaml")
        matrix("controls",f"configs/ablation_matrix_{family}.yaml")
        command("validate_all",["scripts/validate_runs.py"])
        command("build_final_results",["scripts/build_results.py"])
        command("build_final_deliverables",["scripts/build_deliverables.py"])
        command("render_registry",["scripts/render_registry.py"])
        checkpoint("scientific_execution","completed",selected_method=selected,next_step="verify current clean checkout, presentation/demo and freeze the measured technical delivery; human course activities separately recorded")
    except BaseException as error:
        checkpoint("scientific_execution","failed",error=f"{type(error).__name__}: {error}")
        raise


if __name__=="__main__": main()
