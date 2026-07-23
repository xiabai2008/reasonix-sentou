# WebGoat + WebWolf

> **技术栈**: Java 17 + Spring Boot + HSQLDB | **访问**: http://localhost:8081/WebGoat
> **WebWolf**: http://localhost:9090/WebWolf（辅助工具，接收回调、收发邮件）
> **注册**: 首次访问时创建账号

## 漏洞课程映射

WebGoat 按课程组织，每个课程包含多道题目，覆盖了企业级 Java 应用的典型漏洞。

| 课程 | 漏洞 | 对应技能 | 项目工具 |
|:-----|:-----|:---------|:---------|
| (A1) Injection | SQL注入(高级/盲注) | `sqli-sql-injection` | sqlmap |
| (A2) Broken Auth | JWT 破解, 密码重置 | `jwt-oauth-token-attacks`, `authbypass-authentication-flaws` | jwt_tool, jq |
| (A3) Sensitive Data | Insecure Login | `api-auth-and-jwt-abuse` | httpx |
| (A4) XXE | XML外部实体注入 | `xxe-xml-external-entity` | curl, nuclei |
| (A5) Broken Access | IDOR, 隐藏菜单 | `idor-broken-object-authorization` | curl |
| (A6) Security Misconfig | XXE via config | `waf-bypass-techniques` | — |
| (A7) XSS | 反射/存储/DOM XSS | `xss-cross-site-scripting` | dalfox |
| (A8) Deserialization | Java反序列化RCE | `deserialization-insecure` | JYso, ysoserial |
| (A9) Known Vulns | 已知组件漏洞 | `vuln-hunter` | nuclei |
| (A10) CSRF | 跨站请求伪造 | `csrf-cross-site-request-forgery` | Burp |
| (A11) Request Forgeries | SSRF | `ssrf-server-side-request-forgery` | curl |
| (A12) Path Traversal | 路径穿越 | `path-traversal-lfi` | ffuf |
| (A13) Crypto | 编码/签名绕过 | `type-juggling` | hashid |
| Challenge | 综合挑战 | — | 综合 |

## 特色：Java 反序列化练习

WebGoat 的 `(A8) Insecure Deserialization` 课程是练习 Java 反序列化攻击的最佳入门：

```bash
# WebGoat 会在 WebWolf 中给你上传 payload 的位置
# 使用 JYso 生成反序列化 payload:
# (参考 skills/pentest_skills/deserialization-insecure/SKILL.md)

# 配合 nuclei 检测 Java 反序列化:
nuclei -u http://localhost:8081/WebGoat -tags deserialization
```

## WebWolf 的作用

WebWolf 地址: `http://localhost:9090/WebWolf`

- **文件服务器**: 上传恶意文件（XXE payload, 反序列化 payload）
- **邮件收件箱**: 接收 WebGoat 发送的邮件（密码重置等场景）
- **HTTP 回调**: 配合 SSRF 题目接收回调请求

## 推荐路线

| 顺序 | 课程 | 难度 | 重点技能 |
|:-----|:-----|:-----|:---------|
| 1 | (A1) Injection | ⭐⭐ | SQLi 高级技巧 |
| 2 | (A2) Broken Auth | ⭐⭐⭐ | JWT 实战 |
| 3 | (A7) XSS | ⭐⭐ | XSS 全场景 |
| 4 | (A4) XXE | ⭐⭐⭐ | XML 安全 |
| 5 | (A11) SSRF | ⭐⭐⭐ | 服务端请求伪造 |
| 6 | (A8) Deserialization | ⭐⭐⭐⭐ | Java 反序列化（重点！）|
| 7 | Challenge | ⭐⭐⭐⭐⭐ | 综合能力验证 |
