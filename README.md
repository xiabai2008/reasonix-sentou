<div align="center">

# DawnForge · 破晓

**多 Agent 通用的 AI 渗透作战工作台**

> Forge your dawn on the battlefield. — 在战场上锻造你的黎明

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/xiabai2008/reasonix-sentou.svg?style=social&label=Star)](https://github.com/xiabai2008/reasonix-sentou)
[![Hub:Src](https://img.shields.io/badge/Agent-Claude%20%7C%20Codex%20%7C%20OpenCode%20%7C%20Cline-4d5cff)]()

**证据强制反幻觉 · 多 Agent 通用 · 经验持续成长**

</div>

---

## 它是做什么的？

`DawnForge` 不是一个"工具堆"，而是一套**让 AI 稳定参与渗透测试**的可成长作战环境。它把工具、技能、经验、安全边界连成闭环，让 Agent 在长会话中持续理解目标、调用工具、分析结果、沉淀经验。

与普通工具箱最大的不同是三点：

1. **证据强制反幻觉** — 每个结论都带 `EVID` 编号、逐字符校验后才算 `VERIFIED`，从机制上杜绝 AI 编造 flag / 凭证 / 漏洞告警。
2. **多 Agent 通用** — 同一份 persona + 技能库，同时服务 **Claude Code / Codex / OpenCode / Cline / Trae**。
3. **经验持续成长** — 每战必记，越用越懂你的打法（记忆层 + 攻击链 + 成本统计）。

## 快速开始

```bash
git clone https://github.com/xiabai2008/reasonix-sentou.git
cd reasonix-sentou
# 首次部署（下载工具/字典、装依赖、建快捷命令）
./scripts/setup-new-pc.ps1
# 健康检查
python scripts/health-check.py
```

然后在你常用的 Agent（Claude Code / Codex / OpenCode…）中打开项目目录，直接描述目标：

```text
扫一下 192.168.1.10
测一下 http://example.com
帮我审计这个 JS
这个 JWT 看看有没有越权
用 AI 分析一下扫描结果，告诉我下一步
```

Agent 会读取 `AGENTS.md` 自动进入渗透专家角色，按规则选工具和技能。

### 接入你的 Agent

```bash
# 把技能链接/复制到你用的 Agent 约定目录
python scripts/setup-agent-links.py --apply          # 全部
python scripts/setup-agent-links.py --agents claude  # 仅 Claude Code
python scripts/setup-agent-links.py --mode copy      # 用复制代替软链
```

各家 Agent 的配置模板见 `templates/agent-configs/`（opencode/codex/claude 示例）。

## 核心能力

### 工具链（60+）
端口扫描、Web 评估、目录爆破、爬虫、子域名、SQL 注入、XSS、SSTI、反序列化、内网横向、提权……工具本体放 `tools/`，`bin/` 提供统一快捷入口。

| 场景 | 首选 | 备选 |
|:-----|:-----|:-----|
| 快速端口扫描 | naabu | fscan（含服务识别）|
| 内网全扫描 | fscan | — |
| Web 漏洞检测 | nuclei | xray（被动更安静）|
| 目录爆破 | ffuf | gobuster |
| SRC 挖洞 | poxiao | rayscan |
| 深度 SQLi/XSS | rayscan | — |
| SQL 注入 | sqlmap | — |
| XSS 专项 | dalfox | nuclei |
| 提权辅助 | PEASS-ng | — |

### 技能库（60+ Skills）
`skills/pentest_skills/<name>/SKILL.md`，带标准 YAML frontmatter，兼容 Anthropic Agent Skills 格式，覆盖 SQLi、XSS、SSRF、IDOR、JWT、反序列化、WAF 绕过、子域名接管等全部主流漏洞方向。

### 证据闭环（反幻觉铁律）
```
harvest → archive → report
工具输出 → 提取结论 → 分配EVID+逐字符校验 → 沉淀记忆 → 生成可复核报告
```

```bash
python -m scripts.evidence_pack.cli harvest \
  --tag T01 --target $TARGET --claim "SQL 注入存在于 /api/login"
python -m scripts.evidence_pack.cli archive evidence/manifest_T01.json
python -m scripts.evidence_pack.cli report evidence/manifest_T01.json --format md
```

### 经验系统
每次任务结束写入 `memory/pentest-experience-NNN.md`，可复用攻击链记入 `memory/attack-chains.yaml`，成本数据记入 `memory/cost-stats.csv`。经验会反过来影响下一次判断。

### 安全边界
- 默认 `permissions.mode = "ask"`，高危操作人工确认
- `config/scope.yaml` 授权白名单校验
- 三档作战模式：`safe / normal / aggressive`
- 禁止 `.gov` / `.mil`；禁止访问 `169.254.169.254`

## 项目结构

```text
reasonix_sentou/
├── AGENTS.md        多 Agent 自动读取的核心作战说明
├── CLAUDE.md        Claude Code 桥接说明
├── README.md
├── bin/             工具快捷命令
├── config/          字典、payload、作战配置、爆破脚本
├── docs/            设计文档、品牌方案
├── memory/          经验记忆库、攻击链、成本记录
├── scripts/         部署、编排、证据闭环、通用化脚本
├── skills/          Agent 技能体系（60+）
├── templates/       多 Agent 配置模板
└── tools/           工具本体（不入库，部署时下载）
```

## 目录分工

```text
results/   原始扫描结果、JSON 中间结果
reports/   最终 HTML / DOCX / PDF 报告
evidence/  证据包、manifest、最小化样本
```

以上目录和敏感文件已写入 `.gitignore`，默认不提交。

## 为什么你可能喜欢它

- **省 token**：技能按需加载 + append-only 上下文，长会话成本可控。
- **可信**：反幻觉证据闭环，结论可复核、可追责。
- **通用**：一份资产服务所有主流 Agent，不用为每个工具重写一遍。
- **成长**：经验越积越多，越用越顺手。

## 贡献

见 [CONTRIBUTING.md](CONTRIBUTING.md)。反馈 bug 请开 [issue](https://github.com/xiabai2008/reasonix-sentou/issues)，安全漏洞走 [SECURITY.md](SECURITY.md) 私有上报。

## 安全声明

本项目**仅用于授权目标**。使用者须确认测试范围，遵守当地法律法规。贡献者不得提交真实目标、凭据或扫描结果等敏感数据。

## License

[MIT](LICENSE)。第三方工具、字典与模板版权归各自原作者，仅供学习研究。