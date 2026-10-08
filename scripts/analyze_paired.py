#!/usr/bin/env python3
"""Strict paired analysis; invalid inputs never produce a scientific verdict."""
import argparse
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.io_utils import file_hash, write_json
from src.paired import analyze_pairs


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--window',required=True,nargs='+')
    p.add_argument('--streaming',required=True,nargs='+')
    p.add_argument('--manifest',default='data/assets_manifest.json')
    p.add_argument('--split',choices=['test','dev'],default='test')
    p.add_argument('--out',required=True)
    p.add_argument('--n_boot','--n-boot',type=int,default=10000)
    p.add_argument('--bootstrap-seed',type=int,default=0)
    p.add_argument('--diagnostic',action='store_true')
    a=p.parse_args()
    manifest=json.loads(Path(a.manifest).read_text())
    windows=[json.loads(Path(x).read_text()) for x in a.window]
    streams=[json.loads(Path(x).read_text()) for x in a.streaming]
    try:
        for r in windows+streams:
            if r['contract']['assets_manifest_sha256']!=file_hash(a.manifest): raise ValueError('manifest digest mismatch')
        out=analyze_pairs(windows,streams,manifest,a.split,not a.diagnostic,a.bootstrap_seed,a.n_boot)
    except (ValueError,KeyError,TypeError) as e:
        p.error(f'validation_status=invalid: {e}')
    out['inputs']=[dict(path=x,sha256=file_hash(x)) for x in a.window+a.streaming]
    write_json(Path(a.out)/'paired_result.json',out)
    print(json.dumps(out,indent=2))


if __name__=='__main__': main()
