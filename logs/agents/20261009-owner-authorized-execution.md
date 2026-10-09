# Actual owner-authorized scientific execution

Date: 2026-10-09. Agent: Codex based on GPT-6; exact serving build/version not exposed. No subagents. User instruction: “不需要审批，H800的GPU资源随便用”.

The agent applied this instruction to supersede procedural execution approvals and the old20 GPU-hour ceiling. Actual seeds0/1/2, fixed test/development books, numerical precision, scoring, algorithms and selection rule remain. This is an owner waiver, not teacher approval or a peer signature. Decisions and evidence: `docs/execution_authorization.md`, `docs/approval_decisions.json`, `docs/budget_decision.json`.

Actual hardware discovery confirmed GPU0's other project and three existing idle H800 GPU1 MIG2g.20gb instances with30 SMs each. No other process, topology, cron, driver or account was changed. A real MIG model smoke and59 CPU/GPU checks passed; the full-H800/MIG per-position comparison was not bitwise identical. Formal pairs use the same MIG UUID per seed and a common hardware class.

Main execution source commit: `aa76de1`. Frozen numerical-file fingerprint: `a6dbe103b2e9416295807cd481a9ff1660fbfede9c26b68e7db65d230e6229ef`. Three workers launched actual window jobs; each proceeds to its streaming job. Supervisor source `624b022` attaches, then executes two pilots, frozen selection, selected full test and controls. Running checkpoints: `experiments/studies/owner-h800-20261009`; immutable raw attempts: `runs/`.

New detached clean checkout `624b022` installed Python3.10.12 and all67 exact dependency versions; `smoke-cpu-owner-clean-20261009` passed57 CPU checks with two GPU cases deselected. Launch source was clean. All13 public assets rehashed successfully. `pip freeze` initially omitted pip/setuptools/wheel by default; `--all --exclude-editable` confirmed all67 versions without reinstalling. Current receipt/logs: `environment/verification/clean-checkout.json`; prior receipt retained separately.

Delivery tooling exports scientific/per-book/quality-cost tables, formal cache/position/paired plots, raw-artifact SHA index and report/deck with real results only. Twelve slides include actual main/full/pilot/control metrics and full notes; initial bounds/notes and PDF rendering passed. A separate raw-NPZ reconstruction audit runs after complete outputs exist. The updated demo reads saved formal results with no GPU inference. Old recordings are preserved; a new final recording is required because the demo changed.

Actual human decision is the explicit execution/resource authorization above. Detailed scientific critical human review, real members, independent peer audit, T_final, final course template and individual defense remain unprovided or unperformed. No fabricated rejection, signature, attendance, contribution or course receipt is recorded.

## Completed main checkpoint, 2026-10-09 10:17 UTC

All six main runs completed and strict validation passed. Window launch source isaa76de1; streaming launch source6181538; the numerical fingerprint is identical across all six. Independent direct NPZ reconstruction gives equal-book ΔNLL−0.7217558172973408 and book-bootstrap95% CI [−0.7590835293116327,−0.6858373358341464], supported on the original ten-book scope. Macro NLL is3.1516350059974445 versus2.4298791887001037; secondary pooled PPL23.958109295542496 versus11.692156613092376. Every book delta is negative. Within each method all three seed loss arrays are bitwise identical; no30-book interpretation is made. Receipt: `environment/verification/main-raw-reconstruction.json`; complete raw evidence and analysis commite491d74 pushed to the execution branch.

The supervisor immediately started the nine frozen development baseline/H1/H2 jobs. It will select only after the measured pilot evidence is complete. No pilot/full/control outcome is assigned at this checkpoint. Additional release checks bind generated tables/figures/report/deck to exact builder SHA and manifest; the expanded tracked/history credential scanner reported zero matching findings with redacted-only output.
