#!/usr/bin/env python3
"""Read progress without allocating a GPU or changing scientific artifacts."""
import datetime
import json
from pathlib import Path
import sys
import yaml
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.run_store import states,spent
from scripts.run_matrix import resolve


def snapshot():
    observed=states(); matrices=["reproduction","pilot","improvement_matrix_h1","improvement_matrix_h2","ablation_matrix_h1","ablation_matrix_h2"]
    names=["reproduction_matrix","pilot_matrix"]+matrices[2:]
    current=[]
    for name in names:
        matrix=yaml.safe_load((ROOT/"configs"/(name+".yaml")).read_text())
        for job in resolve(matrix):
            row=observed.get(job["run_id"])
            if not row: continue
            path=ROOT/row["artifact_path"]
            manifest=json.loads((ROOT/job["config"]["assets_manifest"]).read_text())
            books=manifest[matrix["split"]+"_books"]
            lengths={book["book_id"]:min(book["full_token_length"],matrix["cap"])-1 for book in books}
            done=json.loads((path/"progress.json").read_text()).get("completed_books",[]) if (path/"progress.json").exists() else []
            total=sum(lengths.values()); predicted=sum(lengths[book] for book in done)
            latest=None
            if (path/"stdout.log").exists():
                with open(path/"stdout.log","rb") as stream:
                    stream.seek(max(0,(path/"stdout.log").stat().st_size-65536))
                    for line in stream.read().decode(errors="replace").splitlines():
                        try: item=json.loads(line)
                        except (ValueError,TypeError): continue
                        if isinstance(item,dict) and "step" in item and "book" in item: latest=item
            if latest and latest["book"] not in done: predicted+=latest["step"]+1
            if row["status"]=="completed": predicted=total
            elapsed=row.get("runtime_seconds")
            if elapsed is None and row.get("started_at"):
                elapsed=(datetime.datetime.now(datetime.timezone.utc)-datetime.datetime.fromisoformat(row["started_at"])).total_seconds()
            current.append(dict(run_id=job["run_id"],state=row["status"],completed_books=len(done),total_books=len(books),predictions_observed=predicted,predictions_total=total,percent=round(100*predicted/total,2),latest=latest,elapsed_seconds=round(elapsed,1) if elapsed is not None else None,gpu_hours=row.get("gpu_hours"),device=row["gpu_uuid"]))
    checkpoints=sorted((ROOT/"experiments/studies").glob("*/state.json"))
    return dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),study_states=[json.loads(path.read_text()) for path in checkpoints],runs=current,spent_or_reserved_device_instance_hours=spent())


if __name__=="__main__": print(json.dumps(snapshot(),indent=2))
