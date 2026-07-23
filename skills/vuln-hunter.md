---
name: vuln-hunter
description: 漏洞专项检测入口 - 涵盖 SQLi/XSS/SSRF/IDOR/命令注入/反序列化等 52 个漏洞方向，提供检测流程、Payload、绕过技巧
---

# vuln-hunter — 漏洞专项检测入口

覆盖 **52 个漏洞方向**，每个方向包含完整的检测流程、Payload 和绕过技巧。

## 使用方式

在 Reasonix 中调用某个漏洞技能时，直接说出漏洞名称即可触发对应的 skill。

## 漏洞分类索引

以下条目均对应实际存在的 `SKILL.md` 目录。普通 Markdown 资料单独放在“绕过参考文档”和“辅助参考”中，避免 Reasonix 把资料页误判为可加载技能。

### 注入类
| 技能路径 | 漏洞类型 |
|:---------|:---------|
| `pentest_skills/sqli-sql-injection` | SQL 注入 |
| `pentest_skills/cmdi-command-injection` | 命令注入 |
| `pentest_skills/ssti-server-side-template-injection` | SSTI 模板注入 |
| `pentest_skills/expression-language-injection` | EL 表达式注入 |
| `pentest_skills/jndi-injection` | JNDI 注入 |
| `pentest_skills/crlf-injection` | CRLF 注入 |
| `pentest_skills/email-header-injection` | 邮件头注入 |
| `pentest_skills/xslt-injection` | XSLT 注入 |
| `pentest_skills/injection-checking` | 注入类通用检查 |
| `pentest_skills/nosql-injection` | NoSQL 注入 |

### 认证与授权
| 技能路径 | 漏洞类型 |
|:---------|:---------|
| `pentest_skills/auth-sec` | 认证与授权入口路由 |
| `pentest_skills/authbypass-authentication-flaws` | 认证绕过 |
| `pentest_skills/jwt-oauth-token-attacks` | JWT/OAuth 攻击 |
| `pentest_skills/jwt-privilege-escalation` | JWT 权限提升 |
| `pentest_skills/api-auth-and-jwt-abuse` | API 认证滥用 |
| `pentest_skills/api-authorization-and-bola` | API 授权/BOLA |
| `pentest_skills/idor-broken-object-authorization` | IDOR/BOLA |
| `pentest_skills/oauth-oidc-misconfiguration` | OAuth/OIDC 配置错误 |
| `pentest_skills/saml-sso-assertion-attacks` | SAML SSO 断言攻击 |
| `pentest_skills/type-juggling` | PHP 类型混淆 |

### Web 前端与逻辑
| 技能路径 | 漏洞类型 |
|:---------|:---------|
| `pentest_skills/ai-assisted-code-audit` | AI 辅助前端代码审计 |
| `pentest_skills/xss-cross-site-scripting` | XSS 跨站脚本 |
| `pentest_skills/dalfox-xss-scanner` | Dalfox XSS 专项扫描 |
| `pentest_skills/js-reverse-bypass` | 前端 JS 逆向与加密绕过 |
| `pentest_skills/csrf-cross-site-request-forgery` | CSRF 跨站请求伪造 |
| `pentest_skills/clickjacking` | 点击劫持 |
| `pentest_skills/cors-cross-origin-misconfiguration` | CORS 配置错误 |
| `pentest_skills/csp-bypass-advanced` | CSP 绕过 |
| `pentest_skills/dangling-markup-injection` | dangling 标记注入 |
| `pentest_skills/open-redirect` | 开放重定向 |
| `pentest_skills/web-cache-deception` | Web 缓存欺骗 |
| `pentest_skills/race-condition` | 条件竞争 |
| `pentest_skills/business-logic-vuln` | 业务逻辑漏洞入口 |
| `pentest_skills/business-logic-vulnerabilities` | 业务逻辑漏洞场景 |

### 文件与资源
| 技能路径 | 漏洞类型 |
|:---------|:---------|
| `pentest_skills/file-access-vuln` | 文件访问漏洞 |
| `pentest_skills/xxe-xml-external-entity` | XXE 外部实体注入 |
| `pentest_skills/path-traversal-lfi` | 路径遍历/LFI |
| `pentest_skills/upload-insecure-files` | 文件上传漏洞 |
| `pentest_skills/insecure-source-code-management` | 不安全的源码管理 |

### API 与架构
| 技能路径 | 漏洞类型 |
|:---------|:---------|
| `pentest_skills/api-sec` | API 安全入口路由 |
| `pentest_skills/api-recon-and-docs` | API 侦察与文档 |
| `pentest_skills/graphql-and-hidden-parameters` | GraphQL 与隐藏参数 |
| `pentest_skills/http2-specific-attacks` | HTTP/2 攻击 |
| `pentest_skills/request-smuggling` | HTTP 请求走私 |
| `pentest_skills/http-parameter-pollution` | HTTP 参数污染 |
| `pentest_skills/http-host-header-attacks` | Host 头攻击 |
| `pentest_skills/websocket-security` | WebSocket 安全 |

### 高级与特殊
| 技能路径 | 漏洞类型 |
|:---------|:---------|
| `pentest_skills/ctf-web` | CTF Web 专项 — 快速解题模式 |
| `pentest_skills/ctf-reverse` | CTF 逆向 — 二进制分析 |
| `pentest_skills/ctf-pwn` | CTF PWN — 漏洞利用 |
| `pentest_skills/ctf-crypto` | CTF 密码学 — 加解密攻击 |
| `pentest_skills/ctf-misc` | CTF Misc — 隐写/取证/流量分析 |
| `pentest_skills/deserialization-insecure` | 反序列化漏洞 |
| `pentest_skills/jyso-exploit` | JYso JNDI 与反序列化利用 |
| `pentest_skills/memshell-injection` | Java 内存马注入 |
| `pentest_skills/prototype-pollution` | 原型链污染 |
| `pentest_skills/prototype-pollution-advanced` | 原型链污染高级 |
| `pentest_skills/dns-rebinding-attacks` | DNS 重绑定攻击 |
| `pentest_skills/ssrf-server-side-request-forgery` | SSRF 服务端请求伪造 |
| `pentest_skills/subdomain-takeover` | 子域名劫持 |
| `pentest_skills/privilege-escalation` | 提权辅助 |
| `pentest_skills/sstimap-exploit` | SSTImap 自动检测利用 |
| `pentest_skills/waf-bypass-techniques` | WAF 绕过技术 |
| `pentest_skills/401-403-bypass-techniques` | 401/403 绕过 |

### 绕过参考文档
| 文档路径 | 说明 |
|:---------|:-----|
| `pentest_skills/bypass-skills/INDEX.md` | 绕过技巧总览 |
| `pentest_skills/bypass-skills/waf-and-request-bypass.md` | WAF 与请求绕过 |
| `pentest_skills/bypass-skills/auth-and-token-bypass.md` | 认证与令牌绕过 |
| `pentest_skills/bypass-skills/ssrf-and-parser-bypass.md` | SSRF 与解析器绕过 |
| `pentest_skills/bypass-skills/injection-filter-bypass.md` | 注入过滤器绕过 |
| `pentest_skills/bypass-skills/file-and-path-bypass.md` | 文件与路径绕过 |
| `pentest_skills/bypass-skills/browser-policy-bypass.md` | 浏览器策略绕过 |
| `pentest_skills/bypass-skills/cors-and-origin-bypass.md` | CORS 与来源绕过 |
| `pentest_skills/bypass-skills/cache-and-key-bypass.md` | 缓存与密钥绕过 |
| `pentest_skills/bypass-skills/header-and-response-bypass.md` | 头与响应绕过 |
| `pentest_skills/bypass-skills/host-and-routing-bypass.md` | 主机与路由绕过 |
| `pentest_skills/bypass-skills/redirect-and-url-validation-bypass.md` | 重定向与 URL 验证绕过 |

### 规划中技能
| 规划路径 | 漏洞类型 |
|:---------|:---------|
| `pentest_skills/session/index` | 会话管理 |

### 📋 辅助参考
| 路径 | 说明 |
|:-----|:-----|
| `skills/references/common-paths` | 常见敏感路径 |
| `skills/references/detection-rules` | 漏洞检测规则 |
| `skills/references/wooyun-cases` | **WooYun 22K 真实案例库**（频率统计 + 测试协议 + 案例速查） |
| `skills/references/dnslog-usage` | DNSLog 使用方法 |
| `skills/references/product-default-credentials` | 产品默认口令 |
| `skills/references/product-fingerprints` | 产品指纹识别 |
| `skills/references/http-test-usage` | HTTP 测试方法 |
| `skills/references/report-json-format` | 报告 JSON 格式 |

## 快速上手

```bash
# 选择一个漏洞类型，阅读对应的 SKILL.md
cat skills/pentest_skills/sqli-sql-injection/SKILL.md

# 结合工具使用
# 例如: SQL 注入 → sqlmap -u <url> --batch
#       Windows内网横向 → impacket (psexec/wmiexec/secretsdump)
#       HTTP流量调试 → mitmweb (Web界面) / mitmdump
#       XSS 检测 → 手动 curl 测试
#       参数发现 → arjun -u <url>
#       目录遍历 → ffuf 爆破
#       哈希识别 → hashid <hash>
```

## 所有资源路径
`/c/Tools/reasonix_sentou/skills/pentest_skills/`
