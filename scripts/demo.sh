#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python_executable="${CISC_PYTHON:-.venv-verified/bin/python}"
"$python_executable" scripts/run_smoke.py --mode cpu
"$python_executable" scripts/validate_runs.py --run runs/D-S1-20261008 --out /tmp/cisc8006-demo-validation.json
"$python_executable" -c 'import json; r=json.load(open("runs/D-S1-20261008/result.json")); print({k:r[k] for k in ("run_id","macro_book_nll","scored_tokens","git_commit")})'
