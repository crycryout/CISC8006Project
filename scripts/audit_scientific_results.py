#!/usr/bin/env python3
"""Reconstruct paired statistics directly from every frozen raw NPZ loss array."""
import argparse
import json
import math
from pathlib import Path
import sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.io_utils import file_hash,now,write_json
from scripts.validate_runs import validate_run


def audit(stage,spec):
    baseline,candidate=spec["baseline"],spec["candidate"]
    book_rows={}; raw_files=[]; repeats={"baseline":[],"candidate":[]}
    for label,paths in [("baseline",baseline),("candidate",candidate)]:
        for relative in paths:
            directory=ROOT/Path(relative).parent
            validate_run(directory)
            result=json.loads((ROOT/relative).read_text()); seed=result["contract"]["seed"]
            values={}
            for row in result["per_book"]:
                book=row["book_id"]; raw=directory/"books"/book/"position_nll.npz"
                with np.load(raw,allow_pickle=False) as trace:
                    losses=trace["nll"].copy(); mask=trace["scored_mask"]
                    expected=np.arange(len(losses))>=1025
                    if not np.array_equal(mask,expected): raise ValueError("raw score mask changed")
                    total=float(np.sum(losses[mask],dtype=np.float64)); count=int(np.count_nonzero(mask))
                    values[book]=dict(seed=seed,total=total,count=count,mean=total/count,raw_nll=losses)
                book_rows.setdefault(book,{"baseline":{},"candidate":{}})[label][seed]=values[book]
                raw_files.append(dict(path=str(raw.relative_to(ROOT)),sha256=file_hash(raw)))
            repeats[label].append(values)
    if len(baseline)!=3 or len(candidate)!=3: raise ValueError("three actual seeds are required")
    rows=[]
    for book,groups in book_rows.items():
        if set(groups["baseline"])!={0,1,2} or set(groups["candidate"])!={0,1,2}: raise ValueError("unpaired seeds")
        base=np.mean([v["mean"] for v in groups["baseline"].values()])
        cand=np.mean([v["mean"] for v in groups["candidate"].values()])
        delta=np.mean([groups["candidate"][seed]["mean"]-groups["baseline"][seed]["mean"] for seed in (0,1,2)])
        rows.append(dict(book_id=book,baseline_nll=float(base),candidate_nll=float(cand),delta=float(delta)))
    differences=np.array([row["delta"] for row in rows])
    # Resample the ten (or three development) books, never thirty book-seed rows.
    generator=np.random.default_rng(0)
    indices=generator.integers(0,len(rows),size=(10000,len(rows)))
    samples=np.mean(differences[indices],axis=1)
    interval=np.percentile(samples,[2.5,97.5]).tolist()
    summary=json.loads((ROOT/"results"/stage/"summary.json").read_text())
    paired=json.loads((ROOT/"results"/stage/"paired_result.json").read_text())
    def close(measured,reported,label):
        if not math.isclose(measured,reported,rel_tol=1e-12,abs_tol=1e-12): raise ValueError(stage+": raw reconstruction differs: "+label)
    close(float(differences.mean()),summary["paired_macro_delta_nll"],"mean paired delta")
    for actual,reported in zip(interval,summary["bootstrap_ci95"]): close(actual,reported,"bootstrap interval")
    if [row["book_id"] for row in rows]!=[row["book_id"] for row in paired["per_book"]]: raise ValueError("book ordering changed")
    for raw_row,reported in zip(rows,paired["per_book"]):
        for key in ("baseline_nll","candidate_nll","delta"): close(raw_row[key],reported[key],"per-book "+key)
    seed_spread={}
    for label,runs in repeats.items():
        means=[np.mean([v["mean"] for v in run.values()]) for run in runs]
        micros=[sum(v["total"] for v in run.values())/sum(v["count"] for v in run.values()) for run in runs]
        close(float(np.mean(means)),summary[label]["macro_book_nll"],label+" macro NLL")
        close(float(np.mean(micros)),summary[label]["micro_token_nll"],label+" micro NLL")
        close(float(np.exp(np.mean(micros))),summary[label]["micro_token_ppl"],label+" pooled PPL")
        same=all(np.array_equal(runs[0][book]["raw_nll"],run[book]["raw_nll"]) for run in runs[1:] for book in runs[0])
        seed_spread[label]=dict(actual_seeds=[0,1,2],macro_nll_range=float(max(means)-min(means)),all_position_losses_bitwise_identical=same)
    verdict="supported" if interval[1]<0 else "not_supported" if interval[0]>0 else "inconclusive"
    if verdict!=summary["claim_status"]: raise ValueError("raw verdict differs")
    return dict(stage=stage,status="pass",n_books=len(rows),paired_macro_delta_nll=float(differences.mean()),bootstrap_ci95=interval,
                claim_status=verdict,seed_spread=seed_spread,raw_files=raw_files,
                paired_result_sha256=file_hash(ROOT/"results"/stage/"paired_result.json"))


def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("--stage",choices=["reproduction","improvement"]); p.add_argument("--out",default="environment/verification/scientific-raw-reconstruction.json")
    args=p.parse_args(); inputs=json.loads((ROOT/"results/final_input_manifest.json").read_text())
    stages=[(args.stage,inputs[args.stage])] if args.stage else [("reproduction",inputs["reproduction"]),("improvement",inputs["improvement"]),*(("ablations/"+name,spec) for name,spec in inputs["ablations"].items())]
    results=[audit(stage,spec) for stage,spec in stages]
    write_json(ROOT/args.out,dict(checked_at=now(),status="pass",kind="agent engineering reconstruction; not independent human peer review",audit_script_sha256=file_hash(Path(__file__)),input_manifest_sha256=file_hash(ROOT/"results/final_input_manifest.json"),bootstrap=dict(seed=0,resamples=10000,unit="book"),stages=results))
    print(json.dumps([dict(stage=row["stage"],status=row["status"],n_books=row["n_books"],claim_status=row["claim_status"],seed_spread=row["seed_spread"]) for row in results],indent=2))


if __name__=="__main__": main()
