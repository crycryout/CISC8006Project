#!/usr/bin/env bash
# One-command smoke test (Week-5 requirement, in place early).
# Runs the cache-index oracle (CPU) then both arms of the tiny R0001 run (GPU).
# Usage:  bash scripts/run_smoke.sh
set -euo pipefail
cd "$(dirname "$0")/.."

source .venv/bin/activate
# Model + tokenizer are fully cached; offline flags stop from_pretrained from
# issuing slow network checks that can stall the run for minutes.
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1

RUN_ID=R0001
BOOK=data/pg19/test/10146.txt
if [ -e "runs/${RUN_ID}" ] && [ "${ALLOW_RESMOKE:-0}" != "1" ]; then
  echo "runs/${RUN_ID} already exists (refusing to overwrite; set ALLOW_RESMOKE=1 to rerun into it)" >&2
  exit 1
fi
mkdir -p "runs/${RUN_ID}"
python scripts/write_metadata.py --run_id "$RUN_ID" --phase start 2>/dev/null || true
trap 'python scripts/write_metadata.py --run_id "$RUN_ID" --phase end 2>/dev/null || true' EXIT

echo "== [1/3] cache-index oracle (CPU, independent) =="
python audit/cache_index_test.py

echo "== [2/3] R0001 window arm (0 + 1024) =="
python scripts/eval_ppl.py --run_id "$RUN_ID" --method window \
  --sink_tokens 0 --recent_tokens 1024 \
  --book_files "$BOOK" --max_tokens_per_book 4096 \
  2>&1 | tee "runs/${RUN_ID}/window_stdout.log"

echo "== [3/3] R0001 streaming arm (4 + 1020) =="
python scripts/eval_ppl.py --run_id "$RUN_ID" --method streaming \
  --sink_tokens 4 --recent_tokens 1020 \
  --book_files "$BOOK" --max_tokens_per_book 4096 \
  2>&1 | tee "runs/${RUN_ID}/streaming_stdout.log"

echo "== smoke complete: runs/${RUN_ID}/{window,streaming}/result.json =="
