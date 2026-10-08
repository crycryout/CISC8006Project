# CISC8006: auditable StreamingLLM reproduction

当前为技术审核候选包，**尚未完成正式复现、改进评测或最终课程 freeze**。状态入口：[TASK_STATUS.md](TASK_STATUS.md)；必须的人类决定：[review_packet.md](docs/review_packet.md)。执行分支 `codex/h800-course-completion-20261008`，原有实验保持原样。

已验证：原10本书、独立 RoPE/attention/K/V/logit fixtures、完整模型2×2诊断、失败保留、逐位置无损输出和重建脚本。修正版单本 smoke 的 window/StreamingLLM NLL=3.051129/2.223681，3070 scored；不是10本书结论。科学门槛和真实审批由发布检查区分。

## Install and verify

1. `bash scripts/setup_env.sh .venv-verified` 建立 Python3.10 环境，安装固定官方 CUDA13 PyTorch 与完整已验证依赖锁，再 editable install 当前 checkout。无需改驱动或系统包。原 `.venv` 保留。
2. `source .venv-verified/bin/activate`，然后 `python scripts/prepare_data.py --manifest data/assets_manifest.json` 恢复公共 pinned 资产；`python scripts/verify_assets.py --protocol configs/protocol_v2.yaml` 复验权重、tokenizer、split lists、文本和token hashes。GPU 前先准备，离线不会猜测下载成功。
3. `bash scripts/run_smoke.sh --mode cpu` 无模型/无GPU执行独立fixture并产生唯一run。重复ID必须失败。`CUDA_VISIBLE_DEVICES=0 python scripts/run_tests.py` 为完整H800 fixture计时登记；`CUDA_VISIBLE_DEVICES=0 bash scripts/run_smoke.sh --mode gpu` 执行已准备模型smoke，全部占用/失败计入预算。
4. `python scripts/run_matrix.py --matrix configs/reproduction_matrix.yaml --dry-run` 列出完整6 jobs、预算、复用状态和路径，绝不启动GPU。正式 `--execute` 需要真实审批、完整前置证据和可行预算；H1/H2、full和controls有各自矩阵。单遍文件以 `_seed0_proposal.yaml` 命名，只有真实教师豁免才有效。不要直接修改JSON把待审伪装为批准。
5. `python scripts/validate_runs.py --registry experiments/registry.jsonl`；`python scripts/build_results.py --manifest results/final_input_manifest.json`；`python scripts/build_deliverables.py`。最终 `bash scripts/release_check.sh` 在科学/人类证据未完成时退出2；`--candidate` 仅生成明确标记的审核快照。正式通过后才由真实成员 freeze/tag/提交。

`HF_HOME` 可迁移模型缓存。书籍 root 可用 `--asset-root` 恢复/复验；运行自定义位置时还需让 `--book-files` 指向实际冻结文本。所有hash相对资产内容，禁止重新选择更好的test书。可读数据入口：[data/README.md](data/README.md)。

## Evidence and actual scope

| Entry | Purpose |
|---|---|
| `experiments/registry.jsonl`, `experiment_registry.md` | 追加状态、实际source/config/data/seed/选中GPU/耗时/失败；旧实验为legacy |
| `runs/<unique-id>/` | 注册、metadata、逐书metrics和NPZ、stdout/stderr、hash清单；禁止覆盖，失败retry用新ID |
| `results/diagnostics/`, `figures/diagnostic_*` | 当前已测2×2与scorer对照；单本结果不作正式CI判定 |
| `results/final_input_manifest.json`, `results/build_provenance.json` | exact输入、重建命令、参数与artifact hashes；缺少科学run明确pending |
| `report/report_draft.pdf`, `presentation/defense_draft.pptx`, `audit/peer_audit/` | 可审阅报告/deck/demo/独立审计材料；人类审核与个人答辩不由Agent代签 |

Primary统计是书级等权seed配对NLL差；micro pooled PPL为secondary。输入 cap16384，短书12204保留7141，scored start1025，每组144337 scored。预算是eviction后1024，forward可见1025。实际3个模型seed不等于bootstrap seed，也不把10本变成30个独立样本。

仓库的20 GPU-h默认上限继续生效。实测修正路径约24.192 predictions/s，原完整任务估算至少21.06h且还没计 calibration/retry，必须先获得可行的真实预算/豁免决定。GPU0每晚01:30改MIG、09:00恢复；launcher拒绝越过01:20的jobs。GPU1现有MIG不调整。

Pinned官方 raw-K pos-shift 是faithful baseline修复，不是原创improvement。三个候选、两pilot和一个完整改进按[方案](docs/improvement_hypotheses.md)准备；没有编造结果。论文位置机制、Fig3/Fig5和独立书reset的差异见[paper comparison](docs/paper_comparison.md)。AI、人类角色、许可证和数据来源见 `AI_USAGE.md`、`CONTRIBUTIONS.md`、`LICENSES.md`、`SECURITY.md`。
