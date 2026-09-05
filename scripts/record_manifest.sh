#!/usr/bin/env bash
# Record checksums + environment info into auditable files.
# Usage: bash scripts/record_manifest.sh
set -euo pipefail
cd "$(dirname "$0")/.."

echo "== model + dataset checksums =="
{
  echo "# Generated $(date -u +%Y-%m-%dT%H:%M:%SZ) by scripts/record_manifest.sh"
  echo "# Model: EleutherAI/pythia-2.8b @ 2a259cdd96a4beb1cdf467512e3904197345f6a9"
  sha256sum "$HOME"/.cache/huggingface/hub/models--EleutherAI--pythia-2.8b/snapshots/2a259cdd96a4beb1cdf467512e3904197345f6a9/* 2>/dev/null
  echo "# PG19 test books (GCS deepmind-gutenberg, via official test_files.txt)"
  sha256sum data/pg19/metadata.csv data/pg19/test/*.txt
} > environment/data_checksums.txt
tail -5 environment/data_checksums.txt

echo "== pip freeze =="
.venv/bin/pip freeze > environment/pip-freeze.txt

echo "== system info =="
{
  echo "# Generated $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv
  python3 --version
  uname -a
  .venv/bin/python -c "import torch, transformers; print('torch', torch.__version__); print('transformers', transformers.__version__)"
} > environment/system-info.txt
cat environment/system-info.txt
echo "done."
