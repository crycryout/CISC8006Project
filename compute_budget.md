# Compute contract and actual accounting

Default ceiling: **20 GPU-h**, including unsuccessful attempts and model loading. It remains active until a genuine approved budget decision is recorded in `docs/budget_decision.json`; no exception is currently active.

Actual append-only events: `experiments/registry.jsonl`; current charge and forecast: `environment/verification/budget-review.json`. Historical0.25h is a conservative reserve because old model-loading durations were unrecorded (forward lower bound0.098567h). Prior direct H800 fixtures are separately conservatively charged0.02h; new model/fixture attempts charge one selected device times whole-process wall seconds. CPU/network-only preparation and CPU smoke allocate zero GPUs. No currency cost is separately metered.

Corrected4096-token diagnostics measure24.192–24.657 predictions/s. Forecast uses actual154587 predictions per main arm, natural short book included, and60 setup seconds/job. Three-seed reproduction≈10.750h; validation baseline/H1/H2 pilots≈2.689h; one full improvement≈5.375h; two three-seed development controls≈1.793h. Required total was21.061h at first review and rises with actual verification charge; calibration and retries are additional. Historical31.7 input-tokens/s estimates do not authorize a21+h plan.

Concrete review alternatives: obtain an actual deterministic single-pass exemption for main reproduction and deterministic full improvement, retaining three-seed development pilots/controls (initial forecast10.311h); or an actually approved higher ceiling with overhead/retry margin. `_seed0_proposal.yaml` configurations remain proposals. A waiver must explicitly cover the relevant phase; random-anchor controls always have actual seeds0/1/2. No test book, primary cap, score boundary or unfavorable seed is silently removed.

At12h re-estimate all remaining required tasks; at16h add no optional work. Every job reserves a hard time limit under the actual ceiling; killed/failed attempts retain evidence, and unresolved running reservations remain charged. `run_matrix --dry-run` never starts a GPU and displays the complete jobs, reuse and cost. Estimated feasibility is reviewed again before execution.

GPU0 root cron enables MIG at01:30 and restores full mode09:00 Asia/Macao. Launcher refuses a job whose reserved limit crosses01:20. GPU1 is currently three MIG instances, not a second free full H800. No topology, driver or other users' workloads are changed.
