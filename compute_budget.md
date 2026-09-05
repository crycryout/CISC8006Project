# Compute Budget

**Ceiling:** ≤ 20 GPU-hours total (initial, per claim.md). All numbers below are updated per run; the registry (`experiment_registry.md`) is the source of truth for realized spend.

## Realized spend

| Date | Run | GPU-time | Purpose |
|---|---|---|---|
| 2026-09-05 | R0000-setup | ~0 GPU-h (CPU/network only) | pins, downloads, environment |
| 2026-09-05 | R0000-harnesscheck | 0.03 GPU-h (2×48 s @160m) | harness validation, small model |
| 2026-09-05 | R0001 smoke | 0.07 GPU-h (127 s + 131 s) | viability + tokens/s measurement (2.8B) |

## Measured throughput (R0001, Pythia-2.8B fp16, 1× H800, token-by-token decode + per-step eviction)

| Arm | tokens/s | GPU-h per 16,384-token book |
|---|---|---|
| window `0+1024` | 32.2 | 0.141 |
| streaming `4+1020` | 31.2 | 0.146 |

(Throughput is dominated by per-step Python/launch overhead of the official token-by-token evaluation semantics, not by GPU compute — both arms sit at 6.9 GB / 80 GB memory, 0% idle-heavy.)

## Extrapolation to the full protocol

Formula: `GPU-h = books × 2 arms × max_tokens_per_book / tokens_per_second / 3600`.

- **Chosen cap: `max_tokens_per_book = 16384`** (⇒ 15,358 scored NLL indices per book: 16384 tokens → 16383-entry `nlls` array → indices 1025..16382; 12,288 more than the smoke's 3,070).
- 10 books × 2 arms × 16,384 tokens @ ~31.7 tok/s ⇒ **≈ 2.89 GPU-h per full pass**.
- Sensitivity arms (sink ∈ {1,2,8}, 3-book subset) ≈ 0.43 + 0.43×2/10 ≈ 0.86 GPU-h.
- Diagnosis reruns reserve: 3 full passes ≈ 8.7 GPU-h.
- Grand total worst case ≈ **12.5 GPU-h — inside the 20 GPU-hour ceiling** with margin.

## Decision (frozen after R0001, 2026-09-05)

Keep 10 books @ 16,384 tokens/book for the primary comparison. No rescope needed.

## Decision points

- If measured tokens/s makes a 16,384-token/book protocol exceed 8 GPU-h per full pass, cap `max_tokens_per_book` at 8,192 (still ≫ budget 1024 ⇒ ≈7k scored positions/book) **before** the final reproduction, and record the rescope here + in `data_manifest.md`.
- Never exceed the ceiling silently; if unavoidable, stop and request instructor approval (SKILL §17).
