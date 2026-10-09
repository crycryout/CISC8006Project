# StreamingLLM: measured H800 scientific delivery

Owner-authorized complete scientific evidence; human course activities separately recorded.

## Claim and current evidence

We study whether retaining four initial attention-sink tokens improves equal-book post-overflow NLL over window attention with a 1024-position retained KV budget. The registered scientific execution is complete and source-linked; real human course activities are separately recorded. Main result: Equal-book candidate-minus-baseline NLL difference -0.721756 nats/token; book-cluster 95% CI [-0.759084, -0.685837]; verdict supported. 10 books, actual model seeds [0, 1, 2]. Baseline macro NLL 3.151635, candidate 2.429879; secondary micro PPL 23.9581 versus 11.6922. Selected-method result: Equal-book candidate-minus-baseline NLL difference 0.000108 nats/token; book-cluster 95% CI [-0.000064, 0.000303]; verdict inconclusive. 10 books, actual model seeds [0, 1, 2]. Baseline macro NLL 2.429879, candidate 2.429987; secondary micro PPL 11.6922 versus 11.6934. The user explicitly waived procedural approvals and the 20 GPU-hour ceiling on 2026-10-09. This is an owner instruction, not a teacher approval or a peer signature. The main claim uses complete strict paired outputs, never a historical smoke.

## Mechanism and position correction

StreamingLLM retains initial sinks and recent K/V. With GPT-NeoX RoPE, raw keys must be cached before rotation and receive positions continuous within the current cache on each forward. Matching only the new token's position ID cannot establish correct query-key distances. The pinned official patch is enabled on every layer of both arms. This restores the published baseline mechanism and is not an original improvement.

## Fixed data and scoring

Pinned Pythia-2.8B and tokenizer; original ten PG19 test books, independent book resets. Input cap 16384; book 12204 has 7141 tokens. Total inputs 154597, predictions 154587, scored positions 144337 per arm/seed. Input x[i] predicts x[i+1]; eviction follows forward. First scored step 1025 predicts target x[1026]. A 4096-token smoke therefore scores 3070 positions. Text/model/token hashes and all per-book masks are checked.

## Statistics and independent verification

Primary estimand: seed-paired per-book NLL deltas averaged within book, then averaged equally over books. Percentile 95% CI uses 10000 book-cluster resamples, RNG seed 0. Actual model seeds 0, 1, 2 are distinct from bootstrap seeds and never create 30 independent books. Micro token NLL/PPL is secondary; exp(macro NLL) is macro-derived PPL. Fixtures test known probabilities, unequal lengths, boundaries and missing/duplicate/nonfinite contracts. An independent three-layer tiny GPT-NeoX reference checks trigonometric RoPE, raw-K, every layer K/V, attention and final logits through multiple evictions; real-model integration uses the full 32-layer pinned checkpoint. H800 fp16/bf16 tolerances are preset. All 6 FP16/BF16 GPU reference cases pass unchanged preset tolerances; largest absolute logits error 0.001953125. Per-case K/V/attention/logits maxima and p50/p95/p99 are in environment/verification/reference-error-distributions.json. These tiny-fixture results do not bound all full-model errors. The audit script reconstructs NLL, PPL, book deltas, bootstrap intervals and actual seed spread directly from saved NPZ arrays; this remains agent engineering verification.

## Measured 2 by 2 diagnostic

D-W0-20261008: NLL 5.450578; D-S0-20261008: NLL 5.292458; D-W1-20261008: NLL 3.051129; D-S1-20261008: NLL 2.223681. Each run uses one historically exposed smoke book, 4096 inputs and 3070 scored positions. Faithful positions change both absolute losses and the method gap. Actual retained K+V bytes plateau 480MiB in legacy and 320MiB in faithful positions, matching between methods within each position policy. This local effect diagnoses the old implementation; it cannot establish a ten-book population conclusion, systems speedup or million-token stability. Position NLL arrays, KV traces, launch source hashes and costs are preserved.

## Formal reproduction and paper comparison

Equal-book candidate-minus-baseline NLL difference -0.721756 nats/token; book-cluster 95% CI [-0.759084, -0.685837]; verdict supported. 10 books, actual model seeds [0, 1, 2]. Baseline macro NLL 3.151635, candidate 2.429879; secondary micro PPL 23.9581 versus 11.6922. Descriptive 512-step equal-book position bins: bin starting 1025: candidate-minus-baseline -0.611089 nats/token, 10 books; bin starting 15873: candidate-minus-baseline -0.749713 nats/token, 9 books. Partial last bins are not zero-padded; exact book coverage is saved in the companion CSV. Bin differences are secondary and do not replace the primary whole-scored-region book estimand. Paper arXiv v4 section 3.2 defines cache-relative positions; Figure 3 gives short-stream comparisons, Figure 5 super-long-stream results, and Figure 4 the cache schematic. The paper concatenates books; independent-book reset and post-overflow aggregation are explicit deviations. Formal methods are paired on the same existing H800 MIG 2g.20gb instance for each seed, with the same 30-SM hardware class across seeds. Full-GPU/MIG fp16 diagnostic outputs were not bitwise identical; the scored smoke-prefix mean shift was 0.000489 nats/token. Their results are not mixed in a formal pair. No paper speedup or full-H800 throughput equivalence is inferred.

## Three improvement hypotheses and two pilots

H1 selects the smallest k in {1,2,4,8} covering 90% of first-eight attention mass from queries 64 through 511, then freezes k within the book; negligible/invalid mass falls back to four. H2 protects position 0 and chooses the three highest-mass positions 1 through 63, breaks ties earlier, preserves chronological order and deduplicates recent K/V. Both use only causal prefix attention and a fixed 1024 retained budget. H3 is optional preallocated rolling-KV systems work, motivated only if a profiler shows material allocation cost; it is not implemented. Validation books 1022, 11155 and 13089 were selected without losses; cap 8192 and actual seeds 0/1/2 were frozen before pilot evaluation.

## Pilots, selection, full evaluation and controls

h1_adaptive_sink: development delta -0.005345, 95% CI [-0.016612, 0.000460], runtime ratio 1.0026, peak-memory ratio 1.0000, acceptable cost True; h2_sink_selection: development delta -0.008053, 95% CI [-0.016347, -0.001836], runtime ratio 1.0084, peak-memory ratio 1.0000, acceptable cost True. Selection follows the frozen lower-mean-NLL/cost rule with runtime and peak-memory ratios at most 1.10. If neither qualifies, simpler H1 is evaluated as the preregistered negative-result fallback. The owner delegated this rule; no parameter search or test selection is added. Recorded selection: h2_sink_selection. Full comparison against fixed-four StreamingLLM: Equal-book candidate-minus-baseline NLL difference 0.000108 nats/token; book-cluster 95% CI [-0.000064, 0.000303]; verdict inconclusive. 10 books, actual model seeds [0, 1, 2]. Baseline macro NLL 2.429879, candidate 2.429987; secondary micro PPL 11.6922 versus 11.6934. Selected controls: h2_h2_forced_prefix: Equal-book candidate-minus-baseline NLL difference 0.000000 nats/token; book-cluster 95% CI [0.000000, 0.000000]; verdict inconclusive. 3 books, actual model seeds [0, 1, 2]. Baseline macro NLL 2.612087, candidate 2.612087; secondary micro PPL 13.6275 versus 13.6275. h2_random_anchors: Equal-book candidate-minus-baseline NLL difference 0.016333 nats/token; book-cluster 95% CI [0.000450, 0.030454]; verdict not_supported. 3 books, actual model seeds [0, 1, 2]. Baseline macro NLL 2.612087, candidate 2.628419; secondary micro PPL 13.6275 versus 13.8519. Full-checkpoint forced-prefix control: all 9 development book-seed NLL/input/mask arrays match the fixed-four baseline bitwise; exact receipt environment/verification/forced-prefix-identity.json. Forced-prefix identity is independently tested; H1 has calibration-only/fixed-k controls, H2 forced-prefix/random-anchor controls. Controls use the development set and cannot be treated as full-test effects. Only the selected family's controls are required and executed. Largest selected-minus-fixed-four book deltas: 22424: 0.000822 nats/token; 10321: 0.000273 nats/token. Maximum per-book delta range across actual seeds: 0. Frozen anchor-set counts across the 30 actual book-seed evaluations: {'[0, 1, 5, 49]': 3, '[0, 1, 29, 57]': 3, '[0, 1, 59, 63]': 3, '[0, 1, 21, 41]': 3, '[0, 1, 53, 57]': 3, '[0, 1, 62, 63]': 3, '[0, 1, 52, 54]': 3, '[0, 1, 24, 42]': 3, '[0, 1, 54, 56]': 3, '[0, 1, 24, 43]': 3}; fallbacks 0. These are descriptive cases on the frozen test set, not a further tuning rule. Per-book frozen anchors/k and calibration intervals are in tables/improvement_book_selections.csv.

## Compute, provenance and reproducibility

Current spent/reserved charge is 23.882927 device-instance hours, with a conservative 0.27h historical reserve. Full-GPU and MIG instance wall-hours are not normalized billing or currency cost. The user authorized unrestricted resources; 20h is no longer an execution limit. Three existing idle H800 MIG instances run seed workers concurrently, preserving another project on GPU0. Each attempt records selected UUID/parent, 30-SM class, driver, clock/power snapshot, source/config/data hashes, status, per-book recovery and registered-run wall time. The timer begins after the launch Git snapshot and run-directory creation and ends at finish(), includes model loading/inference/failure intervals, and excludes preflight/startup, the initial Git snapshot and post-finish checksum/exit tails. These are the same stored runtime_seconds used by the frozen cost rule; no cost field or threshold is changed. Runtime comparisons use the matched MIG class; clocks are not locked. Calibration intervals include necessary prefix forward passes and attention collection, measured as host wall time; they are not isolated extra kernel costs and are not added again to the registered-run charge. Incremental cost is assessed through registered-run ratios and controls. Pinned Python 3.10.12 / torch 2.14.0+cu130 / Transformers 4.33.0 and NVML bindings restore through setup. GPU1 instances are unaffected by GPU0's nightly cron.

## Limitations, AI reflection and human delivery

The ten fixed books are not a random sample of all PG19; one test book was previously observed. Three deterministic evaluations do not add independent books. Development selection uses only three books; attention proxies may fail, quality may not improve and calibration may exceed cost thresholds. Runtime order is not counterbalanced, clocks are unlocked and the three instances share a physical parent; ratios support the registered descriptive cost gate, not a causal speedup claim. The report preserves negative, inconclusive and failed outcomes. Agent verification is engineering verification, not an independent peer audit. The user's explicit authorization supersedes procedural approvals, while no teacher approval, member contribution, critical human review, deadline, final template or submission receipt is fabricated. Actual roster, T_final, peer review and individual defense remain human facts. Members can use the peer/defense packet. Exact Codex serving version was not exposed.

## References and artifact entry points

StreamingLLM: https://arxiv.org/html/2309.17453v4 ; official code pinned in third_party/streaming-llm. Model: pinned EleutherAI/pythia-2.8b revision and Apache-2.0 model card. PG19: DeepMind official processed GCS texts and pinned split lists. Rebuild: python scripts/build_results.py --manifest results/final_input_manifest.json ; python scripts/build_deliverables.py. Input/run hashes: results/build_provenance.json. Decisions: docs/review_packet.md. AI/roles: AI_USAGE.md and CONTRIBUTIONS.md.

## Reproduction per book

Source: `tables/reproduction_per_book.csv`. Negative delta favors the candidate; controls use development books.

| book_id | baseline_nll | candidate_nll | delta | scored_tokens |
|---|---|---|---|---|
| 10146 | 3.054432 | 2.222721 | -0.831712 | 15358 |
| 10321 | 3.704848 | 3.002012 | -0.702837 | 15358 |
| 10356 | 3.264875 | 2.570339 | -0.694536 | 15358 |
| 10762 | 3.722634 | 3.063084 | -0.659550 | 15358 |
| 12204 | 2.766364 | 1.976411 | -0.789953 | 6115 |
| 15562 | 2.916400 | 2.202056 | -0.714344 | 15358 |
| 22424 | 2.939753 | 2.234202 | -0.705551 | 15358 |
| 24553 | 3.402428 | 2.641161 | -0.761267 | 15358 |
| 2544 | 3.247901 | 2.505462 | -0.742439 | 15358 |
| 25646 | 2.496714 | 1.881346 | -0.615368 | 15358 |

## Development pilots

Source: `tables/pilot_comparison.csv`. Negative delta favors the candidate; controls use development books.

| method | paired_macro_delta_nll | ci95_low | ci95_high | runtime_ratio | peak_memory_ratio |
|---|---|---|---|---|---|
| h1_adaptive_sink | -0.005345 | -0.016612 | 0.000460 | 1.002620 | 1.000000 |
| h2_sink_selection | -0.008053 | -0.016347 | -0.001836 | 1.008424 | 1.000000 |

## Selected-method full test

Source: `tables/improvement_per_book.csv`. Negative delta favors the candidate; controls use development books.

| book_id | baseline_nll | candidate_nll | delta | scored_tokens |
|---|---|---|---|---|
| 10146 | 2.222721 | 2.222454 | -0.000266 | 15358 |
| 10321 | 3.002012 | 3.002284 | 0.000273 | 15358 |
| 10356 | 2.570339 | 2.570026 | -0.000313 | 15358 |
| 10762 | 3.063084 | 3.063067 | -0.000017 | 15358 |
| 12204 | 1.976411 | 1.976573 | 0.000162 | 6115 |
| 15562 | 2.202056 | 2.202287 | 0.000231 | 15358 |
| 22424 | 2.234202 | 2.235024 | 0.000822 | 15358 |
| 24553 | 2.641161 | 2.641333 | 0.000173 | 15358 |
| 2544 | 2.505462 | 2.505398 | -0.000064 | 15358 |
| 25646 | 1.881346 | 1.881423 | 0.000076 | 15358 |

## Scientific summary and controls

Source: `tables/scientific_summary.csv`. Negative delta favors the candidate; controls use development books.

| comparison | n_books | paired_macro_delta_nll | ci95_low | ci95_high | claim_status | runtime_ratio | peak_memory_ratio |
|---|---|---|---|---|---|---|---|
| reproduction | 10 | -0.721756 | -0.759084 | -0.685837 | supported | 1.003282 | 1.000000 |
| improvement | 10 | 0.000108 | -0.000064 | 0.000303 | inconclusive | 0.995707 | 1.000000 |
| ablations/h2_h2_forced_prefix | 3 | 0.000000 | 0.000000 | 0.000000 | inconclusive | 1.008119 | 1.000000 |
| ablations/h2_random_anchors | 3 | 0.016333 | 0.000450 | 0.030454 | not_supported | 1.005264 | 1.000000 |
