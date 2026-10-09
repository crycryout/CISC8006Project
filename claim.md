# Central claim, frozen operational definition

Status: original portal submission/instructor review is not evidenced. The user explicitly authorized v2 scientific execution without procedural approvals on 2026-10-09; registered runs are in progress and no final verdict is assigned before complete paired validation. Original wording/protocol are preserved in Git at `48e57c6`. Current status and any measured verdict are in `results/reproduction/status.json` and `summary.json`.

> On the fixed PG19 evaluation using pinned Pythia-2.8B and a1024-position retained KV budget, StreamingLLM retaining four initial attention-sink tokens plus recent tokens has lower equal-book post-overflow mean NLL than pure window attention, with positions continuous within each arm's cache.

Both arms: same10 books/token paths, cap16384 (short books unchanged), fp16 forward/fp32 scorer, cache-relative raw-K position patch, after-forward eviction, scored indices≥1025, actual model seeds0/1/2. Primary: mean of book-level seed-paired ΔNLL, candidate minus window, nats/token. Book-cluster percentile95% CI uses10000 resamples, bootstrap seed0. If upper<0 → supported; lower>0 → not_supported; otherwise → inconclusive. Invalid run/contract → no scientific status. Exponentiating macro NLL gives macro-derived PPL; pooled micro PPL is secondary and is labelled separately.

The user superseded the original 20 GPU-h ceiling with unrestricted H800 authorization; failed/loading/retry attempts remain accounted. No test book replacement or result-driven parameter selection. Model, books, precision, scoring and actual seeds remain frozen. Baseline/candidate share the same H800 MIG 2g.20gb instance per seed. Individual defense, genuine peer review and course submission remain human activities; no such completion is invented.

Scope excludes training, other model families, the paper's million-token/full-concatenated-stream claims, recomputation speedups and downstream benchmarks. Restoring paper position semantics is a baseline correction, not a project improvement. Improvement candidates are preregistered separately in `docs/improvement_hypotheses.md`.
