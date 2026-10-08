#!/usr/bin/env python3
"""Rebuild diagnostics and (when available) scientific tables/figures from raw artifacts."""
import argparse
import csv
import json
import math
from pathlib import Path
import sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.io_utils import file_hash, now, write_json
from src.metrics import aggregate
from src.paired import analyze_pairs
from scripts.validate_runs import validate_run


def write_csv(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with open(path,"w",newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]),lineterminator="\n"); writer.writeheader(); writer.writerows(rows)


def plot_positions(results,path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(8,4))
    coverage=[]
    for label,items in results.items():
        curves={}
        for directory,result in items:
            for book in result["per_book"]:
                trace=np.load(directory/"books"/book["book_id"]/"position_nll.npz")
                losses=trace["nll"]
                for start in range(1025,len(losses),512):
                    curves.setdefault(start,[]).append(float(losses[start:start+512].astype(np.float64).mean()))
        xs=sorted(curves)
        ax.plot(xs,[np.mean(curves[x]) for x in xs],label=label)
        for x in xs: coverage.append(dict(method=label,first_step=x,mean_book_bin_nll=float(np.mean(curves[x])),n_book_seed_pairs=len(curves[x]),n_books=len({b["book_id"] for _,r in items for b in r["per_book"] if b["input_tokens"]-1>x})))
    ax.set(xlabel="prediction step (scored region begins at 1025)",ylabel="equal-book mean bin NLL (nats)")
    ax.legend(); fig.tight_layout(); fig.savefig(path,dpi=180); plt.close(fig)
    write_csv(path.with_suffix(".csv"),coverage)


def build_diagnostics(paths):
    out=ROOT/"results/diagnostics"; out.mkdir(parents=True,exist_ok=True)
    rows=[]; items={}
    for path in paths:
        directory=ROOT/Path(path).parent
        validate_run(directory)
        result=json.loads((ROOT/path).read_text()); contract=result["contract"]
        rows.append(dict(run_id=result["run_id"],method=result["method"],position_policy=contract["position_policy"],scorer_precision=contract["scorer_precision"],book_ids=";".join(result["book_ids"]),scored_tokens=result["scored_tokens"],macro_book_nll=result["macro_book_nll"],micro_token_ppl=result["micro_token_ppl"],predictions_per_second=result["predictions_per_second"],peak_gpu_memory_mb=result["peak_gpu_memory_mb"],source_commit=result["git_commit"],result_sha256=file_hash(ROOT/path)))
        items[result["run_id"]]=[(directory,result)]
    write_csv(out/"comparison.csv",rows)
    write_json(out/"summary.json",dict(validation_status="valid",claim_status=None,purpose="single exposed smoke-book2×2 diagnostic; not formal reproduction",runs=rows))
    plot_positions(items,ROOT/"figures/diagnostic_nll_vs_position.png")
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(7,3.5))
    for label,entries in items.items():
        r=entries[0][1]; trace=r["per_book"][0]["cache_trace"]
        ax.plot([x["step"] for x in trace],[x["retained_length"] for x in trace],label=label)
    ax.set(xlabel="prediction step",ylabel="retained KV positions",ylim=(0,1100)); ax.legend(fontsize=7); fig.tight_layout(); fig.savefig(ROOT/"figures/diagnostic_cache_plateau.png",dpi=180); plt.close(fig)
    first=next(iter(items.values()))[0][1]["per_book"][0]["cache_trace"]
    fig,ax=plt.subplots(figsize=(7,3.5)); ax2=ax.twinx()
    ax.plot([x["step"] for x in first],[x["retained_length"] for x in first],color="navy",label="retained length")
    ax2.plot([x["step"] for x in first],[x["kv_bytes"]/1024**2 for x in first],color="gray",linestyle="--",label="measured KV MiB")
    ax.set(xlabel="prediction step",ylabel="retained KV positions"); ax2.set_ylabel("tensor K+V bytes (MiB)")
    ax.set_title("All four arms retain the same length and bytes; forward peak is 1025",fontsize=9)
    fig.tight_layout(); fig.savefig(ROOT/"figures/diagnostic_kv_bytes.png",dpi=180); plt.close(fig)
    return dict(state="diagnostic_complete",runs=[r["run_id"] for r in rows])


def load_runs(paths):
    records=[]
    for path in paths:
        directory=ROOT/Path(path).parent; validate_run(directory)
        records.append((directory,json.loads((ROOT/path).read_text())))
    return records


def scientific(stage,spec,manifest):
    directory=ROOT/"results"/stage; directory.mkdir(parents=True,exist_ok=True)
    paths=spec["baseline"]+spec["candidate"]
    missing=[p for p in paths if not (ROOT/p).exists()]
    if missing:
        write_json(directory/"status.json",dict(state="pending",missing=missing,claim_status=None))
        return dict(state="pending",missing_runs=len(missing))
    base=load_runs(spec["baseline"]); candidate=load_runs(spec["candidate"])
    out=analyze_pairs([r for _,r in base],[r for _,r in candidate],manifest,spec.get("split","test"))
    out["inputs"]=[dict(path=p,sha256=file_hash(ROOT/p)) for p in paths]
    write_json(directory/"paired_result.json",out); write_csv(directory/"per_book.csv",out["per_book"])
    summary=dict(paired_macro_delta_nll=out["paired_macro_delta_nll"],bootstrap_ci95=out["bootstrap_ci95"],claim_status=out["claim_status"],n_books=out["n_books"],seeds=[r["contract"]["seed"] for _,r in base],primary="equal-book seed-paired NLL difference")
    for label,items in [("baseline",base),("candidate",candidate)]:
        summary[label]={k:float(np.mean([r[k] for _,r in items])) for k in ("macro_book_nll","macro_derived_ppl","micro_token_nll","micro_token_ppl","peak_gpu_memory_mb","predictions_per_second")}
        summary[label]["runtime_seconds"]=float(np.mean([json.loads((d/"metadata.json").read_text())["runtime_seconds"] for d,_ in items]))
        summary[label]["macro_derived_ppl"]=math.exp(summary[label]["macro_book_nll"])
        summary[label]["micro_token_ppl"]=math.exp(summary[label]["micro_token_nll"])
    write_json(directory/"summary.json",summary)
    figure_prefix=stage.replace("/","_")
    plot_positions(dict(baseline=base,candidate=candidate),ROOT/"figures"/(figure_prefix+"_nll_vs_position.png"))
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(8,4)); xs=np.arange(len(out["per_book"]))
    ax.scatter(xs,[r["delta"] for r in out["per_book"]]); ax.axhline(0,color="gray",linewidth=1)
    ax.axhline(out["paired_macro_delta_nll"],color="navy",label="equal-book paired mean")
    ax.axhspan(*out["bootstrap_ci95"],alpha=.12,label="book-cluster95% CI")
    ax.set_xticks(xs,[r["book_id"] for r in out["per_book"]],rotation=45); ax.set(ylabel="candidate − baseline NLL (nats/token)"); ax.legend(); fig.tight_layout(); fig.savefig(ROOT/"figures"/(figure_prefix+"_per_book_delta.png"),dpi=180); plt.close(fig)
    return dict(state="complete",claim_status=out["claim_status"])


def pilots(spec,manifest):
    directory=ROOT/"results/pilots"; directory.mkdir(parents=True,exist_ok=True)
    paths=[p for group in spec.values() for p in group]
    if any(not (ROOT/p).exists() for p in paths):
        write_json(directory/"status.json",dict(state="pending",claim_status=None))
        return dict(state="pending")
    baseline=load_runs(spec["streaming"]); rows=[]
    for method in ["h1_adaptive_sink","h2_sink_selection"]:
        candidate=load_runs(spec[method])
        paired=analyze_pairs([r for _,r in baseline],[r for _,r in candidate],manifest,"dev")
        runtimes=lambda items:np.mean([json.loads((d/"metadata.json").read_text())["runtime_seconds"] for d,_ in items])
        peaks=lambda items:np.mean([r["peak_gpu_memory_mb"] for _,r in items])
        row=dict(method=method,paired_macro_delta_nll=paired["paired_macro_delta_nll"],ci95_low=paired["bootstrap_ci95"][0],ci95_high=paired["bootstrap_ci95"][1],runtime_ratio=float(runtimes(candidate)/runtimes(baseline)),peak_memory_ratio=float(peaks(candidate)/peaks(baseline)),n_books=3)
        row["cost_acceptable"]=row["runtime_ratio"]<=1.10 and row["peak_memory_ratio"]<=1.10
        rows.append(row); write_json(directory/(method+"_paired.json"),paired)
    write_csv(directory/"comparison.csv",rows)
    winners=[r for r in rows if r["paired_macro_delta_nll"]<0 and r["cost_acceptable"]]
    nominated=sorted(winners,key=lambda r:(r["paired_macro_delta_nll"],r["runtime_ratio"],r["method"]))[0]["method"] if winners else "h1_adaptive_sink"
    write_json(directory/"selection_proposal.json",dict(nominated_method=nominated,human_decision="pending",basis="preregistered quality/cost rule; H1 negative-result fallback",rows=rows))
    return dict(state="complete",nominated_method=nominated,human_decision="pending")


def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("--manifest",default="results/final_input_manifest.json"); a=p.parse_args()
    spec=json.loads(Path(a.manifest).read_text()); assets=json.loads((ROOT/"data/assets_manifest.json").read_text()); (ROOT/"figures").mkdir(exist_ok=True)
    status=dict(built_at=now(),input_manifest_sha256=file_hash(a.manifest))
    status["diagnostics"]=build_diagnostics(spec["diagnostics"])
    status["reproduction"]=scientific("reproduction",spec["reproduction"],assets)
    status["pilots"]=pilots(spec["pilots"],assets)
    status["improvement"]=scientific("improvement",spec["improvement"],assets) if spec.get("improvement") else dict(state="pending_real_method_selection")
    status["ablations"]={}
    for name,control in spec.get("ablations",{}).items():
        status["ablations"][name]=scientific("ablations/"+name,control,assets)
    write_json(ROOT/"results/completion.json",status)
    (ROOT/"tables").mkdir(exist_ok=True)
    import shutil
    shutil.copyfile(ROOT/"results/diagnostics/comparison.csv",ROOT/"tables/diagnostic_comparison.csv")
    index=[]
    for path in spec["diagnostics"]:
        result=json.loads((ROOT/path).read_text()); directory=Path(path).parent
        index.append(dict(claim_id=result["run_id"],role="measured_single_book_diagnostic",value=result["macro_book_nll"],run_id=result["run_id"],source_commit=result["git_commit"],config_path=str(directory/"config_used.json"),metrics_path=path,raw_path=str(directory/"books"/result["book_ids"][0]/"position_nll.npz"),result_sha256=file_hash(ROOT/path)))
    index.append(dict(claim_id="central_claim",role=status["reproduction"]["state"],value="not yet evaluated" if status["reproduction"]["state"]!="complete" else status["reproduction"]["claim_status"],run_id="see final_input_manifest",source_commit="see per-run metadata",config_path="configs/reproduction_matrix.yaml",metrics_path="results/reproduction/paired_result.json" if status["reproduction"]["state"]=="complete" else "results/reproduction/status.json",raw_path="see final_input_manifest",result_sha256="pending" if status["reproduction"]["state"]!="complete" else file_hash(ROOT/"results/reproduction/paired_result.json")))
    write_csv(ROOT/"results/claim_to_artifact.csv",index)
    artifacts=[]
    for folder in ["results","figures"]:
        for path in sorted((ROOT/folder).rglob("*")):
            if path.is_file() and path.name!="build_provenance.json": artifacts.append(dict(path=str(path.relative_to(ROOT)),sha256=file_hash(path)))
    write_json(ROOT/"results/build_provenance.json",dict(command=[sys.executable]+sys.argv,input_runs=spec,artifacts=artifacts,aggregation="equal-book512-step bins starting1025; late-bin book coverage CSV",parameters=dict(bin_size=512,bootstrap_seed=0,n_boot=10000)))
    print(json.dumps(status,indent=2))


if __name__=="__main__": main()
