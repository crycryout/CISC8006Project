# CISC8006: auditable StreamingLLM reproduction

第 3/4 步：完整主复现、两个开发集 pilot 和 H2 完整 test 已完成并从原始 NPZ 重算；两组消融正在执行。原 10 本书、实际 seed 0/1/2 的主 ΔNLL=−0.721756，书级 95% CI [−0.759084, −0.685837]，判定 `supported`。H2 按冻结开发集规则选出，但完整 test 的 ΔNLL=+0.00010773，95% CI [−0.00006435,+0.00030269]，判定 `inconclusive`，未证明改善。执行分支 `codex/h800-course-completion-20261008`；[当前状态](TASK_STATUS.md)与 `python scripts/study_status.py` 提供实际进度。

用户于 2026-10-09 明确指示“不需要审批，H800的GPU资源随便用”，已取消本次执行的审批前置与旧 20 GPU-h 上限。三个现有 H800 GPU1 MIG 2g.20gb 实例分配给 seed 0/1/2；方法按相同 UUID 配对，保留全部成本、失败和原始输出。[授权记录](docs/execution_authorization.md)是用户指令，不是教师批准或同伴签名。

已验证：59 项 CPU/H800 检查，新 checkout 的 67 个完整依赖版本、57 项 CPU 检查和 13 份公共资产哈希，原始实验无覆盖、完整模型 2×2 诊断、失败恢复与图表重建。诊断 smoke 的 window/StreamingLLM NLL=3.051129/2.223681，3070 scored；该单本值独立于正式结论。

## Install and verify

1. `bash scripts/setup_env.sh .venv-verified` 建立 Python3.10 环境，安装固定官方 CUDA13 PyTorch 与完整已验证依赖锁，再 editable install 当前 checkout。无需改驱动或系统包。原 `.venv` 保留。
2. `source .venv-verified/bin/activate`，然后 `python scripts/prepare_data.py --manifest data/assets_manifest.json` 恢复公共 pinned 资产；`python scripts/verify_assets.py --protocol configs/protocol_v2.yaml` 复验权重、tokenizer、split lists、文本和token hashes。GPU 前先准备，离线不会猜测下载成功。
3. `bash scripts/run_smoke.sh --mode cpu` 无模型/无 GPU 执行独立 fixture，产生唯一 run；重复 ID 必须失败。GPU fixture/smoke 可指定空闲设备 UUID，通过 `CUDA_VISIBLE_DEVICES=<UUID> python scripts/run_tests.py` 登记真实费用；已占用实例不要重复分配。
4. `python scripts/run_matrix.py --matrix configs/reproduction_matrix.yaml --dry-run` 列出完整 6 jobs、估算、复用状态和路径。`--execute` 在现有用户授权下执行；完整复现→pilot→冻结选择→full→controls 由 `scripts/complete_study.py` 顺序监督。当前监督器已运行，不应另启相同 study/ID。单 seed 提案未启用，全部真实 seed 保留。
5. 完成后依次运行 `python scripts/validate_runs.py`、`python scripts/build_results.py`、`python scripts/audit_scientific_results.py`、`python scripts/build_deliverables.py`。`bash scripts/release_check.sh --technical` 验证科学/工程交付；默认检查另列真实人类活动，缺失时退出 2。`--candidate` 只生成审核快照。

`HF_HOME` 可迁移模型缓存。书籍 root 可用 `--asset-root` 恢复/复验；运行自定义位置时还需让 `--book-files` 指向实际冻结文本。所有hash相对资产内容，禁止重新选择更好的test书。可读数据入口：[data/README.md](data/README.md)。

## Evidence and actual scope

| Entry | Purpose |
|---|---|
| `experiments/registry.jsonl`, `experiment_registry.md` | 追加状态、实际source/config/data/seed/选中GPU/耗时/失败；旧实验为legacy |
| `runs/<unique-id>/` | 注册、metadata、逐书metrics和NPZ、stdout/stderr、hash清单；禁止覆盖，失败retry用新ID |
| `results/diagnostics/`, `figures/diagnostic_*` | 当前已测2×2与scorer对照；单本结果不作正式CI判定 |
| `results/final_input_manifest.json`, `results/build_provenance.json`, `results/raw_artifact_index.csv` | 精确输入、命令、参数、原始输出与表图哈希；缺少科学 run 明确 pending |
| `report/`, `presentation/`, `audit/peer_audit/` | 执行期间生成 draft；完成后生成 report.pdf 与 defense.pptx，以及实际 demo、同伴审计材料 |

Primary统计是书级等权seed配对NLL差；micro pooled PPL为secondary。输入 cap16384，短书12204保留7141，scored start1025，每组144337 scored。预算是eviction后1024，forward可见1025。实际3个模型seed不等于bootstrap seed，也不把10本变成30个独立样本。

当前资源上限明确为 unlimited，仍记录失败、加载和注册运行区间的 device-instance wall-hours，起止边界见[compute budget](compute_budget.md)，不能当作归一化整卡账单。MIG smoke 实测 22.255 predictions/s；矩阵用保守 15 predictions/s 做规划。GPU0 的其它项目与 nightly cron 保持原样，GPU1 的三个现有实例不受该 cron 影响。完整 H800 与 MIG 的 FP16 诊断并非 bitwise 相同，正式配对只使用共同 MIG 硬件类。

Pinned官方 raw-K pos-shift 是faithful baseline修复，不是原创improvement。三个候选、两pilot和一个完整改进按[方案](docs/improvement_hypotheses.md)准备；没有编造结果。论文位置机制、Fig3/Fig5和独立书reset的差异见[paper comparison](docs/paper_comparison.md)。AI、人类角色、许可证和数据来源见 `AI_USAGE.md`、`CONTRIBUTIONS.md`、`LICENSES.md`、`SECURITY.md`。
