# Current reproduction diagnosis

Formal reproduction is complete under the user's explicit authorization, on the original ten books and three actual seeds. All six runs pass strict raw validation and independent NPZ reconstruction. Paired equal-book ΔNLL is−0.7217558173, 95% book-bootstrap CI [−0.7590835293, −0.6858373358], **supported**. Macro NLL is3.1516350060 for window and2.4298791887 for fixed-four; secondary pooled micro PPL23.9581092955 versus11.6921566131. All ten book deltas are negative, ranging−0.8317118794 to−0.6153676440. Within each method the three actual seed arrays are bitwise identical. Main receipt: `environment/verification/main-raw-reconstruction.json`. The table below remains a separate controlled one-book mechanism diagnosis.

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

The completed ten-book comparison uses matched H800 MIG instances under the owner waiver; the old resource ceiling is superseded. Window launches record source `aa76de1`, streaming launches `6181538`, and all six share the frozen numerical fingerprint `a6dbe103b2e9416295807cd481a9ff1660fbfede9c26b68e7db65d230e6229ef`. Exact source/config mappings are in each launch metadata and the raw index. Do not extrapolate the one-book diagnostic means, select test parameters or substitute historical smoke for main evidence. Paper deviations and direct comparison limits are in `docs/paper_comparison.md`.
