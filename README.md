# Reasonix 渗透作战工作台

`reasonix_sentou` 是一个专门为 Reasonix 准备的本地渗透测试工作环境。它不是简单的工具集合，而是围绕 Reasonix 自动加载、DeepSeek prefix-cache、渗透技能编排、工具调用、经验积累和安全边界设计的一套 AI 辅助作战台。

项目代号为“破晓”。在本目录下启动 Reasonix 后，Reasonix 会自动读取 `AGENTS.md`，进入渗透测试专家角色，并根据用户输入的 IP、URL、域名、端口、代码文件或扫描结果选择对应工具链和技能路径。

## 核心定位

这个项目解决的是“AI 如何稳定参与渗透测试”的问题。传统工具箱只提供命令和字典，本项目额外提供 Reasonix 可读取的上下文、技能、流程、经验和安全约束，让 AI 在长会话中持续理解目标、调用工具、分析结果、沉淀经验。

项目适合以下场景：

- 授权 Web 渗透测试
- CTF / 靶场 / 考试环境
- SRC 信息收集与漏洞验证
- 前端代码审计与接口分析
- JWT / API 越权分析
- 内网资产探测与弱口令验证
- 扫描结果整理和报告生成
- 渗透经验长期积累

## 工作方式

在项目目录下启动 Reasonix：

```powershell
cd C:\Tools\reasonix_sentou
reasonix
```

启动后会自动加载：

```text
AGENTS.md       破晓 persona、工具路线、技能路由、安全规则
reasonix.toml   Reasonix 配置、缓存策略、权限策略
skills/         主技能、漏洞专项技能、参考知识
bin/            工具快捷入口
config/         字典、payload、爆破脚本、工具清单
```

用户可以直接描述目标，例如：

```text
扫一下 192.168.1.10
测一下 http://example.com
帮我审计这个 JS
这个 JWT 看看有没有越权
用 AI 分析一下扫描结果，告诉我下一步
```

Reasonix 会根据 `AGENTS.md` 中的规则选择工具和技能，而不是每次从零判断。

## 项目结构

```text
reasonix_sentou/
├── AGENTS.md                    Reasonix 自动加载的核心作战说明
├── reasonix.toml                Reasonix 项目配置
├── README.md                    项目总览
├── bin/                         工具快捷命令
├── config/                      字典、payload、爆破脚本、工具清单
├── docs/                        设计文档和实验记录
├── memory/                      经验记忆库、攻击链和成本记录
├── scripts/                     部署、迁移、工具恢复和编排脚本
├── skills/                      Reasonix 技能体系
├── tools/                       渗透工具本体
├── ctf_exam_web01/              靶场和 CTF 案例数据
└── tmp/                         临时脚本和历史中间文件
```

输出目录约定：

```text
results/   原始扫描结果、AI prompt、JSON 中间结果
reports/   最终 HTML / DOCX / PDF 报告
evidence/  漏洞截图、HTTP 响应、PoC 证据、最小化敏感样本
```

这些目录和常见敏感文件类型已经写入 `.gitignore`，默认不提交到 Git。

## Reasonix 配置

`reasonix.toml` 是项目的 Reasonix 配置入口：

```toml
[agent]
system_prompt_file = "AGENTS.md"
cold_resume_prune = true
soft_compact_ratio = 0.5
tool_result_snip_ratio = 0.6
compact_ratio = 0.8
compact_force_ratio = 0.9
planner_model = "deepseek-pro"
auto_plan = "off"

[permissions]
mode = "ask"
```

这些配置针对渗透测试长会话做了优化。扫描和工具输出通常很长，`tool_result_snip_ratio` 用来控制旧工具结果占用；`soft_compact_ratio` 尽量保留稳定前缀，配合 DeepSeek prefix-cache 降低成本；`auto_plan = "off"` 和 `permissions.mode = "ask"` 用于避免 AI 未经确认执行高风险操作。

## AGENTS.md

`AGENTS.md` 是这个项目的核心。Reasonix 启动后会读取它，获得“破晓”的身份、工具使用规则、技能路由、常见任务处理方式和安全约束。

它包含：

- 身份设定：Reasonix 渗透测试专家，代号“破晓”
- 核心原则：先分析后行动、由浅入深、多工具互补、结果导向、安全合规
- 工具总览：端口扫描、Web 评估、HTTP 探活、目录爆破、爬虫、子域名、SQL 注入、内网横向等
- 技能总览：主技能、漏洞专项技能、AI 辅助技能
- 常见任务速查：IP、网站、信息收集、内网横向、批量扫描、验证码登录、CMS 模板 RCE 等
- 字典库说明：弱口令、用户名、路径、设备默认口令、Fuzz payload
- 工具抉择速查：不同场景下优先使用的工具
- WSL 环境说明：Kali Linux、nmap、hydra、gobuster 等
- 经验积累系统：每次任务后记录成功方法、失败踩坑、成本和攻击链
- 安全沙箱规范：高危操作隔离、授权检查、不可行操作清单

## 工具体系

工具本体位于 `tools/`，快捷入口位于 `bin/`。`bin/` 适合作为 Reasonix 调用层，隐藏工具真实路径和平台差异。

| 场景 | 首选工具 | 说明 |
|:-----|:---------|:-----|
| 快速端口扫描 | `naabu` | 快速发现开放端口 |
| 内网综合扫描 | `fscan` | 存活、端口、服务、弱口令、POC 一体化 |
| Web 指纹识别 | `httpx` | 状态码、标题、技术栈 |
| Web 漏洞检测 | `nuclei` | 模板覆盖面广，适合批量验证 |
| 被动 Web 评估 | `xray` | 适合代理流量分析 |
| 目录爆破 | `ffuf` | 速度快，参数灵活 |
| URL 收集 | `gau`、`katana` | 被动历史 URL 和主动爬虫互补 |
| 子域名收集 | `subfinder`、`oneforall` | 快速收集和综合收集搭配 |
| SQL 注入 | `sqlmap`、`rayscan` | 自动化检测和深度验证 |
| XSS 专项 | `dalfox` | 参数分析和 DOM XSS 检测 |
| SSTI 专项 | `SSTImap` | 模板引擎识别和验证 |
| JS 逆向 | `SpiderX` | 前端加密逻辑分析 |
| Java 反序列化 | `JYso`、`ysoserial` | JNDI、反序列化、回显、内存马 |
| 提权辅助 | `PEASS-ng` | Linux/Windows 提权枚举 |
| 内网横向 | `impacket` | psexec、wmiexec、secretsdump |
| WSL 工具 | `nmap`、`masscan`、`hydra`、`john` | Kali Linux 环境调用 |

## 技能体系

`skills/` 是给 Reasonix 读取的知识和流程层。它不是普通文档，而是 AI 调度工具和判断路线时使用的“技能库”。

主技能包括：

| 技能 | 作用 |
|:-----|:-----|
| `pentest-master` | 总指挥，根据目标类型选择路线 |
| `port-scan` | 端口扫描和服务识别 |
| `web-poc` | Web 漏洞检测和 POC 验证 |
| `bruteforce` | 弱口令爆破和验证码场景 |
| `intel-gather` | 域名、子域名、URL、证书信息收集 |
| `vuln-hunter` | 漏洞专项技能索引 |
| `report-gen` | 报告生成 |

漏洞专项覆盖：

- SQL 注入
- XSS
- SSRF
- IDOR / BOLA
- 命令注入
- CSRF
- JWT / OAuth
- GraphQL
- CORS
- 文件访问
- XXE
- 请求走私
- 原型链污染
- WebSocket
- 反序列化
- WAF 绕过
- 业务逻辑漏洞
- 子域名接管
- SSTI
- JNDI

## AI 辅助渗透能力

项目新增了专门面向 Reasonix 的 AI 辅助技能。

### 前端代码审计

技能路径：

```text
skills/pentest_skills/ai-assisted-code-audit/SKILL.md
```

触发场景：

```text
审计前端代码
看一下 JS
解包 Webpack
分析 SourceMap
找接口
看前端有没有泄露
```

审计重点：

- JWT 角色体系
- API 端点
- 硬编码密钥
- 前端权限控制
- DOM XSS
- SourceMap 泄露
- localStorage / sessionStorage / Cookie 使用
- 业务逻辑暴露

### JWT 权限提升

技能路径：

```text
skills/pentest_skills/jwt-privilege-escalation/SKILL.md
```

触发场景：

```text
JWT
Authorization Bearer
role
isAdmin
permissions
scope
orgId
userId
```

分析重点：

- JWT header / payload 解码
- `role=0/1/2` 角色层级
- `userId`、`orgId`、`tenantId` 横向越权
- `permissions`、`scope`、`isAdmin` 权限判断
- 低权限 Token 访问高权限接口
- 前端权限矩阵和后端验证差异

### AI 扫描结果研判

脚本路径：

```text
scripts/ai-pentest-orchestrator.py
```

用途：

- 对 URL / IP / 域名执行基础信息收集
- 运行轻量漏洞扫描
- 整理结果为结构化 Markdown
- 生成适合贴回 Reasonix 的 AI 分析提示词

示例：

```powershell
python scripts/ai-pentest-orchestrator.py --target http://example.com
python scripts/ai-pentest-orchestrator.py --target 192.168.1.10 --type ip
```

脚本不会直接执行高危利用，主要用于“工具扫描 + AI 研判”的衔接。

## 字典和爆破

`config/` 提供多套常用字典：

| 字典 | 场景 |
|:-----|:-----|
| `top100-passwords.txt` | 快速试探 |
| `admin-top500.txt` | admin 账号常用密码 |
| `elite-passwords.txt` | 精华弱口令合集 |
| `mega-passwords.txt` | 大规模弱口令尝试 |
| `users-common.txt` | 常见用户名 |
| `ctf-passwords.txt` | CTF / 考试场景 |
| `cn-passwords.txt` | 中文环境弱口令 |
| `web-dirs-common.txt` | 常见 Web 路径 |
| `subdomains-top5000.txt` | 常见子域名 |

`config/brute.py` 是项目内置的通用登录爆破工具，支持：

- 表单登录
- JSON API 登录
- Basic Auth
- 多用户爆破
- 自动表单字段识别
- 代理调试
- 验证码 OCR

常用命令：

```powershell
python config/brute.py http://target/login -u admin -d config/elite-passwords.txt
python config/brute.py http://target/login -u admin --auto-form --captcha
python config/brute.py http://target/login -U config/users-common.txt -d config/admin-top500.txt
python config/brute.py http://target/login -u admin --json
```

## 典型工作流

### IP 扫描

```text
用户输入：扫一下 192.168.1.10
```

Reasonix 应先判断目标是内网还是外网：

```powershell
naabu -host 192.168.1.10
fscan -h 192.168.1.10
```

内网优先 `fscan`，外网优先 `naabu + httpx + nuclei`。

### Web 测试

```text
用户输入：测一下 http://example.com
```

推荐路线：

```powershell
httpx -u http://example.com -title -tech-detect -status-code
nuclei -u http://example.com -as -rl 10
ffuf -u http://example.com/FUZZ -w config/web-dirs-common.txt
```

如果发现登录页，再根据场景进入弱口令、SQLi、SSTI、JWT 或业务逻辑分析。

### 前端代码审计

```text
用户输入：帮我看一下这个 Webpack 解包出来的 JS
```

Reasonix 应加载 `ai-assisted-code-audit`，优先分析：

- API Base URL
- 登录接口
- Token 存储方式
- 角色判断逻辑
- 路由守卫
- 后台接口
- 敏感字段

如果发现 `role`、`isAdmin`、`permissions`，继续加载 `jwt-privilege-escalation`。

### JWT 越权分析

```text
用户输入：这个 JWT 看看有没有越权
```

推荐分析：

```powershell
echo "<JWT>" | jq -R 'split(".") | .[0],.[1] | @base64d | fromjson'
```

然后结合前端代码或接口响应判断：

- 是否存在角色层级
- 是否能横向访问其他用户
- 是否能跨租户访问
- 后端是否只信任前端传入字段
- 低权限 Token 是否能读高权限接口

### 扫描结果 AI 研判

```powershell
python scripts/ai-pentest-orchestrator.py --target http://example.com
```

脚本会生成：

```text
results/ai_prompt_*.md
results/report_*.json
```

将 `ai_prompt_*.md` 内容交给 Reasonix，即可继续做攻击链分析和下一步验证建议。

## 经验积累系统

这是本项目最有长期价值的设计之一。每次渗透任务结束后，Reasonix 应记录一次 `pentest-experience-NNN`，让环境越用越懂你的打法。

经验文件默认保存到：

```text
memory/
├── README.md
├── pentest-experience-001.md
├── attack-chains.yaml
├── cost-stats.csv
└── templates/
    ├── pentest-experience-template.md
    └── attack-chain-template.yaml
```

经验记录包括：

- 目标概况：IP、端口、技术栈、CMS 类型
- 成功手法：有效方法、利用步骤、原因
- 失败记录：无效方法、踩坑、误判
- 关键口令：默认密码、数据库凭据、弱口令模式
- 工具链：各阶段使用的工具和效果
- 方法论总结：可复用的攻击模式

经验不是普通日志，而是 Reasonix 后续启动时可以利用的记忆层。它能帮助 AI 避免重复踩坑，优先选择已验证过的路径。

多次复用的经验应从 `memory/` 升级到 `AGENTS.md` 或对应 `SKILL.md`，这样 Reasonix 启动后可以直接把它当成默认方法。

### 攻击链追踪

项目鼓励把多个低危或中危问题串成攻击链，例如：

```yaml
attack_chains:
  - id: CHAIN-001
    summary: "路径穿越 → 读取 DB 配置 → MySQL 弱口令 → 写 webshell"
    nodes:
      - vuln: "路径穿越"
        impact: "读取配置文件"
        prerequisite: "目标存在可控文件读取参数"
      - vuln: "信息泄露"
        impact: "获得数据库账号密码"
        prerequisite: "成功读取配置文件"
      - vuln: "MySQL 弱口令"
        impact: "数据库控制"
        prerequisite: "数据库可访问"
    final_impact: "RCE"
    kill_chain_phase: [recon, exploitation, lateral_movement]
```

这种结构能让 Reasonix 后续不是孤立看漏洞，而是主动思考漏洞之间的组合关系。

### 成本和缓存记录

每次任务结束后建议在 Reasonix 中执行：

```text
/stats
```

记录：

- 缓存命中率
- 总 token
- 总费用
- 会话轮次
- 有效轮次

长期积累这些数据，可以评估 DeepSeek prefix-cache 在渗透场景里的真实收益，并持续优化 `AGENTS.md` 和技能文件。

结构化成本数据追加到：

```text
memory/cost-stats.csv
```

## 安全边界

本项目只用于授权目标。使用前必须确认测试范围，不对未授权资产执行扫描、爆破、利用或横向移动。

默认原则：

- 扫描前确认目标授权范围
- 大范围扫描先小规模验证
- 不扫描 `.gov` / `.mil` 目标
- 不访问云元数据地址 `169.254.169.254`
- 不在生产环境直接写文件或修改配置
- 不批量爆破超过 100 个目标的同一服务
- 高危利用必须隔离执行
- 发现漏洞后先保存证据，再决定是否继续深入

高危操作建议隔离：

| 操作 | 隔离方式 |
|:-----|:---------|
| `sqlmap --os-shell` | Docker 隔离 |
| Metasploit 利用 | Kali WSL |
| 浏览器自动化 | Playwright 容器 |
| WebShell 写入 | 人工确认后执行 |
| 敏感文件读取 | 只读验证，保存最小证据 |

## 新电脑部署

从 Git 仓库恢复环境：

```powershell
git clone git@github.com:xiabai2004/reasonix-sentou.git
cd reasonix_sentou
.\scripts\setup-new-pc.ps1
```

部署脚本会尝试完成：

- 检查项目结构
- 下载工具和字典
- 安装 Python 依赖
- 添加 `bin/` 到 PATH
- 检查 WSL Kali
- 安装 Kali 常用工具
- 执行基础验证

工具下载依赖：

- Git
- GitHub CLI `gh`
- Python
- PowerShell
- 可选：WSL Kali Linux

部署后建议运行健康检查：

```powershell
python scripts/health-check.py
```

健康检查会验证：

- `AGENTS.md` 和 `reasonix.toml`
- 关键目录和关键工具
- 工具版本信息
- Python 依赖
- 技能索引一致性
- 旧路径残留
- 工具包装器目标存在性和一致性
- `.gitignore` 是否覆盖敏感输出

## 维护建议

这个项目会随着使用不断成长，建议维护时遵守几个原则：

- 新工具先写入 `config/tools-manifest.json`
- 新技能放到 `skills/pentest_skills/<skill-name>/SKILL.md`
- 新技能同步加入 `skills/vuln-hunter.md`
- 新经验沉淀到 `pentest-experience-NNN`
- 单次任务经验优先写入 `memory/pentest-experience-NNN.md`
- 多次复用的经验升级进 `AGENTS.md` 或对应技能
- 扫描结果、报告、证据不要提交到 Git
- 根目录只放核心文件，历史脚本迁移到 `cases/` 或 `archive/`
- 定期检查旧路径和失效包装器
- 定期同步 `vuln-hunter.md` 与实际技能目录
- 每次迁移或新增工具后运行 `python scripts/health-check.py`

## 作战配置

`config/` 下新增了三个作战配置文件，让 Reasonix 的行为更可控：

### 授权范围 (`config/scope.yaml`)

定义授权目标白名单。扫描前 Reasonix 或编排脚本自动校验：

```powershell
python scripts/check-scope.py 192.168.1.1
python scripts/check-scope.py http://example.com
python scripts/check-scope.py --file targets.txt --json
```

支持 CIDR、域名通配符、精确 IP、URL 前缀四种授权方式。内网地址默认封禁但可通过白名单放行。

### 作战模式 (`config/modes.yaml`)

三档模式控制工具链选择和参数约束：

| 模式 | 说明 | 典型场景 |
|:-----|:-----|:---------|
| safe | 仅被动信息收集，不发送攻击载荷 | 客户交付前侦察 |
| normal | 默认模式，含漏洞检测但不执行高危利用 | 常规授权测试 |
| aggressive | 全工具全参数，高危操作需人工确认 | 深度渗透 |

Reasonix 从用户输入中自动识别模式关键词，也可显式指定。

### 战术模板 (`config/combat-templates.yaml`)

为 5 种常见目标类型预定义标准攻击链：

| 模板 | 目标类型 | 核心流程 |
|:-----|:---------|:---------|
| web-target | Web 应用 | httpx 探活 → nuclei + xray → ffuf 目录 → katana URL |
| api-target | API 接口 | httpx → arjun 参数 → JWT 分析 → 越权验证 |
| internal-network | 内网横向 | fscan 存活 → nuclei 验证 → impacket 横向 |
| frontend-audit | 前端审计 | katana 收集 JS → SourceMap 检测 → AI 代码审计 |
| subdomain-recon | 子域名 | subfinder → gau + katana → httpx 存活验证 |

### 技能索引 (`skills/skills-index.json`)

62 个技能的结构化 JSON 索引。Reasonix 按需加载对应技能的 SKILL.md，而非每次全量读取 vuln-hunter.md，节省 token。

### 结果格式化 (`scripts/format-results.py`)

将 fscan、nuclei、httpx、naabu、subfinder、katana 的原始输出统一转为 JSON，便于报告生成和 AI 分析：

```powershell
python scripts/format-results.py results/
python scripts/format-results.py results/fscan.txt --type fscan
python scripts/format-results.py results/ --list
python scripts/format-results.py results/ -o results/formatted.json
```

## 项目价值

`reasonix_sentou` 的价值不在于工具数量，而在于把工具、AI、经验和安全边界连成一个持续成长的工作环境。

每次使用都会留下经验，每次经验都会影响下一次判断。随着 `AGENTS.md`、`skills/` 和 `pentest-experience-*` 不断积累，Reasonix 会越来越理解你的作战习惯、工具偏好、常见目标和有效打法。

这是一个面向 Reasonix 的可成长型 AI 渗透测试作战环境。
