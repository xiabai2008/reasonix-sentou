# Week 8 — 综合攻击链实战

> **靶场**: DVWA + Juice Shop + WebGoat（多靶场联动）| **工具**: 全部
> **技能**: `pentest-master`（总指挥模式）| **难度**: ⭐⭐⭐⭐⭐ | **预计时间**: 8 小时

## 本周目标

将前 7 周所学技能**串联成完整的攻击链**。模拟真实渗透测试场景：从一个入口点开始，横向移动，逐步获取最高权限。

## 攻击链设计原则

真实渗透不是单点漏洞利用，而是**漏洞组合**。低危漏洞组合可以变成高危攻击：

```
信息泄露 → 凭证获取 → 认证绕过 → 权限提升 → 数据窃取/RCE
  Lv1          Lv2         Lv3         Lv4          Lv5
```

## 练习任务

### 任务 1: 攻击链 A — "从目录遍历到 RCE" (DVWA, 2h)

```
Phase 1: 信息收集
  → ffuf 发现 /backup/ 目录存在目录遍历
  → 下载 backup.zip（包含数据库配置）
  
Phase 2: 凭证获取  
  → 从 config.php 中提取 MySQL 账号密码
  → admin / P@ssw0rd123

Phase 3: 权限提升
  → 用 sqlmap 读取 users 表
  → 破解 admin 密码哈希
  → 登录后台 /admin/

Phase 4: 代码执行
  → 后台存在文件上传功能
  → 绕过扩展名限制上传 WebShell
  → 获得服务器 shell

最终影响: RCE (Remote Code Execution)
```

**操作规程**:
```bash
# Phase 1
ffuf -u http://localhost:8080/FUZZ -w config/web-dirs-medium.txt -fc 404

# Phase 2
curl http://localhost:8080/backup/config.php.bak

# Phase 3
sqlmap -u "http://localhost:8080/vulnerabilities/sqli/?id=1&Submit=Submit" \
  --cookie="..." -D dvwa -T users --dump --batch

# Phase 4 — 手动构造上传绕过
```

### 任务 2: 攻击链 B — "从 SSRF 到内网横移" (Juice Shop, 2h)

```
Phase 1: SSRF 发现
  → Juice Shop 某功能接受外部 URL
  → 尝试访问 internal API

Phase 2: 内网探测
  → 通过 SSRF 扫描 localhost 端口
  → 发现内部管理接口 :3001

Phase 3: 权限提升
  → 管理接口使用弱 JWT
  → 破解或绕过 JWT 签名
  
Phase 4: 数据窃取
  → 通过管理接口导出用户数据
  → 包含密码哈希和 PII

最终影响: 数据泄露 + 权限提升
```

### 任务 3: 攻击链 C — "从 XSS 到账号接管" (DVWA, 1.5h)

```
Phase 1: XSS 发现
  → DVWA 存储型 XSS（/vulnerabilities/xss_s/）
  → 注入 XSS payload

Phase 2: Session 劫持
  → 构造 Cookie 窃取 payload
  → 通过 WebHook/DNSLog 接收受害者 Cookie

Phase 3: 账号接管
  → 利用窃取的 Session 冒充管理员
  → 访问需要认证的页面

Phase 4: 持久化
  → 在管理后台创建新管理员账号
  → 即使原始 Session 过期也能保持访问

最终影响: 完整账号接管
```

### 任务 4: 生成完整渗透报告 (2h)

使用项目报告生成工具：

```bash
# 整理所有发现到 results/
python scripts/format-results.py results/week08/ -o results/week08_summary.json

# 生成 AI 分析报告
python scripts/ai-pentest-orchestrator.py --target http://localhost:8080

# 记录攻击链到 memory/
cp memory/templates/attack-chain-template.yaml memory/attack-chain-001.yaml
# 编辑记录完整的攻击链
```

## 攻击链模板

```yaml
attack_chain:
  id: CHAIN-XXX
  name: "攻击链名称"
  target: "靶场名称"
  cvss_combined: 9.8
  
  nodes:
    - step: 1
      vuln: "漏洞名称"
      cvss: 5.0
      impact: "阶段性影响"
      technique: "使用的技术"
      tool: "使用的工具"
      prerequisite: "前置条件"
    
    - step: 2
      vuln: "第二个漏洞"
      cvss: 7.5
      impact: "进一步影响"
      # ... 以此类推，直到最终目标
  
  final_impact: "RCE / 数据泄露 / 权限提升"
  kill_chain_phase: [recon, exploitation, lateral_movement, exfiltration]
  lessons: "学到的经验"
```

## 交付物

```markdown
## 攻击链 A
- 入口点: _____
- 每一步的漏洞和利用方法
- 最终获得的权限: _____
- 攻击链图 (ASCII):
  
  信息泄露 → 凭证 → 登录 → 上传 → RCE
    5min     2min    1min   5min   1min
           总计: 13 分钟完成攻击链

## 攻击链 B
...

## 攻击链 C
...

## 总结
- 最有效的一次攻击链: _____
- 最意外的漏洞组合: _____
- 如果我是防守方，应该先修哪个漏洞: _____
- 本周学到的 3 个最重要的经验:
  1. _____
  2. _____
  3. _____
```

## 评分

| 完成项 | 分数 |
|:-------|:-----|
| 完成 1 条攻击链 | 60 分 |
| 完成 2 条攻击链 | 80 分 |
| 完成 3 条攻击链 + 报告 | 100 分 |
| 发现意外的漏洞组合 | +10 加分 |
