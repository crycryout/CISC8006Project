# Experiment registry

Machine events: `experiments/registry.jsonl`. Historical Markdown preserved in `docs/legacy_experiment_registry.md`; legacy outputs are diagnostic only. No row claims a final reproduction verdict.

| Run | Phase / seed | State | Source commit | Wall seconds / GPU-h | Artifact |
|---|---|---|---|---|---|
| D-W0-20261008 | diagnostic / 0 | completed | `77189031` | 171.079 / 0.047522 | `runs/D-W0-20261008` |
| smoke-cpu-a-20261008 | smoke / 0 | completed | `77189031` | 3.558 / 0.000000 | `runs/smoke-cpu-a-20261008` |
| smoke-cpu-b-20261008 | smoke / 0 | completed | `77189031` | 3.719 / 0.000000 | `runs/smoke-cpu-b-20261008` |
| D-S0-20261008 | diagnostic / 0 | completed | `77189031` | 170.733 / 0.047426 | `runs/D-S0-20261008` |
| D-W1-20261008 | diagnostic / 0 | completed | `77189031` | 193.477 / 0.053744 | `runs/D-W1-20261008` |
| D-S1-20261008 | diagnostic / 0 | completed | `77189031` | 197.385 / 0.054829 | `runs/D-S1-20261008` |
| scorer-legacy-20261008 | diagnostic / 0 | completed | `77189031` | 74.648 / 0.020735 | `runs/scorer-legacy-20261008` |
| recovery-failed-20261008 | diagnostic / 0 | failed | `77189031` | 75.530 / 0.020981 | `runs/recovery-failed-20261008` |
| fixtures-h800-11f7e21a9a8a | smoke / 0 | completed | `77189031` | 6.328 / 0.001758 | `runs/fixtures-h800-11f7e21a9a8a` |
| R0000-harnesscheck | legacy_smoke / None | legacy_recorded | `2c895ed8` | 96.140 / included in legacy reserve | `runs/R0000-harnesscheck` |
| R0001 | legacy_smoke / None | legacy_recorded | `fbdc9e67` | 258.700 / included in legacy reserve | `runs/R0001` |
| smoke-gpu-clean-s1-20261008 | smoke / 1 | completed | `77189031` | 75.744 / 0.021040 | `runs/smoke-gpu-clean-s1-20261008` |
| recovery-retry-20261009 | diagnostic / 0 | completed | `77189031` | 146.157 / 0.040599 | `runs/recovery-retry-20261009` |
| smoke-cpu-a29b6758c903 | smoke / 0 | completed | `6a915de5` | 4.200 / 0.000000 | `runs/smoke-cpu-a29b6758c903` |
| smoke-cpu-clean-checkout-20261009 | smoke / 0 | completed | `5e81fdea` | 5.754 / 0.000000 | `runs/smoke-cpu-clean-checkout-20261009` |

Spent/reserved charge: 0.578634 GPU-h. Budget includes historical0.25h plus0.02h conservative prior uninstrumented H800-fixture reserve. New attempts use whole-process wall-clock timing. Costs are not separately metered. Failed attempts remain visible and never enter claim inference.
