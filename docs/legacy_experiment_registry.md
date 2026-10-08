# Experiment Registry

One row per consequential run. Template: `templates/experiment-registry.md`. Never overwrite a run directory.

| Run ID | Date | Git commit | Config | Command | Hardware | Result path | Status | Purpose | Conclusion |
|--------|------|-----------|--------|---------|----------|-------------|--------|---------|------------|
| R0000-setup | 2026-09-05 | (pre-first-commit) | — | manual: clone/pin official repo, venv build, model+PG19 download | stluo-gpu03, 1× H800 PCIe 80GB | `environment/`, `data_manifest.md` | done | Pin official code, environment, model, dataset for auditable reproduction | Official repo pinned @ 2e50426; transformers==4.33.0 stack viable on H800; model+data cached locally |
| R0000-harnesscheck | 2026-09-05 | `2c895ed` | (CLI flags in `runs/R0000-harnesscheck/*/config_used.json`) | `scripts/eval_ppl.py` ×2 arms, pythia-160m, book 10146, 4096 tokens | stluo-gpu03, 1× H800 PCIe 80GB | `runs/R0000-harnesscheck/` | done | Validate harness end-to-end on the small model before touching the claim model | Both arms ran (85 tok/s @160m); window NLL 5.583 vs streaming 5.499 on scored region — sink benefit directionally observable already; NOT a claim-scale result |
| R0001 | 2026-09-05 | `fbdc9e6` | `configs/smoke.yaml` | `bash scripts/run_smoke.sh` | stluo-gpu03, 1× H800 PCIe 80GB | `runs/R0001/` | done | Tiny smoke: verify Pythia-2.8B + PG19 + NLL pipeline runs and measure tokens/s | Pipeline runs at 32 tok/s (window) / 31 tok/s (streaming), 6.9 GB peak; window NLL 5.451 vs streaming 5.292 on book 10146 — sink gap directionally present at claim scale; 10-book × 16k protocol ⇒ ≈2.9 GPU-h/pass, inside ceiling |
