# Reproduction v2 amendment and owner authorization

State: scientific execution authorized by the user's explicit 2026-10-09 waiver; not an instructor-approved protocol or human peer review. Original version remains in Git at `48e57c6:protocol.md` and `48e57c6:claim.md`. The actual instruction and machine records are in `docs/execution_authorization.md` and `docs/approval_decisions.json`.

| Change | Evidence / reason | Consequence |
|---|---|---|
| Apply pinned official raw-K/cache-relative RoPE to both arms | Independent trigonometric layer/attention/logit fixtures; `tests/test_position_reference.py` | Repairs paper §3.2 semantics; not an original improvement |
| Score fp32 logits while forward stays fp16 | Known-probability fixtures; short scorer contrast follows full-model diagnostic | Separates forward precision from loss accumulation |
| Name book-equal primary and token-weighted secondary | Existing protocol already averages books; unequal-length fixture gives 2 vs 2.5 | Avoids interpreting pooled PPL as the primary estimand |
| Implement actual seeds 0,1,2 | Strict seed matrix; seed-paired deltas averaged within book | No deterministic exemption; 10 books remain 10 clusters |
| Reject missing/mismatched/unfinished evidence | Config, pairing, NPZ and checksum validation | Invalid evidence has no scientific verdict |

Unchanged: Pythia-2.8B revision, original 10 PG19 test books, 16384 cap with natural short book, retained budget 1024, one token per forward, after-forward eviction, first scored step 1025, actual seeds 0/1/2, 10000 book-cluster resamples. The user superseded the old 20 GPU-h ceiling; all device-instance costs/failures remain recorded.

The registered execution protocol is `reproduction-v2-owner-authorized`; complete jobs are in `configs/reproduction_matrix.yaml`. Dry-run never starts a GPU. The evaluator requires a genuine authorization record, including the explicit owner waiver, and still rejects missing selected-method evidence or mismatched contracts.

Evidence: `environment/verification/fixtures-all.log`, actual H800 fixture runs, `data/assets_manifest.json`, `results/diagnostics/summary.json`, `docs/audit_resolution.md`, matrix launch records and actual cost. The owner waived procedural execution approvals after these concrete corrections and diagnostics were prepared. No teacher confirmation is inferred from this document.

Frozen pilots: fixed H1/H2 algorithms from the execution plan, development IDs 1022/11155/13089, cap 8192, actual seeds 0/1/2. H1 threshold 0.90; queries 64–511; H2 protects position0 and selects top3 positions1–63, ties earlier. No parameter search. Whole-process runtime and peak allocated memory acceptance ratios both 1.10.

Selection rule, before observing results: invalid evidence stops execution; prefer negative paired macro NLL and acceptable measured cost; if both qualify, choose more negative delta, then lower runtime, then H1 on an exact tie. If neither qualifies, evaluate H1 as the simpler causal mechanism for a full negative-result result. The owner delegated application of this frozen rule; the agent records the actual immutable pilot proposal SHA and selection before full test inference. H2 never wins merely because it beats window; improvement compares against faithful fixed4 StreamingLLM.

Hardware amendment: the three existing H800 GPU1 MIG 2g.20gb instances provide 30 SMs each. Methods pair on the same UUID for each seed and all seeds share the recorded hardware class. Full-GPU/MIG diagnostic outputs are not bitwise identical and never form a formal pair; `environment/verification/mig-hardware-comparison.json` retains the measured differences. GPU0's unrelated workload, MIG topology and cron are unchanged. Runtime ratios are descriptive registered-run observations with unlocked clocks and fixed method order, not a kernel-speedup claim; `compute_budget.md` records the exact launch-snapshot/finish timer boundary.

The user authorized a scientific/technical freeze after checks pass. Human course submission, peer audit and individual defense remain separately recorded factual activities. A scientific tag never certifies those activities.
