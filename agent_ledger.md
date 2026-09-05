# Agent Ledger

One row per AI interaction that can change scientific evidence. Template: `templates/agent-ledger.md`.
Rules: `agent_policy.md`. Humans verify every consequential output.

| ID | Date | Tool / model | Delegated task | AI proposal (summary) | Human decision | Verification | Evidence |
|----|------|--------------|----------------|----------------------|----------------|--------------|----------|
| E0001 | 2026-09-05 | Claude Code (GLM 5.3, CLI agent) | Bootstrap the whole Week-3/4 deliverable set: repo skeleton, pinned official-code checkout, environment, Pythia-2.8B+PG19 smoke run, GPU-hour estimate, claim.md, Week-4 claim_map draft, submission text | Full scaffold as committed in the first push; central-claim wording per course SKILL recommended text; 10-book preregistration plan; cache-index oracle design | accept (claim text) / accept (scaffold, pending team review of [placeholders]) | Human read claim wording against SKILL §6 recommended text before portal submission; smoke-test run R0001 reproducible via `scripts/run_smoke.sh` | commit: see first push; run: R0001 |

## Pending / open items for the team

- [ ] Fill team member names in `submission/week3_submission.md` before the 2026-09-06 23:59 portal deadline (registered submitter posts it).
- [ ] Human review of claim_map.md draft before treating it as team position in office hour (Wed 2026-09-09 14:00–15:00, N21-2001f).
- [ ] After smoke test: human sanity-check that window arm actually degrades after overflow on ≥1 book before locking max-tokens-per-book.
