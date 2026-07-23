# Week 1 — 信息收集与资产侦察

> **靶场**: DVWA + Juice Shop | **工具**: subfinder, httpx, naabu, katana, gau
> **技能**: `intel-gather`, `port-scan`
> **难度**: ⭐ | **预计时间**: 4 小时

## 本周目标

掌握渗透测试第一步：**信息收集**。学会在不触发告警的前提下，最大化获取目标信息。

## 练习任务

### 任务 1: 被动信息收集 (1h)

对 DVWA (localhost:8080) 和 Juice Shop (localhost:3000) 执行信息收集：

```bash
# HTTP 探活 + 技术栈识别
httpx -u http://localhost:8080 -title -tech-detect -status-code -follow-redirects
httpx -u http://localhost:3000 -title -tech-detect -status-code -follow-redirects

# 记录发现:
# - Web 服务器类型和版本
# - 编程语言/框架
# - 使用的 JavaScript 库
# - 响应头中的敏感信息 (Server, X-Powered-By 等)
```

### 任务 2: 目录枚举 (1h)

```bash
# 用 ffuf 爆破常见路径
ffuf -u http://localhost:8080/FUZZ -w config/web-dirs-common.txt -fc 404
ffuf -u http://localhost:3000/FUZZ -w config/web-dirs-common.txt -fc 404

# 记录:
# - 发现了哪些路径？
# - 有没有备份文件 (.bak, .old, .zip)？
# - 有没有 git/svn 泄露？
# - 有没有 phpinfo() 页面？
```

### 任务 3: 端口扫描 (30min)

```bash
# 扫描本地运行的服务
netstat -an | grep LISTENING

# 或使用 naabu (如果目标在外网)
naabu -host localhost -top-ports 1000

# 记录:
# - 除了 80/443，还有哪些端口开放？
# - 这些端口对应什么服务？
```

### 任务 4: AI 辅助分析 (30min)

```bash
# 运行编排脚本
python scripts/ai-pentest-orchestrator.py --target http://localhost:8080 --type url

# 将生成的 ai_prompt_*.md 内容在 Reasonix 中分析
# 让 AI 给出下一步建议
```

## 交付物

在 `NOTES.md` 中记录：

```markdown
## 目标 1: DVWA (localhost:8080)

### 技术栈
- Web Server: _____
- 语言/框架: _____
- 关键响应头: _____

### 发现的路径
- /_____ (状态码 __)
- /_____ (状态码 __)

### 安全相关发现
- [ ] 有备份文件泄露
- [ ] 有目录遍历
- [ ] 有敏感信息泄露

## 目标 2: Juice Shop (localhost:3000)
...
```

## 复盘要点 (练习后对照)

打开 `EXPECTED.md` 对比：
1. 你发现了哪些我列出的东西？哪些没发现？
2. 哪个工具的输出对你最有价值？哪个最没用？
3. 信息收集阶段最容易忽略什么？
