#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python_executable="${CISC_PYTHON:-.venv-verified/bin/python}"
smoke_output="$("$python_executable" scripts/run_smoke.py --mode cpu)"
printf '%s\n' "$smoke_output"
smoke_id="${smoke_output%%:*}"
cat "runs/$smoke_id/stdout.log"
"$python_executable" scripts/demo_evidence.py
