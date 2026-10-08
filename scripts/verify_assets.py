#!/usr/bin/env python3
"""Fail closed on missing, altered or retokenized assets; never change manifests."""
import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.io_utils import file_hash, now, write_json
from scripts.prepare_data import describe


def verify(manifest_path, asset_root):
    from huggingface_hub import hf_hub_download
    from transformers import AutoTokenizer
    manifest=json.loads(Path(manifest_path).read_text())
    for name, expected in manifest["model_files"].items():
        path=hf_hub_download(manifest["model"],name,revision=manifest["model_revision"],local_files_only=True)
        if file_hash(path)!=expected["sha256"] or Path(path).stat().st_size!=expected["bytes"]:
            raise ValueError(f"model asset hash/size mismatch: {name}")
    for split, expected in manifest["split_lists"].items():
        path=hf_hub_download("deepmind/pg19",f"data/{split}_files.txt",repo_type="dataset",revision=manifest["dataset_revision"],local_files_only=True)
        if file_hash(path)!=expected["sha256"]:
            raise ValueError(f"split list mismatch: {split}")
    tokenizer=AutoTokenizer.from_pretrained(manifest["model"],revision=manifest["tokenizer_revision"],local_files_only=True)
    for book in manifest["test_books"]+manifest["dev_books"]:
        actual=describe(tokenizer,Path(asset_root),book["file"],book["token_cap"])
        if actual!=book:
            raise ValueError(f"text/token contract changed: {book['file']}")
    return {"verified_at":now(),"validation_status":"valid","manifest_sha256":file_hash(manifest_path),
            "test_books":len(manifest["test_books"]),"dev_books":len(manifest["dev_books"]),
            "test_input_tokens":sum(b["input_tokens"] for b in manifest["test_books"]),
            "test_scored_tokens":sum(max(b["input_tokens"]-1026,0) for b in manifest["test_books"])}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest",default="data/assets_manifest.json")
    parser.add_argument("--asset-root",default="data/pg19")
    parser.add_argument("--protocol",help="YAML protocol with assets_manifest and asset_root")
    parser.add_argument("--out",default="environment/verification/assets.json")
    args=parser.parse_args()
    if args.protocol:
        import yaml
        protocol=yaml.safe_load(Path(args.protocol).read_text())
        args.manifest=protocol["assets_manifest"]
        args.asset_root=protocol.get("asset_root",args.asset_root)
    result=verify(args.manifest,args.asset_root)
    write_json(args.out,result)
    print(json.dumps(result,indent=2))


if __name__=="__main__":
    main()
