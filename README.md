# CISC8006 Project: Scaled-Faithful Reproduction of StreamingLLM

**Course:** CISC8006 Advanced Machine Learning
**Paper:** Xiao, Tian, Chen, Han, Lewis. *Efficient Streaming Language Models with Attention Sinks.* ICLR 2024.
**Official code:** `mit-han-lab/streaming-llm` (MIT license), vendored under `third_party/streaming-llm` at a pinned commit.
**Reproduction tier:** Scaled-faithful (same hypothesis, comparison, task family, and metric as the paper; reduced model scale / token count / hardware).

## Mission

An auditable research pipeline:

**Claim → Protocol → Harness → Pilot → Reproduce → Diagnose → Improve → Ablate → Freeze → Defend**

We never optimize for a positive result. A negative or null result is acceptable when the protocol is fixed, uncertainty is reported, discrepancies are diagnosed, and artifacts are auditable.

## Central claim (v1, submitted 2026-09-06)

> On a fixed PG19 evaluation using Pythia-2.8B and a 1024-token KV-cache budget, StreamingLLM, which retains four initial attention-sink tokens together with recent tokens, achieves lower long-sequence perplexity than pure window attention after the cache begins evicting old tokens.

Full specification and decision rule: [`claim.md`](claim.md).

## Repository layout

```text
project/
├── README.md                  this file
├── claim.md                   target claim v1 + decision rule (frozen for submission)
├── feasibility.md             why this is feasible under our compute ceiling
├── compute_budget.md          GPU-hour accounting + extrapolation
├── claim_map.md               Week-4 draft: assumptions/baselines/metrics/falsification
├── protocol.md                reproduction protocol (frozen after instructor review)
├── agent_policy.md            AI-use policy
├── agent_ledger.md            AI-assistance ledger (human decision per entry)
├── data_manifest.md           model revisions, dataset files, checksums, book list
├── experiment_registry.md     one row per consequential run
├── submission/                course-portal submission texts
├── environment/               pins: third_party.md, pip-freeze.txt, system-info.txt
├── configs/                   smoke / window / streaming / improvement configs
├── scripts/                   run_smoke.sh, run_reproduction.sh, analyze_results.sh ...
├── audit/                     cache-index oracle tests + expected/actual traces
├── runs/                      R0001/... per-run config, log, result.json, metadata.json
├── third_party/streaming-llm/ official repo, vendored at pinned commit
├── figures/  tables/          generated artifacts
├── report/  defense/          final report + defense prep
└── templates/                 registry / ledger templates
```

## Quick start

```bash
source .venv/bin/activate
bash scripts/run_smoke.sh          # deterministic tiny run, writes runs/R000x/
python audit/cache_index_test.py   # cache-index oracle (no GPU needed)
```

## Timeline (course gates)

| Date | Gate | Status |
|---|---|---|
| 2026-09-06 23:59 | Paper + central claim submission | **submitted text in `submission/week3_submission.md`** |
| 2026-09-07..13 | Instructor review; refine claim on request | in progress |
| 2026-09-09 | Week-4 claim-map draft | `claim_map.md` (draft) |
| 2026-09-13 | Paper/claim freeze | pending |
| 2026-09-16 | Week-5: protocol + agent policy + harness smoke | pending |
| 2026-09-23 | Week-6: locked env + provenance + baseline | pending |
| 2026-09-30 | Week-7: pass/rescope gate | pending |

## Team

- [team member names — to be completed in the course portal by the registered submitter]
