# Target Claim v1.1

**Status:** ready for submission by 2026-09-06 23:59 (course portal, *Final Project Paper and Claim*); **not yet submitted as of 2026-09-05**.
After the portal entry is actually made, update this line to: `Status: submitted 2026-09-06 at HH:MM HKT`. Under instructor review 2026-09-07..13; target freeze 2026-09-13.
**Change policy:** after the freeze, any change to paper, model family, dataset, primary metric, or reproduction tier requires explicit instructor approval (see `agent_policy.md` stop conditions and SKILL §17).

## Central claim (one falsifiable relation)

> On a fixed PG19 evaluation using Pythia-2.8B and a 1024-token KV-cache budget, StreamingLLM retaining four initial attention-sink tokens together with recent tokens achieves lower post-overflow token negative log-likelihood (and therefore lower perplexity under the same aggregation) than pure window attention.

This is the exact text to be submitted to the course portal (see `submission/week3_submission.md`). It contains exactly one testable relation and no improvement hypotheses. The metric named in the claim (token NLL, with perplexity as a strictly derived quantity under the same aggregation) is identical to the preregistered primary metric and decision rule below — no metric ambiguity between claim, protocol, and test.

## Full operational specification

| Item | Value |
|---|---|
| Model | `EleutherAI/pythia-2.8b` (revision pinned in `data_manifest.md`) |
| Tokenizer | model-default GPT-NeoX BPE tokenizer (revision pinned) |
| Dataset | PG19 **test** split, preregistered book list (default: 10 books, `data_manifest.md`) |
| Cache budget | 1024 KV positions (both arms) |
| Baseline A — window | `sink_tokens = 0`, `recent_tokens = 1024` |
| Method B — streaming | `sink_tokens = 4`, `recent_tokens = 1020` |
| Primary metric | token-level NLL on scored positions (post-overflow region) |
| Derived metric | perplexity = exp(mean NLL) |
| Systems metrics | peak KV-cache / GPU memory; optional decode latency |
| Precision | fp16 (official evaluation default; recorded per run) |
| Compute ceiling | ≤ 20 GPU-hours total (initial) |
| Uncertainty unit | book (paired); paired bootstrap 95% CI over books |

## Decision rule (preregistered)

The primary claim is **recovered** only if all of the following hold:

1. Both arms use the same model, tokenizer, books, token ranges, cache budget, precision, and scoring code.
2. The evaluation includes positions after the 1024-token cache has overflowed. Under the official eviction semantics (eviction happens *after* each forward pass), the first prediction made under an already-evicted cache is step index 1025; the scored region is therefore NLL-array indices `idx ≥ 1025`, where `nlls[idx]` scores the prediction of token `idx+1` (see `protocol.md` §3 indexing convention).
3. Paired mean `ΔNLL = NLL_streaming − NLL_window < 0` over books.
4. The paired-bootstrap 95% CI for `ΔNLL` lies entirely below 0.

If the CI crosses 0 → **inconclusive**. If the protocol is valid and the CI lies above 0 → **not recovered**. We do not rewrite the claim to match observed results.

## What is explicitly out of scope

- The paper's 4-million-token runs; all model families (Llama-2, MPT, Falcon); fine-tuning with a dedicated sink token; throughput/speedup claims (22.2× sliding-window recomputation comparison); LongBench downstream tasks.
- Any improvement hypothesis (deferred to Week 8 portfolio; see SKILL §12).
