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

- [ ] Fill team member names in `submission/week3_submission.md` before the 2026-09-06 23:59 portal deadline (registered submitter posts it).
- [ ] Human review of claim_map.md draft before treating it as team position in office hour (Wed 2026-09-09 14:00–15:00, N21-2001f).
- [ ] After smoke test: human sanity-check that window arm actually degrades after overflow on ≥1 book before locking max-tokens-per-book.
