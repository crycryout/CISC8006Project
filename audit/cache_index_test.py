#!/usr/bin/env python3
"""CPU retention/RoPE audit; historical traces remain untouched in expected_traces/."""
from pathlib import Path
import os
import subprocess
import sys
root=Path(__file__).resolve().parents[1]
raise SystemExit(subprocess.call([sys.executable,'-m','pytest','tests/test_position_reference.py','-q','-k','not gpu_precision_reference'],cwd=root,env=dict(os.environ,CUDA_VISIBLE_DEVICES='')))
