#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
target="${1:-.venv-verified}"
if [[ ! -e "$target/bin/python" ]]; then
  if command -v uv >/dev/null; then
    uv venv --python python3 "$target"
  else
    python3 -m venv --without-pip "$target"
  fi
fi
if command -v uv >/dev/null; then
  uv pip install --python "$target/bin/python" pip
  uv pip install --python "$target/bin/python" torch==2.14.0+cu130 --index-url https://download.pytorch.org/whl/cu130
  uv pip install --python "$target/bin/python" -r environment/requirements.txt
else
  if ! "$target/bin/python" -m pip --version >/dev/null 2>&1; then
    curl --fail --location https://bootstrap.pypa.io/get-pip.py -o "$target/get-pip.py"
    "$target/bin/python" "$target/get-pip.py"
  fi
  "$target/bin/python" -m pip install torch==2.14.0+cu130 --index-url https://download.pytorch.org/whl/cu130
  "$target/bin/python" -m pip install -r environment/requirements.txt
fi
"$target/bin/python" -m pip check
"$target/bin/python" -m pip freeze > "$target/installed-freeze.txt"
"$target/bin/python" -c 'import torch, transformers, numpy; print(torch.__version__, transformers.__version__, numpy.__version__)'
