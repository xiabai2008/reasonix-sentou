# 品牌命名方案（Branding）

> 目标：为多 Agent 通用的 AI 渗透作战工作台定名，兼顾传播力、记忆度与差异化。
> 命名字段：`<品牌名>` — 仓库名、项目代号、社区话题词统一使用。

## 核心差异化（命名的锚点）

1. **证据强制反幻觉** — 每个结论带 EVID 编号、逐字符校验，杜绝编造
2. **多 Agent 通用** — 同一份技能库 + persona 服务 Claude Code / Codex / OpenCode / Trae
3. **经验持续成长** — 每战必记，越用越懂你的打法（记忆层 + 攻击链）

## 候选方案

| 名称 | 中文义 | 命名逻辑 | 传播力 | 备注 |
|:-----|:-------|:---------|:-------|:-----|
| **DawnForge** | 破晓锻造 | 保留既有"破晓"身份 + Forge（锻造/成长），暗合"经验持续锻造" | ★★★★ | **主推**，品牌延续 |
| **Grimoire** | 魔法书 | 一本不断生长、收录所有攻击技法的魔法书，呼应技能库+经验记忆 | ★★★★★ | 单字记忆强，star 吸引力高 |
| **VeriPwn** | 验证即拿下 | Veri(验证/证据) + Pwn，直击"证据强制"核心 | ★★★★ | 主打反幻觉卖点 |
| **OmniRed** | 全境红队 | Omni(多 Agent/全场景) + Red(红队)，强调通用性 | ★★★ | 偏工具感 |
| **ProofDawn** | 黎明见证 | Proof(证据) + Dawn(破晓)，双关"黎明即证据确凿" | ★★★ | 含蓄 |

## 决定

**最终品牌名 = DawnForge**（仓库名 / 代号 / 社区话题统一）
- 保留"破晓"作为中文代号与 persona 身份，DawnForge 作为英文品牌名。
- 主 slogan：**Forge your dawn on the battlefield.**（在战场上锻造你的黎明）
- 次要 slogan：**Evidence-forced, memory-grown, agent-agnostic.**（证据强制、记忆成长、Agent 无关）

### 落地约定

| 场景 | 值 |
|:-----|:---|
| 英文品牌名 | `DawnForge` |
| 中文代号 | 破晓（persona / 技能身份） |
| GitHub 仓库名 | `dawnforge`（若占用则 `dawnforge-pentest`） |
| README 标题 | `DawnForge · 破晓` |
| AGENTS.md 标题 | `DawnForge 渗透作战工作台` |
| 版权头 | `Copyright (c) 2026 DawnForge Contributors` |

> 技术路径（本地文件夹 `reasonix_sentou`、`reasonix.toml` 文件名）为硬编码基础设施，保持不动，避免破坏脚本与包装器。