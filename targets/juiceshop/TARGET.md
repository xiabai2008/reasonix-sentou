# OWASP Juice Shop

> **技术栈**: Node.js + Angular (SPA) | **访问**: http://localhost:3000
> **注册**: 无需真实邮箱，注册后自动登录
> **挑战数**: 100+ (按难度: ⭐→⭐⭐⭐⭐⭐⭐)

## 与项目技能映射

Juice Shop 是现代 Web 应用的典型代表。与 DVWA 不同，它没有"安全等级"切换——所有漏洞都是"天然存在"的，模拟真实场景。

| 漏洞类别 | 挑战示例 | 对应技能 | 工具 |
|:---------|:---------|:---------|:-----|
| SQL Injection | Login Admin | `sqli-sql-injection` | DevTools, curl |
| SSRF | Blockchain Tycoon | `ssrf-server-side-request-forgery` | curl, gopher |
| JWT 攻击 | Forged JWT, Token Sale | `jwt-oauth-token-attacks` | jwt.io, jq |
| SSTI | SSTI via email | `ssti-server-side-template-injection` | curl, SSTImap |
| 原型链污染 | "NoSQL" DoS | `prototype-pollution` | DevTools, curl |
| XSS | DOM XSS, Bonus Payload | `xss-cross-site-scripting` | dalfox |
| IDOR | Hor. Privilege Escalation | `idor-broken-object-authorization` | curl, Burp |
| API 滥用 | API-Only Products | `api-authorization-and-bola` | curl |
| 文件访问 | Poison Null Byte | `path-traversal-lfi` | curl |
| 注册/登录绕 | CAPTCHA Bypass | `business-logic-vulnerabilities` | Burp Intruder |

## 特色练习

### JWT 攻击链

```bash
# 1. 获取任意用户 JWT (浏览器 DevTools → Application → Local Storage → token)
# 2. 解码 JWT:
echo "<JWT>" | cut -d. -f2 | base64 -d 2>/dev/null | jq .
# 3. 尝试修改 role/email 等字段
# 4. 使用 jwt_tool 或手动构造
```

### 前端代码审计

Juice Shop 的 Angular 源码在 GitHub 开源，配合 `ai-assisted-code-audit` 技能：
```bash
# 分析前端路由和 API 调用
# 找隐藏的管理接口 /administration
# 检查 Score Board 的挑战描述作为提示
```

## 快速信息收集

```bash
httpx -u http://localhost:3000 -tech-detect -title -status-code
# 打开 http://localhost:3000 → 注册 → 查看 Score Board
# Score Board 在 http://localhost:3000/#/score-board (需先找到入口)
```

## 推荐路线

| 阶段 | 目标 | 建议花时间 |
|:-----|:-----|:----------|
| 入门 ⭐ | 完成 1-2 星挑战，熟悉应用 | 2-3 小时 |
| 进阶 ⭐⭐ | SQLi, XSS, IDOR 等经典漏洞 | 4-6 小时 |
| 高级 ⭐⭐⭐⭐+ | JWT, SSRF, SSTI, 原型链污染 | 8+ 小时 |
