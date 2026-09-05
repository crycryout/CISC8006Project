#!/usr/bin/env bash
# Paired analysis over books: per-book NLL table, paired dNLL, bootstrap 95% CI.
# Usage: bash scripts/analyze_results.sh runs/R0002
set -euo pipefail
cd "$(dirname "$0")/.."
source .venv/bin/activate
RUN_DIR="${1:?usage: analyze_results.sh <run_dir>}"
python scripts/analyze_paired.py --window "$RUN_DIR/window/result.json" --streaming "$RUN_DIR/streaming/result.json" --out "$RUN_DIR"
