<div align="center">

# DawnForge · 破晓

**Multi-agent AI Penetration Testing Workbench**
**多 Agent 通用的 AI 渗透作战工作台**

> Forge your dawn on the battlefield. — 在战场上锻造你的黎明

`English` · [**中文**](README.zh-CN.md)

[![Release](https://img.shields.io/github/v/release/xiabai2008/dawnforge-pentest?include_prereleases&label=Release&color=orange)](https://github.com/xiabai2008/dawnforge-pentest/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/xiabai2008/dawnforge-pentest/actions/workflows/ci.yml/badge.svg)](https://github.com/xiabai2008/dawnforge-pentest/actions)
[![Hits](https://hits.sh/xiabai2008/dawnforge-pentest.svg?label=Visitors&color=263759&labelColor=263759)](https://hits.sh/xiabai2008/dawnforge-pentest/)
[![GitHub stars](https://img.shields.io/github/stars/xiabai2008/dawnforge-pentest.svg?style=social&label=Star)](https://github.com/xiabai2008/dawnforge-pentest)
[![GitHub forks](https://img.shields.io/github/forks/xiabai2008/dawnforge-pentest.svg?style=social&label=Fork)](https://github.com/xiabai2008/dawnforge-pentest)

**Evidence-enforced anti-hallucination · Agent-agnostic · Continuously growing memory**
**证据强制反幻觉 · 多 Agent 通用 · 经验持续成长**

![DawnForge social preview](./.github/social-preview.jpg)

</div>

---

## What is it? / 它是做什么的？

`DawnForge` is not a "pile of tools" — it is a **growable AI-powered penetration testing environment**. It links tools, skills, experience, and security boundaries into a closed loop, letting an AI agent continuously understand targets, invoke tools, analyze results, and accumulate experience across long sessions.

`DawnForge` 不是一个"工具堆"，而是一套**让 AI 稳定参与渗透测试的可成长作战环境**。它把工具、技能、经验、安全边界连成闭环，让 Agent 在长会话中持续理解目标、调用工具、分析结果、沉淀经验。

Three things set it apart / 与普通工具箱最大的不同是三点：

1. **Evidence-enforced anti-hallucination / 证据强制反幻觉** — Every conclusion carries an `EVID` number and is verified character-by-character before being marked `VERIFIED`, structurally preventing AI from fabricating flags / credentials / vulnerability alerts.
2. **Agent-agnostic / 多 Agent 通用** — One persona + skill library serves **Claude Code / Codex / OpenCode / Cline / Trae**.
3. **Continuously growing memory / 经验持续成长** — Record every battle; the more you use it, the more it understands your playbook (memory layer + attack chains + cost stats).

---

## Quick Start / 快速开始

**One-command clone + setup / 一键克隆 + 下载工具：**

```powershell
git clone https://github.com/xiabai2008/dawnforge-pentest.git && cd dawnforge-pentest && .\scripts\download-tools.ps1 && .\scripts\setup-new-pc.ps1
```

> Clones the repo, downloads all tools & dictionaries, then configures the environment (deps + PATH). — 克隆仓库、下载全部工具与字典、并完成环境配置（依赖 + PATH）。

Or step by step / 或分步执行：

```bash
git clone https://github.com/xiabai2008/dawnforge-pentest.git
cd dawnforge-pentest
# First-time setup (download tools/dicts, install deps, create shortcuts)
# 首次部署（下载工具/字典、装依赖、建快捷命令）
./scripts/setup-new-pc.ps1
# Health check / 健康检查
python scripts/health-check.py
```

Then open the project directory in your preferred agent (Claude Code / Codex / OpenCode…) and describe your target directly:

然后在你常用的 Agent（Claude Code / Codex / OpenCode…）中打开项目目录，直接描述目标：

```text
扫一下 192.168.1.10                    Scan this IP
测一下 http://example.com              Test this website
帮我审计这个 JS                         Audit this JS
这个 JWT 看看有没有越权                Check this JWT for privilege escalation
用 AI 分析一下扫描结果                 Analyze scan results with AI
```

The agent reads `AGENTS.md` and automatically enters the pentest-expert persona, choosing tools and skills by the rules.

Agent 会读取 `AGENTS.md` 自动进入渗透专家角色，按规则选工具和技能。

### Connect your agent / 接入你的 Agent

```bash
# Link/copy skills to your agent's convention directory
python scripts/setup-agent-links.py --apply          # all / 全部
python scripts/setup-agent-links.py --agents claude  # Claude Code only / 仅 Claude Code
python scripts/setup-agent-links.py --mode copy      # copy instead of symlink / 用复制代替软链
```

Per-agent config templates live in `templates/agent-configs/` (opencode/codex/claude examples).

各家 Agent 的配置模板见 `templates/agent-configs/`（opencode/codex/claude 示例）。

### Download the tools / 工具下载

> **⚠️ First step / 第一步必读**：Tool binaries are **not** bundled in the repo. After cloning, run `download-tools.ps1` **before** using any `bin/` command (`fscan`, `nuclei`, `poxiao`…), otherwise they will fail with "not found". — 工具本体**不入库**。克隆后请**先**运行 `download-tools.ps1`，再使用 `bin/` 下的任何命令（`fscan`、`nuclei`、`poxiao`…），否则会提示找不到工具。

> **🪟 Platform / 平台**：Windows + PowerShell is the primary target, with optional WSL Kali for nmap/hydra. The tool downloader is `.ps1`; skills, scripts, and evidence loop are cross-platform. — 以 **Windows + PowerShell** 为主，可选 WSL Kali 提供 nmap/hydra。工具下载脚本为 `.ps1`；技能库、脚本和证据闭环跨平台可用。

```bash
# One-command download of all tools + dictionaries / 一键下载全部工具与字典
.\scripts\download-tools.ps1
# Force re-download / 强制重新下载
.\scripts\download-tools.ps1 -Force
```

Requirements (Windows) / 前置条件（Windows）：
- **git** — for cloned tools & dictionaries ([git-scm.com](https://git-scm.com/downloads))
- **python** — optional, for bundled dictionary generation ([python.org](https://www.python.org/downloads/))
- **Network** access to GitHub Releases — 需要能访问 GitHub Releases

> **Rate-limit tip / 限流提示**：Anonymous GitHub API is limited to ~60 req/h, enough for a single download. If you hit a `403`, set `$env:GITHUB_TOKEN` to a [personal access token](https://github.com/settings/tokens) and re-run. — 匿名 GitHub API 限流约 60 次/小时，单次下载够用。若遇 `403`，设置 `$env:GITHUB_TOKEN` 指向个人访问令牌后重跑即可。

The tool list lives in `config/tools-manifest.json` (each entry: source repo + asset pattern + target path). Edit it to customize your toolchain.

工具清单见 `config/tools-manifest.json`（每项含来源仓库、资产匹配、目标路径）。编辑它即可定制你的工具链。

#### Tool manifest / 工具清单

<!-- TOOL-TABLE:BEGIN -->
| Tool / 工具 | Role / 用途 | Source / 来源 |
|:---|:---|:---|
| nuclei | Vulnerability scan (125k+ templates) / 漏洞扫描 | [projectdiscovery/nuclei](https://github.com/projectdiscovery/nuclei) |
| naabu | Fast port scan / 快速端口扫描 | [projectdiscovery/naabu](https://github.com/projectdiscovery/naabu) |
| httpx | HTTP probing / tech-stack fingerprint / Web 探活 | [projectdiscovery/httpx](https://github.com/projectdiscovery/httpx) |
| subfinder | Passive subdomain enumeration / 子域名被动枚举 | [projectdiscovery/subfinder](https://github.com/projectdiscovery/subfinder) |
| katana | Crawler / 爬虫 | [projectdiscovery/katana](https://github.com/projectdiscovery/katana) |
| dnsx | DNS toolkit / DNS 工具包 | [projectdiscovery/dnsx](https://github.com/projectdiscovery/dnsx) |
| tlsx | TLS certificate fetch / TLS 证书 | [projectdiscovery/tlsx](https://github.com/projectdiscovery/tlsx) |
| fscan | Intranet port scan + brute-force + POC / 内网扫描 | [shadow1ng/fscan](https://github.com/shadow1ng/fscan) |
| ffuf | Web fuzzer / 目录与参数模糊测试 | [ffuf/ffuf](https://github.com/ffuf/ffuf) |
| gau | URL collection / URL 收集 | [lc/gau](https://github.com/lc/gau) |
| jq | JSON processing / JSON 处理 | [jqlang/jq](https://github.com/jqlang/jq) |
| dalfox | XSS scanner / XSS 专项扫描 | [hahwul/dalfox](https://github.com/hahwul/dalfox) |
| PEASS-ng | Priv-esc assist / 提权辅助 | [carlospolop/PEASS-ng](https://github.com/carlospolop/PEASS-ng) |
| SSTImap | SSTI detect & exploit / SSTI 检测利用 | [vladko312/SSTImap](https://github.com/vladko312/SSTImap) |
| SpiderX | Frontend JS anti-encryption bypass / 前端加密绕过 | [LiChaser/SpiderX](https://github.com/LiChaser/SpiderX) |
| MemShellParty | Java memory-shell injection / Java 内存马注入 | [ReaJason/MemShellParty](https://github.com/ReaJason/MemShellParty) |
| JYso | JNDI + deserialization / JNDI 反序列化 | [qi4L/JYso](https://github.com/qi4L/JYso) |
| poxiao | SRC hunting toolchain (257 CVE) / SRC 挖洞工具链 | [xiabai2008/poxiao](https://github.com/xiabai2008/poxiao) |
| rayscan | Web vuln scanner (SQLi/XSS/OA) / Web 全栈漏洞扫描 | [xiabai2008/rayscan](https://github.com/xiabai2008/rayscan) |
| ruoyi-scan | RuoYi-framework scanner / 若依框架专项扫描 | [xiabai2008/ruoyi-scan](https://github.com/xiabai2008/ruoyi-scan) |
<!-- TOOL-TABLE:END -->

> Dictionaries / 字典库：`SecLists` · `SuperWordlist` · `Dict` · `SaiDict` · `S-BlastingDictionary` — cloned on demand into `config/dictionaries/`（按需克隆到 `config/dictionaries/`）。

---

## Core Capabilities / 核心能力

### Toolchain / 工具链

Port scanning, web assessment, directory brute-force, crawling, subdomain, SQL injection, XSS, SSTI, deserialization, lateral movement, privilege escalation… Tool binaries live in `tools/`, unified entry points in `bin/`.

端口扫描、Web 评估、目录爆破、爬虫、子域名、SQL 注入、XSS、SSTI、反序列化、内网横向、提权……工具本体放 `tools/`，`bin/` 提供统一快捷入口。

> **20 tools are downloadable via `download-tools.ps1`** (see manifest above) + 74 Agent skills. Tool binaries are **not** bundled in the repo — run the one-command download first.
> **20 个工具可通过 `download-tools.ps1` 一键下载**（见上方清单）+ 74 个 Agent 技能。工具本体**不入库**，请先运行一键下载。

| 场景 Scenario | 首选 Preferred | 备选 Alt |
|:-----|:-----|:-----|
| 快速端口扫描 Fast port scan | naabu | fscan（含服务识别）|
| 内网全扫描 Internal full scan | fscan | — |
| Web 漏洞检测 Web vuln detection | nuclei | xray（被动更安静）|
| 目录爆破 Directory fuzz | ffuf | gobuster |
| SRC 挖洞 SRC hunting | poxiao | rayscan |
| 深度 SQLi/XSS | rayscan | — |
| SQL 注入 | sqlmap | — |
| XSS 专项 | dalfox | nuclei |
| 提权辅助 Priv-esc assist | PEASS-ng | — |

### Skill Library (74) / 技能库

`skills/pentest_skills/<name>/SKILL.md`, standard YAML frontmatter, compatible with the Anthropic Agent Skills format. Covers SQLi, XSS, SSRF, IDOR, JWT, deserialization, WAF bypass, subdomain takeover, and all mainstream vulnerability classes.

`skills/pentest_skills/<name>/SKILL.md`，带标准 YAML frontmatter，兼容 Anthropic Agent Skills 格式，覆盖 SQLi、XSS、SSRF、IDOR、JWT、反序列化、WAF 绕过、子域名接管等全部主流漏洞方向。

### Evidence Loop (anti-hallucination core) / 证据闭环（反幻觉铁律）

```
harvest → archive → report
tool output → extract claims → assign EVID + verify char-by-char → archive to memory → generate auditable report
工具输出 → 提取结论 → 分配EVID+逐字符校验 → 沉淀记忆 → 生成可复核报告
```

```bash
python -m scripts.evidence_pack.cli harvest \
  --tag T01 --target $TARGET --claim "SQL 注入存在于 /api/login"
python -m scripts.evidence_pack.cli archive evidence/manifest_T01.json
python -m scripts.evidence_pack.cli report evidence/manifest_T01.json --format md
```

### Experience System / 经验系统

Each task writes `memory/pentest-experience-NNN.md`; reusable attack chains go to `memory/attack-chains.yaml`; cost data to `memory/cost-stats.csv`. Experience feeds back into the next decision.

每次任务结束写入 `memory/pentest-experience-NNN.md`，可复用攻击链记入 `memory/attack-chains.yaml`，成本数据记入 `memory/cost-stats.csv`。经验会反过来影响下一次判断。

> **Your experience is private / 经验是个人私有的** — Personal experience files are `.gitignore`d and never committed. Every user starts from the shared `memory/templates/` skeleton and builds their own experience library.
> 个人经验文件已被 `.gitignore` 忽略，永不提交。每位使用者从仓库的 `memory/templates/` 骨架出发，建立属于自己的经验库。

### Training Ranges (local, Docker) / 本地靶场

`targets/` provides a one-command local training environment (DVWA / Juice Shop / WebGoat / VAmPI) covering PHP / Node.js / Java / Python, with an 8-week learning path.

`targets/` 提供一键启动的本地训练环境（DVWA / Juice Shop / WebGoat / VAmPI），覆盖 PHP / Node.js / Java / Python 四大技术栈，并附 8 周训练路线。

### Security Boundaries / 安全边界

- Default `permissions.mode = "ask"`, high-risk operations require human confirmation — 默认 `permissions.mode = "ask"`，高危操作人工确认
- `config/scope.yaml` authorization whitelist check — 授权白名单校验
- Three combat modes: `safe / normal / aggressive` — 三档作战模式
- `.gov` / `.mil` blocked; `169.254.169.254` cloud metadata blocked — 禁止 `.gov` / `.mil`；禁止访问云元数据地址
- Found a vulnerability in DawnForge itself? Report privately via [SECURITY.md](SECURITY.md) — 发现 DawnForge 自身漏洞？请走 [SECURITY.md](SECURITY.md) 私有上报

---

## Project Structure / 项目结构

```text
dawnforge-pentest/
├── AGENTS.md        核心作战说明（多 Agent 自动读取）
├── CLAUDE.md        Claude Code 桥接说明
├── README.md
├── bin/             工具快捷命令
├── config/          字典、payload、作战配置、爆破脚本
├── docs/            设计文档、品牌方案
├── memory/          经验记忆库、攻击链、成本记录
├── scripts/         部署、编排、证据闭环、通用化脚本
├── skills/          Agent 技能体系（74）
├── targets/         本地靶场一键编排
├── templates/       多 Agent 配置模板
└── tools/           工具本体（不入库，部署时下载）
```

## Directory Duties / 目录分工

```text
results/   raw scan output, JSON intermediates / 原始扫描结果、JSON 中间结果
reports/   final HTML / DOCX / PDF reports / 最终报告
evidence/  evidence packs, manifests, minimal samples / 证据包、manifest、最小化样本
```

These directories and sensitive files are written to `.gitignore` and are not committed by default.

以上目录和敏感文件已写入 `.gitignore`，默认不提交。

---

## Why You Might Like It / 为什么你可能喜欢它

- **Token-efficient / 省 token**: skills loaded on demand + append-only context, controllable long-session cost.
- **Trustworthy / 可信**: anti-hallucination evidence loop — conclusions are auditable and attributable.
- **Universally compatible / 通用**: one asset serves all mainstream agents, no rewriting per tool.
- **Growing / 成长**: experience accumulates; the more you use it, the better it works.

## Contributing / 贡献

Community guidelines: [CODE_OF_CONDUCT](CODE_OF_CONDUCT.md) · [CONTRIBUTING](CONTRIBUTING.md) · [CHANGELOG](CHANGELOG.md) · [AUTHORS](AUTHORS.md)

社区规范：[CODE_OF_CONDUCT](CODE_OF_CONDUCT.md) · [CONTRIBUTING](CONTRIBUTING.md) · [CHANGELOG](CHANGELOG.md) · [AUTHORS](AUTHORS.md)

See [CONTRIBUTING.md](CONTRIBUTING.md). Report bugs via [issues](https://github.com/xiabai2008/dawnforge-pentest/issues), and report security vulnerabilities privately via [SECURITY.md](SECURITY.md).

见 [CONTRIBUTING.md](CONTRIBUTING.md)。反馈 bug 请开 [issue](https://github.com/xiabai2008/dawnforge-pentest/issues)，安全漏洞走 [SECURITY.md](SECURITY.md) 私有上报。

## Responsible Use / 安全声明

**For authorized targets only.** Users must confirm the test scope and comply with local laws and regulations. Contributors must not submit real targets, credentials, or scan results.

本项目**仅用于授权目标**。使用者须确认测试范围，遵守当地法律法规。贡献者不得提交真实目标、凭据或扫描结果等敏感数据。

## License

[MIT](LICENSE). Third-party tools, dictionaries, and templates retain their respective copyrights and are provided for learning and research only.

[MIT](LICENSE)。第三方工具、字典与模板版权归各自原作者，仅供学习研究。

---

## Star History / 点亮 Star

If DawnForge helps you, a star is the best way to say thanks and helps others discover it.

如果 DawnForge 帮到了你，点个 Star 是最好的感谢，也能帮助更多人发现它。

[![Star History Chart](https://api.star-history.com/svg?repos=xiabai2008/dawnforge-pentest&type=Date)](https://star-history.com/#xiabai2008/dawnforge-pentest&Date)

### Support / 支持

- ⭐ Star the repo — 点亮 Star
- 🍴 Fork & PR — 分叉并提交 PR
- 🐛 Report issues — 提交 issue：[issues](https://github.com/xiabai2008/dawnforge-pentest/issues)
- 🔒 Report vulnerabilities privately — 安全漏洞私有上报：[SECURITY.md](SECURITY.md)
- 💬 Share with peers who do authorized pentesting — 分享给做授权渗透的同行