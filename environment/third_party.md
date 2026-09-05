# Third-Party Code Pin

## mit-han-lab/streaming-llm

| Item | Value |
|---|---|
| Upstream | https://github.com/mit-han-lab/streaming-llm |
| Pinned commit | `2e5042606d69933d88fbf909bd77907456b9b4dd` |
| Commit date / subject | 2024-07-11 — "Update README.md" |
| Local path | `third_party/streaming-llm/` (vendored; nested `.git` removed so it is fully tracked by this repo) |
| License | MIT (file: `third_party/streaming-llm/LICENSE`) |
| Re-checkout | `git clone https://github.com/mit-han-lab/streaming-llm && cd streaming-llm && git checkout 2e5042606d69933d88fbf909bd77907456b9b4dd` |

### What we use from it

- `streaming_llm/kv_cache.py` — `StartRecentKVCache` (arm implementations A/B)
- `examples/eval_long_ppl.py` — reference evaluation semantics (token-by-token teacher forcing, NLL accumulation); our harness in `scripts/eval_ppl.py` mirrors this flow with local parquet data loading and scored-region masking
- `streaming_llm/pos_shift/modify_gpt_neox.py` — secondary pos-shift variant only

### Local modifications

**None** to any file under `third_party/streaming-llm/`. Any future compatibility patch is applied as a separate, documented commit touching only `third_party/`, with the failing log preserved (SKILL §7-B).
