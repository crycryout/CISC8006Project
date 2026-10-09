# Agent Ledger

One row per AI interaction that can change scientific evidence. Template: `templates/agent-ledger.md`.
Rules: `agent_policy.md`. Humans verify every consequential output.

| ID | Date | Tool / model | Delegated task | AI proposal (summary) | Human decision | Verification | Evidence |
|----|------|--------------|----------------|----------------------|----------------|--------------|----------|
| E0001 | 2026-09-05 | Claude Code (GLM 5.3, CLI agent) | Bootstrap the whole Week-3/4 deliverable set: repo skeleton, pinned official-code checkout, environment, Pythia-2.8B+PG19 smoke run, GPU-hour estimate, claim.md, Week-4 claim_map draft, submission text | Full scaffold as committed in the first push; central-claim wording per course SKILL recommended text; 10-book preregistration plan; cache-index oracle design | accept (claim text) / accept (scaffold, pending team review of [placeholders]) | Human read claim wording against SKILL §6 recommended text before portal submission; smoke-test run R0001 reproducible via `scripts/run_smoke.sh` | commit: `2c895ed`; run: R0001 |
| E0002 | 2026-09-05 | Claude Code (GLM 5.3, CLI agent) | Independent cache-index oracle design (AI proposal: pure-Python retention simulator as expected-trace generator, mock position-tagged KV tensors driving official `StartRecentKVCache` as actual) | 6 checks incl. per-step trace identity, budget cap, sink placement, cross-arm position-id consistency | accept | Oracle passes; expected vs actual traces committed under `audit/expected_traces/` | commit: `2c895ed`; `audit/cache_index_test.py` |
| E0003 | 2026-09-05 | Claude Code (GLM 5.3, CLI agent) | Harness validation on pythia-160m before the claim model arrived (R0000-harnesscheck) | Run both arms at 160m scale to de-risk the 2.8B smoke | accept | Both arms completed; ΔNLL direction matches paper expectation; pipeline emits course-schema result.json | run: R0000-harnesscheck |
| E0004 | 2026-09-05 | Claude Code (GLM 5.3, CLI agent) | R0001 smoke on the claim model (Pythia-2.8B) and GPU-hour extrapolation; AI proposed freezing `max_tokens_per_book=16384` and keeping 10 books | Cap protocol at 16,384 tokens/book ⇒ ≈2.9 GPU-h/full pass (12.5 GPU-h worst case incl. reruns), no rescope | accept (pending human read of compute_budget.md before Week-5 freeze) | Reproducible via `bash scripts/run_smoke.sh`; numbers cross-checked against result.json elapsed fields | commit: (this push); run: R0001 |

## Pending / open items for the team

- [ ] Fill team member names in `submission/week3_submission.md` before the 2026-09-06 23:59 portal deadline (registered submitter posts it). After submitting, flip the "not yet submitted" status lines in `claim.md` / `submission/week3_submission.md` / `README.md` to the actual timestamp.
- [ ] Human review of claim_map.md draft before treating it as team position in office hour (Wed 2026-09-09 14:00–15:00, N21-2001f).
- [ ] Human sanity-check the harness mechanics and the throughput estimate behind `max_tokens_per_book = 16384`. The token cap is selected **solely from the compute ceiling** (`compute_budget.md`) and must not depend on the observed window-vs-streaming NLL gap. `max_tokens_per_book` was frozen on 2026-09-05 on compute grounds only; any future change needs a compute-based (not performance-based) justification and a documented rescope.

## 2026-10-08 execution entries (actual decisions distinguished)

| ID | Date | Tool / model | Delegated task | Proposal / result | Human decision | Verification | Evidence |
|---|---|---|---|---|---|---|---|
| E0005 | 2026-10-08 | Codex / GPT-6; exact version not exposed | Execute plan§9; inventory, configuration/pairing and position repair | Preserve old files; independent RoPE/K/V/logit tests; immutable schema-v2 outputs | Owner authorized implementation; scientific review pending |55 independent CPU/H800 fixtures, raw assets verified | Commit7718903 and subsequent execution branch; `environment/verification/final-fixtures.log` |
| E0006 | 2026-10-08 | Codex / GPT-6 | Full-model2×2 and scorer/failure diagnostics; fixed improvement proposals and compute review | Corrected single-book losses3.051129/2.223681; default full plan≥21.06h exceeds20h | Protocol/pilot/budget decisions requested; pending | Four4096-token runs, short scorer contrast, deliberately failed second book preserved | `results/diagnostics/`; `runs/recovery-failed-20261008/`; `docs/review_packet.md` |
| E0007 | 2026-10-08 | Codex / GPT-6 | Rebuild scripts, report/deck/demo/peer packet and release checks | Review candidate explicitly distinguishes missing formal science and human ownership | Human report review, peer audit and freeze pending | PDF rendered/read;12 slides with notes; exact result/config/raw hashes | `submission/deliverables_manifest.json`; `audit/peer_audit/`; `AI_USAGE.md` |

These entries do not authenticate historical accept assertions or supply new instructor/member signatures. Actual future reviewer decisions should add dated evidence; do not silently convert pending into accepted.

## Owner-authorized execution, actual dated evidence

| ID | Date | Agent / task | Proposal or action | Actual decision / verification | Evidence |
|---|---|---|---|---|---|
| E0008 |2026-10-09|Codex based on GPT-6; exact serving build not exposed / resource and protocol execution|Keep actual seeds0/1/2 and original data; use three existing matched H800 MIG instances; apply the frozen pilot rule automatically|User explicitly instructed “不需要审批，H800的GPU资源随便用”; owner waiver only, no teacher or peer signature; GPU0 other project and topology preserved|`docs/execution_authorization.md`; frozen numerical SHA `a6dbe103…`; actual67-pin clean installation and57 CPU checks at source624b022|
| E0009 |2026-10-09|Codex / complete main comparison and independent reconstruction|Run six original10-book/three-seed arms; reconstruct all NPZ losses, per-book deltas and book-bootstrap CI|All six actual attempts validate; ΔNLL−0.7217558173,95% CI [−0.7590835293,−0.6858373358], supported; each method's seed arrays bitwise identical; agent engineering verification, human critical review still pending|Window sourceaa76de1 / streaming6181538; main evidence commite491d74; `environment/verification/main-raw-reconstruction.json`;64 indexed diagnostic/main book artifacts|

Two development candidates, selected full test and controls remain in progress at this checkpoint. Later entries must use their actual measured outcomes. No failed/negative attempt, original smoke or historical reviewer assertion is replaced.
