# Current reproduction diagnosis

Formal reproduction: **pending actual protocol/budget approval and six full runs**. Current results are a controlled one-book mechanism diagnosis, not the final claim.

| Retention / positions | Post-overflow NLL | Scored count | Run |
|---|---:|---:|---|
| Window / legacy implicit |5.450577737|3070|D-W0-20261008|
| Four sinks / legacy implicit |5.292458269|3070|D-S0-20261008|
| Window / cache-relative |3.051128998|3070|D-W1-20261008|
| Four sinks / cache-relative |2.223681157|3070|D-S1-20261008|

Both arms change substantially under the published position mechanism. The local sink-minus-window gap is−0.158119 in legacy and−0.827448 in corrected positions. The oldsmoke did not establish faithful StreamingLLM: rotated historical K and repeated implicit current positions were inconsistent after rolling eviction. Restoring raw-K/cache-relative positions belongs to baseline correctness.

Sources/tokenizer/weights/text hashes and original lengths verified. Every-layer frozen-input trigonometric attention, raw-K/V, probabilities and logits pass independent fixtures; preset H800 fp16/bf16 tolerances pass. Retained KV length reaches1024 while forward reaches1025. Measured legacy K+V tensor bytes plateau480MiB; faithful raw-K bytes plateau320MiB, identical between window/sinks within each position policy. Equal retained positions therefore did not mean equal bytes across old/corrected representations. Figure `diagnostic_kv_bytes.png` and the CSV preserve the measured difference; no speed/memory improvement claim is inferred from it. Full scored region is3070 positions; raw NPZ and metrics rebuild the table.

Scorer isolation uses the identical faithful forward prefix (1200 tokens,174 scored), comparing legacy fp16 loss to fp32 loss. Mean scored shift is+0.0000778481 nats/token for legacy minusfp32; maximum per-position absolute difference0.00689125. This small local scorer difference does not explain the multi-nat RoPE effect. It does not bound all future test-book scorer differences. Exact values and parent inputs are in `results/diagnostics/scorer_comparison.json`.

Actual second-book fault injection exits1, preserves first-book10146 metrics/NPZ and records failed status without a final result or scientific verdict. No original R0000/R0001 file was overwritten (hash inventory verification passed). See `environment/verification/integrity-recovery.json`.

Next scientific stage is the frozen original10-book comparison after genuine approval and a feasible resource decision. Do not extrapolate these diagnostic means to allbooks, derive a one-book CI, select test parameters or substitute historical smoke for main evidence. Paper deviations and direct comparison limits are in `docs/paper_comparison.md`.
