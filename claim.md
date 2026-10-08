# Central claim, operational clarification candidate

Status: original portal submission/instructor review not evidenced in this checkout. Candidate v2 protocol requires actual review; no final scientific conclusion yet. Original wording and protocol are preserved in Git at `48e57c6`.

> On the fixed PG19 evaluation using pinned Pythia-2.8B and a1024-position retained KV budget, StreamingLLM retaining four initial attention-sink tokens plus recent tokens has lower equal-book post-overflow mean NLL than pure window attention, with positions continuous within each arm's cache.

Both arms: same10 books/token paths, cap16384 (short books unchanged), fp16 forward/fp32 scorer, cache-relative raw-K position patch, after-forward eviction, scored indices≥1025, actual model seeds0/1/2. Primary: mean of book-level seed-paired ΔNLL, candidate minus window, nats/token. Book-cluster percentile95% CI uses10000 resamples, bootstrap seed0. If upper<0 → supported; lower>0 → not_supported; otherwise → inconclusive. Invalid run/contract → no scientific status. Exponentiating macro NLL gives macro-derived PPL; pooled micro PPL is secondary and is labelled separately.

Total compute ceiling20 GPU-h, including failed/loading/retry attempts. No test book replacement or result-driven parameter selection. Changing model/dataset/tier/primary scope or exceeding budget needs actual approval as recorded in `docs/approval_status.md`. Individual defense, final sign-off and course submission remain human responsibilities.

Scope excludes training, other model families, the paper's million-token/full-concatenated-stream claims, recomputation speedups and downstream benchmarks. Restoring paper position semantics is a baseline correction, not a project improvement. Improvement candidates are preregistered separately in `docs/improvement_hypotheses.md`.
