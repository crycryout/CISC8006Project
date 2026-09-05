# Claim Map — Week 4 Draft

**Status: DRAFT.** Instructor review (7–13 Sept) is ongoing; this map must not be treated as frozen until the claim freeze on 2026-09-13. Any instructor-requested change is documented in the revision log below.

**Maps to central claim (v1.1):**

> On a fixed PG19 evaluation using Pythia-2.8B and a 1024-token KV-cache budget, StreamingLLM retaining four initial attention-sink tokens together with recent tokens achieves lower post-overflow token negative log-likelihood (and therefore lower perplexity under the same aggregation) than pure window attention.

## 1. Assumptions

- **A1 (mechanism).** GPT-NeoX/Pythia allocates large attention mass to the first few tokens ("attention sink"); evicting them while caching only recent tokens destabilizes attention and raises NLL (paper §2, Fig. 2).
- **A2 (faithful at scale).** The sink phenomenon and the window-vs-streaming gap are observable at 2.8B scale on a few thousand tokens per book, not only at the paper's 4M-token scale. The gap is expected to grow with processed length after overflow; we only need enough post-overflow positions to detect it.
- **A3 (KV budget interpretation).** "1024-token budget" = 1024 retained KV positions per layer per arm: window keeps the latest 1024; streaming keeps positions {0..3} ∪ latest 1020. Both arms therefore have identical worst-case KV memory; the comparison isolates *which* positions are kept.
- **A4 (position handling).** Both arms use the official implementation's default position handling for Pythia (implicit `position_ids` derived from current cache length; no RoPE re-mapping). Pos-shift variants, if run, are secondary evidence only.
- **A5 (determinism).** Under fixed seeds, single-book sequential decoding with greedy teacher forcing is deterministic up to GPU nondeterminism; run-to-run NLL variation is dominated by book-level variation, which is our uncertainty unit.

## 2. Baselines

| Arm | Configuration | Role |
|---|---|---|
| A — Window | `sink=0, recent=1024` | primary baseline (the paper's failing case) |
| B — StreamingLLM | `sink=4, recent=1020` | method under test |

Secondary/reference arms (not part of the primary comparison): full cache no-eviction upper reference on truncated prefixes; sink-count sensitivity `0,1,2,4,8`; pos-shift variant.

## 3. Data / split

- **Source:** PG19 **test** split (DeepMind, via Hugging Face `deepmind/pg19`, parquet files checksummed in `data_manifest.md`).
- **Preregistration:** 10 book IDs selected **before any method-performance look**, recorded and frozen in `data_manifest.md`; identical token ranges per book for both arms.
- **Scoring region:** NLL-array indices `idx ≥ 1025`, where `nlls[idx]` scores the prediction of token `idx+1` (post-overflow: the official implementation evicts *after* each forward, so step 1025 is the first prediction made under an already-evicted cache; indexing convention in `protocol.md` §3), on a fixed max-tokens-per-book cap (frozen before final runs on compute grounds only, see `compute_budget.md`).
- **Never** select books by observed method performance.

## 4. Metrics

- **Primary:** token-level mean NLL on the scored region, per book → paired `ΔNLL = NLL_B − NLL_A` per book → paired mean + bootstrap 95% CI over books (10 books, resampling books).
- **Derived:** perplexity = exp(mean NLL).
- **Systems (secondary):** peak GPU memory; KV length over time (constant-budget verification); optional decode latency vs processed length.
- **Reporting discipline:** aggregate uncertainty over **books**, never treat within-book tokens as independent replicates.

## 5. Expected result

- If the paper's mechanism transfers: `ΔNLL < 0` (streaming beats window) with 95% CI excluding 0, and the NLL-vs-position curve for window attention degrades after overflow while streaming stays flat — mirroring paper Fig. 4 shape at smaller scale.

## 6. Falsification condition

The claim is **not supported** if, under a valid protocol (same books/ranges/precision/scorer, post-overflow region included):

- paired mean `ΔNLL ≥ 0` with 95% CI excluding 0 → **not recovered**; or
- the 95% CI includes 0 → **inconclusive**.

Any such outcome is reported as-is; a diagnosis follows the SKILL §11 order (tokenizer/revision → preprocessing → cache indices/position IDs → precision → NLL masking → chunking → library drift → hardware).

## 7. Threats to validity

| # | Threat | Direction | Mitigation |
|---|---|---|---|
| T1 | Scale gap: 2.8B + few-thousand-token books vs paper's 4M tokens may shrink the window-vs-streaming gap toward zero | false negative (inconclusive) | preregistered decision rule accepts inconclusive; record gap-vs-position slope as secondary evidence |
| T2 | Position-ID mismatch between arms after eviction (implicit positions restart from cache length) | confound favoring either arm | cache-index + position-id oracle (`audit/`); pos-shift variant as secondary evidence |
| T3 | Official code expects `transformers==4.33.0` legacy KV tuple; newer stacks change cache internals | breaks eviction silently | pin 4.33.0; compatibility changes isolated in dedicated commits with logs |
| T4 | fp16 numerics on H800 differ from the paper's stated hardware (A6000 for its efficiency benchmarks, §4.5; the paper does not state hardware for its PG19 perplexity runs) | noise in NLL | same precision both arms; paired design; record GPU/driver in every run |
| T5 | PG19 preprocessing/concatenation drift (whitespace, book headers) | shifts absolute NLL | frozen tokenization path; checksummed local parquet; same tokens both arms |
| T6 | Book selection bias | false positive | preregistered book list frozen before performance looks |
| T7 | Scoring-region leakage (scoring pre-overflow warm-up tokens) inflates apparent equivalence | false negative | mask all steps < 1025 in the scorer |
| T8 | Compute ceiling forces < 10 books | wider CI | reduce book count **before** final reproduction, document approved rescope |

## Revision log

| Date | Change | Source |
|---|---|---|
| 2026-09-05 | Initial draft | team + AI assistant (see `agent_ledger.md`) |
