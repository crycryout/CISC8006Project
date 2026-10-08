# Paper comparison and scope limits

Primary source: [StreamingLLM arXiv v4, 7 April 2024](https://arxiv.org/html/2309.17453v4), §3.2 and §4.1. Figure3 is the short-stream language-modeling comparison; Figure5 is the multi-million-token result; Figure4 illustrates the cache. Fixed official implementation is vendored at `2e5042606d69933d88fbf909bd77907456b9b4dd`.

| Dimension | Paper | Candidate project protocol |
|---|---|---|
| Mechanism | Retain initial sinks and recent KV; cached raw K receives positions continuous within the cache (§3.2) | Same position mechanism, independently tested for every GPT-NeoX layer |
| Model | Multiple families/scales, including Pythia2.8B | Only pinned Pythia2.8B; no new training |
| PG19 processing | Concatenated test books (§4.1), cache continues across transitions in official evaluator | Original 10 books separately reset; max16384, short12204 remains7141 |
| Budget | Pythia1024 in language-modeling comparison (§4.1) | Eviction retains≤1024; one forward temporarily sees1025 |
| Metric | Language-modeling perplexity curves / full-stream experiments | Primary equal-book post-overflow NLL difference, secondary token-weighted PPL |
| Hardware / efficiency | Paper has separate training and efficiency experiments | One H800; no claim about paper's speedup or training |

Comparison target is method ordering on this scaled, independent-book protocol. Different aggregation, reset behavior and stream length prevent direct absolute-PPL error calculations. The paper's Table1 values use Llama2-13B, not this pinned model; they are not project acceptance thresholds. No digitized target is fabricated.

Baseline positions are made consistent across both arms. This isolates retained membership; any difference from the paper's exact baseline implementation is disclosed as a controlled-comparison deviation. Reproduction run IDs and formal verdict remain pending in `results/reproduction/`; current 2×2 outputs are diagnostic only. Smoke book10146 was observed historically and is retained to avoid result-driven replacement.
