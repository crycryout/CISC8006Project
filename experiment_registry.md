# Experiment Registry

One row per consequential run. Template: `templates/experiment-registry.md`. Never overwrite a run directory.

| Run ID | Date | Git commit | Config | Command | Hardware | Result path | Status | Purpose | Conclusion |
|--------|------|-----------|--------|---------|----------|-------------|--------|---------|------------|
| R0000-setup | 2026-09-05 | (pre-first-commit) | — | manual: clone/pin official repo, venv build, model+PG19 download | stluo-gpu03, 1× H800 PCIe 80GB | `environment/`, `data_manifest.md` | done | Pin official code, environment, model, dataset for auditable reproduction | Official repo pinned @ 2e50426; transformers==4.33.0 stack viable on H800; model+data cached locally |
| R0001 | 2026-09-05 | (first commit) | `configs/smoke.yaml` | `bash scripts/run_smoke.sh` | stluo-gpu03, 1× H800 PCIe 80GB | `runs/R0001/` | *(filled on run)* | Tiny smoke: verify Pythia-2.8B + PG19 + NLL pipeline runs and measure tokens/s | *(filled on run)* |
