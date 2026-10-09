# Experiment registry

Machine events: `experiments/registry.jsonl`. Historical Markdown preserved in `docs/legacy_experiment_registry.md`; legacy outputs are diagnostic only. Scientific verdicts require complete paired groups in `results/`, never an individual run row.

| Run | Phase / seed | State | Source commit | Wall seconds / device-instance hours | Artifact |
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
| smoke-cpu-ca8f7f22e8f0 | smoke / 0 | completed | `4e54a2a8` | 4.125 / 0.000000 | `runs/smoke-cpu-ca8f7f22e8f0` |
| fixtures-h800-aa78139f486f | smoke / 0 | completed | `5a3c42b9` | 7.030 / 0.001953 | `runs/fixtures-h800-aa78139f486f` |
| mig-equivalence-20261009 | diagnostic / 0 | completed | `5a3c42b9` | 81.641 / 0.022678 | `runs/mig-equivalence-20261009` |
| fixtures-h800-3effa8171396 | smoke / 0 | completed | `5a3c42b9` | 6.430 / 0.001786 | `runs/fixtures-h800-3effa8171396` |
| R-v2-mig-20261009-window-s0 | reproduction / 0 | completed | `aa76de10` | 7345.786 / 2.040496 | `runs/R-v2-mig-20261009-window-s0` |
| R-v2-mig-20261009-window-s2 | reproduction / 2 | completed | `aa76de10` | 7296.856 / 2.026904 | `runs/R-v2-mig-20261009-window-s2` |
| R-v2-mig-20261009-window-s1 | reproduction / 1 | completed | `aa76de10` | 7308.628 / 2.030174 | `runs/R-v2-mig-20261009-window-s1` |
| smoke-cpu-owner-clean-20261009 | smoke / 0 | completed | `624b0229` | 6.115 / 0.000000 | `runs/smoke-cpu-owner-clean-20261009` |
| R-v2-mig-20261009-streaming-s2 | reproduction / 2 | completed | `61815385` | 7327.012 / 2.035281 | `runs/R-v2-mig-20261009-streaming-s2` |
| R-v2-mig-20261009-streaming-s1 | reproduction / 1 | completed | `61815385` | 7344.114 / 2.040032 | `runs/R-v2-mig-20261009-streaming-s1` |
| R-v2-mig-20261009-streaming-s0 | reproduction / 0 | completed | `61815385` | 7352.186 / 2.042274 | `runs/R-v2-mig-20261009-streaming-s0` |
| P-v2-mig-20261009-streaming-s2 | pilot / 2 | completed | `311cc9e1` | 1184.989 / 0.329164 | `runs/P-v2-mig-20261009-streaming-s2` |
| P-v2-mig-20261009-streaming-s0 | pilot / 0 | completed | `311cc9e1` | 1192.339 / 0.331205 | `runs/P-v2-mig-20261009-streaming-s0` |
| P-v2-mig-20261009-streaming-s1 | pilot / 1 | completed | `311cc9e1` | 1184.119 / 0.328922 | `runs/P-v2-mig-20261009-streaming-s1` |
| P-v2-mig-20261009-h1_adaptive_sink-s1 | pilot / 1 | completed | `3c3d9478` | 1211.089 / 0.336414 | `runs/P-v2-mig-20261009-h1_adaptive_sink-s1` |
| P-v2-mig-20261009-h1_adaptive_sink-s2 | pilot / 2 | completed | `3c3d9478` | 1167.769 / 0.324380 | `runs/P-v2-mig-20261009-h1_adaptive_sink-s2` |
| P-v2-mig-20261009-h1_adaptive_sink-s0 | pilot / 0 | completed | `3c3d9478` | 1191.922 / 0.331090 | `runs/P-v2-mig-20261009-h1_adaptive_sink-s0` |
| P-v2-mig-20261009-h2_sink_selection-s2 | pilot / 2 | completed | `10616458` | 1193.780 / 0.331606 | `runs/P-v2-mig-20261009-h2_sink_selection-s2` |
| P-v2-mig-20261009-h2_sink_selection-s0 | pilot / 0 | completed | `10616458` | 1200.386 / 0.333440 | `runs/P-v2-mig-20261009-h2_sink_selection-s0` |
| P-v2-mig-20261009-h2_sink_selection-s1 | pilot / 1 | completed | `10616458` | 1197.282 / 0.332578 | `runs/P-v2-mig-20261009-h2_sink_selection-s1` |
| I-h2-v2-mig-20261009-h2_sink_selection-s1 | improvement / 1 | completed | `10616458` | 7249.791 / 2.013831 | `runs/I-h2-v2-mig-20261009-h2_sink_selection-s1` |
| I-h2-v2-mig-20261009-h2_sink_selection-s0 | improvement / 0 | completed | `10616458` | 7397.372 / 2.054826 | `runs/I-h2-v2-mig-20261009-h2_sink_selection-s0` |
| I-h2-v2-mig-20261009-h2_sink_selection-s2 | improvement / 2 | completed | `10616458` | 7281.592 / 2.022664 | `runs/I-h2-v2-mig-20261009-h2_sink_selection-s2` |
| A-h2-v2-mig-20261009-h2_forced_prefix-s1 | ablation / 1 | completed | `a0d655c7` | 1205.486 / 0.334857 | `runs/A-h2-v2-mig-20261009-h2_forced_prefix-s1` |
| A-h2-v2-mig-20261009-h2_forced_prefix-s2 | ablation / 2 | completed | `a0d655c7` | 1187.704 / 0.329918 | `runs/A-h2-v2-mig-20261009-h2_forced_prefix-s2` |
| A-h2-v2-mig-20261009-h2_forced_prefix-s0 | ablation / 0 | completed | `a0d655c7` | 1197.173 / 0.332548 | `runs/A-h2-v2-mig-20261009-h2_forced_prefix-s0` |
| A-h2-v2-mig-20261009-random_anchors-s2 | ablation / 2 | completed | `52a24010` | 1188.901 / 0.330250 | `runs/A-h2-v2-mig-20261009-random_anchors-s2` |
| A-h2-v2-mig-20261009-random_anchors-s0 | ablation / 0 | completed | `52a24010` | 1198.699 / 0.332972 | `runs/A-h2-v2-mig-20261009-random_anchors-s0` |
| A-h2-v2-mig-20261009-random_anchors-s1 | ablation / 1 | completed | `52a24010` | 1192.594 / 0.331276 | `runs/A-h2-v2-mig-20261009-random_anchors-s1` |
| reference-errors-h800-553bb7d01ae1 | smoke / 17 | completed | `90b962b0` | 2.784 / 0.000773 | `runs/reference-errors-h800-553bb7d01ae1` |
| smoke-cpu-a8a821b8a6cf | smoke / 0 | completed | `81fa4dd2` | 4.321 / 0.000000 | `runs/smoke-cpu-a8a821b8a6cf` |

Spent/reserved charge: 23.882927 device-instance hours. This includes historical0.25h plus0.02h conservative prior uninstrumented H800-fixture reserve. Full-GPU and MIG instance wall-hours are not normalized full-GPU billing or currency cost. New attempts use whole-process wall-clock timing. The user authorized resources without the old20h ceiling. Failed attempts remain visible and never enter claim inference.
