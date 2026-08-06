# DawnForge 证据包补强 — 实现计划 (Implementation Plan)

- 日期: 2026-08-06
- 关联 spec: `docs/specs/2026-08-06-evidence-pack-design.md`
- 状态: 待执行
- 执行语言: Python 3 (兼容现有 scripts/ 目录风格)

---

## 0. 前置检查点 (Review Checkpoint)

- [ ] 确认 `scripts/evidence_pack/` 目录不存在（避免覆盖）
- [ ] 确认 `config/scope.yaml` 存在（`check-scope.py` 依赖）
- [ ] 确认 Python 3 可用（现有脚本均用 Python 3）

**若任一未满足，停止并沟通，不强行开始。**

---

## 1. 任务分解

本计划拆分为 6 个任务，严格按顺序执行，每个任务含验证步骤。

### Task 1 — 脚手架与目录落地

**目标**：创建包结构 + 三个输出目录，遵循 spec §6。

**动作**：
1. 创建 `scripts/evidence_pack/__init__.py`（含版本号常量）。
2. 创建空目录 `evidence/`、`results/`、`reports/`（若不存在）。
3. 在 `evidence/` 下创建 `.gitkeep` 占位（保持空目录入版本库）。

**验证**：
- 运行 `python -c "from pathlib import Path; [print(Path(p).exists()) for p in ['evidence','results','reports']]"`，三个均输出 True。

---

### Task 2 — 证据采集模块 `evidence_harvest.py`

**目标**：实现 spec §3.1 核心逻辑。

**接口**：
```bash
python scripts/evidence_pack/cli.py harvest <out.json> --tag <name> [--target <target>] [--no-verify] [--allow-unverified]
```
- 输入：从 stdin 或 `<out.json>` 前的临时文件读取工具原始输出。实际输入约定：`harvest` 从 stdin 读取原始输出，`--tag` 指定任务标识，`--target` 指定目标。
- 输出：`evidence/manifest_<tag>.json`。

**核心逻辑**：
1. 分配证据号 `EVID-<tag>-<NNN>`（tag 内递增）。
2. 解析 stdin 中的"关键结论"行：约定输入格式为 `<原始行>`，由调用方（AI）用 `--claim` 逐条声明结论；或读取 `--claim-file`（每行一个结论）。
   - 简化落地：`harvest` 接收 `--claim`（可多次，每条一个结论），对每条结论在原始输出中做逐字符匹配。
3. 校验：去空白后，`claim` 必须是原始输出子串 → `[VERIFIED]`；否则 `[UNVERIFIED]`。
4. 默认 `--verify`（校验开启）；`--no-verify` 跳过（仅调试）。
5. 汇总打印 `N verified / M unverified`。
6. 写 `evidence/manifest_<tag>.json`。

**manifest 结构**（对齐 spec §3.1）：`task_id / created_at / target / evidence[]`，每条含 `id/type/source_cmd/claim/status/raw_snippet/timestamp`。

**验证**：
- 构造测试：`echo "mysql root/123456" | ... harvest --target localhost --tag T01 --claim "mysql root/123456"` → status=VERIFIED。
- 构造编造结论：`--claim "flag{invented}"`（不在原始输出）→ status=UNVERIFIED，默认拒绝。

---

### Task 3 — 记忆归档模块 `memory_archive.py`

**目标**：实现 spec §3.2。

**接口**：
```bash
python scripts/evidence_pack/cli.py archive <manifest.json> [--no-dedup]
```

**核心逻辑**：
1. 读 manifest，识别高信号证据（type ∈ {flag, credential, vuln_alert, chain, critical_config}）。
2. 去重：按 `id` 与 `memory/` 下已有经验文件中的证据号比对；`--no-dedup` 跳过。
3. 沉淀：新高信号证据追加到 `memory/pentest-experience-0XX.md`（序号递增）；攻击链条目并入 `memory/attack-chains.yaml`（若证据含 chain 类型）。
4. 噪音（非高信号）不落记忆。

**验证**：
- 运行后用 `Read` 检查新生成的 `pentest-experience-0XX.md` 含该证据，且 `attack-chains.yaml` 未污染。

---

### Task 4 — 报告打包模块 `report_pack.py`

**目标**：实现 spec §3.3。

**接口**：
```bash
python scripts/evidence_pack/cli.py report <manifest.json> [--ai <analysis.md>] [--format html|md]
```

**核心逻辑**：
1. 确保 `reports/` 存在。
2. 读 manifest + 可选 AI 结论文件。
3. 生成报告：目标概况 → 发现摘要（带 `[EVID-0NN]`）→ 攻击路径 → 验证命令 → 证据清单 → 风险等级。
4. HTML 报告醒目标红 `[UNVERIFIED]` 条目；MD 报告用 `> ⚠️ UNVERIFIED`。

**验证**：
- 运行 `report` 后确认 `reports/` 下生成报告文件，且内容含证据号与可复现命令。

---

### Task 5 — CLI 入口 `cli.py`

**目标**：实现 spec §2.2 统一入口。

**动作**：
- `cli.py` 分发 `harvest / archive / report` 三个子命令，参数解析、错误处理（非零退出码）、`--help`。

**验证**：
- `python scripts/evidence_pack/cli.py --help` 显示三个子命令。
- 无子命令或无参数 → 打印用法并退出码 1。

---

### Task 6 — 规则层落地（AGENTS.md + pentest-master.md）

**目标**：实现 spec §5。

**动作**：
1. `AGENTS.md` 新增"## 🛡️ 反幻觉铁律"段（无 EVID 编号结论必须标 `[UNVERIFIED]`；引用统一写 `[EVID-0NN]`；不符即停）。
2. `skills/pentest-master.md` 顶部增加 EVID 规则说明。

**验证**：
- 用 `Grep` 确认两文件均含 `EVID` 与 `反幻觉铁律` 关键词。

---

## 2. 端到端冒烟测试 (Review Checkpoint)

按 spec §8 验收标准逐条验证：

- [ ] §8.1 `harvest` 能生成 manifest 且拒绝编造结论
- [ ] §8.2 `archive` 高信号去重沉淀、噪音不落记忆
- [ ] §8.3 `report` 生成带 `[EVID-0NN]` 的可复核报告
- [ ] §8.4 三目录自动创建并写入
- [ ] §8.5 AGENTS.md 与 pentest-master.md 已加反幻觉铁律
- [ ] §8.6 主流程 `ai-pentest-orchestrator.py` 不受影响（`python scripts/ai-pentest-orchestrator.py --help` 正常）

**冒烟测试脚本**（写入临时目录，不入项目）：
```bash
# harvest 校验
echo "cracked: admin/admin123" | python scripts/evidence_pack/cli.py harvest --tag SMOKE --target localhost --claim "admin/admin123"
# 编造结论应被拒
echo "cracked: admin/admin123" | python scripts/evidence_pack/cli.py harvest --tag SMOKE2 --target localhost --claim "flag{nope}"
# archive
python scripts/evidence_pack/cli.py archive evidence/manifest_SMOKE.json
# report
python scripts/evidence_pack/cli.py report evidence/manifest_SMOKE.json --format md
```

---

## 3. 回滚与恢复

- 每个模块独立，删除 `scripts/evidence_pack/` 即完整回退，不影响现有工具链。
- 规则层改动（AGENTS.md / pentest-master.md）为文档级，可手动还原。
- 冒烟测试产生的 `evidence/`、`reports/` 临时文件在验收后可清理。

---

## 4. 风险与假设

- 假设 Python 3 环境可用（现有脚本已证实）。
- 证据输入协议（`--claim` 逐条声明）为简化约定，后续可扩展为结构化解析。
- `check-scope.py` 前置校验：`report` 与 `archive` 写盘前可选调用；首版默认不强制，避免阻断，但保留接入点。