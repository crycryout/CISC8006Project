# Reproduction v2 amendment for real human review

State: **candidate; not an instructor-approved freeze**. Original version remains in Git at `48e57c6:protocol.md` and `48e57c6:claim.md`.

| Change | Evidence / reason | Consequence |
|---|---|---|
| Apply pinned official raw-K/cache-relative RoPE to both arms | Independent trigonometric layer/attention/logit fixtures; `tests/test_position_reference.py` | Repairs paper §3.2 semantics; not an original improvement |
| Score fp32 logits while forward stays fp16 | Known-probability fixtures; short scorer contrast follows full-model diagnostic | Separates forward precision from loss accumulation |
| Name book-equal primary and token-weighted secondary | Existing protocol already averages books; unequal-length fixture gives 2 vs 2.5 | Avoids interpreting pooled PPL as the primary estimand |
| Implement actual seeds 0,1,2 | Strict seed matrix; seed-paired deltas averaged within book | No deterministic exemption; 10 books remain 10 clusters |
| Reject missing/mismatched/unfinished evidence | Config, pairing, NPZ and checksum validation | Invalid evidence has no scientific verdict |

Unchanged: Pythia-2.8B revision, original 10 PG19 test books, 16384 cap with natural short book, retained budget 1024, one token per forward, after-forward eviction, first scored step 1025, 10000 book-cluster resamples, 20 GPU-h total ceiling.

Candidate protocol is `configs/protocol_v2.yaml`; complete jobs are in `configs/reproduction_matrix.yaml`. Dry-run never starts a GPU. The evaluator independently enforces approval gates, so a shell wrapper cannot bypass them.

Review packet: `environment/verification/fixtures-all.log`, `data/assets_manifest.json`, `results/diagnostics/summary.json` when available, `docs/audit_resolution.md`, exact matrix dry-run and actual budget. Please review the position/scorer correction, the unchanged scientific scope, and the human requirements from the course. Record an actual reviewer, decision timestamp, evidence reference and any required instructor confirmation in `docs/approval_decisions.json` before scientific execution. No approval is inferred from this document.

Pilot proposal: fixed H1/H2 algorithms from the execution plan, development IDs 1022/11155/13089, cap 8192, actual seeds 0/1/2. H1 threshold 0.90; queries 64–511; H2 protects position0 and selects top3 positions1–63, ties earlier. No parameter search. Runtime and extra peak memory acceptance ratios both 1.10. These are proposed choices pending actual team review.

Selection rule, before observing results: eliminate invalid implementations; prefer candidates with lower paired macro NLL and acceptable measured cost; if both improve, choose more negative delta, then lower runtime, then H1 on an exact tie. If neither improves acceptably, nominate H1 as the simpler causal mechanism for a full negative-result evaluation. A real team decision must confirm the rule's application. H2 never wins merely because it beats window; improvement compares against faithful fixed4 StreamingLLM.

Final artifacts will identify candidate versus approved experiment states. No final tag or course submission is made until real freeze approval and human review exist.
