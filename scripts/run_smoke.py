#!/usr/bin/env python3
"""CPU fixture smoke or prepared GPU smoke; always allocate unique immutable IDs."""
import argparse
import os
from pathlib import Path
import subprocess
import sys
import uuid
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.config import DEFAULTS
from src.io_utils import write_json
from src.run_store import RunStore, Tee


def main():
    p=argparse.ArgumentParser(); p.add_argument('--mode',choices=['cpu','gpu'],default='cpu'); p.add_argument('--run-id')
    a=p.parse_args(); rid=a.run_id or 'smoke-'+a.mode+'-'+uuid.uuid4().hex[:12]
    if a.mode=='gpu':
        return subprocess.call([sys.executable,str(ROOT/'scripts/eval_ppl.py'),'--run-id',rid,'--phase','smoke','--method','streaming','--sink-tokens','4','--recent-tokens','1020','--book-files','data/pg19/test/10146.txt','--max-tokens-per-book','4096','--max-gpu-seconds','900'],cwd=ROOT)
    cfg=dict(DEFAULTS,run_id=rid,phase='smoke',device='cpu',method='window')
    store=RunStore(cfg)
    with open(store.directory/'stdout.log','x') as out,open(store.directory/'stderr.log','x') as err:
        code=subprocess.call([sys.executable,'-m','pytest','tests/','-q','-k','not gpu_precision_reference'],cwd=ROOT,stdout=out,stderr=err,env=dict(os.environ,CUDA_VISIBLE_DEVICES=''))
    write_json(store.directory/'result.json',dict(run_id=rid,status='completed' if code==0 else 'failed',purpose='offline CPU fixtures; not a model claim',claim_status=None))
    store.finish(code)
    print(f'{rid}: '+('passed CPU fixtures' if code==0 else 'failed; see stdout.log'))
    return code


if __name__=='__main__': sys.exit(main())
