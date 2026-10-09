# Paper comparison and scope limits

Primary source: [StreamingLLM arXiv v4, 7 April 2024](https://arxiv.org/html/2309.17453v4), §3.2 and §4.1. Figure3 is the short-stream language-modeling comparison; Figure5 is the multi-million-token result; Figure4 illustrates the cache. Fixed official implementation is vendored at `2e5042606d69933d88fbf909bd77907456b9b4dd`.

| Dimension | Paper | Owner-authorized project protocol |
|---|---|---|
| Mechanism | Retain initial sinks and recent KV; cached raw K receives positions continuous within the cache (§3.2) | Same position mechanism, independently tested for every GPT-NeoX layer |
| Model | Multiple families/scales, including Pythia2.8B | Only pinned Pythia2.8B; no new training |
| PG19 processing | Concatenated test books (§4.1), cache continues across transitions in official evaluator | Original 10 books separately reset; max16384, short12204 remains7141 |
| Budget | Pythia1024 in language-modeling comparison (§4.1) | Eviction retains≤1024; one forward temporarily sees1025 |
| Metric | Language-modeling perplexity curves / full-stream experiments | Primary equal-book post-overflow NLL difference, secondary token-weighted PPL |
| Hardware / efficiency | A6000 in its efficiency benchmark (§4.5); PG19 PPL-run hardware unspecified | Existing H800 MIG2g.20gb instances,30SM each; matched UUID per seed; no paper-speedup or full-H800-throughput claim |

Comparison target is method ordering on this scaled, independent-book protocol. Different aggregation, reset behavior and stream length prevent direct absolute-PPL error calculations. The paper's Table1 values use Llama2-13B, not this pinned model; they are not project acceptance thresholds. No digitized target is fabricated.

Baseline positions are made consistent across both arms. This isolates retained membership; any difference from the paper's exact baseline implementation is disclosed as a controlled-comparison deviation. All six reproduction runs now validate and reconstruct directly from raw arrays: paired equal-book ΔNLL−0.7217558173, 95% CI [−0.7590835293,−0.6858373358], supported on the frozen ten-book scope. This matches the predicted method ordering; it does not reproduce the paper's absolute PPL values or4M-token experiment. Exact groups are in `results/final_input_manifest.json`. The2×2 outputs remain diagnostic only. Smoke book10146 was observed historically and is retained to avoid result-driven replacement. Full-H800/MIG diagnostics were not bitwise identical and never enter a mixed-hardware formal pair.
