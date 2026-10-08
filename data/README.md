# Recovering evaluation assets

`assets_manifest.json` is the portable hash contract; `dev_manifest.json` fixes the first three eligible validation books. Original test selection is preserved in `audit/book_list.json`.

1. Run `bash scripts/setup_env.sh .venv-verified`, then use `.venv-verified/bin/python` below.
2. Run `python scripts/prepare_data.py --manifest data/assets_manifest.json --asset-root data/pg19` to restore pinned assets online.
3. Run `python scripts/verify_assets.py --manifest data/assets_manifest.json --asset-root data/pg19` before offline evaluation.

Model/tokenizer are from the pinned Hugging Face revision. Split lists are pinned separately to the recorded PG19 revision. Raw text comes from `https://storage.googleapis.com/deepmind-gutenberg/<split>/<id>.txt` and must match the committed hash. Files are not bundled in Git. Set `HF_HOME` to move the model cache; set `--asset-root` to move book storage. Hashes are relative to that root.

The first manifest was generated without NLL evaluation. `--freeze` refuses to overwrite it. Never rerun selection to replace a bad-performing test book. Book 10146 was previously exposed in smoke and remains in the test set; this limits claims of untouched test data.
