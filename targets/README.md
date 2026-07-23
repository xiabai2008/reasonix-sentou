# Reasonix 渗透靶场 — 实战训练环境

> 一键启动 4 个真实漏洞环境，覆盖 PHP / Node.js / Java / Python 四大技术栈。
> 对应项目内 **59 个漏洞技能**，配合 `AGENTS.md` 中的 AI 辅助分析能力，
> 实现"学习 → 练习 → AI 分析 → 复盘"的完整闭环。

## 快速开始

```powershell
# 启动全部靶场 (首次需拉取镜像，约 3-5 分钟)
.\targets\start-ranges.ps1

# 启动单个靶场
.\targets\start-ranges.ps1 dvwa
.\targets\start-ranges.ps1 juiceshop
.\targets\start-ranges.ps1 webgoat
.\targets\start-ranges.ps1 vampi

# 停止 (保留数据)
.\targets\stop-ranges.ps1

# 完全重置 (清除所有数据)
.\targets\stop-ranges.ps1 -Reset
```

## 四个靶场速览

| 靶场 | 端口 | 技术栈 | 漏洞数量 | 适合练习 |
|:-----|:-----|:-------|:---------|:---------|
| **DVWA** | 8080 | PHP + MySQL | 12 类 | SQLi, XSS, CSRF, LFI, 命令注入 |
| **Juice Shop** | 3000 | Node.js + Angular | 100+ 挑战 | JWT, SSRF, SSTI, 原型链, API |
| **WebGoat** | 8081 | Java + Spring | 13 课程 | 反序列化, XXE, JWT, IDOR |
| **VAmPI** | 5000 | Python + Flask | 7 类 | JWT 越权, BOLA, API 侦察 |

```
┌──────────────────────────────────────────────────────────┐
│                    技术栈全覆盖矩阵                         │
├──────────┬──────────┬──────────┬──────────┬──────────────┤
│          │   PHP    │ Node.js  │   Java   │   Python     │
├──────────┼──────────┼──────────┼──────────┼──────────────┤
│ SQLi     │  DVWA ✅ │ Juice ✅ │ WebGoat✅│              │
│ XSS      │  DVWA ✅ │ Juice ✅ │ WebGoat✅│              │
│ CSRF     │  DVWA ✅ │          │ WebGoat✅│              │
│ LFI      │  DVWA ✅ │ Juice ✅ │ WebGoat✅│              │
│ CMDi     │  DVWA ✅ │          │          │              │
│ JWT      │          │ Juice ✅ │ WebGoat✅│ VAmPI ✅     │
│ SSRF     │          │ Juice ✅ │ WebGoat✅│              │
│ SSTI     │          │ Juice ✅ │          │              │
│ XXE      │          │          │ WebGoat✅│              │
│ IDOR     │          │ Juice ✅ │ WebGoat✅│ VAmPI ✅     │
│ 反序列化 │          │          │ WebGoat✅│              │
│ 原型链   │          │ Juice ✅ │          │              │
│ 文件上传 │  DVWA ✅ │          │          │              │
│ API 漏洞 │          │ Juice ✅ │          │ VAmPI ✅     │
└──────────┴──────────┴──────────┴──────────┴──────────────┘
```

## 训练路线 (建议 8 周)

### 第 1-2 周：经典 Web 漏洞（DVWA）
```
目标: 掌握 SQLi / XSS / CSRF / CMDi / LFI
工具: sqlmap, dalfox, nuclei, ffuf
技能: sqli-sql-injection, xss-cross-site-scripting, cmdi-command-injection
```
→ 详细计划见 [dvwa/TARGET.md](dvwa/TARGET.md)

### 第 3-4 周：现代 Web 应用（Juice Shop）
```
目标: JWT 攻击, SSRF, SSTI, 原型链污染, API 滥用
工具: jwt_tool, SSTImap, curl, Burp Suite
技能: jwt-oauth-token-attacks, ssrf-server-side-request-forgery, ssti-server-side-template-injection
```
→ 详细计划见 [juiceshop/TARGET.md](juiceshop/TARGET.md)

### 第 5-6 周：Java 企业应用（WebGoat）
```
目标: Java 反序列化, XXE, JNDI 注入, 认证绕过
工具: JYso, ysoserial, jndi-exploit
技能: deserialization-insecure, xxe-xml-external-entity, jndi-injection
```
→ 详细计划见 [webgoat/TARGET.md](webgoat/TARGET.md)

### 第 7-8 周：API 专项 + 综合（VAmPI）
```
目标: API Penetration Testing, JWT 权限提升, BOLA/IDOR
工具: curl, jwt_tool, Burp, httpx
技能: jwt-privilege-escalation, api-authorization-and-bola, idor-broken-object-authorization
```
→ 详细计划见 [vampi/TARGET.md](vampi/TARGET.md)

## 配合 AI 分析的工作流

每次练习后，使用项目编排脚本生成 AI 分析提示词：

```powershell
# 对靶场执行基础扫描
python scripts/ai-pentest-orchestrator.py --target http://localhost:8080 --type url

# 将生成的 ai_prompt_*.md 在 Reasonix 中分析攻击链
# 结合 AGENTS.md 中的作战经验，进行深度研判

# 或直接对扫描结果格式化
python scripts/format-results.py results/ -o results/formatted.json
```

## 常见问题

**Q: Docker Desktop 启动后仍然报错？**
A: Windows 需要启用 WSL2 作为 Docker 后端。确保：
```powershell
wsl --install                    # 安装 WSL2
wsl --set-default-version 2      # 设默认版本为 2
```
然后在 Docker Desktop → Settings → General → "Use WSL 2 based engine"

**Q: 端口冲突怎么办？**
A: 靶场端口可在 `docker-compose.yml` 中修改左侧端口号：
```yaml
ports:
  - "8080:80"    # 将左侧 8080 改为其他端口
```

**Q: DVWA 数据库连接失败？**
A: 等待 15-30 秒让 MySQL 完全启动，然后访问 `http://localhost:8080/setup.php`，点击 "Create/Reset Database"。

**Q: Juice Shop 看不到 Score Board？**
A: Score Board 是一个隐藏页面。检查浏览器 DevTools 寻找线索，或尝试访问 `/#/score-board`。

## 镜像大小参考

| 镜像 | 压缩后大小 | 首次拉取时间 |
|:-----|:----------|:------------|
| dvwa (web-dvwa) | ~250 MB | ~2 分钟 |
| dvwa (mysql:5.7) | ~150 MB | ~1 分钟 |
| Juice Shop | ~300 MB | ~2 分钟 |
| WebGoat | ~400 MB | ~3 分钟 |
| VAmPI | ~200 MB | ~1 分钟 |
| **合计** | **~1.3 GB** | **首拉 ~5-10 分钟** |
