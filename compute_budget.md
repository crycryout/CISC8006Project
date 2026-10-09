# Current resource authorization

On2026-10-09 the user explicitly instructed: “不需要审批，H800的GPU资源随便用”. The20 GPU-h cap and procedural approvals are superseded for this execution. `docs/execution_authorization.md` records the real instruction; it is not a fabricated teacher approval. Complete actual seeds0/1/2 and all failures/costs remain recorded. `approved_ceiling_gpu_hours: null` means explicitly unlimited, not an unknown or implicit waiver.

Three existing idle H800 2g.20gb MIG instances run independent seed workers. Both methods for a seed run on the same instance. NVML records actual30 SMs, memory, UUID/parent, driver and clock/power snapshots. Device-instance wall-hours are conservative usage accounting, not normalized full-GPU billing. A full-GPU/MIG smoke comparison is not bitwise identical and is recorded; all formal comparisons use the common MIG hardware class. No other project is stopped, topology/cron is unchanged.

The full-GPU historical forecast was21.186h. New matrices use a conservative15predictions/s planning rate versus the measured22.255 solo MIG rate, reserve a per-job hard timeout and execute3 devices in parallel. The new total and wall-time forecast will be recalibrated from actual first-book progress. GPU1 instances are unaffected by GPU0's nightly MIG cron.

Historical policy (preserved below; superseded only by the explicit instruction above):

# Compute contract and actual accounting

Default ceiling: **20 GPU-h**, including unsuccessful attempts and model loading. It remains active until a genuine approved budget decision is recorded in `docs/budget_decision.json`; no exception is currently active.

Actual append-only events: `experiments/registry.jsonl`; current charge and forecast: `environment/verification/budget-review.json`. Historical0.25h is a conservative reserve because old model-loading durations were unrecorded (forward lower bound0.098567h). Prior direct H800 fixtures are separately conservatively charged0.02h; new model/fixture attempts charge one selected device times whole-process wall seconds. CPU/network-only preparation and CPU smoke allocate zero GPUs. No currency cost is separately metered.

Corrected4096-token diagnostics measure24.192–24.657 predictions/s. Forecast uses actual154587 predictions per main arm, natural short book included, and60 setup seconds/job. Three-seed reproduction≈10.750h; validation baseline/H1/H2 pilots≈2.689h; one full improvement≈5.375h; two three-seed development controls≈1.793h. Required total was21.061h at first review and rises with actual verification charge; calibration and retries are additional. Historical31.7 input-tokens/s estimates do not authorize a21+h plan.

Concrete review alternatives: obtain an actual deterministic single-pass exemption for main reproduction and deterministic full improvement, retaining three-seed development pilots/controls (initial forecast10.311h); or an actually approved higher ceiling with overhead/retry margin. `_seed0_proposal.yaml` configurations remain proposals. A waiver must explicitly cover the relevant phase; random-anchor controls always have actual seeds0/1/2. No test book, primary cap, score boundary or unfavorable seed is silently removed.

At12h re-estimate all remaining required tasks; at16h add no optional work. Every job reserves a hard time limit under the actual ceiling; killed/failed attempts retain evidence, and unresolved running reservations remain charged. `run_matrix --dry-run` never starts a GPU and displays the complete jobs, reuse and cost. Estimated feasibility is reviewed again before execution.

GPU0 root cron enables MIG at01:30 and restores full mode09:00 Asia/Macao. Launcher refuses a job whose reserved limit crosses01:20. GPU1 is currently three MIG instances, not a second free full H800. No topology, driver or other users' workloads are changed.
