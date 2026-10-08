#!/usr/bin/env python3
"""Restore pinned assets or freeze a hash manifest without evaluating a model."""
import argparse
import json
from pathlib import Path
import sys
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.io_utils import file_hash, object_hash, now, write_json

MODEL = "EleutherAI/pythia-2.8b"
REV = "2a259cdd96a4beb1cdf467512e3904197345f6a9"
DATA_REV = "4d28bd77e66947ad3835cf78ed7aaeb4dd87ad8b"
WEIGHT_HASH = "ab496f1c3fd79e3c749a9d5414136a2c8e4224f94eecb261970315cdb0f813fe"
MODEL_FILES = ["config.json", "tokenizer.json", "tokenizer_config.json", "special_tokens_map.json", "model.safetensors"]


def token_hash(ids):
    import numpy as np
    import hashlib
    return hashlib.sha256(np.asarray(ids, dtype="<i8").tobytes()).hexdigest()


def download(url, path):
    path = Path(path)
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".part")
    urllib.request.urlretrieve(url, temporary)
    temporary.replace(path)


def describe(tokenizer, asset_root, rel, cap):
    path = asset_root / rel
    ids = tokenizer(path.read_text(encoding="utf-8"), add_special_tokens=True)["input_ids"]
    return {"book_id":path.stem, "file":rel, "text_sha256":file_hash(path),
            "full_token_length":len(ids), "input_tokens":min(cap,len(ids)),
            "token_ids_sha256":token_hash(ids[:cap]), "token_cap":cap}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default="data/assets_manifest.json", help="structured JSON; Markdown is a human index only")
    parser.add_argument("--asset-root", default="data/pg19")
    parser.add_argument("--freeze", action="store_true", help="first-time freeze; never overwrite an existing manifest")
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()
    from huggingface_hub import hf_hub_download
    from transformers import AutoTokenizer
    manifest_path = Path(args.manifest)
    asset_root = Path(args.asset_root)
    if args.freeze and manifest_path.exists():
        parser.error(f"manifest exists: {manifest_path}; use verify_assets.py")
    pins = {}
    for name in MODEL_FILES:
        path = hf_hub_download(MODEL, name, revision=REV, local_files_only=args.offline)
        pins[name] = {"sha256":file_hash(path), "bytes":Path(path).stat().st_size}
    if pins["model.safetensors"]["sha256"] != WEIGHT_HASH:
        raise ValueError("pinned model weight SHA256 mismatch")
    tokenizer = AutoTokenizer.from_pretrained(MODEL, revision=REV, local_files_only=args.offline)
    split_files = {}
    for split in ("test", "validation"):
        path = hf_hub_download("deepmind/pg19", f"data/{split}_files.txt", repo_type="dataset", revision=DATA_REV, local_files_only=args.offline)
        split_files[split] = {"sha256":file_hash(path), "entries":Path(path).read_text().splitlines()}
    frozen = json.loads((ROOT / "audit/book_list.json").read_text())
    historical = {}
    for line in (ROOT / "environment/data_checksums.txt").read_text().splitlines():
        parts = line.split(maxsplit=1)
        if len(parts)==2:
            historical[parts[1].lstrip("*")] = parts[0]
    if not args.freeze:
        manifest = json.loads(manifest_path.read_text())
        books = manifest["test_books"] + manifest["dev_books"]
        for book in books:
            path = asset_root / book["file"]
            if not path.exists():
                if args.offline:
                    raise FileNotFoundError(f"missing offline asset: {path}")
                download(f"https://storage.googleapis.com/deepmind-gutenberg/{book['file']}",path)
        print("Assets restored; verify with scripts/verify_assets.py")
        return
    test_books = []
    for book in frozen["books"]:
        rel = book["file"]
        if rel not in split_files["test"]["entries"]:
            raise ValueError(f"frozen book outside pinned test list: {rel}")
        path = asset_root / rel
        if not path.exists():
            if args.offline:
                raise FileNotFoundError(path)
            download(f"https://storage.googleapis.com/deepmind-gutenberg/{rel}", path)
        expected = next((v for k,v in historical.items() if k.endswith('/'+rel)),None)
        if expected is None or file_hash(path) != expected:
            raise ValueError(f"historical text hash mismatch/missing: {rel}")
        row = describe(tokenizer,asset_root,rel,16384)
        if row["full_token_length"] != book["token_length"]:
            raise ValueError(f"token length changed: {rel}")
        test_books.append(row)
    dev_books = []
    for rel in split_files["validation"]["entries"]:
        if not rel:
            continue
        path = asset_root / rel
        if not path.exists():
            if args.offline:
                raise FileNotFoundError(f"development text missing offline: {rel}")
            download(f"https://storage.googleapis.com/deepmind-gutenberg/{rel}",path)
        row = describe(tokenizer,asset_root,rel,8192)
        if row["full_token_length"] >= 8192:
            dev_books.append(row)
        if len(dev_books)==3:
            break
    if len(dev_books)!=3:
        raise ValueError("fewer than three eligible validation books")
    manifest = {"schema_version":2,"created_at":now(),"model":MODEL,"model_revision":REV,
                "tokenizer_revision":REV,"add_special_tokens":True,"token_hash_encoding":"int64 little-endian C order",
                "dataset_revision":DATA_REV,"asset_root_hint":"data/pg19","model_files":pins,
                "split_lists":{k:{"sha256":v["sha256"]} for k,v in split_files.items()},
                "test_selection":"unchanged audit/book_list.json", "dev_selection":"first three pinned validation entries with >=8192 tokens; no loss-based selection",
                "test_books":test_books,"dev_books":dev_books}
    write_json(manifest_path,manifest)
    write_json(ROOT/"data/dev_manifest.json",{"created_at":manifest["created_at"],"assets_manifest_sha256":file_hash(manifest_path),"selection_rule":manifest["dev_selection"],"books":dev_books})
    print(json.dumps({"manifest":str(manifest_path),"sha256":file_hash(manifest_path),"test_input_tokens":sum(b["input_tokens"] for b in test_books),"dev_ids":[b["book_id"] for b in dev_books]},indent=2))


if __name__ == "__main__":
    main()
