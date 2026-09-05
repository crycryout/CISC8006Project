#!/usr/bin/env bash
# Full reproduction pass (Week 6+): both arms over the frozen protocol.
# The frozen YAMLs in configs/ are the single source of truth for arms,
# book list, and token cap — this script adds no protocol values of its own.
# Usage: bash scripts/run_reproduction.sh <RUN_ID>
set -euo pipefail
cd "$(dirname "$0")/.."
source .venv/bin/activate
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1  # model cached; skip network checks

RUN_ID="${1:?usage: run_reproduction.sh <RUN_ID>}"
if [ -e "runs/${RUN_ID}" ]; then
  echo "Run ID runs/${RUN_ID} already exists; refusing to overwrite (registry rule: never overwrite a run directory)." >&2
  exit 1
fi
mkdir -p "runs/${RUN_ID}"

python scripts/write_metadata.py --run_id "$RUN_ID" --phase start
trap 'python scripts/write_metadata.py --run_id "$RUN_ID" --phase end' EXIT

python scripts/eval_ppl.py --config configs/window.yaml   --run_id "$RUN_ID" 2>&1 | tee "runs/${RUN_ID}/window_stdout.log"
python scripts/eval_ppl.py --config configs/streaming.yaml --run_id "$RUN_ID" 2>&1 | tee "runs/${RUN_ID}/streaming_stdout.log"

bash scripts/analyze_results.sh "runs/${RUN_ID}"
