#!/usr/bin/env python
"""Preregister the PG19 book list BEFORE any method-performance look.

Selection rule (frozen 2026-09-05, mirrors data_manifest.md):
  first 10 books of the PG19 test split, in dataset order
  (data/test_files.txt from the official HF repo revision), whose tokenized
  length >= 4096 tokens under the pinned tokenizer; ties broken by file order.

Outputs:
  audit/book_list.json  — book ids, titles (from metadata.csv), token lengths
  stdout                — the same, for the experiment log
This script only tokenizes (no model, no GPU) and never computes NLL.
"""

import csv
import json
import os
import sys

from transformers import AutoTokenizer

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL = "EleutherAI/pythia-2.8b"
REVISION = "2a259cdd96a4beb1cdf467512e3904197345f6a9"
TEST_LIST = os.path.expanduser(
    "~/.cache/huggingface/hub/datasets--deepmind--pg19/snapshots/"
    "4d28bd77e66947ad3835cf78ed7aaeb4dd87ad8b/data/test_files.txt"
)
PG19_DIR = os.path.join(REPO_ROOT, "data", "pg19")
MIN_TOKENS = 4096
N_BOOKS = 10


def main():
    tokenizer = AutoTokenizer.from_pretrained(MODEL, revision=REVISION)
    titles = {}
    with open(os.path.join(PG19_DIR, "metadata.csv"), encoding="utf-8") as f:
        for row in csv.reader(f):  # headerless: book_id,title,year,url
            if len(row) >= 2:
                titles[row[0]] = row[1].strip()

    with open(TEST_LIST) as f:
        files = [line.strip() for line in f if line.strip()]

    selected = []
    for rel in files:
        path = os.path.join(PG19_DIR, rel)
        if not os.path.exists(path):
            sys.exit(f"missing local copy of {rel} — download data first")
        with open(path, encoding="utf-8") as f:
            n_tok = len(tokenizer(f.read())["input_ids"])
        book_id = os.path.splitext(os.path.basename(rel))[0]
        print(f"{rel}  tokens={n_tok}")
        if n_tok >= MIN_TOKENS:
            selected.append(
                {"file": rel, "book_id": book_id,
                 "title": titles.get(book_id, "?"), "token_length": n_tok}
            )
        if len(selected) == N_BOOKS:
            break

    if len(selected) < N_BOOKS:
        sys.exit(f"only {len(selected)} books >= {MIN_TOKENS} tokens available")

    out = {
        "selection_rule": f"first {N_BOOKS} test-split books in dataset order with "
                          f"tokenized length >= {MIN_TOKENS} (pinned tokenizer)",
        "model_revision": REVISION,
        "min_tokens": MIN_TOKENS,
        "frozen_at": "2026-09-05",
        "books": selected,
    }
    with open(os.path.join(REPO_ROOT, "audit", "book_list.json"), "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nFroze {len(selected)} books -> audit/book_list.json")


if __name__ == "__main__":
    main()
