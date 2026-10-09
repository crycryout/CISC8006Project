# Individual defense practice

Each real member should answer these independently; document actual rehearsal, not agent-generated certification.

1. Explain attention sinks, why raw-K caching matters for RoPE, and why identical current position IDs did not validate the legacy implementation. Locate the independent reference and distinguish frozen historical hidden states from recomputing a retained sequence.
2. Derive first scored step1025, target1026 and scored counts3070/6115/15358. Explain retained1024 versus forward1025 and derive measured320MiB pure KV separately from peak GPU allocation.
3. Define macro/micro NLL, exp(macro NLL), pooled PPL, book bootstrap and actual model repeats. Explain why10×3 is not30 independent books and why invalid data cannot be a not_supported result.
4. Explain causal calibration and H1/H2 selection, chronological anchors, future-loss prohibition, controls, cost thresholds and negative-result fallback. Locate the actual immutable pilot evidence and owner-delegated rule; distinguish agent execution from a team review. Derive the final full/controls interpretation from their own book sets.
5. Show one actual run/config/source/NPZ/figure hash chain, the original failure counterexamples and their fixes. Explain a real human critical review when it occurs; do not cite an agent test as peer review or claim a fictional contribution.
