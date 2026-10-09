#!/usr/bin/env python3
"""Show the real paired result and one raw-artifact chain without allocating a GPU."""
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.io_utils import file_hash
from scripts.validate_runs import validate_run


def main():
    inputs=json.loads((ROOT/"results/final_input_manifest.json").read_text())
    completion=json.loads((ROOT/"results/completion.json").read_text())
    print("Owner-authorized study; methods matched on H800 MIG 2g.20gb; no GPU inference in this demo.")
    for stage in ("reproduction","improvement"):
        if completion.get(stage,{}).get("state")!="complete":
            print(stage+": registered execution pending; no scientific verdict.")
            continue
        summary_path=ROOT/"results"/stage/"summary.json"
        value=json.loads(summary_path.read_text()); low,high=value["bootstrap_ci95"]
        print(f"{stage}: delta={value['paired_macro_delta_nll']:.6f}, book-CI95=[{low:.6f},{high:.6f}], {value['claim_status']}")
        print(f"  {value['n_books']} books; actual seeds={value['seeds']}; primary equal-book NLL, secondary micro PPL.")
        print(f"  macro NLL {value['baseline']['macro_book_nll']:.6f} -> {value['candidate']['macro_book_nll']:.6f}")
        print(f"  micro PPL {value['baseline']['micro_token_ppl']:.4f} -> {value['candidate']['micro_token_ppl']:.4f}")
        candidate_path=inputs[stage]["candidate"][0]
        directory=ROOT/Path(candidate_path).parent
        check=validate_run(directory)
        result=json.loads((ROOT/candidate_path).read_text()); first=result["per_book"][0]
        raw=directory/"books"/first["book_id"]/"position_nll.npz"
        print("  validated run="+check["run_id"]+"; source="+result["git_commit"])
        print("  result SHA256="+check["result_sha256"])
        print("  book="+first["book_id"]+"; scored="+str(first["scored_tokens"])+"; raw SHA256="+file_hash(raw))
        figure=ROOT/"figures"/(stage+"_per_book_delta.png")
        print("  figure="+str(figure.relative_to(ROOT))+"; SHA256="+file_hash(figure))
        print("  summary SHA256="+file_hash(summary_path))
    print("Complete evidence index: results/raw_artifact_index.csv and results/build_provenance.json")
    print("Actual peer review, individual defense and course submission are separately recorded human activities.")


if __name__=="__main__": main()
