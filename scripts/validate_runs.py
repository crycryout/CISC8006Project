#!/usr/bin/env python3
"""Validate checksums, NPZ token paths/masks and recomputed metrics, without a GPU."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.io_utils import file_hash, write_json
from src.paired import validate_result
from src.run_store import states
from scripts.prepare_data import token_hash


def validate_run(directory):
    directory=Path(directory)
    metadata=json.loads((directory/"metadata.json").read_text())
    if metadata["status"]!="completed" or metadata["exit_code"]!=0: raise ValueError(f"incomplete/failed run: {directory}")
    checksums=directory/"checksums.sha256"
    if not checksums.exists(): raise ValueError("missing artifact checksums")
    listed=set()
    for line in checksums.read_text().splitlines():
        digest,rel=line.split("  ",1)
        if Path(rel).is_absolute() or ".." in Path(rel).parts: raise ValueError("unsafe artifact path")
        if file_hash(directory/rel)!=digest: raise ValueError(f"artifact hash mismatch: {directory}/{rel}")
        listed.add(rel)
    actual={str(p.relative_to(directory)) for p in directory.rglob("*") if p.is_file() and p!=checksums}
    if listed!=actual: raise ValueError("artifact checksum inventory is incomplete")
    result=json.loads((directory/"result.json").read_text())
    if result.get("schema_version")!=2:
        if result.get("artifact_kind")=="fixture": return dict(run_id=result["run_id"],validation_status="valid_accounted_fixture")
        if result.get("purpose"," ").startswith("offline CPU fixtures"): return dict(run_id=result["run_id"],validation_status="valid_cpu_fixture")
        raise ValueError("legacy result cannot enter v2 evidence")
    cfg=json.loads((directory/"config_used.json").read_text())
    if result["run_id"]!=cfg["run_id"] or result["method"]!=cfg["method"] or result["phase"]!=cfg["phase"]: raise ValueError("run/method/phase differs from registered config")
    manifest=json.loads((ROOT/cfg["assets_manifest"]).read_text())
    if result["contract"]["assets_manifest_sha256"]!=file_hash(ROOT/cfg["assets_manifest"]): raise ValueError("manifest changed")
    validate_result(result,manifest,cfg["manifest_split"],cfg["phase"] in {"reproduction","pilot","improvement","ablation"})
    for row in result["per_book"]:
        with np.load(directory/"books"/row["book_id"]/"position_nll.npz",allow_pickle=False) as trace:
            nll,ids,mask=trace["nll"],trace["input_ids"],trace["scored_mask"]
            if len(nll)!=len(ids)-1 or len(ids)!=row["input_tokens"] or not np.isfinite(nll).all(): raise ValueError("raw NLL shape/finiteness mismatch")
            if mask.dtype!=np.bool_ or not np.array_equal(mask,np.arange(len(nll))>=1025): raise ValueError("scored mask off by one")
            if hashlib.sha256(mask.tobytes()).hexdigest()!=row["scored_mask_sha256"] or token_hash(ids)!=row["token_ids_sha256"]: raise ValueError("raw token/mask digest mismatch")
            if not math.isclose(float(nll[mask].astype(np.float64).sum()),row["sum_nll_scored"],rel_tol=1e-12): raise ValueError("raw NLL does not reconstruct metric")
        metrics=json.loads((directory/"books"/row["book_id"]/"metrics.json").read_text())
        if metrics!=row: raise ValueError("per-book artifact inconsistent with result")
    if result["git_commit"]!=metadata["git_commit"] or result["contract"]["numerical_source_sha256"]!=metadata["numerical_source_sha256"]: raise ValueError("launch/source mapping mismatch")
    return dict(run_id=result["run_id"],validation_status="valid",books=len(result["per_book"]),result_sha256=file_hash(directory/"result.json"))


def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("--registry",default="experiments/registry.jsonl"); p.add_argument("--run"); p.add_argument("--out",default="results/run_validation.json")
    a=p.parse_args(); reports=[]
    if a.run: reports.append(validate_run(a.run))
    else:
        for row in states(a.registry).values():
            if row["status"]=="completed": reports.append(validate_run(ROOT/row["artifact_path"]))
            elif row["status"]=="failed": reports.append(dict(run_id=row["run_id"],validation_status="invalid_failed_attempt_preserved",error=row.get("error")))
            elif row["status"]=="legacy_recorded": reports.append(dict(run_id=row["run_id"],validation_status="legacy_evidence_only_not_v2"))
            else: raise ValueError(f"unfinished attempt: {row['run_id']}")
    write_json(a.out,reports); print(json.dumps(reports,indent=2))


if __name__=="__main__": main()
