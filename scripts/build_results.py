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
    counts=sorted({row["n_books"] for row in coverage})
    ax.set_title("Book coverage per bin: "+" to ".join(map(str,counts))+" (exact coverage in companion CSV)",fontsize=9)
    ax.legend(); fig.tight_layout(); fig.savefig(path,dpi=180); plt.close(fig)
    write_csv(path.with_suffix(".csv"),coverage)


def build_diagnostics(paths):
    out=ROOT/"results/diagnostics"; out.mkdir(parents=True,exist_ok=True)
    rows=[]; items={}
    for path in paths:
        directory=ROOT/Path(path).parent
        validate_run(directory)
        result=json.loads((ROOT/path).read_text()); contract=result["contract"]
        rows.append(dict(run_id=result["run_id"],method=result["method"],position_policy=contract["position_policy"],scorer_precision=contract["scorer_precision"],book_ids=";".join(result["book_ids"]),scored_tokens=result["scored_tokens"],macro_book_nll=result["macro_book_nll"],micro_token_ppl=result["micro_token_ppl"],predictions_per_second=result["predictions_per_second"],peak_gpu_memory_mb=result["peak_gpu_memory_mb"],retained_kv_plateau_bytes=max(x["kv_bytes"] for x in result["per_book"][0]["cache_trace"]),source_commit=result["git_commit"],result_sha256=file_hash(ROOT/path)))
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
    lengths=lambda trace:[(x["step"],x["retained_length"]) for x in trace]
    if any(lengths(entries[0][1]["per_book"][0]["cache_trace"])!=lengths(first) for entries in items.values()):
        raise ValueError("diagnostic arms differ in actual retained length; shared-length figure is invalid")
    fig,ax=plt.subplots(figsize=(7,3.5)); ax2=ax.twinx()
    ax.plot([x["step"] for x in first],[x["retained_length"] for x in first],color="navy",label="retained length")
    for label,entries in items.items():
        trace=entries[0][1]["per_book"][0]["cache_trace"]
        ax2.plot([x["step"] for x in trace],[x["kv_bytes"]/1024**2 for x in trace],linestyle="--",label=label+" KV MiB")
    ax.set(xlabel="prediction step",ylabel="retained KV positions"); ax2.set_ylabel("tensor K+V bytes (MiB)")
    ax2.legend(fontsize=7,loc="lower right")
    ax.set_title("Same retained length; measured legacy480MiB / faithful320MiB",fontsize=9)
    fig.tight_layout(); fig.savefig(ROOT/"figures/diagnostic_kv_bytes.png",dpi=180); plt.close(fig)
    return dict(state="diagnostic_complete",runs=[r["run_id"] for r in rows])


def load_runs(paths):
    records=[]
    for path in paths:
        directory=ROOT/Path(path).parent; validate_run(directory)
        records.append((directory,json.loads((ROOT/path).read_text())))
    return records


def plot_cache(items,path):
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,2,figsize=(9,3.5)); rows=[]
    for label,records in items.items():
        points={}
        for _,result in records:
            for book in result["per_book"]:
                for point in book["cache_trace"]:
                    if point["retained_length"]>1024 or point["forward_length"]>1025:
                        raise ValueError("measured formal cache exceeds the frozen budget")
                    points.setdefault(point["step"],[]).append(point)
        xs=sorted(points)
        for step in xs:
            values=points[step]
            rows.append(dict(method=label,step=step,n_book_seed_pairs=len(values),
                             retained_min=min(p["retained_length"] for p in values),retained_max=max(p["retained_length"] for p in values),
                             forward_max=max(p["forward_length"] for p in values),kv_bytes_min=min(p["kv_bytes"] for p in values),kv_bytes_max=max(p["kv_bytes"] for p in values)))
        axes[0].plot(xs,[np.mean([p["retained_length"] for p in points[x]]) for x in xs],label=label)
        axes[1].plot(xs,[np.mean([p["kv_bytes"] for p in points[x]])/1024**2 for x in xs],label=label)
    axes[0].set(xlabel="prediction step",ylabel="retained KV positions"); axes[1].set(xlabel="prediction step",ylabel="actual tensor K+V bytes (MiB)")
    for ax in axes: ax.legend()
    fig.tight_layout(); fig.savefig(path,dpi=180); plt.close(fig)
    write_csv(path.with_suffix(".csv"),rows)


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
    write_json(directory/"status.json",dict(state="complete",claim_status=out["claim_status"],n_books=out["n_books"],seeds=summary["seeds"],paired_result_sha256=file_hash(directory/"paired_result.json")))
    figure_prefix=stage.replace("/","_")
    plot_positions(dict(baseline=base,candidate=candidate),ROOT/"figures"/(figure_prefix+"_nll_vs_position.png"))
    plot_cache(dict(baseline=base,candidate=candidate),ROOT/"figures"/(figure_prefix+"_cache.png"))
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
    decision=json.loads((ROOT/"docs/approval_decisions.json").read_text())["selected_improvement"]
    recorded=decision.get("method")==nominated
    selection_status="recorded_owner_delegated_rule" if recorded else "ready_for_owner_delegated_rule"
    proposal_path=directory/"selection_proposal.json"
    if recorded:
        frozen_proposal=json.loads(proposal_path.read_text())
        if frozen_proposal["nominated_method"]!=nominated or frozen_proposal["rows"]!=rows:
            raise ValueError("pilot evidence changed after the recorded selection")
    else:
        write_json(proposal_path,dict(nominated_method=nominated,selection_status=selection_status,execution_authorization=decision.get("status"),basis="preregistered quality/cost rule; H1 negative-result fallback",rows=rows))
    write_json(directory/"status.json",dict(state="complete",selection_status=selection_status,nominated_method=nominated))
    return dict(state="complete",nominated_method=nominated,selection_status=selection_status)


def build_tables(spec,status):
    """Export the report tables and measured quality/cost comparison together."""
    import shutil
    tables=ROOT/"tables"; tables.mkdir(exist_ok=True)
    shutil.copyfile(ROOT/"results/diagnostics/comparison.csv",tables/"diagnostic_comparison.csv")
    stages=[("reproduction",status["reproduction"]),("improvement",status["improvement"])]
    stages.extend(("ablations/"+name,state) for name,state in status["ablations"].items())
    rows=[]
    for stage,state in stages:
        if state["state"]!="complete": continue
        summary=json.loads((ROOT/"results"/stage/"summary.json").read_text())
        baseline,candidate=summary["baseline"],summary["candidate"]
        row=dict(comparison=stage,n_books=summary["n_books"],seeds=";".join(map(str,summary["seeds"])),
                 baseline_macro_nll=baseline["macro_book_nll"],candidate_macro_nll=candidate["macro_book_nll"],
                 baseline_macro_derived_ppl=baseline["macro_derived_ppl"],candidate_macro_derived_ppl=candidate["macro_derived_ppl"],
                 baseline_micro_nll=baseline["micro_token_nll"],candidate_micro_nll=candidate["micro_token_nll"],
                 baseline_micro_ppl=baseline["micro_token_ppl"],candidate_micro_ppl=candidate["micro_token_ppl"],
                 paired_macro_delta_nll=summary["paired_macro_delta_nll"],ci95_low=summary["bootstrap_ci95"][0],ci95_high=summary["bootstrap_ci95"][1],
                 claim_status=summary["claim_status"],baseline_runtime_seconds=baseline["runtime_seconds"],candidate_runtime_seconds=candidate["runtime_seconds"],
                 runtime_ratio=candidate["runtime_seconds"]/baseline["runtime_seconds"],
                 baseline_peak_gpu_memory_mb=baseline["peak_gpu_memory_mb"],candidate_peak_gpu_memory_mb=candidate["peak_gpu_memory_mb"],
                 peak_memory_ratio=candidate["peak_gpu_memory_mb"]/baseline["peak_gpu_memory_mb"])
        rows.append(row)
        shutil.copyfile(ROOT/"results"/stage/"per_book.csv",tables/(stage.replace("/","_")+"_per_book.csv"))
    if rows: write_csv(tables/"scientific_summary.csv",rows)
    if status["pilots"]["state"]=="complete":
        shutil.copyfile(ROOT/"results/pilots/comparison.csv",tables/"pilot_comparison.csv")
    write_csv(tables/"paper_settings.csv",[
        dict(dimension="model",paper="Pythia2.8B among multiple model families",project="Pinned Pythia2.8B only",source="arXiv2309.17453v4 section4.1; data/assets_manifest.json"),
        dict(dimension="position mechanism",paper="Raw cached K, cache-relative RoPE",project="Pinned official every-layer patch in both methods",source="arXiv2309.17453v4 section3.2; tests/test_position_reference.py"),
        dict(dimension="PG19 stream",paper="Concatenated books",project="Original10 books independently reset; cap16384; short book7141",source="arXiv2309.17453v4 section4.1; protocol.md"),
        dict(dimension="KV budget",paper="Pythia1024 retained positions",project="1024 retained; forward temporarily1025",source="arXiv2309.17453v4 section4.1; per-book cache_trace"),
        dict(dimension="primary metric",paper="Perplexity curves",project="Equal-book post-overflow paired NLL; book bootstrap",source="protocol.md; results/reproduction/paired_result.json"),
        dict(dimension="hardware",paper="Separate efficiency benchmark hardware; PG19 hardware unspecified",project="H800 MIG2g.20gb,30SM; matched instance within each seed",source="docs/paper_comparison.md; per-run registration.json"),
    ])
    cost_rows=[r for r in rows if r["comparison"]!="reproduction"]
    if cost_rows:
        import matplotlib.pyplot as plt
        fig,axes=plt.subplots(1,2,figsize=(10,4))
        for row in cost_rows:
            label=row["comparison"].replace("ablations/","")
            for ax,key in zip(axes,("runtime_ratio","peak_memory_ratio")):
                point=ax.plot(row[key],row["paired_macro_delta_nll"],"o",label=label)[0]
                ax.vlines(row[key],row["ci95_low"],row["ci95_high"],color=point.get_color())
        for ax in axes:
            ax.axhline(0,color="gray",linewidth=1); ax.axvline(1,color="gray",linewidth=1,linestyle="--")
            ax.set_ylabel("candidate − fixed-four NLL (nats/token)")
        axes[0].set_xlabel("registered-run runtime / matched baseline"); axes[1].set_xlabel("peak allocated memory / matched baseline")
        axes[0].legend(fontsize=7); fig.suptitle("Full test and development controls (different book sets)",fontsize=10)
        fig.tight_layout(); fig.savefig(ROOT/"figures/improvement_quality_cost.png",dpi=180); plt.close(fig)
    if spec.get("improvement") and status["improvement"]["state"]=="complete":
        selection=[]
        for path in spec["improvement"]["candidate"]:
            result=json.loads((ROOT/path).read_text())
            for book in result["per_book"]:
                selection.append(dict(run_id=result["run_id"],seed=result["contract"]["seed"],book_id=book["book_id"],
                                      selection=json.dumps(book["selection"],sort_keys=True),
                                      calibration_host_wall_seconds=book["calibration_seconds"],book_runtime_seconds=book["runtime_seconds"],
                                      mean_nll_scored=book["mean_nll_scored"]))
        write_csv(tables/"improvement_book_selections.csv",selection)


def raw_index(spec):
    paths=set(spec["diagnostics"])
    for group in [spec["reproduction"],spec["pilots"],spec.get("improvement") or {},*spec.get("ablations",{}).values()]:
        for value in group.values():
            if isinstance(value,list): paths.update(value)
    rows=[]
    for path in sorted(paths):
        if not (ROOT/path).is_file(): continue
        result=json.loads((ROOT/path).read_text()); directory=Path(path).parent
        for book in result["per_book"]:
            raw=directory/"books"/book["book_id"]/"position_nll.npz"
            metrics=directory/"books"/book["book_id"]/"metrics.json"
            rows.append(dict(run_id=result["run_id"],phase=result["phase"],method=result["method"],seed=result["contract"]["seed"],
                             book_id=book["book_id"],input_tokens=book["input_tokens"],scored_tokens=book["scored_tokens"],
                             source_commit=result["git_commit"],numerical_source_sha256=result["contract"]["numerical_source_sha256"],
                             device_uuid=result.get("device_uuid","legacy metadata"),config_path=str(directory/"config_used.json"),result_path=path,
                             result_sha256=file_hash(ROOT/path),metrics_path=str(metrics),metrics_sha256=file_hash(ROOT/metrics),
                             raw_path=str(raw),raw_sha256=file_hash(ROOT/raw)))
    write_csv(ROOT/"results/raw_artifact_index.csv",rows)


def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("--manifest",default="results/final_input_manifest.json"); a=p.parse_args()
    spec=json.loads(Path(a.manifest).read_text()); assets=json.loads((ROOT/"data/assets_manifest.json").read_text()); (ROOT/"figures").mkdir(exist_ok=True)
    status=dict(built_at=now(),input_manifest_sha256=file_hash(a.manifest))
    status["diagnostics"]=build_diagnostics(spec["diagnostics"])
    status["reproduction"]=scientific("reproduction",spec["reproduction"],assets)
    status["pilots"]=pilots(spec["pilots"],assets)
    status["improvement"]=scientific("improvement",spec["improvement"],assets) if spec.get("improvement") else dict(state="pending_registered_pilot_selection")
    status["ablations"]={}
    for name,control in spec.get("ablations",{}).items():
        status["ablations"][name]=scientific("ablations/"+name,control,assets)
    write_json(ROOT/"results/completion.json",status)
    build_tables(spec,status)
    raw_index(spec)
    index=[]
    for path in spec["diagnostics"]:
        result=json.loads((ROOT/path).read_text()); directory=Path(path).parent
        index.append(dict(claim_id=result["run_id"],role="measured_single_book_diagnostic",value=result["macro_book_nll"],run_id=result["run_id"],source_commit=result["git_commit"],config_path=str(directory/"config_used.json"),metrics_path=path,raw_path=str(directory/"books"/result["book_ids"][0]/"position_nll.npz"),result_sha256=file_hash(ROOT/path)))
    index.append(dict(claim_id="central_claim",role=status["reproduction"]["state"],value="not yet evaluated" if status["reproduction"]["state"]!="complete" else status["reproduction"]["claim_status"],run_id="see final_input_manifest",source_commit="see per-run metadata",config_path="configs/reproduction_matrix.yaml",metrics_path="results/reproduction/paired_result.json" if status["reproduction"]["state"]=="complete" else "results/reproduction/status.json",raw_path="see final_input_manifest",result_sha256="pending" if status["reproduction"]["state"]!="complete" else file_hash(ROOT/"results/reproduction/paired_result.json")))
    for name,state in [("improvement",status["improvement"]),*(("ablations/"+name,state) for name,state in status["ablations"].items())]:
        if name=="improvement" and not spec.get("improvement"): continue
        path="results/"+name+("/paired_result.json" if state["state"]=="complete" else "/status.json")
        index.append(dict(claim_id=name,role=state["state"],value=state.get("claim_status","not yet evaluated"),run_id="see final_input_manifest",source_commit="see raw_artifact_index.csv",config_path="see per-run config_used.json",metrics_path=path,raw_path="results/raw_artifact_index.csv",result_sha256=file_hash(ROOT/path)))
    write_csv(ROOT/"results/claim_to_artifact.csv",index)
    artifacts=[]
    for folder in ["results","figures","tables"]:
        for path in sorted((ROOT/folder).rglob("*")):
            if path.is_file() and path.name!="build_provenance.json": artifacts.append(dict(path=str(path.relative_to(ROOT)),sha256=file_hash(path)))
    write_json(ROOT/"results/build_provenance.json",dict(command=[sys.executable]+sys.argv,builder_sha256=file_hash(Path(__file__)),input_manifest_sha256=file_hash(a.manifest),input_runs=spec,artifacts=artifacts,aggregation="equal-book512-step bins starting1025; late-bin book coverage CSV",parameters=dict(bin_size=512,bootstrap_seed=0,n_boot=10000)))
    print(json.dumps(status,indent=2))


if __name__=="__main__": main()
