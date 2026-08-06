# Reasonix 证据包补强 — 设计规格 (Spec)

- 日期: 2026-08-06
- 状态: 已获用户认可，待实现
- 作者: Reasonix 破晓
- 关联议题: 对标 VulnClaw 的反幻觉机制，将"证据强制"从模型自觉升级为代码硬约束

---

## 1. 背景与问题

上一轮对比分析结论：Reasonix 的工具纵深（60+ 成熟工具）是护城河，但**证据链依赖宿主模型自律 + 事后人工复核**，缺乏代码级的结构性保证。VulnClaw 用代码强制"证据必须逐字符出现在真实工具输出"，这是 Reasonix 必须补齐的短板。

当前三个具体痛点：

1. `ai-pentest-orchestrator.py` 将工具原始输出**直接塞进 AI prompt**，无证据编号、无逐字符校验、不追溯原始命令——编造 flag 无结构性拦截。
2. `evidence/` 与 `results/` 目录在 AGENTS.md 中声明但**尚未实际创建**，证据留存机制是空的。
3. 8 份经验文件已沉淀，但**无高信号证据与普通噪音的区分**，冷热记忆治理停留在配置参数层。

### 1.1 目标

- 将"反幻觉"从规则约束升级为**脚本层代码强制 + 规则引导双层**。
- 落地证据采集、记忆归档、报告打包三件套，形成可复核、可复现、可回放的证据闭环。
- 保持现有缓存经济优势不被破坏（证据校验只在小样本上做，不拖慢主流程）。

### 1.2 非目标（YAGNI）

- 不做独立的证据图数据库（Neo4j 等），沿用轻量级文件化方案。
- 不替换现有 `ai-pentest-orchestrator.py` 主流程，而是新增模块并接入。
- 不做全量逐字符强制（避免拖慢高频工具调用），只对关键结论强制。

---

## 2. 架构（方案 B — 模块化 CLI）

新增 `scripts/evidence_pack/` 包，三个独立模块 + 统一 CLI 入口。

```
scripts/evidence_pack/
  __init__.py
  cli.py                    # 统一入口: evidence-pack <子命令>
  evidence_harvest.py       # 证据采集 + 证据号分配 + 逐字符归属校验
  memory_archive.py         # 高信号证据 → 经验/攻击链去重沉淀
  report_pack.py            # 证据包清单 → 可复核报告
```

### 2.1 模块职责边界

| 模块 | 做什么 | 怎么用 | 依赖什么 |
|:-----|:-----|:-----|:-----|
| `evidence_harvest` | 采集工具输出 → 分配 EVID 编号 → 逐字符校验 → 产出 manifest | `evidence-pack harvest <out> --tag <name>` | 工具原始输出文件/stdin |
| `memory_archive` | 读 manifest → 识别高信号 → 去重沉淀到经验/攻击链 | `evidence-pack archive <manifest.json>` | `evidence_harvest` 的产出 |
| `report_pack` | 读 manifest + 结论 → 生成可复核报告到 `reports/` | `evidence-pack report <manifest.json> --ai <analysis.md>` | `evidence_harvest` 的产出 |

每个模块单一职责、可独立 CLI 测试、可组合复用。任一模块出问题不影响其他模块，可分阶段灰度启用。

### 2.2 统一入口伪代码

```python
# cli.py
def main():
    sub = sys.argv[1]  # harvest | archive | report
    if sub == "harvest": evidence_harvest.main()
    elif sub == "archive": memory_archive.main()
    elif sub == "report": report_pack.main()
```

---

## 3. 组件详情

### 3.1 evidence_harvest — 证据采集（核心，解决反幻觉）

**输入**：工具原始输出（nuclei/fscan/httpx/手动粘贴），支持从文件或 stdin 读取。

**处理流程**：
1. 对每条**关键结论**（flag / 凭证 / 漏洞告警）分配 `EVID-001` 递增编号。
2. 记录元数据：来源命令、时间戳、原始输出片段、目标。
3. `--verify` 硬校验：结论必须**逐字符出现在真实输出**，否则标 `[UNVERIFIED]` 并拒绝进入报告。
4. 产出 `evidence/manifest.json`（证据清单）+ 最小化证据样本文件。

**证据号格式**：`EVID-<NNN>`，全局递增，跨任务不重复（用任务前缀，如 `EVID-T001-001`）。

**校验规则（代码强制）**：
- `--verify` 为默认开启的硬校验开关；`--no-verify` 可显式关闭（仅用于调试）。
- 结论字符串必须能在原始输出中找到完全匹配（去空白后）。
- 校验通过 → 标记 `[VERIFIED]`，进入报告。
- 校验失败 → 标记 `[UNVERIFIED]`，默认**拒绝**进入最终报告；仅当带 `--allow-unverified` 时才以高风险标注形式保留，且报告醒目标红。
- 汇总统计: 校验结束时打印 `N verified / M unverified`，供人工复核。

**manifest.json 结构**：
```json
{
  "task_id": "T001",
  "created_at": "2026-08-06T10:00:00",
  "target": "http://example.com",
  "evidence": [
    {
      "id": "EVID-T001-001",
      "type": "vuln_alert",
      "source_cmd": "nuclei -u http://example.com -as -j",
      "claim": "SQL 注入存在于 /api/login",
      "status": "VERIFIED",
      "raw_snippet": "snippet from original output",
      "timestamp": "2026-08-06T10:00:01"
    }
  ]
}
```

### 3.2 memory_archive — 记忆归档（解决冷热记忆治理）

**输入**：`manifest.json` + 可选 AI 结论文件。

**处理流程**：
1. 读 manifest，识别**高信号证据**（type 为 flag/credential/vuln_alert）。
2. 与 `memory/pentest-experience-NNN.md`、`memory/attack-chains.yaml` 现有内容做**去重**（按证据 ID 或内容哈希）。
3. 新证据追加到新经验文件（序号递增），攻击链条目并入 `attack-chains.yaml`。
4. 普通噪音不落记忆，避免污染。

**高信号判定**：type ∈ {flag, credential, vuln_alert, chain, critical_config}。

### 3.3 report_pack — 报告打包（解决目录与报告规范化）

**输入**：`manifest.json` + AI 分析结论文件。

**处理流程**：
1. 真正落地 `evidence/ results/ reports/` 三目录分工（若不存在则创建）。
2. 生成可复核报告：每个结论带 `[EVID-0NN]` 链接 + 可复现命令。
3. 产出 `reports/` 下的 HTML/Markdown 报告。

**报告结构**：目标概况 → 发现摘要（带证据号）→ 攻击路径 → 验证命令 → 证据清单 → 风险等级。

---

## 4. 数据流

```
工具输出 → harvest(编号+校验) → manifest.json
        → AI 分析(结论引用 EVID 编号)
        → memory_archive(高信号沉淀)
        → report_pack(可复核报告)
```

### 4.1 与现有 orchestrator 的关系

- `ai-pentest-orchestrator.py` 保持独立，不重构。
- 可选接入：在 orchestrator 的 Phase 4 后调用 `evidence-pack harvest`，把扫描输出先过证据校验再进 AI prompt。
- 分阶段灰度：先单独用 evidence-pack，验证稳定后再接入 orchestrator。

---

## 5. 规则层（双层中的"规则"）

### 5.1 AGENTS.md 新增"反幻觉铁律"段

- 任何无 EVID 编号的结论必须标记 `[UNVERIFIED]`，禁止直接断言。
- 引用证据时统一写 `[EVID-0NN]`。
- 发现结论与原始输出不符 → 立即停止并复核，不继续下钻。

### 5.2 各 skill 统一规则

- 在 `pentest-master.md` 及关键专项 skill 顶部增加：分析与报告阶段必须引用 EVID 编号。

---

## 6. 文件与目录规划

| 路径 | 用途 | 状态 |
|:-----|:-----|:-----|
| `scripts/evidence_pack/cli.py` | 统一入口 | 新建 |
| `scripts/evidence_pack/evidence_harvest.py` | 证据采集 | 新建 |
| `scripts/evidence_pack/memory_archive.py` | 记忆归档 | 新建 |
| `scripts/evidence_pack/report_pack.py` | 报告打包 | 新建 |
| `scripts/evidence_pack/__init__.py` | 包标记 | 新建 |
| `evidence/` | 证据包 + manifest + 最小化样本 | 新建（首次运行创建） |
| `results/` | 原始扫描结果 | 新建（首次运行创建） |
| `reports/` | 最终可复核报告 | 新建（首次运行创建） |
| `AGENTS.md` | 新增反幻觉铁律段 | 修改 |
| `skills/pentest-master.md` | 增加 EVID 规则 | 修改 |

---

## 7. 错误处理与测试

### 7.1 错误处理

| 场景 | 行为 |
|:-----|:-----|
| 结论无证据标注 | 标记 `[UNVERIFIED]`，默认拒绝进入报告 |
| 校验失败（逐字符不匹配） | 标记 `[UNVERIFIED]`，需 `--allow-unverified` 放行 |
| 证据文件缺失 | 明确报错并提示路径 |
| manifest 格式错误 | 返回非零退出码 + 错误信息 |
| 目标未授权 | 调用 `check-scope.py` 前置校验，拒绝执行 |

### 7.2 测试

- 每个模块独立 CLI 可测（`evidence-pack harvest/archive/report`）。
- 用 `format-results.py` 历史输出或 `memory/pentest-experience-001.md` 内容做回归样例。
- 单元测试：构造一个编造结论，验证其被 `--verify` 拒绝。

### 7.3 安全合规

- 所有操作仅限授权目标；写入 `evidence/` 前先经 `check-scope.py` 校验。
- 证据样本做最小化处理（脱敏），敏感内容不进入 git（`.gitignore` 已覆盖）。

---

## 8. 验收标准

1. `evidence-pack harvest` 能从工具输出生成 manifest，且能**拒绝编造结论**（测试用例验证）。
2. `evidence-pack archive` 能将高信号证据去重沉淀到经验/攻击链，且噪音不落记忆。
3. `evidence-pack report` 能生成带 `[EVID-0NN]` 链接的可复核报告。
4. `evidence/ results/ reports/` 三目录按首次运行自动创建并写入。
5. AGENTS.md 与 pentest-master.md 已加入反幻觉铁律与 EVID 规则。
6. 主流程 `ai-pentest-orchestrator.py` 不受影响，灰度接入后正常运行。

---

## 9. 与对标（VulnClaw）的映射

| 补强项 | 对标 VulnClaw 能力 | 落地方式 |
|:-----|:-----|:-----|
| 证据强制 | 代码强制"逐字符出现在真实输出" | `evidence_harvest` 的 `--verify` 硬校验 |
| 高信号预览 | 冷热记忆分离 + 高信号预览 | `memory_archive` 高信号判定 |
| 可复核报告 | 证据号 + 复现包 + curl 存档 | `report_pack` 报告生成 |

---

## 10. 附录

- 回滚方案：所有新增模块独立于主流程，删除 `scripts/evidence_pack/` 即可完全回退，不影响现有工具链。
- 后续扩展（不在本次范围）：证据→Mermaid 攻击链流程图、证据包的 Web 可视化面板。