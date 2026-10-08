# CISC8006 课程合规审计与 H800 完成计划

**结论：选题适合课程，现有仓库是有价值的初步实现，但还不能作为完成版提交。先修复评测忠实性与可复现性，再完成正式复现，以及「3 个改进假设 → 2 个 pilot → 1 个完整评测」，最后打包报告、幻灯片、证据与个人答辩。无需重选论文。**

本文面向在 H800 服务器上接手的 Codex。它既是审计报告，也是按依赖顺序执行的任务书；不是已经完成实验的证明，也不代表教师批准了协议变更。

| 审计项目 | 内容 |
|---|---|
| 审计日期 | 2026-10-08，Asia/Shanghai |
| 仓库 | https://github.com/crycryout/CISC8006Project |
| 审计基线 | `main`，`a3ffaf0f514c9e79b7d3395dfc768f469a6df80a` |
| 课程来源 | 用户提供的 Student Guide 与 Full Specification 两份 UMMoodle HTML，正文版本 2026-09-02 |
| 审计方法 | 阅读仓库目录、核心源码、配置、环境记录、已有实验输出、提交历史；核对论文与固定版本 Transformers 源码；执行小型 CPU 反例检查 |
| 本次未做 | 未连接用户 H800；未重跑模型；未证明依赖能在新机器安装；未验证历史人类审核或教师批准的真实性 |
| 本次交付范围 | 新增本任务书；代码修复与模型实验由服务器上的 Codex 后续执行 |
| 时间解释 | 不按旧日历或中间 checkpoint 判定逾期，只按最终交付内容规划依赖；准确的最终截止时间未包含在当前可确认信息中，不臆造 |

**开始前的注意事项：**课程材料本身保留共同 artifact freeze 和审批要求。本文遵循用户要求，不做日期扣分审计；这不等于代表教师取消这些规定。应把最新 UMMoodle 公告中的最终实验/写作冻结时间记为 `T_final`，所有科学输出在它之前完成。Full Specification §11 将部分细则标为待最终发布确认；报告模板、页数、数值资源上限、展示时长等以最新公告为准。以下将已明确的科学要求与保守的交付建议分开说明。

## 阅读导航

1. [审计结论与课程逐项映射](#1-审计结论与课程逐项映射)
2. [必须优先修复的问题](#2-必须优先修复的问题)
3. [冻结后的评测协议](#3-冻结后的评测协议)
4. [按依赖执行的工作包](#4-按依赖执行的工作包)
5. [改进假设与实验设计](#5-改进假设与实验设计)

后续部分：[预算与完成顺序](#6-预算与完成顺序)、[最终交付与答辩](#7-最终交付与答辩)、[验收清单](#8-验收清单)、[直接交给-codex-的启动指令](#9-直接交给-codex-的启动指令)、[来源与审计边界](#10-来源与审计边界)。

## 1. 审计结论与课程逐项映射

### 1.1 当前已经具备什么

| 已有基础 | 仓库证据 | 可以保留的价值 |
|---|---|---|
| 清楚的单一研究命题 | `claim.md`、`claim_map.md` | Pythia-2.8B、PG19、1024 KV 位置预算、StreamingLLM 对 window 的 post-overflow NLL 比较，范围可控 |
| 固定模型与书目 | `data_manifest.md`、`audit/book_list.json`、`configs/{window,streaming}.yaml` | 已记录模型 revision、10 本书及数据哈希；不用重新挑「效果好的书」 |
| 可审阅的评测循环 | `scripts/eval_ppl.py` | teacher forcing、每步 eviction、每本书输出；关键机制很容易定位 |
| 独立缓存保留规则检查 | `audit/cache_index_test.py` | Python oracle 对照官方切片逻辑，是有效的独立工作基础；但覆盖范围不足 |
| 历史 smoke 与开发记录 | `runs/R0000-harnesscheck/`、`runs/R0001/`、registry、ledger、提交历史 | 证明仓库已积累初步运行证据；应原样保留并明确局限 |

`R0001` 已提交的结果：同一本书 `10146`，每组 4096 输入 token，3070 scored token，window NLL=5.450579，streaming NLL=5.292441，差值约 −0.158138 nats/token。它只是单本书、旧位置编码实现下的 smoke，不是正式复现判定。

### 1.2 最终要求对照表

状态定义：**已有基础**=可以继续用但需补证；**待完成**=仓库中没有足够最终证据；**必须修复**=现有逻辑会阻碍结果有效性或独立复现。不能将「仓库中未见」解释为线下从未完成。

| 课程项 | 分值 | 当前判断 | 最终应提供的证据 |
|---|---:|---|---|
| A. Scope 与 claim 理解 | 5 | 已有基础；批准状态与 paper figure 指向需核对 | 单一 claim、复现层级、论文结果定位、差异表、真实审批记录、fallback |
| B. Protocol 与评测设计 | 10 | 必须修复；RoPE、聚合口径、随机性方案未闭环 | 固定协议、配对验证、已知答案 fixture、随机性/不确定性方案、预算 |
| C. Pilot 与现场审计 | 10 | 有历史 smoke；新 clone 不能直接执行现有 smoke 命令 | 干净环境安装、唯一 run ID、小型真实模型检查、正确性测试、审计说明 |
| D. 正式复现与差异诊断 | 20 | 待完成；未见 10 本书正式结果及 CI | 完整结果、书级配对区间、论文直接比较、诊断、三态结论 |
| E. 改进实验与消融 | 20 | 待完成；`improvement.yaml` 只有占位 | 3 个机制假设、2 个经批准 pilot、1 个完整评测、控制/消融/失败案例 |
| F. Artifact、报告、Agent 来源 | 15 | 部分文档已有；结果重建与最终报告缺失 | 可运行 release、结果证据链、报告、AI ledger、许可证与来源 |
| G. 展示与演示 | 5 | 待完成 | 最终 deck、演示脚本、录制 fallback、全员分工与排练 |
| H. 个人技术答辩 | 10 | 不能从仓库判定 | 每人能够解释方法、代码、指标、Agent 决策与限制 |
| I. 个人贡献 | 5 | 待补仓库证据 | `CONTRIBUTIONS.md`、真实角色/提交/实验/审核记录、按课程要求的同伴反馈 |

**不估算当前分数，不承诺最终分数。**当前最大缺口是正式复现与改进两个各 20 分的证据模块，以及科学正确性的前置问题。无需追求正向改进、百万 token、更多模型或者训练新模型才能达成课程目标。

### 1.3 必须完成的最小科学闭环

1. 建立与论文机制一致、独立测过的 StreamingLLM 基线。
2. 用冻结的 10 本书完成有不确定性分析的主比较。
3. 基于诊断提出三个假设并对两个做可审计 pilot。
4. 对一个选定改进完成公平对照、消融、失败分析。
5. 把全部结论关联到可取回的实验输出，并完成报告、演示和个人答辩准备。

## 2. 必须优先修复的问题

### P0-01：主方法缺少真正的缓存位置重映射

**位置：**`scripts/eval_ppl.py` 中模型加载及 forward/eviction 循环；`claim_map.md` 的 A4；`environment/third_party.md` 将 pos-shift 列为 secondary 的表述。

**已确认事实：**harness 只调用 `StartRecentKVCache`，没有调用仓库已有的 `enable_gpt_neox_pos_shift_attention`。固定版本 Transformers 4.33.0 的默认 GPT-NeoX attention 把旋转后的 K 存入 cache；新 token 的默认 position ID 来自 `past_length`。填满并滚动后，缓存长度不变，新 token 会反复使用相同 position ID，旧 K 的旋转位置也没有按缓存顺序重新整理。两组当前 token 的 ID 相同，不足以证明整个 Q/K 的相对位置正确。

论文 §3.2 的关键机制是以缓存内的连续位置计算位置编码，而不只是保留开头 token。当前实现因此不能直接声称是完整忠实的 StreamingLLM。此判断依据论文、固定版本源码与本仓库调用链；性能影响大小仍需 H800 诊断实验确认。

**修改动作：**

1. 在 `src/position_policy.py` 或等价模块显式区分 `legacy_implicit` 与 `cache_relative` 两种位置策略。
2. 为 GPT-NeoX 的 `cache_relative` 路径接入并审阅固定版本官方 pos-shift patch，检查修改覆盖每个 attention 层。
3. 增加 raw-K、重映射位置、attention output 与 logits 的独立验证。
4. 把旧 R0000/R0001 标为 legacy diagnostic，不修改其 JSON，不把修复后的结果写回旧目录。
5. 通过小型 2×2 诊断确认方法与位置策略的作用，然后由团队完成协议变更审阅及必要的教师确认。

**最小 2×2 诊断矩阵：**

| ID | 保留策略 | 位置策略 | 用途 |
|---|---|---|---|
| D-W0 | 0+1024 | legacy implicit | 重现旧 window 行为 |
| D-S0 | 4+1020 | legacy implicit | 重现旧 streaming 行为 |
| D-W1 | 0+1024 | cache-relative | 修复位置语义后的受控 baseline |
| D-S1 | 4+1020 | cache-relative | 忠实 StreamingLLM 候选 |

推荐主比较 D-S1 对 D-W1：两者只改变保留哪些 KV，位置机制一致。必须核对论文对应 baseline 的位置处理；若论文原比较另有配置，把该差异列入 scaled-faithful deviation，必要时保留 D-S1 对论文原 baseline 的次要比较。**不要只修 streaming 而保留损坏 window 来夸大差距。不要把恢复论文已有 pos-shift 算作自己的 improvement。**

验收：溢出前两种位置实现的输出在预设容差内一致；溢出后独立参考支持 D-W1/D-S1 的 Q/K 相对位置；固定预算、窗口成员与 scored region 全部可断言；正常与异常输出均有新 run ID。

### P0-02：配置文件中的 model/revision/precision 会被默认值忽略

**位置：**`scripts/eval_ppl.py::parse_args`，审计基线约 50–81 行。

`argparse` 给 `model`、`model_revision`、`precision` 先设置非空默认值，后续 YAML 合并只写入当前值为 `None` 的字段。结果是 YAML 的这些值不会生效。当前 fp16/Pythia 配置碰巧与默认值相同，掩盖了问题；后续 bf16、fixture 模型或敏感性实验可能用错配置。

本次隔离原函数、用配置 stub 执行的反例：配置提供 `model=CONFIG_MODEL`、`model_revision=CONFIG_REV`、`precision=bf16`，解析输出仍为 Pythia-2.8B、旧 revision、fp16。此检查未加载模型。

**修改：**采用「程序默认值 → YAML → 用户明确提供的 CLI」三级合并；用 `None` 或 `argparse.SUPPRESS` 区分未提供参数；合并后集中验证类型、枚举、未知键、范围与互相依赖关系。YAML 当前还可绕过 CLI choices，必须一起修复。

验收 fixture：只用 YAML、只用 CLI、两者冲突、错误 precision、拼错 key、空书目、重复书目、负 token 数、错误 budget、未知 position policy 全覆盖；无效配置必须在模型加载前失败。保存最终生效配置与 SHA256。

### P0-03：配对分析会用不完整交集给出「复现成功」

**位置：**`scripts/analyze_paired.py::main`，约 36–53 行。

当前书目不一致仅输出 WARNING，随后取交集；没有校验模型 revision、tokenizer、数据哈希、scored token 数、位置策略、precision、预算或注册协议。相同 `book_id` 重复出现也会被字典静默覆盖。

本次真实执行原分析脚本的 CPU 反例：window 包含 A/B 两本，streaming 仅有 A，一对数据差值 −1。脚本退出码为 0，并输出 `RECOVERED` 与零宽 CI `[-1,-1]`。这不是可接受的最终证据。

**修改：**分析前执行 fail-closed 的配对合同验证。两组必须覆盖注册 manifest 的完整集合，每本 token hash、实际长度、scoring mask 一致；只允许预声明的 method/sink policy 字段不同。不同 source commit 可以在已记录、已验证等价的分析授权下比较，但不能静默放行。对缺书、重复书、空结果、NaN、Infinity、未完成 run 一律报错。

分开保存 `validation_status` 与 `claim_status`：无效实验不是科学上的 not supported，也不应伪装成合法 inconclusive。有效协议内使用 `supported / not_supported / inconclusive`；正文显示课程对应拼写。单本 smoke 不产生最终 claim status。

验收：上述反例必须非零退出；两组完整且有效时才输出 CI；正差值、负差值、恰好触零、跨零都检查。不得通过放宽验证来让历史错误结果进入主表。

### P0-04：当前 smoke 命令在新 clone 上失败，且允许覆盖旧证据

**位置：**`scripts/run_smoke.sh`、`scripts/eval_ppl.py`。

仓库已经跟踪 `runs/R0001/`，而 smoke 固定 `RUN_ID=R0001`，默认看到目录就退出。`ALLOW_RESMOKE=1` 又允许往旧目录覆盖结果，和仓库自己的 immutable-run 原则冲突。README 还假定 `.venv` 与所有外部数据已经存在。

**修改：**

1. 将 smoke run ID 改为用户参数或自动唯一值，并禁止覆盖已完成/已存在的 run。
2. 分开 offline CPU fixture smoke 与 prepared-environment GPU smoke。
3. 让 evaluator 本身使用独占输出目录/原子写入，不依赖外层 shell 才保护结果。
4. 增加完整 setup 与数据准备说明；离线参数只在资产已验证存在后使用。
5. 用干净 checkout 实测两次连续 smoke 均成功，并产出两个不同 run ID。

应支持无外网、无模型的 CPU 审计路径；GPU smoke 需要在 README 明确先执行 prepare。CPU fixture 成功不能替代真实模型 smoke 成功。

### P0-05：主统计量与结果汇总口径不一致

**位置：**`claim.md`、`protocol.md`、`scripts/eval_ppl.py` 的总 mean、`scripts/analyze_paired.py` 的 paired mean。

协议使用「每本平均 NLL → 各书等权平均差值」，而 evaluator 顶层 `mean_nll` 使用 scored token 加权。10 本书中 `12204` 仅 7141 token，其 scored count 为 6115；其他 9 本每本 15358。书长不等，所以这两个统计量不是同一个量。

**推荐修复：**保留原协议已有的书级等权 primary estimand，命名为 `macro_book_nll`、`paired_macro_delta_nll`。另行报告 `micro_token_nll`、`micro_token_ppl`。不得用 micro 的 PPL 配上 macro 的差值 CI 却不说明。

完整长度核算（基于当前 manifest，服务器必须重验 token hash/长度）：

| 项目 | 数值 |
|---|---:|
| 每组实际输入 token 总数 | `9×16384+7141 = 154597` |
| 每组 next-token prediction 总数 | `154597−10 = 154587` |
| 每组 scored token 总数 | `9×15358+6115 = 144337` |
| 两组 scored token 总数 | `288674` |
| 4096-token smoke 的 scored token 数 | `4095−1025 = 3070` |

不要为凑齐 16384 token 删除短书、重复其内容、跨书填充或改选长书。`configs/smoke.yaml` 注释写 3071，应修正文档注释；真实结果中的 3070 与现有索引定义一致。

### P0-06：测试不足以证明 metric 和真实模型 cache 正确

`audit/cache_index_test.py` 的 retention oracle 是有用工作，但「position-id consistency」检查只是两次调用相同辅助函数；它没有检查真实模型的旋转 K、QK logits 或实际 position IDs。该测试制造两层 K/V，却只读第一层 K 的 tag，不能证明所有层和 V 都正确。

增加独立测试：已知概率的 NLL；不等书长的 macro/micro；错一位的 scoring mask；实际 tiny GPT-NeoX 的位置与 cache；每层 K/V 长度及成员；跨书 cache reset；两组前溢出一致性；输出完整性。详见工作包 WP2。

### P0-07：正式复现、改进和最终包尚无证据

截至审计 commit，registry 只有 setup、harnesscheck、R0001；`report/`、`defense/`、`tables/` 为占位；未见改进结果、完整结果表或最终报告。`configs/improvement.yaml` 只有方法名占位，不等于提出了合格假设。

后续重点应是按本文完成科学闭环。不要只补 README 的完成勾选、增加无来源图或把 smoke 文本改成正式结论。

### P1：结果可追溯与交付问题

| ID | 具体问题 | 修改与验收 |
|---|---|---|
| P1-01 | `position_nll.json` 被 gitignore；已有 PNG 没有对应绘图脚本 | 为正式 run 保存压缩 NLL 数组或足以完全重建图表的统计；外置文件记录 URI、hash、恢复步骤；增加绘图入口 |
| P1-02 | registry 缺少 seed、data_version、runtime、cost 等显式字段 | 建结构化 registry，由程序登记 planned/running/completed/failed；Markdown 可从它生成 |
| P1-03 | metadata 只列所有 GPU，没有 selected GPU/退出码/失败状态；commit 在 evaluator 结束时获取 | 启动前锁定 source commit、dirty diff hash、GPU UUID、命令；记录 status、exit code、timing、错误路径 |
| P1-04 | run 全部结束才写结果，中断损失整批书 | 逐书原子落盘；失败 run 原样保留；retry 用新 ID 并引用 parent；不混合不同协议片段 |
| P1-05 | `.gitignore` 未排除 `.env` 等敏感本地文件 | 增加规则、`.env.example` 与 release 前 secret scan；不要提交 Moodle 登录页面及私人审批邮件全文 |
| P1-06 | `AI_USAGE.md`、`CONTRIBUTIONS.md` 不存在，ledger 缺具体审核人、代表性片段 | 保留原 ledger，新增课程标准入口或索引；补真实人物/证据，不追填虚构批准 |
| P1-07 | `agent_policy.md` 错称必须有一次拒绝 AI 的记录 | 课程要求有实质 critical review，可接受/修改/拒绝/升级；纠正文案，不能表演或伪造拒绝 |
| P1-08 | 多处引用 `SKILL §...`，仓库中未见该 SKILL | 用具体仓库路径和内容替代不可访问引用；不能要求审阅者依赖作者机器上的私有 skill |
| P1-09 | 数据文档混用 parquet 与 raw txt，freeze 脚本依赖固定 HOME cache，日期硬编码 | 统一真实 raw `.txt` 路径；参数化 cache/data root；新 manifest 使用真实时间并保留旧版 |
| P1-10 | 官方脚本在书间延续 cache，本项目每本重置 `past=None` | 把独立书级实验列为明确 deviation；不能声称除三条小改动外完全相同 |
| P1-11 | `claim_map.md` 把 Fig.4 当 NLL 趋势图 | 重新核对版本与 figure mapping；Fig.4 是 cache 示意，短/长流结果应定位实际结果图 |
| P1-12 | seed/exemption 没有可核查实现；bootstrap seed 不等于模型运行 seed | 按 §3.5 固定重复方案，必要时记录教师认可的替代不确定性方案 |

### P2：需要纠正但不应拖延主任务的问题

环境文件中的 torch/CUDA 版本必须在服务器实际检查，不因版本看起来新就指控记录不实，也不盲目升级环境。`environment.yml` 只有空 dependencies 和注释，不能单独视为可安装锁；`pip-freeze.txt` 还需要可取得的 wheel/source、Python/driver 支持及 clean-install 验证。

`feasibility.md` 的 KV 内存估算用了不可靠的层数/维度组合和重复因子。改为读取模型 config，并用实际张量 `numel × element_size` 验证：`2 × n_layers × batch × n_kv_heads × retained_length × head_dim × dtype_bytes`。不要把总 peak GPU allocation 等同于纯 KV 内存。

保留式预算是 eviction 后最多 1024，当前 forward 会暂时看见 1025 个 KV 位置，cat 也可能产生临时分配。两组应记录相同的预算定义；不能宣称「任意时刻绝不超过 1024」。如果改成 forward 前 eviction，就改变了 scoring 与语义，需另行验证/批准。

`compute_budget.md` 中额外 3 种 sink、每种 3 本书的敏感性成本，按旧吞吐与 16k 长度约 1.3 GPU-h，并非现有含混表达所得的约 0.86；应改用 manifest 实际长度与任务矩阵计算。不要继续累加旧文档中的估算数字。

四个缓存 trace JSON 合计约 34.5 MB，expected/actual 的 blob 分别完全一致属于测试通过的正常现象，不是伪造证据的依据。后续可以保存小型可读 trace、hash、差异摘要与生成脚本，历史版本继续可查。

## 3. 冻结后的评测协议

### 3.1 不随结果改变的主合同

以下是推荐修订，不自动替代教师已批准的协议。团队应核对批准记录，保留旧版和 amendment，批准后才用于正式科学结论。

| 字段 | 推荐主合同 |
|---|---|
| 研究问题 | 固定预算和正确位置编码下，保留 4 个起始 KV 是否降低 post-overflow NLL |
| 模型 | `EleutherAI/pythia-2.8b`，revision `2a259cdd96a4beb1cdf467512e3904197345f6a9`，服务器验证资产可得 |
| tokenizer | 同 revision；明确 `add_special_tokens`、BOS/EOS 策略；保存 token IDs hash |
| 数据 | 原 10 本 PG19 test，顺序保持 manifest，不按结果删换 |
| 输入长度 | 每本 `min(original_token_length,16384)`，书间重置 cache |
| baseline | window 0+1024，已验证的 cache-relative positions |
| StreamingLLM | sink 4+recent 1020，同一位置策略 |
| forward/eviction | 单 token teacher forcing，先 forward 再 eviction；post-eviction retained budget=1024 |
| precision | 两组相同；优先延续 fp16 权重/forward；NLL 在 fp32 logits 上计算，明确这与历史 scorer 的变化 |
| 主指标 | per-book mean NLL 的等权配对差值，单位 nats/token，越小越好 |
| 次指标 | token-weighted NLL/PPL、位置分箱曲线、KV 实际字节、GPU peak、延迟 |
| 统计单位 | 独立书籍作为 bootstrap cluster；重复 seed 不把 10 本变成 30 本独立样本 |
| 总资源 | 先遵守仓库已有 20 GPU-h 上限；确认其是否教师最终资源合同，不能自行视为可超 |

这个主 claim 是方法排序，不自动包含「整个后溢出序列稳定」「达到原论文绝对 PPL」「无限长」「22.2× speedup」或下游任务质量。强结论需要额外证据，不能随手写进摘要。

### 3.2 精确的索引与边界

输入 `x[0:T]`，step `i` 输入 `x[i]`，计算目标 `x[i+1]` 的 NLL，故 `i∈[0,T−2]`。B=1024。

| step | forward 前 cache | forward 可见 KV 数 | forward 后 | 是否纳入主评分 |
|---:|---:|---:|---|---|
| 1023 | 1023 | 1024 | 不必驱逐 | 否 |
| 1024 | 1024 | 1025 | 第一次驱逐，留下 1024 | 否：本次预测还没使用已经驱逐后的 cache |
| 1025 | 1024 | 1025 | 再次驱逐 | 是：第一次使用已驱逐 cache 预测 |

因此 `first_scored_idx=1025`，对应目标 `x[1026]`，`n_scored=max(T−1026,0)`。这不是待修复的 off-by-one bug；应修注释、增加边界测试而非凭直觉改成 1024。若后来采用不同 eviction 语义，必须重新推导并使用不同 protocol ID。

### 3.3 聚合、PPL 与判定规则

令 `l[m,b,i]` 为方法 m、书 b、评分位置 i 的 NLL，`n_b` 为该书评分位置数：

```text
book_nll[m,b] = sum_i l[m,b,i] / n_b
d[b] = book_nll[streaming,b] - book_nll[window,b]
primary_delta = mean_b d[b]
macro_book_nll[m] = mean_b book_nll[m,b]
micro_token_nll[m] = sum_b(n_b * book_nll[m,b]) / sum_b n_b
micro_token_ppl[m] = exp(micro_token_nll[m])
macro_derived_ppl[m] = exp(macro_book_nll[m])
```

`macro_derived_ppl` 是各书 PPL 的几何平均对应量，不是 pooled corpus perplexity，也不是各书 PPL 的算术平均。图例、表头、正文必须写清口径。

对 10 个配对书级差值进行 10000 次有放回 bootstrap，报告 percentile 95% CI、bootstrap RNG seed、书级原始值以及样本数。书目按固定列表选取，不是随机代表全部 PG19；区间反映该书集上的变异，外推应保守。小样本/非随机选书是限制，不因 CI 排除零就能宣称普遍成立。

| 前置与区间 | 状态 |
|---|---|
| 任何协议/完整性检查失败 | `validation_status=invalid`，不输出最终科学判定 |
| 全部有效，CI 上界 <0 | `claim_status=supported` |
| 全部有效，CI 下界 >0 | `claim_status=not_supported` |
| 全部有效，CI 包含或触及 0 | `claim_status=inconclusive` |

不能不断增加 books、改 scoring range、换 seed 或改 bootstrap 算法，直到 CI 排除零。必要的探索分析单独标 exploratory，不能替换 preregistered primary。

### 3.4 测试集与开发集隔离

原书 `10146` 已用于 smoke 并看过结果，应在 contamination/limitations 中说明；不要再声称最终 10 本从未被观察。继续保留冻结集合，防止结果导向替换。可预先登记「去掉已暴露 smoke 书」作为补充敏感性分析，但主结果仍覆盖原 10 本，不能事后选其中更好的一种。

改进开发优先使用 **PG19 validation** 中按固定 split-list 顺序选出的前 3 本、token 长度至少 8192 的书，pilot 上限 8192。先核实实际 split 列表存在且数量满足，再冻结 manifest。不要使用 final test 的 NLL 选阈值、sink 数、anchor 集或最佳 seed。若 validation 可用书不足，按实际长度记账并在看方法结果前固定替代协议，不偷偷从 test 借书。

开发集没有可用授权下载路径时，先完成代码/fixture 和获取路径诊断；不要把测试集当无声明的调参集。book IDs、文本 hash、tokens hash、选择理由都进入 `data/dev_manifest.json`。

### 3.5 三个 seed 与不确定性

课程默认要求随机比较至少 3 个 seed。teacher-forced、`model.eval()`、无抽样的固定书目评测可能是确定性的；**不能把 3 个 bootstrap seed 写成 3 次模型重复，也不能把相同确定性结果当 30 个独立数据点。**

推荐执行方案：

1. 实现 `--seed`，同时设置 Python、NumPy、Torch CPU/CUDA，记录可控的 determinism、TF32、attention backend 配置。
2. 默认用 `[0,1,2]` 做主两组的重复运行，展示实际差异；如果完全一致，也如实报告。
3. 对每本书先汇总对应 seed 的成对差值，再以书作为 cluster 计算主 CI；另外给 seed 范围/均值与随机性解释。
4. 若教师已批准 deterministic evaluation 使用单遍加 paired book bootstrap，附真实批准证据并按批准方案节约算力。
5. 含随机 anchor/control 的改进必须按固定 3 seeds 执行，除非另有明确批准；不得以确定性 baseline 为由免除随机方法重复。

更复杂的两级 bootstrap 只有在设计确有独立的算法随机性、样本足够且团队能够解释时才增加，不默认扩展统计工程。

### 3.6 对照论文，而非强行复制数字

建立 `docs/paper_comparison.md`：论文版本、准确图表/段落、原实验模型/数据处理/预算、项目设置、指标定义、能比较什么、不能比较什么、项目结果 run IDs。

主 claim 应定位论文语言建模比较；cache 示意图不能冒充实验图。原文连续书流与本项目独立 reset 的区别必须醒目；模型名称/规模、长度、post-overflow-only 与全流聚合的区别都应记录。没有完全相同设置的原文数值时，不伪造 target number，不把不同模型或不同 PPL 口径的差距当 reproduction error。

对可比设置比较同单位的数值；对当前 scaled-faithful 设置明确比较排序和趋势。需要从图中提取数值时标为 digitized approximate，并保存提取方法及误差说明。不能从图形猜测小数点后多位。

## 4. 按依赖执行的工作包

每个工作包完成后更新 `TASK_STATUS.md`：状态、真实 source commit、测试、run ID、产物、剩余阻塞。不要等整个项目结束才整理。

### WP0：保护现场并确定可用证据

**依赖：**无。**预计：**0.5–1.5 人工小时，不跑 GPU。

1. 读取服务器仓库中的 `AGENTS.md`、本任务书及已有 protocol，检查工作树和当前 commit。
2. 清点服务器本地未提交的 runs、日志、模型、数据、批准记录与成员信息。
3. 将现有正式或失败实验登记为已存在证据，并通过 config/hash 判断能否复用。
4. 创建 `TASK_STATUS.md` 和 `docs/audit_resolution.md`，逐项关联 P0/P1 与修复证据。
5. 在 `docs/approval_status.md` 记录真实已批准项和未知项，未知写 `pending`。

只读命令（在已 clone 的仓库根目录执行）：

```bash
git status --short
git rev-parse HEAD
git log -8 --oneline
rg --files -g AGENTS.md -g '*protocol*' -g '*claim*' -g '*registry*' -g '*metadata*'
nvidia-smi --query-gpu=index,uuid,name,memory.total,driver_version --format=csv
```

不要 `git reset --hard`、清空 runs、删除 venv，或者为追求干净工作树覆盖用户工作。必要时创建隔离 worktree/branch。文件不在 GitHub 不等于服务器没有；先检查再补跑。

**验收：**baseline commit 与服务器最新状态的差异已理解，现有实验保留，下一步没有重复昂贵工作。人工审批只阻塞需要它的科学发布/变更，不阻塞可独立完成的代码修复、测试、文档草案。

### WP1：建立可重建环境和数据入口

**依赖：**WP0。**预计：**1–3 人工小时；下载时间独立计入，不能假设固定带宽。

**需修改/新增：**README、environment 文档/锁、`scripts/setup_env.sh`、`scripts/prepare_data.py`、`scripts/verify_assets.py`、`.env.example`。

1. 从现有可运行环境采集版本、wheel 来源、driver、GPU capability、`pip check` 和 import 检查。
2. 在新的环境中安装固定依赖，保存完整安装命令和实际成功日志。
3. 下载或验证 pinned model/tokenizer、PG19 split lists、原 10 本及开发集，生成可移植 manifest。
4. 对源文本、模型文件、token IDs 分别验证哈希，发现不同就停止对应评测并定位来源。
5. 写清 online preparation 和 offline run 两条路径，并在准备完成后才开启 offline flags。

不能把固定版本「latest upgrade」作为默认修复方式；已有 H800 工作环境优先保留。若旧 torch wheel 不可获得，记录真实安装错误，挑选可用兼容版本，做关键行为回归，然后建立新 environment ID。不能仅改 `pip-freeze.txt` 让它看起来可安装。

模型/数据 checksum 记录改为相对 asset root 或结构化文件条目，避免硬编码 `/home/...`。`freeze_book_list.py` 在 verify 模式不能重写已冻结列表或重复制造历史日期。数据准备应包含 raw `.txt` 的确切来源、重试/校验、split list 固定 revision；现有三个泛用下载/修复脚本不是完整的数据准备入口。

**验收：**从 clean checkout 创建环境并恢复原 10 本；token lengths 与 manifest 对上；缺文件/错 hash/未缓存模型有明确失败信息；README 不再从不存在的 `.venv` 直接起跑。

### WP2：修复评测并建立独立验证

**依赖：**WP1。**预计：**4–8 人工小时，tiny model 与诊断总预算先限 1 GPU-h。

推荐模块边界：

| 文件/模块 | 职责 |
|---|---|
| `src/config.py` | 配置合并、校验、resolved config、hash |
| `src/position_policy.py` | 显式 GPT-NeoX 位置策略及 patch 验证 |
| `src/cache_policy.py` | window / prefix sinks / 后续改进的 KV 保留规则 |
| `src/metrics.py` | NLL、mask、宏/微汇总，尽量与 CUDA 解耦 |
| `scripts/eval_ppl.py` | CLI 编排、逐书执行、调用上述模块；保留兼容入口 |

这是职责建议，不要求为了文件数量进行大重构。修复必须可审阅，尽量每个 commit 解决一种科学风险。

**第一组测试：CPU 即可完成。**

| 测试 | 输入/动作 | 必须满足 |
|---|---|---|
| 已知 NLL | 目标概率 0.5 和 0.25 | NLL 分别 ln2/ln4，均值约 1.03972077，PPL≈2.82842712 |
| 均匀 logits | 词表大小 V、全零 logits | NLL=ln V，PPL=V |
| 宏/微区别 | 书A：1 token,NLL=1；书B：3 tokens,NLL=3 | macro=2，micro=2.5；程序不能混淆 |
| scoring 边界 | T=1025/1026/1027/4096/7141/16384 | n_scored=0/0/1/3070/6115/15358；主分析拒绝零 scored 数据 |
| 合同与异常 | 缺书/多书/重复/NaN/错revision/错mask | 非零退出、不生成 supported |

**第二组测试：真实 attention，但可用随机小模型在 CPU/fp32 跑。**

1. 用小型 GPT-NeoX config 和小预算 B=8 或16，构造超过 3B 的序列，确保多次 eviction。
2. 用独立显式 attention/RoPE 计算参考值，对照 patch 的 raw-K 与位置重映射；不是再次调用同一 patch 当 expected。
3. 对每层 K 与 V 验证预算、保留历史 ID、顺序、无重复，以及跨书 reset 后与单独运行一致。
4. 验证未溢出时 window 与 sink arms 输出一致、patch 与未 patch 输出一致，覆盖 prefill=1 的实际路径。
5. 先在 fp32 确定容差，再在 H800 实际精度做回归；记录误差分布，不能看见失败后不断放宽阈值。

tiny 模型的预算可小于1024，只限 fixture/diagnostic config；正式主协议仍强制 B=1024。不要为测试拆掉正式实验预算检查。

独立参考应对冻结的 hidden/QKV 或层级 attention 数学作验证。**不要把「重算保留 token 的完整模型」当成 rolling cache 的逐位正确性 oracle**，因为历史 KV 的 hidden states 依赖当时上下文，重算会改变它们。

**第三组测试：H800 集成。**同一短书/开发书的 4096-token 2×2 诊断；保留原精度 scorer 与 fp32 scorer 差异的短对照，避免把 scorer 变化误归因于 RoPE。诊断使用同环境、同数据、同长度，分别保存新 run。

**验收：**P0-01/02/03/04/05/06 有闭环，所有失败反例被拦截，团队可解释 cache 与位置处理。未经确认的科学改动可以完成诊断与 amendment 草案，正式主协议发布需真实审阅。

### WP3：建立不可覆盖的注册、运行与结果链

**依赖：**WP2 的 schema/config 确定。**预计：**2–4 人工小时。

建议机器 registry：`experiments/registry.jsonl` 或 CSV，加字段说明。每个 run 至少包括：

```json
{
  "run_id": "unique-id",
  "phase": "reproduction",
  "status": "planned",
  "registered_at": "actual timestamp",
  "git_commit": "source commit at launch",
  "git_dirty": false,
  "protocol_id": "reproduction-v2",
  "config_path": "configs/...yaml",
  "config_sha256": "resolved-config hash",
  "data_manifest_sha256": "manifest hash",
  "model_revision": "pinned revision",
  "seed": 0,
  "gpu_uuid": "selected GPU",
  "hardware": "measured description",
  "environment_id": "verified environment",
  "command": "exact command with sensitive values redacted",
  "runtime_seconds": null,
  "gpu_hours": null,
  "cost": "not separately metered; basis documented",
  "metrics_path": null,
  "artifact_path": "runs/unique-id/",
  "parent_run_id": null,
  "exit_code": null
}
```

字段示例是 schema 草案，不是真实 run；不得将它直接登记成已完成实验。JSONL 可以使用追加事件与派生最终状态，避免不透明覆盖；CSV 也可配受版本控制的状态变更记录。

| 每个 run 文件 | 内容 |
|---|---|
| `registration.json`、`config_used.json`、`metadata.json` | 运行前合同、解析后参数、硬件/环境/源码与状态 |
| `books/<id>/metrics.json` | 实际长度、scored count、NLL sum/mean、hash、耗时 |
| `books/<id>/position_nll.npz` | 原始 NLL 或无损压缩、索引约定；不存模型权重 |
| `stdout.log`、`stderr.log`、`result.json` | 执行日志与汇总；失败时保留已完成书及错误信息 |
| `checksums.sha256` | 结果与日志哈希；生成时排除自身，避免自引用 |

启动时先检查输出路径未存在，再写 registration；失败结束写 failed 和 exit_code，不能只写 ended_at。当前 smoke 中 `2>/dev/null || true` 会隐藏 metadata 错误，正式 run 应移除这种忽略。

将 `git_commit` 在 launch 时锁定，不要运行中提交新代码后在结尾采集 HEAD 作为实验源码。单卡实验记录真正的 GPU UUID，不把机器里两张卡都算作已使用。GPU-hours 为实际占用卡数×墙钟小时；同时跑两卡不减少总 GPU-hours。

**验收：**模拟第二本书异常可留下第一本完整结果及 failed 状态；重复 ID 被拒绝；analysis 只吃 completed 且 valid run；可以从一个表格单元格追到 config/source/raw artifact。

### WP4：冻结协议并完成正式复现

**依赖：**WP2/3通过；真实所需批准已记录。**预计：**1–2 人工小时组织；默认三重复主实验约 8.1 GPU-h，需以修复后 pilot 更新。

1. 发布修订 `claim.md`、`protocol.md`、claim map、deviations、manifest 和统计计划，并记录 freeze commit。
2. 注册两个主方法×三个 seed 的完整 10-book 实验矩阵。
3. 运行全部主实验，失败重试用新 ID；对运行预算持续记账。
4. 用严格分析入口生成逐书结果、paired CI、主结论和图表。
5. 写 discrepancy diagnosis 与 paper comparison，包括支持、未支持或不确定的真实结论。

可在两张空闲 H800 上运行两个独立进程；无需 tensor parallel、distributed training 或两卡模型切分。速度比较用隔离 GPU 与成对/交错顺序，记录时钟/功耗/其他负载，不能用共享卡同时跑两个方法的耗时判断快慢。

复现必须产出：`results/reproduction/per_book.csv`、`summary.json`、`paired_result.json`、NLL-vs-position、per-book delta、cache plateau、`docs/reproduction_diagnosis.md`。文件名可等价调整，证据链接不能缺。

**诊断顺序：**先查源数据/tokenizer/hash，再查索引/位置与 cache，再查 precision/backend/env，最后讨论模型或缩放差异。任何补充诊断都使用新 run ID，不能用诊断中最有利的配置覆盖冻结主实验。

### WP5：执行两个改进 pilot 并选择完整评测

**依赖：**主复现已理解；假设与 pilot 得到课程要求的批准。**预计：**H1/H2 合计 4–8 人工小时，默认 pilot GPU 预算 2小时。

1. 按 §5 写三个完整 hypothesis cards，关联真实复现诊断，尚未观察到的机制写成待检验预测。
2. 冻结开发集与 H1/H2 的参数、算力、选拔规则和失败定义。
3. 在开发集执行 baseline、H1、H2 的 pilot，保存全部 seed、失败及负结果。
4. 生成 `results/pilots/comparison.csv` 和方法选择的可审阅说明。
5. 由团队根据预登记规则确认一个方法进入完整评测，并记录实际决定。

无需等某个周数才开始已获批准、依赖已满足的工作；仓库中「Week 10 才激活」的占位注释不应成为人为停工原因。反之，不因时间紧跳过复现诊断和审批事实。

### WP6：完成一个改进的完整评测与消融

**依赖：**WP5。**预计：**2–4 人工小时组织，新增完整方法三重复约 4.1 GPU-h；消融预算约1.5 GPU-h。

1. 冻结选定方法及阈值，在原10本test上完整运行与主 baseline 相同的 token/seed 协议。
2. 对照已冻结 StreamingLLM baseline 计算每书 paired delta 和不确定性。
3. 在预注册数据/长度上执行核心消融与开销控制。
4. 按预定义标准检查最差书、长位置段和方法失败条件。
5. 完成 `docs/improvement_evaluation.md`，明确正、零或负结果以及可信范围。

baseline 数值结果只有在模型、token hash、precision、scorer、position policy、硬件相关数值环境与代码路径验证等价时才能复用；否则必须补跑，预算同步重算。若修改任何共用评分或模型路径，不能把修复前 baseline 与修复后 improvement 直接配对。

### WP7：完成报告、展示、同伴审计及冻结

**依赖：**WP4/6 科学输出齐全。**预计：**8–12 团队人工小时，另留审核/返工时间。

1. 自动生成最终表图与 claim-to-artifact 索引。
2. 完成报告和 deck，逐一核对所有数字与 run/config 链接。
3. 让真实同伴使用脱敏 setup packet 执行 smoke，记录失败与修复。
4. 完成人工审核、AI ledger、贡献记录和每人答辩练习。
5. 在最后冻结前创建不可移动的最终 tag 与明确 commit，生成 release manifest 和 amendment 规则。

只有 Codex 自己重跑不能称为完成「peer audit」。找不到同伴时写明未完成，准备好 packet；不伪造签名/意见。真实报告、展示和个人答辩由团队承担，Agent 能协助准备但不能代替评估。

## 5. 改进假设与实验设计

### 5.1 为什么不直接扫 sink 数量当作全部改进

`sink∈{0,1,2,4,8}` 是有用消融，但仅换参数、挑最低 test NLL，不足以完成有诊断、有控制的改进研究。下面提供三个**候选假设**；它们不是已证实的创新，也不保证收益。先把诊断证据写进 hypothesis card，再让团队和教师确认。

推荐优先 pilot H1 和 H2，二者共用 prefix calibration 基础设施，无训练，不切换模型；H3 是偏系统的备选设计，只在诊断、时间和批准允许时考虑。不能为了凑「3 个」把 RoPE bug fix 算作第三个改进。

| 假设 | 研究变化 | 预计实现投入 | 主要风险 | 默认角色 |
|---|---|---:|---|---|
| H1 因果前缀校准的 sink 数量选择 | 用已看到的 prefix attention 选择本书固定 sink 数，替代所有书一律4 | 3–6小时 | 多/少几个 recent token 收益可能极小；attention proxy 不可靠 | pilot 1 |
| H2 保留首 token 的 attention-selected anchors | 固定4个 anchor 预算，但从早期 prefix 选出其余3个，替代直接保留最前4个 | 4–8小时 | sink 与语义重要性不同，非连续 anchors 可能降低稳定性 | pilot 2 |
| H3 预分配滚动 KV 实现 | 保持算法语义，减少缓存拼接和分配开销 | 12–24小时 | legacy attention 仍 concat；环形布局、RoPE重映射与实际收益难度较高 | 备选 hypothesis，不要求运行 |

预计时间为规划范围，不是测量结果。若 H1/H2 都无收益，仍从科学可解释性和正确性选择一个完整评测；课程允许零/负结果得分。

### 5.2 H1：因果 prefix calibration 选择 sink 数量

**诊断连接：**验证不同书在早期 tokens 的 attention concentration 是否差异明显；固定4个 sinks 是否对部分书过少或过多。没有差异也是合理的 falsification，不能先声称存在。

**明确算法 v1：**

1. 在处理本书前512个输入 token 时，只收集 query steps 64–511 对最前8个 token 的注意力质量；不读取后续 target loss 来决策。
2. 对所有层/heads 的上述注意力概率按固定方式求和，得到 `a[0:8]`，统计方式写入协议。
3. 选择候选 `{1,2,4,8}` 中最小的 k，使 `sum(a[:k])/sum(a[:8]) ≥ 0.90`；分母过小或非有限则使用4，并记录 fallback。
4. 在首次 eviction 前确定 k，后续保留初始 k 个 KV 与最新 `1024−k` 个 KV；本书内不再改变 k。
5. 所有位置使用已验证 cache-relative 路径；每本书重置 calibration 与 cache。

`512`、`64`、`0.90` 是可审阅的默认候选值，最终必须在看 test 改进结果之前冻结；只允许在明确的 validation 搜索预算内改动。前8个 token 本身的 attention fraction 是代理指标，不应描述为最优 sink 选择的理论保证。

决策发生在 cache 第一次驱逐之前，因此不会尝试复活已经丢失的 KV，也不会使用未来 token。prefix calibration 在 teacher forcing 中只读取当前及过去输入；不得看完整 book 后再回溯选 k。下一本书重新从头校准，不能把上一本文本的统计带过去。

**可证伪预测：**相对固定4-sink baseline，H1 的 post-overflow macro NLL 有改善，或者在预设小的质量损失容忍范围内揭示固定4并非必要；若大部分书仍选4、质量/开销没有优势，报告无效，不继续扩大参数搜索。

**必须控制：**

| 对照 | 目的 |
|---|---|
| 固定4、正常无校准 baseline | 与真实原方法对比总体收益/成本 |
| 固定4、执行相同 calibration 但丢弃选择结果 | 隔离采集 attention 本身的时间/显存与潜在数值影响 |
| 预注册固定 k 消融（例如2与8） | 判断改进来自真正的按书选择，还是一个普遍更好固定值 |
| 同一 H1 但关闭 adaptive selection、强制 k=4 | 验证代码路径在相同策略下回到 baseline |

主改进结论必须对固定4 baseline；不能仅比窗口差的方法好就叫改进。报告各书 k、calibration耗时、后溢出NLL、总体吞吐与额外峰值显存。

### 5.3 H2：保留首 token 的 attention-selected anchors

**诊断连接：**早期 token 中吸收 attention 的位置可能不是统一的0–3；但 sink 不等于语义相关 token。该假设的价值是检验「固定前缀 vs 因果选出的早期 anchors」，允许发现固定前缀更稳。

**明确算法 v1：**

1. 在与 H1 相同的 query steps 64–511，对前64个历史位置累计所有层/heads 的注意力质量。
2. 强制保留 position0，再从 positions1–63 中按累计质量选择3个；并列时优先较早位置。
3. 将选出的4个 anchor 按原始时间顺序排列，作为固定 anchor 集，不按 score 排列 KV。
4. 从第一次 eviction 开始，保留这4个 anchors，再从其他历史位置中选最新1020个；去重并保持时序。
5. 对实际保留序列应用连续 cache-relative 位置，未来不更新 anchor 集，不读取未来 NLL。

不能把中间 anchors 当 `StartRecentKVCache(start_size=4)` 直接切片实现。需要保留位置标签，并在 eviction 时按照明确集合/顺序 gather K/V；所有层使用同一套全局 anchor IDs，避免不必要的异构每层布局。预算上限在每一步验证，anchor 恰好位于近期集合时只保留一次，并补足可用最近 token，不能偷偷少保留或超过预算。

**可证伪预测：**H2 能在部分 early-attention 分布明显偏移的书上降低 NLL；若首4个 token 已是最稳定 sinks、重排造成信息损失或选出的 anchors 无益，则会出现零/负结果。

| 必要对照/消融 | 判别什么 |
|---|---|
| 原 StreamingLLM 固定0–3 | 主比较 |
| 保留首token+随机3个早期anchors，3 seeds | 收益是否来自 attention-informed selection，而非多样化位置 |
| H2 强制输出0–3 | 检查实现能退化为原方法 |
| 在开发集关闭强制首token | 首 token 保护是否必要；不必在 test 做大矩阵 |

若进入完整评测，默认优先保留「强制0–3」正确性消融与随机 anchor 控制；关闭首token属于预算内的补充诊断。所有 pilot 包括失败都要保存。

### 5.4 H3：预分配滚动 KV 的系统实现

**诊断连接：**只有 profiler 显示 KV 拼接/分配占实际显著开销时才实施；旧文档称 launch/Python dominated 并非 profiler 证据。

**假设：**在固定模型、position policy、token路径与NLL质量下，预分配 sink 区和 recent ring buffer 可降低每步 cat/allocation 开销，提升稳定吞吐或降低延迟波动。

实施需同时处理 attention 内部的 `torch.cat(past,key)` 与外部 eviction；只优化外面一个 concat，不能声称消除了所有 cache copy。cache-relative RoPE 常要求按逻辑顺序读取和旋转 raw keys；环形 buffer 的物理顺序不等于逻辑顺序。如果最终每步重新 materialize contiguous KV，必须把复制成本计入，不能隐藏它。

**独立验收：**在相同输入上保留的历史token集合一致、raw-K/V与attention结果正确、NLL在冻结容差内；GPU测量包含实际模型forward、cache维护与必要重排。分开 GPU event 时间和 host end-to-end 时间。

**控制：**原 cat 实现、预分配但仍 contiguous gather、完整 ring 路径；benchmark 顺序交错、同GPU独占、warmup后多次计时。先报告与当前 faithful implementation 的实现差异，不泛化为打败论文所有优化实现。

此方案对用户 AI Infra 兴趣更贴近，但不是本课程完成的必要条件。H1/H2 可按时交付时，不应为 CUDA Graph、Triton kernel 或完整 serving runtime 重新扩大范围。

### 5.5 Pilot 矩阵与选拔规则

默认开发数据：3本 validation，每本最多8192 tokens。默认 seeds=0,1,2。方法为固定4 baseline、H1、H2，共9个 method×seed jobs，每个job处理3本书。无需为各个候选重新训练。

先做 CPU correctness 和 tiny GPU smoke，再跑这个矩阵；同一书/seed 的两组必须匹配 token path 与 mask。两个假设共用 calibration 数据采集时，记录复用边界；不能省略其相对真实baseline的运行开销。

**必须在 pilot 结果产生之前冻结的选拔规则：**

1. 剔除违反因果性、预算、数值正确性或协议的实现，保存原因和失败证据。
2. 在有效候选中比较 paired macro ΔNLL、书间一致性和真实计算开销。
3. 如果一个候选改善质量且开销可接受，优先进入完整评测。
4. 如果两个都零/负，选择实现最可靠、机制最可解释、最能被消融证伪的候选，不追加无限搜索。
5. 由团队对预登记规则的应用给出真实审核意见，不由 Agent 虚构「导师已批准」。

建议用 `max_runtime_ratio=1.10` 和 `max_extra_peak_memory_ratio=1.10` 作默认可接受开销阈值；这些是本计划建议，不是课程规定，必须在 pilot 前确认。用固定预测数和固定预算下的Pareto比较，不把「KV预算相同」直接叫做所有计算成本完全一致。

### 5.6 公平性、不确定性与负结果报告

| 维度 | 固定/报告要求 |
|---|---|
| 数据与样本量 | 相同split、相同books、相同token IDs、相同scored range；不允许改进组多看未来数据 |
| 模型与数值 | 相同model revision、precision、scorer、position mechanism、backend；采集attention导致backend变化要有dummy control |
| 内存 | KV retained=1024；额外统计tensor、临时attention矩阵、workspace另计，不能隐去 |
| 计算 | calibration/token selection计入总时间；pilot两候选使用同样开发样本和预声明预算；若明显额外计算，给匹配/归一化分析或承认未满足公平约束 |
| 统计 | 书级配对CI、随机方法3 seeds；主假设一项，其他趋势标secondary/exploratory；不把最小seed当最终结果 |

若最终没赢，应回答：假设预测什么、实际何处不成立、消融排除了什么、剩余不确定性是什么。结果为负不等于工程失败；协议违规或不可追溯才会让相关比较失去证据价值。

## 6. 预算与完成顺序

### 6.1 H800 算力预算

旧R0001平均吞吐约31.7 input tokens/s，是**历史旧实现测量**。用实际154597 tokens/arm保守估算：每组约1.35 GPU-h，两组约2.71 GPU-h；三重复约8.13 GPU-h。计时实际只预测154587步，差别很小；新代码应使用真实prediction数作为吞吐分子。

RoPE修复、fp32 NLL、attention calibration、共享机器负载都可能改变吞吐。**下面是分配上限/估算，不是保证20小时必然够。**WP2 后每项都必须用新实测外推。

| 预算桶 | 规划 GPU-h | 说明 |
|---|---:|---|
| 已登记历史运行 | 0.10 | 当前文档约值，先清点服务器是否还有其他已消费实验 |
| 正确性与2×2诊断 | 1.00 | 包括真实模型smoke、小型位置/scorer检查 |
| 主复现2 arms×3 seeds | 8.13 | 基于原10本实际长度与旧吞吐估算 |
| H1/H2开发集pilots | 2.00 | 基线+两改进，3本×8192×3 seeds，另有少量calibration overhead |
| 选定改进完整3 seeds | 4.07 | 复用严格匹配的冻结baseline；否则重算预算 |
| 消融与核心控制 | 1.50 | 预注册开发集/短流，不默认再跑整个10本大矩阵 |
| 审计与演示验证 | 0.20 | 主要为CPU smoke、短GPU check |
| 故障/慢速/重试余量 | 3.00 | 保留，不预先分配给可选花活 |
| **合计** | **20.00** | 计划上限，所有实际消耗含失败计入 |

成本模型建议：

```text
estimated_gpu_hours(job)
  = sum_b(predictions_for_book_b / measured_predictions_per_second)
    / 3600 * repeat_count * allocated_gpu_count
    + measured_calibration_and_setup_gpu_hours

remaining = approved_ceiling - sum(actual_gpu_hours_all_attempts)
```

setup/加载时间如果占用GPU也计入；不要只统计成功forward。无法准确单独计费的机器记录 `not separately metered` 和GPU-h口径，不编造美元费用。

**预算触发器：**累计到12 GPU-h时重算剩余必需任务；达到16 GPU-h时停止新增可选实验；预测必需任务会超过20时，先准备具体缩减/替代方案并由团队按已有权限与课程要求确认，不能默默超限。

确定性主复现如有真实批准，可用单遍+book bootstrap节约约5.4 GPU-h；不能由Agent自行宣布豁免。去掉必要第二pilot、去掉完整改进评测或删掉不利seed不是合法省算力办法。

### 6.2 人力与墙钟时间

建议预留 **30–50团队人工小时、6–10个有连续工作时段的工作日**，并尽量让最终包提前至少48小时达到可提交状态。若环境已完全可用、服务器已有合格主实验，工作量可下降；若需要申请协议变更/环境修复，等待时间另外算，不能保证。

| 相对阶段 | 优先工作 | 退出条件 |
|---|---|---|
| 第1阶段 | WP0/1，确认资产、批准与环境 | 不会覆盖旧工作；能在声明环境加载模型/数据 |
| 第2阶段 | WP2/3，评测正确性与注册器 | P0故障反例被修复；新smoke可重复 |
| 第3阶段 | WP4，正式复现与诊断 | 合法主结论及不确定性、论文比较产生 |
| 第4阶段 | WP5/6，两pilot、一完整改进、消融 | 改进闭环完成，正/负结果都有证据 |
| 第5阶段 | WP7，报告展示、同伴检查与freeze | 清洁安装成功，全部表图可重建，成员签核真实 |

这些不是对课程周次或旧日期的检查，而是依赖顺序。计算可后台运行时，成员同步写方法/实验协议/文献部分，但不要提前编造结果。

### 6.3 截止压力下的裁剪顺序

**先裁剪可选项：**H3实现、第二模型、百万token、下游任务、性能kernel、全长度大规模参数搜索。

**保留必需项：**正确且公平的baseline、完整主比较、3个hypotheses、2个pilot、1个full evaluation、核心消融、不确定性与失败记录、报告/deck/贡献/AI证据。

如果剩余时间无法完成上述必需项，输出实际完成度和最小可提交证据，请团队就必要rescope与教师沟通；不要把一个未完成项目标记为fully compliant。本文不知道准确 `T_final`，因此只能给成本估计和完成路径，不能无条件保证按某个未给出的日期完成。

## 7. 最终交付与答辩

### 7.1 推荐最终文件布局

现有结构可以继续使用；课程接受等价结构，不必为了和示例一致大搬家。

```text
README.md
COURSE_AUDIT_AND_H800_EXECUTION_PLAN.md
TASK_STATUS.md
claim.md
claim_map.md
protocol.md
compute_budget.md
data_manifest.md
AI_USAGE.md
CONTRIBUTIONS.md
LICENSES.md
SECURITY.md
.env.example
environment/
configs/
src/
tests/
scripts/
experiments/registry.jsonl
data/dev_manifest.json
data/README.md
docs/approval_status.md
docs/audit_resolution.md
docs/protocol_amendments.md
docs/paper_comparison.md
docs/reproduction_diagnosis.md
docs/improvement_hypotheses.md
docs/pilot_selection.md
docs/improvement_evaluation.md
logs/agents/
runs/<new-run-id>/
results/reproduction/
results/pilots/
results/improvement/
results/claim_to_artifact.csv
figures/
tables/
report/
presentation/
audit/peer_audit/
defense/
submission/freeze_checklist.md
submission/release_manifest.json
submission/amendments.md
```

新增文件不是自带分数；每份应有真实内容和明确用途，避免复制大量空模板。许可证需逐项核对模型、PG19、上游代码、图/论文资产，记录修改和再分发规则，不能只写「所有东西都是MIT」。

### 7.2 最少应有的表图

| ID | 内容 | 证据输入 |
|---|---|---|
| T1 | 论文设置 vs 本项目设置与deviations | 固定论文版本、protocol、approval |
| T2 | 10本书的window/StreamingLLM NLL、delta、scored count | 主复现全部seed结果 |
| T3 | 汇总macro/micro指标、paired CI、claim status | 严格统计脚本输出 |
| T4 | 三个假设、两个pilot、选择依据 | hypothesis cards、全部pilot结果 |
| T5 | 完整改进、核心消融、runtime/memory成本 | 选定方法及控制run |

| ID | 图 | 要表达的问题 |
|---|---|---|
| F1 | NLL-vs-position，两主方法 | 差距出现在何处，是否随长度消失/扩大 |
| F2 | per-book paired delta及总体CI | 是否只靠一两本书撑起结论 |
| F3 | KV retained length/bytes vs position | 固定预算是否真实生效 |
| F4 | improvement vs baseline的quality–cost图或分组图 | 改进的收益和代价是否匹配 |

每图保存脚本入口、输入列表、参数、输出hash。长度不等的曲线在晚期bin可用书数减少，要显示或注明 `n_books`；不把短书以0填充，也不悄悄drop整本书。汇总分箱应与主/次统计口径一致并标注。

### 7.3 报告结构

课程 Full Specification 提及 proposed 8-page main-text limit；Student Guide 要求以最终公告为准。可先按8页组织草稿，最终用已公布模板与页数，不能把建议当绝对规定。

| 建议章节 | 必须回答 | 约占正文（建议） |
|---|---|---:|
| Claim与方法 | 测什么、为什么、sink/rolling cache/position如何工作 | 1–1.5页 |
| Protocol与忠实性 | 数据/指标/统计/预算、与论文差异、独立验证 | 1.5页 |
| Reproduction与diagnosis | 正式结果、paper比较、支持状态、旧bug的影响 | 1.5–2页 |
| Improvement与消融 | 三假设、两pilot、一full、控制与失败解释 | 2页 |
| Limitations、Agent反思、结论 | 边界、数据暴露、人工验证与未解决问题 | 1页左右 |

参考文献与附录是否计入以模板为准。报告区分 measured facts、interpretation、hypothesis 和 limitation。出现“显著”“稳定”“更快”“内存恒定”等词时，都应明确其统计/测量依据与适用范围。

### 7.4 AI ledger 和贡献记录

可让 `AI_USAGE.md` 成为现有 `agent_ledger.md` 的标准入口，但不能只有无内容链接。至少三阶段的 consequential interaction 都要有：任务、日期、委托/审核成员、实际可见tool/model/version（未知写not exposed）、建议、接受/修改/拒绝/升级、人工验证与证据链接。代表性脱敏prompt/output摘录保存到 `logs/agents/`。

本次审计可以记录为「代码审阅与后续设计」交互；**不能预先标记为人类已经审核通过**。后续成员读取并验证具体问题，例如重现P0-02/P0-03反例、对照论文位置编码，再记录自己的决定。课程不要求捏造一次AI拒绝。

`CONTRIBUTIONS.md`按真实成员记录：负责组件、实验run、图表/报告章节、peer review、commit/issue/日志证据。Git作者名或一行“大家贡献相同”不足以证明全部个人贡献，也不能把Agent提交伪装为某个同学已完成的人类审查。

### 7.5 Security、数据出境与来源

为每个外部服务/Agent记录实际发送的数据类型、用途、是否包含第三方限制内容、脱敏方式；不要声称所有原始书文本都未发送，除非确有检查。本次任务书只需引用课程规则，不上传用户提供HTML中的登录状态、用户信息或内部链接参数。

release前扫描tracked文件和相关历史中的token、密码、SSH key、`.env`，保存工具版本与脱敏结果；发现泄露先通知团队并按实际需要轮换，不自行在公开仓库打印完整secret。`.env.example`只含占位值。

### 7.6 展示、演示与个人问答

Full Specification 给出的建议格式为15分钟团队展示、10分钟问答、2分钟过渡；最终时间以教师安排为准。所有成员发言并准备个人技术问题，不能只让写代码的人负责全部解释。

建议12页左右：claim、机制、固定协议、独立测试、主结果、差异诊断、三个hypotheses、两个pilots、完整改进、消融与失败、复现/Agent证据、限制与结论。页数是建议，不新增课程要求。

演示以 CPU fixture 或短 GPU smoke、一个run与一张图的证据链为主，限定2–3分钟。准备同commit对应的录屏fallback，不能现场临时跑昂贵实验来替代冻结输出。

每位成员至少能独立回答以下五类问题：

1. 为什么attention sink有帮助，为什么保留KV还必须正确处理RoPE？
2. 1024预算、1025评分起点、15358/6115 scored count分别怎么推导？
3. macro/micro NLL、PPL、book bootstrap与3个seed各在解决什么问题？
4. 两个pilot为什么公平、最终方法为什么被选中、负结果说明了什么？
5. 哪个Agent建议被实际核验、具体改过哪行代码、哪些结论仍不确定？

不能使用实时Agent代答被考核的个人问题，除非教师明确允许的演示内容。答辩后按课程规则准备回应补充；补充解释不能偷偷替换冻结实验。

### 7.7 最终freeze的正确做法

代码、配置、环境、数据恢复方法、注册器、结果、报告、deck、ledger、贡献记录必须在共同freeze包内一致。将实验source commit与后续artifact/package commit分开记录，它们可以不同，但映射明确。

`release_manifest.json`应记录实际artifact路径和hash，不包含自身hash；release commit不可能在自身内容中直接自洽地写入自己的最终SHA。可在commit生成后用annotated tag/tag message、release记录或外部提交回执写最终commit SHA，避免无限修改自引用文件。

tag如 `cisc8006-final-v1` 一经提交冻结不移动、不force-push。后续修复保留原artifact，通过amendment和新commit记录；只做课程允许的表述/可访问性/获批打包修复，不重新做科学实验后替换原freeze证据。

## 8. 验收清单

以下勾选框初始全部为空，表示供后续执行者验收；不能因为本文已经给出设计就勾选完成。每个完成项在 `TASK_STATUS.md` 附真实路径/commit/run。

### Gate A：评测正确性

- [ ] cache-relative RoPE 已实现、逐层检查并与独立参考验证。
- [ ] 配置覆盖、未知键、数据完整性、配对验证全部 fail-closed。
- [ ] NLL、macro/micro、scoring边界与所有K/V的独立fixture通过。
- [ ] 两次新smoke使用不同ID成功，旧runs无覆盖，失败可审计。
- [ ] 2×2诊断与旧实现局限已记录，主协议修订有真实审核状态。

### Gate B：正式复现

- [ ] 原10本书、实际token数量与scored mask验证一致，所有正式输出可取回。
- [ ] 主方法与baseline使用同一合同，仅预声明因素不同。
- [ ] 三seed或真实获批替代方案完成，书级CI与逐书值均可重建。
- [ ] claim使用三态结论，invalid run与科学结果分开。
- [ ] 论文对应结果、deviations、diagnosis和limits有明确证据。

### Gate C：改进

- [ ] 三个假设具有诊断依据、可证伪预测、控制和预算。
- [ ] 两个获批pilot在独立开发数据完成，所有失败/负结果保留。
- [ ] 全评测方法由预登记规则与真实团队决定选出。
- [ ] 一个完整改进在冻结test协议评测，baseline可比、成本已匹配或合理归一化。
- [ ] 核心消融、不确定性、额外开销与failure cases齐全。

### Gate D：可复现包

- [ ] clean environment setup与资产恢复验证通过，独立审核人能完成smoke。
- [ ] 每张表/图都有精确命令与源run/config/hash，可从保存输出重建。
- [ ] registry包含commit、data、seed、hardware、runtime、cost、status、artifact。
- [ ] provenance、licence、AI来源、数据出境与secret检查有真实记录。
- [ ] freeze manifest、不可移动tag、最终commit与amendment规则一致。

### Gate E：人类交付

- [ ] 报告与deck使用最终模板/页数/时长要求，数值与冻结结果一致。
- [ ] 三阶段consequential AI使用和一次实质critical review可追溯。
- [ ] 贡献记录、真实peer audit与修复记录齐全。
- [ ] 每位成员独立解释关键机制、代码、统计、改进与失败。
- [ ] 演示fallback、最终提交入口和所需审批由实际成员确认。

**完成定义：**科学门槛、工程门槛和人类交付均具备真实证据。某项未达成时标partial/pending，不能宣称已经“完全符合课程”。负面科学结论本身不使Gate失败；错误协议、缺失证据或伪造记录会使Gate失败。

## 9. 直接交给 Codex 的启动指令

将下面整段交给 H800 服务器上、已进入本仓库的 Codex。此段是项目执行prompt，不是本机已安装的skill，也不要求任何本仓库之外的隐藏SKILL。

```text
你接手 crycryout/CISC8006Project。目标是在课程最终artifact freeze之前，
把现有StreamingLLM项目完成为可审计、可复现、可答辩的课程项目。

首先完整读取根目录 COURSE_AUDIT_AND_H800_EXECUTION_PLAN.md、
服务器可见的AGENTS.md、claim.md、protocol.md、agent_policy.md、
experiment_registry.md、agent_ledger.md和data_manifest.md。
检查当前git状态、已有本地实验和真实审批记录；不要覆盖用户未提交内容。
本文审计基线是a3ffaf0f514c9e79b7d3395dfc768f469a6df80a，
如果服务器/远端已有更新，重新核对相关问题后合并后续计划，不盲目回滚。

按WP0→WP1→WP2→WP3→WP4→WP5→WP6→WP7推进，
优先修复P0-01到P0-06，然后正式复现，再完成3个hypotheses、
2个pilots、1个完整改进评测、核心消融和最终交付。
每个工作包完成后记录真实测试结果、commit、run_id、产物和未决问题。
输出默认中文，结论优先；每次进度说明当前Gate和下一个明确动作。

不可违反：
- 不把旧R0001当作最终复现；不覆盖旧run，不删除失败或负结果。
- 不把pos-shift修复当成原创改进；不把相同position_id误当RoPE正确。
- 不在test上选择改进超参数；不更换冻结10本书以追求收益。
- 不把bootstrap seed当模型重复；不把10本×3seed当30本独立书。
- 不把KV预算相同等同于全部计算预算相同。
- 不虚构指标、教师批准、人类审核、同伴审计、个人贡献或Agent版本。
- 不超过已确认GPU预算；默认按现有20 GPU-h合同计全部失败和成功运行。
- 不把仅生成文件当作完成；主结论必须有run/config/source/artifact证据链。

可自主完成已授权的代码修复、fixture、数据/环境检查、记录器、图表脚本、
文档草稿和技术验证，不要在每个小步骤请求确认。
原课程/项目确实要求教师或团队批准的协议改变、豁免、scope变化，
先把代码验证、对照证据、具体amendment和审批材料做完整；
再只请求真正需要的人类决定，同时继续其他不依赖审批的工作。
审批缺失不是fabricate approval的理由，也不是停止全部独立工作的理由。

优先pilot本文H1与H2，参数在validation实验前冻结。
若二者不改善，按预登记规则选择一个完成负结果评测，不无限搜参。
H3、额外模型、长流百万token、CUDA Graph、Triton重写都不是必需项。

把准确T_final记录进TASK_STATUS.md；若未知，列为待确认而继续技术工作。
先完成关键证据，尽量在T_final前48小时准备好最终包。
最终交付包括可安装repo、测试、registry、原始/压缩输出、表图重建命令、
报告、deck、demo、AI_USAGE、CONTRIBUTIONS、peer audit材料与freeze manifest。
真实个人答辩、人类审核和课程提交由成员完成，不能由Agent虚假代签。
```

### 9.1 建议实现的命令接口

**下列为目标接口设计，当前仓库尚未实现；Codex应先实现并实测，再写进正式README。不要直接复制当现成命令执行。**

```bash
# 建立/验证环境与资产
bash scripts/setup_env.sh
python scripts/prepare_data.py --manifest data_manifest.md
python scripts/verify_assets.py --protocol configs/protocol_v2.yaml

# 无模型CPU测试与独立GPU smoke
python -m pytest tests/ -q
bash scripts/run_smoke.sh --mode cpu --run-id smoke-cpu-unique
CUDA_VISIBLE_DEVICES=0 bash scripts/run_smoke.sh --mode gpu --run-id smoke-gpu-unique

# 正式运行矩阵：必须先通过注册与预算检查
python scripts/run_matrix.py --matrix configs/reproduction_matrix.yaml --dry-run
python scripts/run_matrix.py --matrix configs/reproduction_matrix.yaml --execute

# 结果验证、生成图表与发布检查
python scripts/validate_runs.py --registry experiments/registry.jsonl
python scripts/build_results.py --manifest results/final_input_manifest.json
bash scripts/release_check.sh
```

prepare可改为读取结构化manifest，`data_manifest.md`保留人类入口；实现时应选一致格式而不是专门写脆弱Markdown parser。`run_matrix.py`的dry-run必须列出完整jobs、预算、现有run复用与输出路径，不能隐式启动GPU。

### 9.2 推荐提交边界

| 提交 | 应包含 | 应保留的验证证据 |
|---|---|---|
| `fix: validate config and paired evaluation contracts` | P0-02/03/05与CPU tests | 旧反例失败、新逻辑正确 |
| `fix: restore cache-relative position semantics` | position adapter、真实attention测试 | 独立参考与2×2diagnostic |
| `feat: add immutable runs and reproducible setup` | unique IDs、metadata、registry、setup/data | clean smoke与失败恢复 |
| `docs: freeze reproduction protocol v2` | 审批事实、deviations、统计/预算 | 实际freeze source commit |
| `experiment: reproduce and evaluate improvements` | 分次提交实验记录、分析、改进、消融 | 每次对应真实run与输出 |

最后再提交报告/deck/ledger/贡献和打包。实验可以按方法/阶段拆更多小commit，不用把所有实验挤进一个提交，也不为让历史好看补造虚假旧commit。

## 10. 来源与审计边界

### 10.1 课程材料

只引用用户提供的课程正文；没有访问用户Moodle会话，也没有把HTML登录界面公开到仓库。

| 来源 | 核对的主要内容 | 附件SHA256 |
|---|---|---|
| CISC8006 Course Project and Grading: Student Guide，2026-09-02 | 单claim、3→2→1、Agent、最终包、85团队+15个人 | `4e19ad7ecb52e2e67a57ba691c00e633005d90425bee21b286a5c72c2be34fe2` |
| CISC8006 Course Project: Full Specification and Grading Criteria，2026-09-02正文 | §2–5科学与来源要求，§6freeze，§7–8评分与证据规则，§9–11展示/清单/待确认项 | `20cab6d91610196c91e5b19b140ab57ad6eee7c680853d09abbde41bf1107aef` |

上表hash用于识别本次审计输入，不意味着应公开附件本身。最新最终公告优先于这两份文件中的暂定细节。

### 10.2 技术一手来源

- [StreamingLLM论文，arXiv v4](https://arxiv.org/html/2309.17453v4)：§3.2位置处理、§4.1语言建模设置及对应图表。本文的具体代码修复与实验设计是审计推导，不是论文已经证明的新方法。
- [官方StreamingLLM仓库](https://github.com/mit-han-lab/streaming-llm)，本项目记录的pin为 `2e5042606d69933d88fbf909bd77907456b9b4dd`；实际核读本仓库vendored代码与README。
- [Transformers v4.33.0 GPT-NeoX源码](https://github.com/huggingface/transformers/blob/v4.33.0/src/transformers/models/gpt_neox/modeling_gpt_neox.py)：默认position_ids、K旋转与cache保存顺序。
- [本项目审计快照](https://github.com/crycryout/CISC8006Project/tree/a3ffaf0f514c9e79b7d3395dfc768f469a6df80a)：所有「当前仓库」判断限定于此快照。

### 10.3 关键源码证据索引

| 结论 | 快照中的路径/函数 |
|---|---|
| 配置默认值覆盖问题 | `scripts/eval_ppl.py::parse_args` |
| 缺少pos-shift、fp16 scorer、book reset | `scripts/eval_ppl.py::main` |
| book intersection继续计算 | `scripts/analyze_paired.py::main` |
| position test缺少真实模型验证 | `audit/cache_index_test.py::implicit_position_ids`及main check5 |
| upstream提供实际pos-shift路径 | `third_party/streaming-llm/streaming_llm/pos_shift/modify_gpt_neox.py` |
| upstream across-book cache行为 | `third_party/streaming-llm/examples/eval_long_ppl.py` 的past定义位置 |
| smoke固定R0001并允许覆盖 | `scripts/run_smoke.sh` |
| manifest短书与token数量 | `audit/book_list.json`、`data_manifest.md` |
| 现有结果只有smoke阶段 | `experiment_registry.md`、`runs/R0001/*/result.json` |
| 数据来源文字不一致 | `claim_map.md`、`feasibility.md`、`environment/third_party.md`与`data_manifest.md` |

### 10.4 本次实际执行的最小检查

| 检查 | 操作 | 结果/范围 |
|---|---|---|
| 配置优先级反例 | 隔离原parse_args函数，提供YAML stub | model/revision/precision仍保持CLI非空默认值，确认bug；无模型执行 |
| 缺书反例 | 运行原analyze_paired.py，window=A/B、streaming=A | 退出0并输出RECOVERED与零宽CI，确认fail-open问题 |
| 书长核算 | 读取实际book_list.json按cap计算 | 每组154597输入、144337 scored；服务器仍须复验tokenizer资产 |
| 历史NLL读取 | 读取R0001两组result.json | delta≈−0.158138；未重跑、不推断为正式成功 |
| 固定版本语义核对 | 阅读Transformers4.33源码与vendoredpos-shift | 确认默认rotated-K缓存与missing patch；性能影响待GPU实验 |

本次环境未提供PyTorch/H800，因此没有执行真实cache oracle、GPU smoke、模型集成回归或干净安装。所有未来验收与预算都明确标为待执行。仓库以外可能存在补充实验、审批或贡献材料；服务器接手时首先清点，不能把本次快照审计当作对线下工作的否定。



