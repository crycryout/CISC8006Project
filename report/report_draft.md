# StreamingLLM: technical review candidate

Measured diagnostics; formal scientific results and human freeze pending.

## Claim and current evidence

We study whether retaining four initial attention-sink tokens improves equal-book post-overflow NLL over window attention with a 1024-position retained KV budget. The current artifact is a review candidate: scientific reproduction, validation pilots, method selection and human freeze approval are pending. Diagnostics are measured; no final claim verdict is asserted.

## Mechanism and position correction

StreamingLLM retains initial sinks and recent K/V. With GPT-NeoX RoPE, raw keys must be cached before rotation and receive positions continuous within the current cache on each forward. Matching only the new token's position ID cannot establish correct query-key distances. The pinned official patch is enabled on every layer of both arms. This restores the published baseline mechanism and is not an original improvement.

## Fixed data and scoring

Pinned Pythia-2.8B and tokenizer; original ten PG19 test books, independent book resets. Input cap 16384; book 12204 has 7141 tokens. Total inputs 154597, predictions 154587, scored positions 144337 per arm/seed. Input x[i] predicts x[i+1]; eviction follows forward. First scored step 1025 predicts target x[1026]. A 4096-token smoke therefore scores 3070 positions. Text/model/token hashes and all per-book masks are checked.

## Statistics and independent verification

Primary estimand: seed-paired per-book NLL deltas averaged within book, then averaged equally over books. Percentile 95% CI uses 10000 book-cluster resamples, RNG seed 0. Actual model seeds 0, 1, 2 are distinct from bootstrap seeds and never create 30 independent books. Micro token NLL/PPL is secondary; exp(macro NLL) is macro-derived PPL. Fixtures test known probabilities, unequal lengths, boundaries, missing/duplicate/nonfinite contracts, raw-K, every layer K/V, attention and logits. H800 fp16/bf16 tolerances are preset.

## Measured 2 by 2 diagnostic

D-W0-20261008: NLL 5.450578; D-S0-20261008: NLL 5.292458; D-W1-20261008: NLL 3.051129; D-S1-20261008: NLL 2.223681. Each run uses one historically exposed smoke book, 4096 inputs and 3070 scored positions. Faithful positions change both absolute losses and the method gap. Actual retained K+V bytes plateau480MiB in legacy and320MiB in faithful positions, matching between methods within each position policy. This local effect diagnoses the old implementation; it cannot establish a ten-book population conclusion, systems speedup or million-token stability. Position NLL arrays, KV traces, launch source hashes and costs are preserved.

## Reproduction status and paper comparison

Formal six-job reproduction matrix is implemented but not run: protocol approval and a feasible approved budget path are missing. Paper arXiv v4 section 3.2 defines cache-relative positions; Figure 3 gives short-stream language-modeling comparisons, Figure 5 gives super-long-stream results, and Figure 4 illustrates the cache. The paper concatenates books; our independent-book reset and post-overflow aggregation are explicit deviations. No incompatible absolute-PPL target or paper speedup is claimed. Current stage status: {"state": "pending", "missing_runs": 6}

## Three improvement hypotheses and two pilots

H1 selects the smallest k in {1,2,4,8} covering 90% of first-eight attention mass from queries 64 through 511, then freezes k within the book. H2 protects position 0 and chooses the three highest-mass positions 1 through 63, breaks ties earlier, preserves chronological order and deduplicates recent K/V. Both use only causal prefix attention and a fixed 1024 retained budget. H3 is optional preallocated rolling-KV systems work, motivated only if a profiler shows material allocation cost; it is not implemented. Validation books 1022, 11155 and 13089 were selected without losses; pilot cap 8192 and actual seeds 0/1/2 are proposed before any tuning.

## Selection, full evaluation and controls

Compare valid H1/H2 pilots against faithful fixed-four StreamingLLM. Acceptable runtime and extra peak-memory ratios are proposed at 1.10. Prefer lower paired NLL at acceptable cost; if neither improves, nominate simpler H1 for a full negative-result evaluation without additional searches. A real team decision must confirm selection. Full evaluation retains the original test contract. Controls include forced-prefix identity, calibration-only fixed-four and fixed-k for H1; forced-prefix and three-seed random-anchor control for H2. These experiments remain pending; no improvement or ablation values are invented.

## Compute, provenance and reproducibility

Current spent/reserved charge is 0.578634 GPU-hours, including conservative historical accounting. The measured slowest faithful throughput is 24.192 predictions/s. The required default plan estimate is 21.186 GPU-hours, above the enforced 20-hour ceiling before calibration/future retry overhead. A concrete budget decision is required. Source commit is captured at launch; every attempt has a unique ID, status, selected GPU UUID, checksum inventory and per-book recovery. Fresh Python3.10.12 checkout installation matches all dependency pins, restores thirteen public text assets and passes53 CPU fixtures. Model weights and split lists were rehashed from the public HF cache. GPU0 has a scheduled MIG change at 01:30/09:00 Asia/Macao; the launcher checks execution windows.

## Limitations, AI reflection and human delivery

The ten fixed books are not a random sample of all PG19; one test book was previously observed. Deterministic repeated evaluations do not add independent books. Candidate attention proxies may fail and calibration may exceed fair cost thresholds. Independent fixture verification was performed by the agent, not a peer. No teacher approval, member contribution, critical human review, deadline, final template or submission receipt is fabricated. Members must review scientific decisions, execute a genuine peer audit and individually explain mechanism, masks, aggregation, seeds, controls and failures. Exact Codex serving version was not exposed.

## References and artifact entry points

StreamingLLM: https://arxiv.org/html/2309.17453v4 ; official code pinned in third_party/streaming-llm. Model: pinned EleutherAI/pythia-2.8b revision and Apache-2.0 model card. PG19: DeepMind official processed GCS texts and pinned split lists. Rebuild: python scripts/build_results.py --manifest results/final_input_manifest.json ; python scripts/build_deliverables.py. Input/run hashes: results/build_provenance.json. Decisions: docs/review_packet.md. AI/roles: AI_USAGE.md and CONTRIBUTIONS.md.
