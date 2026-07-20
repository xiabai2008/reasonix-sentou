---
name: reasonix-pentest
description: 全能 Web 渗透测试助手 - Reasonix 驱动的 AI 渗透作战工作台，提供端口扫描、Web漏洞检测、弱口令爆破等能力
---

# Reasonix 渗透作战工作台

代号"破晓" — 基于 Reasonix (DeepSeek) 的 AI 渗透副驾驶，集成 50+ 安全工具、52 个漏洞专项技能、272 个字典库。

## 启动

```bash
cd C:\Tools\reasonix_sentou
reasonix          # 自动加载 AGENTS.md（破晓 persona）
```

Reasonix 启动后即进入"破晓"模式，可直接描述目标（IP/URL/域名），AI 自动分析并调度工具。

## 可用技能

| 命令 | 说明 |
|------|------|
| `/pentest-master` | 总指挥，智能调度所有资源 |
| `/port-scan` | 端口扫描与资产探测 |
| `/web-poc` | Web 漏洞检测与 POC 扫描 |
| `/bruteforce` | 弱口令爆破（含验证码 OCR） |
| `/intel-gather` | 信息收集 |
| `/vuln-hunter` | 52 个漏洞方向入口 |
| `/report-gen` | 报告生成 |

## 核心工具（70+，位于 tools/ + WSL）

| 类别 | 工具 |
|:-----|:-----|
| 端口扫描 | naabu, fscan, nmap(Kali WSL), masscan(Kali WSL) |
| Web 评估 | nuclei(12.5w模板), xray, httpx, afrog, pocsuite3 |
| 目录爆破 | ffuf, gobuster, feroxbuster, dirsearch |
| URL/爬虫 | katana, gau, arjun |
| 子域名 | subfinder, dnsx, tlsx, ksubdomain, oneforall |
| SQL 注入 | sqlmap, rayscan |
| 内网横向 | impacket(psexec/wmiexec/secretsdump), fscan |
| 爆破 | hydra(Kali WSL), john(Kali WSL), brute.py(自研含OCR) |
| 代理调式 | mitmproxy/mitmweb, proxychains4(Kali WSL) |
| 指纹识别 | EHole, httpx |
| WebShell | antsword(蚁剑), behinder(冰蝎), godzilla(哥斯拉) |
| 自研 | poxiao(SRC挖洞), rayscan(SQLi/XSS深度) |
| 其他 | jq(JSON), hashid, stegoveritas, ysoserial, JNDI-Injection-Exploit |

## 字典库（272 个 / ~190MB）

位于 `config/` 和 `config/dictionaries/`，覆盖：通用弱口令、中文特色、CTF、CMS 默认密码、Fuzz 路径、SQLi payload、子域名、设备默认口令。

快捷调用：
```bash
python config/brute.py <url> -u admin -d config/elite-passwords.txt
python config/brute.py <url> --auto-form --captcha   # 含验证码 OCR
```

## 目录结构

```
reasonix_sentou/
├── skills/            # AI 技能（52 个漏洞专项 + 6 个主技能 + 参考数据）
├── tools/             # 50+ 安全工具
├── bin/               # 快捷命令（已加入 PATH）
├── config/            # 字典、配置文件、brute.py
├── scripts/           # 部署/迁移脚本
├── reports/           # 渗透报告输出
├── AGENTS.md          # 破晓 persona + 全量方法论
├── reasonix.toml      # Reasonix 项目配置
└── README.md          # 本说明
```

## 系统要求

- **OS:** Windows 10/11
- **Reasonix:** v1.17+（`npm i -g reasonix`）
- **DeepSeek API Key:** 需设环境变量 `DEEPSEEK_API_KEY`
- **WSL:** Kali Linux（重型工具），可选但推荐
- **Python:** 3.10+（`ddddocr`、`requests`）

## 新环境部署

```bash
# 1. 克隆仓库（工具二进制和字典库不在 git 中）
git clone git@github.com:xiabai2004/reasonix-sentou.git
cd reasonix_sentou

# 2. 自动下载恢复所有工具和字典
.\scripts\download-tools.ps1

# 3. 一键环境配置（PATH + Python 依赖 + WSL Kali）
.\scripts\setup-new-pc.ps1
```

> `setup-new-pc.ps1` 会自动检测：如果工具未下载，先调用 `download-tools.ps1`。因此也可以只跑第 3 步，它会自动补第 2 步。

## 注意事项

- ⚠️ 仅用于授权环境下的渗透测试
- 遵守相关法律法规
- 扫描前确保已获得目标授权
- 每次渗透结束后记录 `/stats`（token 消耗 + 缓存命中率）到经验记忆
