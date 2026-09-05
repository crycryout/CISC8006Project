#!/usr/bin/env python
"""Paired analysis: window vs streaming over preregistered books.

Inputs : two result.json files produced by scripts/eval_ppl.py
Outputs: per-book NLL table, paired dNLL per book, paired mean,
         paired-bootstrap 95% CI (10k resamples over books),
         classification under the preregistered decision rule (claim.md).
"""

import argparse
import json

import numpy as np


def load_per_book(path):
    r = json.load(open(path))
    return r, {b["book_id"]: b["mean_nll_scored"] for b in r["per_book"]}


def paired_bootstrap(deltas, n_boot=10_000, seed=0):
    rng = np.random.default_rng(seed)
    n = len(deltas)
    boots = rng.choice(deltas, size=(n_boot, n), replace=True).mean(axis=1)
    return float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--window", required=True)
    p.add_argument("--streaming", required=True)
    p.add_argument("--out", required=True, help="run dir to write paired_result.json")
    p.add_argument("--n_boot", type=int, default=10_000)
    args = p.parse_args()

    wr, w = load_per_book(args.window)
    sr, s = load_per_book(args.streaming)

    shared = sorted(set(w) & set(s))
    if len(shared) < len(w) or len(shared) < len(s):
        print(f"WARNING: book mismatch window={sorted(w)} streaming={sorted(s)}")

    deltas = {b: s[b] - w[b] for b in shared}
    arr = np.array([deltas[b] for b in shared])
    mean = float(arr.mean())
    lo, hi = paired_bootstrap(arr, args.n_boot)

    if lo < 0 and hi < 0:
        verdict = "RECOVERED (paired mean dNLL < 0, 95% CI entirely below 0)"
    elif lo > 0 and hi > 0:
        verdict = "NOT RECOVERED (95% CI entirely above 0)"
    else:
        verdict = "INCONCLUSIVE (95% CI crosses 0)"

    out = {
        "window_run": wr["run_id"],
        "streaming_run": sr["run_id"],
        "books": shared,
        "per_book_nll_window": {b: w[b] for b in shared},
        "per_book_nll_streaming": {b: s[b] for b in shared},
        "per_book_dNLL": deltas,
        "paired_mean_dNLL": mean,
        "bootstrap_ci95": [lo, hi],
        "decision_rule": "recovered iff mean dNLL<0 and 95% CI entirely below 0",
        "verdict": verdict,
    }
    with open(f"{args.out}/paired_result.json", "w") as f:
        json.dump(out, f, indent=2)

    print(f"books={len(shared)}  paired mean dNLL={mean:+.4f}  95% CI [{lo:+.4f}, {hi:+.4f}]")
    print(verdict)


if __name__ == "__main__":
    main()
