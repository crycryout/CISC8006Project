#!/usr/bin/env python
"""Evaluation harness (v0) — CISC8006 StreamingLLM reproduction.

Mirrors the official evaluation semantics of
third_party/streaming-llm/examples/eval_long_ppl.py (token-by-token teacher
forcing, `StartRecentKVCache` eviction after every step, fp16, implicit
position ids), with three auditable differences:

  1. data source  : local PG19 test .txt files (checksummed in data_manifest.md)
                    instead of `load_dataset("pg19", ...)` — the text content is
                    identical (PG19 books are raw .txt on GCS; the HF script
                    wraps exactly those files);
  2. scored region: per-position NLLs are recorded for ALL positions and the
                    scored mask is applied at aggregation time (default: only
                    positions whose prediction was made under an already-evicted
                    cache, i.e. step index >= cache_budget + 1 = 1025;
                    see README "off-by-one note");
  3. outputs      : machine-readable result.json (course schema) + per-position
                    NLL trace for NLL-vs-position plots.

Off-by-one note (official semantics): eviction happens AFTER the forward pass.
Step idx runs on cache length idx, sees idx+1 positions, then the cache is
evicted to <= budget. The first prediction made *under an evicted cache* is
therefore step 1025 (predicting token 1026) for budget 1024. Both arms share
this semantics; it matches the official implementation exactly.

Usage:
  python scripts/eval_ppl.py --config configs/smoke.yaml
  (or explicit CLI overrides; config values are overridden by CLI flags)
"""

import argparse
import json
import os
import subprocess
import sys
import time

import torch
import yaml
from torch.nn import CrossEntropyLoss
from transformers import AutoModelForCausalLM, AutoTokenizer

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "third_party", "streaming-llm"))

from streaming_llm.kv_cache import StartRecentKVCache  # noqa: E402


def parse_args():
    p = argparse.ArgumentParser()
    # CLI flags take precedence over the config file; unset flags fall back to
    # the config, then to the default. Required-ness is validated after merge.
    p.add_argument("--config", type=str, default=None)
    p.add_argument("--run_id", type=str, default=None)
    p.add_argument("--method", type=str, default=None, choices=["window", "streaming"])
    p.add_argument("--model", type=str, default="EleutherAI/pythia-2.8b")
    p.add_argument("--model_revision", type=str, default="2a259cdd96a4beb1cdf467512e3904197345f6a9")
    p.add_argument("--book_files", type=str, nargs="+", default=None, help="path(s) to PG19 .txt")
    p.add_argument("--sink_tokens", type=int, default=None)
    p.add_argument("--recent_tokens", type=int, default=None)
    p.add_argument("--max_tokens_per_book", type=int, default=None)
    p.add_argument("--min_scored_idx", type=int, default=None,
                   help="default: cache_budget+1 (=1025); see off-by-one note")
    p.add_argument("--precision", type=str, default="fp16", choices=["fp16", "bf16", "fp32"])
    p.add_argument("--output_dir", type=str, default=None, help="default runs/<run_id>/<method>")
    args = p.parse_args()

    if args.config:
        with open(args.config) as f:
            cfg = yaml.safe_load(f) or {}
        for k, v in cfg.items():
            if getattr(args, k, None) is None and v is not None:
                setattr(args, k, v)

    missing = [f for f in ("run_id", "method", "book_files", "sink_tokens",
                           "recent_tokens", "max_tokens_per_book")
               if getattr(args, f) in (None, [])]
    if missing:
        p.error(f"missing required arguments (CLI or config): {', '.join('--' + m for m in missing)}")
    return args


def git_commit():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True).strip()
    except subprocess.CalledProcessError:
        return "uncommitted"


def load_text_tokens(tokenizer, path, max_tokens):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    enc = tokenizer(text, return_tensors="pt")
    return enc.input_ids[:, :max_tokens]


def main():
    args = parse_args()
    budget = args.sink_tokens + args.recent_tokens
    assert budget == 1024, f"primary-comparison budget must be 1024, got {budget}"
    min_scored = args.min_scored_idx if args.min_scored_idx is not None else budget + 1

    out_dir = args.output_dir or os.path.join(REPO_ROOT, "runs", args.run_id, args.method)
    os.makedirs(out_dir, exist_ok=True)

    device = "cuda"
    dtype = {"fp16": torch.float16, "bf16": torch.bfloat16, "fp32": torch.float32}[args.precision]

    tokenizer = AutoTokenizer.from_pretrained(args.model, revision=args.model_revision)
    model = AutoModelForCausalLM.from_pretrained(
        args.model, revision=args.model_revision, torch_dtype=dtype
    ).to(device)
    model.eval()

    kv_cache = StartRecentKVCache(
        start_size=args.sink_tokens, recent_size=args.recent_tokens, k_seq_dim=2, v_seq_dim=2
    )
    loss_fn = CrossEntropyLoss(reduction="none")

    per_book = []
    all_pos_nll = {}
    t0 = time.perf_counter()
    torch.cuda.reset_peak_memory_stats()

    for book_path in args.book_files:
        input_ids = load_text_tokens(tokenizer, book_path, args.max_tokens_per_book)
        seq_len = input_ids.size(1)
        past = None
        nlls = torch.zeros(seq_len - 1)
        with torch.no_grad():
            for idx in range(seq_len - 1):
                x = input_ids[:, idx: idx + 1].to(device)
                out = model(x, past_key_values=past, use_cache=True)
                logits = out.logits.view(-1, model.config.vocab_size)
                past = out.past_key_values
                label = input_ids[:, idx + 1: idx + 2].to(logits.device).view(-1)
                nlls[idx] = loss_fn(logits, label).item()
                past = kv_cache(past)

        scored = nlls[min_scored:]
        book_id = os.path.splitext(os.path.basename(book_path))[0]
        per_book.append(
            {
                "book_id": book_id,
                "tokenized_length": int(seq_len),
                "scored_tokens": int(scored.numel()),
                "mean_nll_all_positions": float(nlls.mean()),
                "mean_nll_scored": float(scored.mean()),
                "ppl_scored": float(torch.exp(scored.mean())),
                "mean_nll_by_128tok_bin": [
                    float(b.mean()) for b in torch.split(nlls, 128) if b.numel()
                ],
            }
        )
        all_pos_nll[book_id] = [float(v) for v in nlls]

    elapsed = time.perf_counter() - t0
    total_scored = sum(b["scored_tokens"] for b in per_book)
    mean_nll = float(sum(b["mean_nll_scored"] * b["scored_tokens"] for b in per_book) / max(total_scored, 1))

    result = {
        "run_id": args.run_id,
        "git_commit": git_commit(),
        "method": args.method,
        "model": args.model,
        "model_revision": args.model_revision,
        "tokenizer_revision": args.model_revision,
        "dataset": "pg19-test",
        "book_ids": [b["book_id"] for b in per_book],
        "cache_budget": budget,
        "sink_tokens": args.sink_tokens,
        "recent_tokens": args.recent_tokens,
        "precision": args.precision,
        "min_scored_idx": min_scored,
        "scored_tokens": total_scored,
        "mean_nll": mean_nll,
        "perplexity": float(torch.exp(torch.tensor(mean_nll))),
        "peak_gpu_memory_mb": int(torch.cuda.max_memory_allocated() / 1024**2),
        "elapsed_seconds": round(elapsed, 2),
        "tokens_per_second_overall": round(
            sum(b["tokenized_length"] for b in per_book) / elapsed, 2
        ),
        "per_book": per_book,
        "semantics": {
            "eviction": "official StartRecentKVCache, eviction after forward",
            "position_ids": "implicit (transformers GPT-NeoX: start at past length)",
            "harness": "scripts/eval_ppl.py mirroring examples/eval_long_ppl.py",
        },
    }

    with open(os.path.join(out_dir, "result.json"), "w") as f:
        json.dump(result, f, indent=2)
    with open(os.path.join(out_dir, "position_nll.json"), "w") as f:
        json.dump(all_pos_nll, f)
    with open(os.path.join(out_dir, "config_used.json"), "w") as f:
        json.dump(vars(args), f, indent=2)

    print(json.dumps({k: result[k] for k in
                      ["run_id", "method", "mean_nll", "perplexity", "scored_tokens",
                       "peak_gpu_memory_mb", "elapsed_seconds", "tokens_per_second_overall"]}, indent=2))


if __name__ == "__main__":
    main()
