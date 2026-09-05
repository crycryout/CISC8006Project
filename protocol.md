# Reproduction Protocol

**Status: SKELETON — Week 5 deliverable (due 2026-09-16).**
This file becomes the frozen protocol only after instructor review completes (claim freeze 2026-09-13). Sections marked *(measured)* are filled from R0001+.

## 1. Arms

| Arm | sink_tokens | recent_tokens | Total KV budget |
|---|---|---|---|
| A window | 0 | 1024 | 1024 |
| B streaming | 4 | 1020 | 1024 |

## 2. Fixed factors (both arms)

Model `EleutherAI/pythia-2.8b` @ revision *(pin in data_manifest.md)*; default tokenizer; fp16; same PG19 test books (preregistered list, `data_manifest.md`); same max tokens per book *(frozen after R0001, see compute_budget.md)*; same scored region (first scored NLL-array index = 1025, defined precisely in §3); same scorer code; same GPU (1× H800 PCIe 80GB, driver pinned in environment/system-info.txt).

## 3. Procedure per book

**Indexing convention (used everywhere — protocol, code, analysis):** with teacher forcing, step `idx` feeds token `idx` and scores the prediction of token `idx+1`, i.e. `nlls[idx] = −log P(token_{idx+1} | tokens ≤ idx, arm-specific KV cache)`. The array `nlls` has length `tokens−1`; `idx` runs from 0. **First scored index = `min_scored_idx = cache_budget + 1 = 1025`**: eviction happens *after* each forward pass, so step 1025 is the first prediction made under an already-evicted cache. Scored set = `{nlls[idx] : idx ≥ 1025}`.

1. Tokenize full book text with the frozen path (no truncation at tokenization time).
2. Feed tokens sequentially with teacher forcing, `use_cache=True`, one token per step (official evaluation semantics, `third_party/streaming-llm/examples/eval_long_ppl.py`).
3. After each step, apply arm-specific eviction (`StartRecentKVCache`): A keeps latest 1024; B keeps {0..3} ∪ latest 1020.
4. Record per-position NLL of the next token; scored region = steps ≥ 1025 (first prediction made under an already-evicted cache; see `scripts/eval_ppl.py` "off-by-one note").

## 4. Aggregation

Per-book mean NLL over scored positions → paired `ΔNLL_B−A` per book → paired mean, bootstrap 95% CI (10,000 resamples over books) → decision per `claim.md` §Decision rule.

## 5. Secondary measurements

- NLL vs position (binned) per arm
- sink-count sensitivity {0,1,2,4,8} on a fixed book subset
- KV-length trace + peak GPU memory (constant-budget verification)
- optional: decode latency vs processed length

## 6. Diagnostics plan

If outcome deviates from expectation, follow SKILL §11 order: tokenizer/revision → PG19 preprocessing → cache indices/position IDs → precision → NLL masking → chunking → library drift → hardware. One factor per diagnostic run; new run ID each time.

## 7. Agent-use policy

See `agent_policy.md` (due in full at Week 5 alongside this protocol).
