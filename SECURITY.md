# Artifact handling

Private SSH keys, tokens, `.env`, Moodle sessions, credentials and raw approval email bodies must not enter tracked artifacts. `.env.example` contains placeholders. Publish redacted decision references rather than private correspondence. Asset preparation downloads public pinned model and processed PG19 texts; it does not upload those assets.

The current Codex interaction shares repository code, configuration, hashes, logs and aggregate scientific outputs with the agent service. Raw book text is read locally by the tokenizer; no book text has been printed in this session's tool output. That scoped observation does not prove every historical session kept text local. External services contacted: GitHub for fetch, PyTorch/package registries for installation, Hugging Face and GCS for public assets, arXiv/official project pages for source verification. Do not copy login/session HTML into prompts or the repository.

The authorized GitHub artifact delivery includes public PG19 book IDs, capped input token IDs and per-position NLL/mask arrays in compressed NPZ files. Token IDs can reconstruct the capped public-text excerpts; their inclusion is disclosed and is not a claim that all text representations remain local. They support exact token/mask/metric reconstruction. Full raw `.txt` books and model weights are excluded. No private course HTML, credentials or restricted personal data are bundled.

`scripts/release_check.py` scans tracked files and historical diffs for credential patterns, saving only path/pattern/count, never matched secret values. A positive scan blocks release and requires verification; no destructive history rewrite or credential rotation is performed automatically.
