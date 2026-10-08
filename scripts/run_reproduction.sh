#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
exec "${CISC_PYTHON:-.venv-verified/bin/python}" scripts/run_matrix.py --matrix configs/reproduction_matrix.yaml --execute "$@"
