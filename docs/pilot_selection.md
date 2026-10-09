# Measured pilot selection

All nine development baseline/H1/H2 runs are complete and strictly validated on frozen IDs1022,11155,13089, cap8192 and actual seeds0/1/2. Direct raw-NPZ reconstruction passes for both candidates: `environment/verification/pilot-raw-reconstruction.json`. Each method's three actual seed loss arrays are bitwise identical; three books remain the uncertainty units.

| Candidate | Paired mean ΔNLL | Book-bootstrap95% CI | Registered runtime / baseline | Peak memory / baseline | Development verdict |
|---|---:|---|---:|---:|---|
| H1 adaptive sink |−0.0053448941|[−0.0166115776,0.0004601404]|1.0026204417|1.000000|inconclusive|
| H2 anchor selection |−0.0080531545|[−0.0163472468,−0.0018359957]|1.0084236115|1.000000|supported on the three-book scope|

Both have negative mean ΔNLL and acceptable registered runtime/peak-memory ratios≤1.10. The frozen rule ranks point means and costs, not CI significance. H2 has the lower qualifying mean and was selected at2026-10-09 11:17:07 UTC. No fallback or additional parameter search was needed. The three-book pilot CI does not establish a full-test effect.

Immutable proposal: `results/pilots/selection_proposal.json`, SHA256 `51845b744f16c83a9298348eb86e2b5f5ffb546e6e04d9cd6afa0d6ee5087f79`. Selection actor: agent applying the frozen owner-authorized rule, recorded in `docs/approval_decisions.json`; no teacher or human scientific review is claimed. Rebuild verifies the proposal remains unchanged after selection.

H2 full test now runs on the original ten books with actual seeds0/1/2, reusing the compatible fixed-four main baseline. Only H2 forced-prefix and random-anchor development controls follow. No test NLL chooses a threshold, anchor-selection rule, seed or book.
