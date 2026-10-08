#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python_executable="${CISC_PYTHON:-.venv-verified/bin/python}"
if [[ ! -x "$python_executable" ]]; then
  echo 'Run bash scripts/setup_env.sh .venv-verified first' >&2
  exit 2
fi
exec "$python_executable" scripts/run_smoke.py "$@"
