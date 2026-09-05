# Feasibility Assessment

**Claim under assessment:** see `claim.md` (Target Claim v1).
**Ceiling:** ≤ 20 GPU-hours total; single-GPU (1× H800 PCIe 80GB) available.

## Why the paper is reproducible at our scale

1. **No training.** StreamingLLM's mechanism is inference-time KV-cache eviction; nothing is fine-tuned for the primary claim.
2. **Small inspectable intervention.** `StartRecentKVCache` is ~80 lines of PyTorch (vendored at `third_party/streaming-llm/streaming_llm/kv_cache.py`); behavior is unit-testable without a GPU (`audit/cache_index_test.py`).
3. **Cheap metric.** Token NLL needs one forward pass per token with teacher forcing — no sampling, no human eval.
4. **Public everything.** Model (`EleutherAI/pythia-2.8b`), dataset (PG19 test), official code (MIT) all reachable from our environment; HF/GitHub/PyPI direct-connect verified 2026-09-05.
5. **Memory fits trivially.** Pythia-2.8B fp16 ≈ 5.6 GB weights + 1024-position KV cache (32 layers × 1024 × 2 × 32 heads × 128 dim × 2 (K+V) × 2 bytes ≈ 0.5 GB) ≪ 80 GB. No offloading or tensor parallelism needed.

## Main feasibility risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Legacy `transformers==4.33.0` vs current torch/CUDA on H800 (sm_90) | medium | blocks official code path | compatibility changes isolated per commit with logs (SKILL §7-B); fallback: same eviction logic reimplemented against a pinned modern stack, documented as a behavior-affecting change |
| Token-by-token official eval is slow → GPU-hours underestimate | high | ceiling breach | measure tokens/s in smoke test; extrapolate per-book cost; cap max tokens/book **before** final runs |
| PG19 hub format drift (script→parquet) | medium | data not auditable | download parquet once, checksum, load locally (`data_manifest.md`) |
| Long runs interrupted (shared box) | medium | lost runs | per-run checkpointless but restartable design; book-level granularity; registry logs partial status |
| 10 books × 2 arms exceed ceiling | medium | forced rescope | preregistered fallback: reduce book count before final reproduction with documented approval |

## GPU-hour budget — measured (R0001, 2026-09-05)

Measured throughput of the official token-by-token evaluation semantics on Pythia-2.8B fp16, 1× H800:

- window `0+1024`: **32.2 tok/s**; streaming `4+1020`: **31.2 tok/s** (per-step eviction included; dominated by launch/Python overhead, GPU mostly idle, 6.9 GB peak).

Full primary pass (10 books × 2 arms × 16,384 tokens) ≈ **2.9 GPU-h**; worst case incl. sensitivity arms and diagnosis reruns ≈ 12.5 GPU-h — inside the 20 GPU-h ceiling with margin. Details and freeze decision: `compute_budget.md`.

## Scope discipline

If the official implementation cannot be made auditable within the ceiling, rescope to a **Component** reproduction (cache-eviction behavior + NLL on synthetic/short streams) **before the Week-7 gate**, with instructor approval — never a silent change.
