#!/usr/bin/env python3
"""The original list is immutable. Verify portable assets instead of refreezing it."""
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
from scripts.verify_assets import main
if __name__=='__main__': main()
