#!/usr/bin/env python3
"""Account the complete H800 fixture process as one immutable test attempt."""
import os
from pathlib import Path
import subprocess
import sys
import uuid
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.config import DEFAULTS
from src.io_utils import write_json
from src.run_store import RunStore
from scripts.eval_ppl import hardware


def main():
    rid='fixtures-h800-'+uuid.uuid4().hex[:12]
    cfg=dict(DEFAULTS,run_id=rid,phase='smoke',method='window',device='cuda',max_gpu_seconds=180)
    store=RunStore(cfg,hardware('cuda'))
    with open(store.directory/'stdout.log','x') as out,open(store.directory/'stderr.log','x') as err:
        try:
            code=subprocess.call([sys.executable,'-m','pytest','tests/','-q'],cwd=ROOT,stdout=out,stderr=err,timeout=180)
        except subprocess.TimeoutExpired: code=124
    write_json(store.directory/'result.json',dict(run_id=rid,status='completed' if code==0 else 'failed',artifact_kind='fixture',purpose='independent CPU and H800 fixtures; not a scientific claim',claim_status=None))
    row=store.finish(code)
    print(f'{rid}: exit={code}, whole-process GPU charge={row["gpu_hours"]:.6f}h')
    print((store.directory/'stdout.log').read_text())
    return code


if __name__=='__main__': sys.exit(main())
