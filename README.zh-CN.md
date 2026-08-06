<div align="center">

# DawnForge · 破晓

**多 Agent 通用的 AI 渗透作战工作台**
**Multi-agent AI Penetration Testing Workbench**

> 在战场上锻造你的黎明 — Forge your dawn on the battlefield.

[![Release](https://img.shields.io/github/v/release/xiabai2008/dawnforge-pentest?include_prereleases&label=Release&color=orange)](https://github.com/xiabai2008/dawnforge-pentest/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/xiabai2008/dawnforge-pentest/actions/workflows/ci.yml/badge.svg)](https://github.com/xiabai2008/dawnforge-pentest/actions)
[![Hits](https://hits.sh/xiabai2008/dawnforge-pentest.svg?label=Visitors&color=263759&labelColor=263759)](https://github.com/xiabai2008/dawnforge-pentest)
[![GitHub stars](https://img.shields.io/github/stars/xiabai2008/dawnforge-pentest.svg?style=social&label=Star)](https://github.com/xiabai2008/dawnforge-pentest)
[![GitHub forks](https://img.shields.io/github/forks/xiabai2008/dawnforge-pentest.svg?style=social&label=Fork)](https://github.com/xiabai2008/dawnforge-pentest)

**证据强制反幻觉 · 多 Agent 通用 · 经验持续成长**

![DawnForge 社交预览图](./.github/social-preview.jpg)

</div>

---

## 这是什么？

`DawnForge` 不是"工具堆"，而是一套**让 AI 稳定参与渗透测试的可成长作战环境**。它把工具、技能、经验、安全边界连成闭环，让 Agent 在长会话中持续理解目标、调用工具、分析结果、沉淀经验。

与普通工具箱最大的不同是三点：

1. **证据强制反幻觉** — 每个结论都带 `EVID` 编号，且在被标记为 `VERIFIED` 前逐字符校验，从结构上阻止 AI 编造 flag / 凭据 / 漏洞告警。
2. **多 Agent 通用** — 一套 persona + 技能库同时服务 **Claude Code / Codex / OpenCode / Cline / Trae**。
3. **经验持续成长** — 记录每场战斗；用得越多，它越懂你的打法（记忆层 + 攻击链 + 成本统计）。

---

## 快速开始

**一键克隆 + 下载工具：**

```powershell
git clone https://github.com/xiabai2008/dawnforge-pentest.git && cd dawnforge-pentest && .\scripts\download-tools.ps1 && .\scripts\setup-new-pc.ps1
```

> 克隆仓库、下载全部工具与字典、并完成环境配置（依赖 + PATH）。

或分步执行：

```bash
git clone https://github.com/xiabai2008/dawnforge-pentest.git
cd dawnforge-pentest
# 首次部署（下载工具/字典、装依赖、建快捷命令）
./scripts/setup-new-pc.ps1
# 健康检查
python scripts/health-check.py
```

然后在你常用的 Agent（Claude Code / Codex / OpenCode…）中打开项目目录，直接描述目标：

```text
扫一下 192.168.1.10                    信息收集 → 端口扫描 → 漏洞检测
测一下 http://example.com              技术栈识别 → 双引擎漏洞扫描
帮我审计这个 JS                         前端代码 / SourceMap / API 审计
这个 JWT 看看有没有越权                JWT 角色体系 / 权限矩阵越权验证
用 AI 分析一下扫描结果                 AI 研判攻击链下一步
```

Agent 会读取 `AGENTS.md` 自动进入渗透专家角色，按规则选工具和技能。

### 接入你的 Agent

```bash
# 链接/复制技能到你 Agent 的约定目录
python scripts/setup-agent-links.py --apply          # 全部
python scripts/setup-agent-links.py --agents claude  # 仅 Claude Code
python scripts/setup-agent-links.py --mode copy      # 用复制代替软链
```

各家 Agent 的配置模板见 `templates/agent-configs/`（opencode/codex/claude 示例）。

### 工具下载

> 工具本体**不入库**（避免仓库臃肿与供应链风险），首次运行自动从各工具官方源下载。

```bash
# 一键下载全部工具与字典
.\scripts\download-tools.ps1
# 强制重新下载
.\scripts\download-tools.ps1 -Force
```

前置条件（Windows）：
- **git** — 克隆类工具与字典库需要（[git-scm.com](https://git-scm.com/downloads)）
- **python** — 可选，用于生成自建字典（[python.org](https://www.python.org/downloads/)）
- **网络** — 需要能访问 GitHub Releases

> **限流提示**：匿名 GitHub API 限流约 60 次/小时，单次下载够用。若遇 `403`，设置 `$env:GITHUB_TOKEN` 指向个人访问令牌后重跑即可。

工具清单见 `config/tools-manifest.json`（每项含来源仓库、资产匹配、目标路径）。编辑它即可定制你的工具链。

#### 工具清单

<!-- TOOL-TABLE:BEGIN -->
| 工具 | 用途 | 来源 |
|:---|:---|:---|
| nuclei | 漏洞扫描（12.5w+ 模板） | [projectdiscovery/nuclei](https://github.com/projectdiscovery/nuclei) |
| naabu | 快速端口扫描 | [projectdiscovery/naabu](https://github.com/projectdiscovery/naabu) |
| httpx | Web 探活 / 技术栈指纹 | [projectdiscovery/httpx](https://github.com/projectdiscovery/httpx) |
| subfinder | 子域名被动枚举 | [projectdiscovery/subfinder](https://github.com/projectdiscovery/subfinder) |
| katana | 爬虫 | [projectdiscovery/katana](https://github.com/projectdiscovery/katana) |
| dnsx | DNS 工具包 | [projectdiscovery/dnsx](https://github.com/projectdiscovery/dnsx) |
| tlsx | TLS 证书信息 | [projectdiscovery/tlsx](https://github.com/projectdiscovery/tlsx) |
| fscan | 内网扫描（端口+爆破+POC） | [shadow1ng/fscan](https://github.com/shadow1ng/fscan) |
| ffuf | 目录与参数模糊测试 | [ffuf/ffuf](https://github.com/ffuf/ffuf) |
| gau | URL 收集 | [lc/gau](https://github.com/lc/gau) |
| jq | JSON 处理 | [jqlang/jq](https://github.com/jqlang/jq) |
| dalfox | XSS 专项扫描 | [hahwul/dalfox](https://github.com/hahwul/dalfox) |
| PEASS-ng | 提权辅助 | [carlospolop/PEASS-ng](https://github.com/carlospolop/PEASS-ng) |
| SSTImap | SSTI 检测利用 | [vladko312/SSTImap](https://github.com/vladko312/SSTImap) |
| SpiderX | 前端 JS 加密绕过 | [LiChaser/SpiderX](https://github.com/LiChaser/SpiderX) |
| MemShellParty | Java 内存马注入 | [ReaJason/MemShellParty](https://github.com/ReaJason/MemShellParty) |
| JYso | JNDI 注入 + 反序列化 | [qi4L/JYso](https://github.com/qi4L/JYso) |
| poxiao | SRC 挖洞工具链（257 CVE） | [xiabai2008/poxiao](https://github.com/xiabai2008/poxiao) |
| rayscan | Web 全栈漏洞扫描（8种SQLi/XSS/OA） | [xiabai2008/rayscan](https://github.com/xiabai2008/rayscan) |
| ruoyi-scan | 若依框架专项扫描 | [xiabai2008/ruoyi-scan](https://github.com/xiabai2008/ruoyi-scan) |
<!-- TOOL-TABLE:END -->

> 字典库：`SecLists` · `SuperWordlist` · `Dict` · `SaiDict` · `S-BlastingDictionary` — 按需克隆到 `config/dictionaries/`。

---

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

### 技能库（60+）

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

> **经验是个人私有的** — 个人经验文件已被 `.gitignore` 忽略，永不提交。每位使用者从仓库的 `memory/templates/` 骨架出发，建立属于自己的经验库。

### 本地靶场

`targets/` 提供一键启动的本地训练环境（DVWA / Juice Shop / WebGoat / VAmPI），覆盖 PHP / Node.js / Java / Python 四大技术栈，并附 8 周训练路线。

### 安全边界

- 默认 `permissions.mode = "ask"`，高危操作人工确认
- `config/scope.yaml` 授权白名单校验
- 三档作战模式：`safe / normal / aggressive`
- 禁止 `.gov` / `.mil`；禁止访问云元数据地址（`169.254.169.254`）
- 发现 DawnForge 自身漏洞？请走 [SECURITY.md](SECURITY.md) 私有上报

---

## 项目结构

```text
dawnforge-pentest/
├── AGENTS.md        核心作战说明（多 Agent 自动读取）
├── CLAUDE.md        Claude Code 桥接说明
├── README.md
├── bin/             工具快捷命令
├── config/          字典、payload、作战配置、爆破脚本
├── docs/            设计文档、品牌方案
├── memory/          经验记忆库、攻击链、成本记录（个人私有，不入库）
├── scripts/         部署、编排、证据闭环、通用化脚本
├── skills/          Agent 技能体系（60+）
├── targets/         本地靶场一键编排
├── templates/       多 Agent 配置模板
└── tools/           工具本体（不入库，部署时下载）
```

### 目录分工

```text
results/   原始扫描结果、JSON 中间结果
reports/   最终 HTML / DOCX / PDF 报告
evidence/  证据包、manifest、最小化样本
```

以上目录和敏感文件已写入 `.gitignore`，默认不提交。

---

## 为什么你可能喜欢它

- **省 token**：技能按需加载 + append-only 上下文，长会话成本可控。
- **可信**：反幻觉证据闭环，结论可复核、可追责。
- **通用**：一套资产服务所有主流 Agent，无需逐工具改写。
- **成长**：经验持续积累；用得越多，效果越好。

---

## 贡献

社区规范：[CODE_OF_CONDUCT](CODE_OF_CONDUCT.md) · [CONTRIBUTING](CONTRIBUTING.md) · [CHANGELOG](CHANGELOG.md) · [AUTHORS](AUTHORS.md)

见 [CONTRIBUTING.md](CONTRIBUTING.md)。反馈 bug 请开 [issue](https://github.com/xiabai2008/dawnforge-pentest/issues)，安全漏洞走 [SECURITY.md](SECURITY.md) 私有上报。

---

## 点亮 Star

如果 DawnForge 帮到了你，点个 Star 是最好的感谢，也能帮助更多人发现它。

[![Star History Chart](https://api.star-history.com/svg?repos=xiabai2008/dawnforge-pentest&type=Date)](https://star-history.com/#xiabai2008/dawnforge-pentest&Date)

### 支持

- ⭐ 点亮 Star
- 🍴 分叉并提交 PR
- 🐛 提交 issue：[issues](https://github.com/xiabai2008/dawnforge-pentest/issues)
- 🔒 安全漏洞私有上报：[SECURITY.md](SECURITY.md)
- 💬 分享给做授权渗透的同行

---

## 安全声明

本项目**仅用于授权目标**。使用者须确认测试范围，遵守当地法律法规。贡献者不得提交真实目标、凭据或扫描结果等敏感数据。

## License

[MIT](LICENSE)。第三方工具、字典与模板版权归各自原作者，仅供学习研究。