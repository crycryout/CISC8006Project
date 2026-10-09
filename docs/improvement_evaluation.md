# Selected full improvement evaluation

H2 sink selection was chosen after all nine development runs completed, using the frozen owner-delegated mean/cost rule. Its development ΔNLL−0.0080531545,95% CI [−0.0163472468,−0.0018359957], runtime ratio1.0084236115 and memory ratio1.0 qualified and ranked ahead of H1. Evidence: `docs/pilot_selection.md`; immutable proposal SHA51845b744f16c83a9298348eb86e2b5f5ffb546e6e04d9cd6afa0d6ee5087f79. This pilot result does not assign the full-test verdict.

All three actual H2 full-test seed0/1/2 runs completed on2026-10-09 by13:20 UTC and strictly validate: `I-h2-v2-mig-20261009-h2_sink_selection-s0`, `s1`, `s2`. Launch source is1061645; numerical source SHA is `a6dbe103b2e9416295807cd481a9ff1660fbfede9c26b68e7db65d230e6229ef`. Original ten books, cap16384/natural short7141, fp16 forward/fp32 scoring, cache-relative positions, independent book resets and1024 retained positions remain frozen. The reused baseline is the compatible complete fixed-four main group; matched UUID, data/token/mask/model/numerical-source contracts were checked before comparison.

H2 protects position0 and freezes the top three causal attention-ranked positions1..63 from queries64..511. Chronological order, deduplication and recent filling preserve the1024 budget. Test-book prefixes are causal inputs to this preregistered algorithm; no future loss or test performance selects the rule. All30 per-book seed selections and calibration intervals are in `tables/improvement_book_selections.csv`. No fallback occurred; anchors and loss arrays are bitwise identical across the three actual seeds for each book.

The full-test primary equal-book candidate-minus-fixed-four ΔNLL is **+0.0001077281761**, book-bootstrap95% CI **[−0.00006434621625,+0.0003026897247]**, verdict **inconclusive**. Four books favor H2 and six favor fixed-four. This does not establish a test-set quality improvement, a harmful effect, or exact equivalence. The development benefit did not establish a generalizable improvement on this frozen ten-book test. Evidence: `results/improvement/summary.json`, `per_book.csv`, `paired_result.json`, and independent raw-array receipt `environment/verification/improvement-raw-reconstruction.json`.

| Metric | Fixed-four | H2 |
|---|---:|---:|
| Equal-book macro NLL |2.4298791887|2.4299869169|
| Secondary micro PPL |11.6921566131|11.6933755901|
| Mean registered-run seconds |7341.1039884|7309.5850625|
| Peak allocated MiB |6445.9438477|6445.9438477|

The observed runtime ratio is0.9957065142 and memory ratio1.0; unlocked clocks, method order and shared physical parent prevent a causal speedup inference. Whole calibration host intervals sum to207.6065544/202.9008460/204.2003455 seconds for seeds0/1/2. They include ordinary prefix inference and attention collection, and are not isolated extra overhead or an additional charge.

Descriptive failure cases: book22424 has the largest unfavorable delta+0.000822374 with frozen anchors[0,1,52,54]; book10321 follows at+0.000272643 with[0,1,29,57]. Book10356 has the largest favorable delta−0.000312895 with[0,1,59,63]. These cases do not identify the cause of the loss change and do not trigger further test tuning. Late-position curves retain exact512-step bin coverage rather than zero-padding short books.

Required H2 controls are forced positions0..3 with the same prefix collection, and position0 plus three seeded random anchors. Both use the original three development books and actual seeds0/1/2. The six runs started after the full test completed and are currently running; their verdicts are pending. H1 controls remain unused proposals; only the selected family's two controls are required.

Registered-run duration includes model loading/inference/failures and has the exact boundary in `compute_budget.md`. Full cost ratios, book-cluster CI, late-position coverage and worst-book cases come from actual outputs; the selected controls will be added after completion. All failures and negative/inconclusive outcomes are retained. The user authorized execution without further approval; genuine human course activities remain separately recorded.
