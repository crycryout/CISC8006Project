#!/usr/bin/env bash
# Full reproduction pass (Week 6+): both arms over the preregistered book list.
# Usage: bash scripts/run_reproduction.sh <RUN_ID> [max_tokens_per_book]
set -euo pipefail
cd "$(dirname "$0")/.."
source .venv/bin/activate
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1  # model cached; skip network checks

RUN_ID="${1:?usage: run_reproduction.sh <RUN_ID> [max_tokens]}"
MAXTOK="${2:-16384}"   # TODO: freeze default after R0001 (compute_budget.md)

BOOKS=$(python -c "
import json
print(' '.join('data/pg19/' + b['file'] for b in json.load(open('audit/book_list.json'))['books']))")

mkdir -p "runs/${RUN_ID}"
{ echo "host=$(hostname) gpu=$(nvidia-smi --query-gpu=name,driver_version --format=csv,noheader | head -1)";
  echo "started=$(date -u +%Y-%m-%dT%H:%M:%SZ)"; } > "runs/${RUN_ID}/metadata.json"

python scripts/eval_ppl.py --run_id "$RUN_ID" --method window \
  --sink_tokens 0 --recent_tokens 1024 \
  --book_files $BOOKS --max_tokens_per_book "$MAXTOK" \
  2>&1 | tee "runs/${RUN_ID}/window_stdout.log"

python scripts/eval_ppl.py --run_id "$RUN_ID" --method streaming \
  --sink_tokens 4 --recent_tokens 1020 \
  --book_files $BOOKS --max_tokens_per_book "$MAXTOK" \
  2>&1 | tee "runs/${RUN_ID}/streaming_stdout.log"

bash scripts/analyze_results.sh "runs/${RUN_ID}"
