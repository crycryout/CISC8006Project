# Feasibility and measured limits

Scope: pinned Pythia2.8B inference only, original10 PG19 test books, retained budget1024. Full H800 GPU0 currently available; GPU1 has three existing MIG instances and is not a second full device. Root cron changes GPU0 MIG at01:30 and09:00 Asia/Macao; run_matrix checks the available window and never changes topology.

Model config has32 layers, hidden2560, heads32, head_dim80. FP16 retained KV formula is2(K,V)×32×1(batch)×32×1024×80×2 bytes=335544320 bytes (320MiB). Verify actual tensor numel×element_size per run. Forward may temporarily see1025 and concat/attention workspaces contribute extra allocation; peak GPU memory is not pure KV memory.

Verified asset preparation recovers all frozen test texts and validation books without model scoring. Clean install uses Python3.10, fixed Transformers4.33 and actual available PyTorch2.14+cu130 wheel. Setup/download errors are preserved in environment/verification; no blind upgrades or host package changes. Every-layer raw-K/attention/logit fixtures pass. Main risk is slow token-by-token decoding plus position-remap/calibration overhead; completed diagnostics update the matrix throughput estimate before approved formal execution.

Budget20 GPU-h includes failed runs and model loading. Cost estimates use actual154587 predictions per arm, not10×16384 assumed equal lengths. Launcher reserves time, evaluator has a hard limit, and failed runs preserve completed books; new IDs for retries. Freeze approvals and reviewer sign-off remain genuine prerequisites. Historical speed was not profiler evidence of a specific bottleneck; no performance optimization claim is made.
