# Compute Budget

**Ceiling:** ≤ 20 GPU-hours total (initial, per claim.md). All numbers below are updated per run; the registry (`experiment_registry.md`) is the source of truth for realized spend.

## Realized spend

| Date | Run | GPU-time | Purpose |
|---|---|---|---|
| 2026-09-05 | R0000-setup | ~0 GPU-h (CPU/network only) | pins, downloads, environment |
| 2026-09-05 | R0001 smoke | *(fill from result.json)* | viability + tokens/s measurement |

## Measured throughput (R0001)

*(filled after smoke — fields below are placeholders until then)*

| Arm | tokens/s (decode, 1×H800, fp16, Pythia-2.8B) | GPU-h per 16k-token book |
|---|---|---|
| window `0+1024` | *(measured)* | *(measured)* |
| streaming `4+1020` | *(measured)* | *(measured)* |

## Extrapolation to the full protocol

Formula: `GPU-h = books × 2 arms × max_tokens_per_book / tokens_per_second / 3600`.

- 10 books × 2 arms × 16,384 tokens at 100 tok/s ⇒ ≈ **0.91 GPU-h** per full pass.
- Sensitivity arms (sink ∈ {1,2,8} on a 3-book subset) add ≈ 25% of a full pass.
- Diagnosis reruns (SKILL §11) reserve: 3× full pass.
- Total worst case ≈ 5 full passes ⇒ well within the 20 GPU-hour ceiling. **Placeholder numbers; replace with measured values after R0001.**

## Decision points

- If measured tokens/s makes a 16,384-token/book protocol exceed 8 GPU-h per full pass, cap `max_tokens_per_book` at 8,192 (still ≫ budget 1024 ⇒ ≈7k scored positions/book) **before** the final reproduction, and record the rescope here + in `data_manifest.md`.
- Never exceed the ceiling silently; if unavoidable, stop and request instructor approval (SKILL §17).
