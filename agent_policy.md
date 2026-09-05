# AI-Use Policy

**Course:** CISC8006 — team project
**Principle:** AI tools accelerate evidence production; **humans own every consequential decision**. Every output that can change scientific evidence is logged in `agent_ledger.md` with a human accept/modify/reject/escalate decision and a verification step.

## Allowed AI assistance

- Explaining the paper and its figures
- Implementing harness code, unit tests, analysis scripts
- Debugging (including proposing hypotheses for discrepancies)
- Ablation brainstorming
- Adversarial review of our own claims and code

## Not delegable (human-only decisions)

- Selecting/changing the central claim, primary metric, dataset, model family, reproduction tier
- Freezing or rescoping the protocol
- Approving a compatibility change that may alter numerical behavior
- Signing off a reproduction conclusion (recovered / not recovered / inconclusive)
- Choosing which improvement hypothesis advances (must follow preregistered criteria)

## Stop conditions (SKILL §17)

Any of the following halts work pending instructor approval:

- primary metric changes; dataset changes; model family changes; tier changes
- cache-budget change for the primary claim
- compute ceiling must be exceeded
- evaluation would need hidden/private APIs or inaccessible data
- a compatibility change may alter the algorithm
- the target claim is no longer falsifiable

## Logging rules

- Log **only** interactions that can change scientific evidence (code, analysis, interpretation), not routine Q&A
- Each ledger entry: date; tool/model; delegated task; AI proposal; human decision (accept/modify/reject/escalate); verification; evidence link (commit + run ID)
- The course requires evidence of human ownership: at least one **genuine, documented rejection** of an AI suggestion. We do not fabricate rejections to satisfy the rubric; if a rejection exists it will appear in the ledger with its reasoning.

## Provenance of this repository

Initial scaffold (directory layout, claim/claim-map drafts, harness skeleton, smoke test, audit tests) was AI-generated under human instruction on 2026-09-05; the human reviewed the claim text and approved submission. See `agent_ledger.md` entry E0001.
