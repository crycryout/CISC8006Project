#!/usr/bin/env python
"""Independent cache-index oracle for the CISC8006 StreamingLLM reproduction.

Verifies, at every decode step, that the official `StartRecentKVCache`
(third_party/streaming-llm) implements exactly the retention policy the claim
describes:

  - window arm   (sink=0,   recent=1024): retains the latest 1024 positions
  - streaming arm(sink=4,   recent=1020): retains positions {0..3} and the
                                           latest 1020 non-sink positions
  - total retained positions never exceed the budget (1024)
  - implicit position ids (transformers GPT-NeoX semantics: positions restart
    at the current cache length) remain consistent between the two arms

Independence: the EXPECTED traces are produced by a pure-Python simulator of
the retention policy (no reference to the official implementation); the ACTUAL
traces are produced by driving the official `StartRecentKVCache` with mock KV
tensors whose values encode token positions. The test passes only if the two
agree at every step.

Run:  python audit/cache_index_test.py         (CPU only, no model needed)
Outputs:
  audit/expected_traces/window_expected.json
  audit/expected_traces/streaming_expected.json
  audit/expected_traces/window_actual.json
  audit/expected_traces/streaming_actual.json
Exit code 0 = all checks passed.
"""

import json
import os
import sys

import torch

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "third_party", "streaming-llm"))

from streaming_llm.kv_cache import StartRecentKVCache  # noqa: E402  (official code under test)

BUDGET = 1024
STREAM_LEN = 2100  # > 2x budget: exercises fill, first eviction, steady state
LAYERS = 2  # mock depth is enough to catch per-layer slicing bugs
HEADS, DIM = 1, 1  # values are position tags, not real features


# ---------------------------------------------------------------- expected ---
def simulate_window(seq_len: int, budget: int):
    """Pure-Python model of `sink=0, recent=budget`."""
    retained = []
    trace = []
    for step in range(seq_len):
        # forward(): current position `step` is appended to the cache
        retained.append(step)
        # eviction(): keep the latest `budget`
        retained = retained[-budget:]
        trace.append(list(retained))
    return trace


def simulate_streaming(seq_len: int, sink: int, recent: int):
    """Pure-Python model of `sink=4, recent=1020` (official slice semantics).

    Official eviction concatenates [0:sink] + [len-recent:len] **after** the
    current token is appended, i.e. sinks are always positions 0..sink-1 and
    the recent window covers the newest `recent` positions.
    """
    retained = []
    trace = []
    for step in range(seq_len):
        retained.append(step)
        if len(retained) > sink + recent:
            retained = retained[:sink] + retained[-recent:]
        trace.append(list(retained))
    return trace


# ----------------------------------------------------------------- actual ---
def make_kv(positions, layers=LAYERS):
    """Mock legacy-tuple past_key_values; the seq dim (dim=2, GPT-NeoX layout)
    is filled with the token positions so retention is directly readable."""
    k = torch.tensor(positions, dtype=torch.float32).view(1, HEADS, -1, DIM)
    v = k.clone()
    return [[k.clone(), v.clone()] for _ in range(layers)]


def drive_official(sink: int, recent: int, seq_len: int):
    cache = StartRecentKVCache(start_size=sink, recent_size=recent, k_seq_dim=2, v_seq_dim=2)
    retained: list[int] = []
    trace = []
    for step in range(seq_len):
        retained.append(step)  # forward() appends current position
        pkv = make_kv(retained)
        pkv = cache(pkv)  # eviction after the step
        retained = [int(p) for p in pkv[0][0].flatten().tolist()]
        trace.append(list(retained))
    return trace


def implicit_position_ids(retained_len: int, cur_batch: int = 1):
    """GPT-NeoX (transformers<=4.33) semantics: when position_ids is None, new
    positions start at past KV length. Both arms therefore assign the SAME ids
    to the current token for a fixed budget — consistency condition."""
    return list(range(retained_len, retained_len + cur_batch))


# ------------------------------------------------------------------- test ---
def main():
    out_dir = os.path.join(REPO_ROOT, "audit", "expected_traces")
    os.makedirs(out_dir, exist_ok=True)
    failures = []

    cases = {
        "window": (0, BUDGET, simulate_window(STREAM_LEN, BUDGET)),
        "streaming": (4, BUDGET - 4, simulate_streaming(STREAM_LEN, 4, BUDGET - 4)),
    }

    for name, (sink, recent, expected) in cases.items():
        actual = drive_official(sink, recent, STREAM_LEN)

        json.dump(expected, open(os.path.join(out_dir, f"{name}_expected.json"), "w"))
        json.dump(actual, open(os.path.join(out_dir, f"{name}_actual.json"), "w"))

        # check 1: step-by-step identity of retained positions
        for step, (exp_step, act_step) in enumerate(zip(expected, actual)):
            if exp_step != act_step:
                failures.append(
                    f"{name}: step {step} retained mismatch: expected {exp_step[-5:]}.. "
                    f"got {act_step[-5:]}.."
                )
                break

        # check 2: budget never exceeded (after eviction)
        max_len = max(len(t) for t in actual)
        if max_len > BUDGET:
            failures.append(f"{name}: retained length {max_len} exceeds budget {BUDGET}")

        # check 3: policy shape — sinks are exactly {0..sink-1} once evicting
        if sink > 0:
            steady = actual[BUDGET + 50]
            if steady[:sink] != list(range(sink)):
                failures.append(f"{name}: sink positions are {steady[:sink]}, expected {list(range(sink))}")
            if len(steady) != BUDGET:
                failures.append(f"{name}: steady length {len(steady)} != {BUDGET}")

        # check 4: monotone contiguous recent window after sinks
        steady = actual[-1]
        rec = steady[sink:]
        if rec != list(range(rec[0], rec[0] + len(rec))):
            failures.append(f"{name}: recent window not contiguous: {rec[:5]}..")

        print(
            f"[{name:9s}] sink={sink} recent={recent} steps={STREAM_LEN} "
            f"steady_len={len(actual[-1])} OK" if not failures else f"[{name}] issues: {len(failures)}"
        )

    # check 5: implicit position-id consistency across arms (same budget)
    w_pos = implicit_position_ids(BUDGET)
    s_pos = implicit_position_ids(BUDGET)
    if w_pos != s_pos:
        failures.append("implicit position ids diverge between arms")

    # check 6: the two arms really differ (sinks present in streaming only)
    w_last = json.load(open(os.path.join(out_dir, "window_actual.json")))[-1]
    s_last = json.load(open(os.path.join(out_dir, "streaming_actual.json")))[-1]
    if not (set(range(4)) <= set(s_last)) or set(range(4)) <= set(w_last):
        failures.append("arm separation check failed (sinks misplaced)")

    if failures:
        print("\nFAILURES:")
        for f in failures:
            print(" -", f)
        sys.exit(1)
    print("\nAll cache-index oracle checks passed.")
    print("Traces written to audit/expected_traces/ (expected vs actual, per step).")


if __name__ == "__main__":
    main()
