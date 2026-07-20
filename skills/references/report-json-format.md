# report_{timestamp}.json 格式参考

本文档定义 Phase 6 最终输出文件 `workspace/report_{timestamp}.json` 的示例结构、字段约束以及 `type -> type_zh` 映射表。

## report_{timestamp}.json 格式（Phase 6 最终输出）

```json
{
  "report_meta": {
    "report_id": "VUL-2026-XXXXX",
    "generated_at": "2026-05-15 02:00:00",
    "tester": "vibe-pentest-agent-v1",
    "scope": {
      "target_url": "http://target:port/",
      "tech_stack": ["java", "spring_boot_3", "halo_cms"]
    },
    "test_accounts": [
      {"role": "管理员", "username": "admin", "password": "***"}
    ]
  },
  "summary": {
    "total": 7,
    "critical": 0,
    "high": 1,
    "medium": 1,
    "low": 4,
    "info": 1
  },
  "vulnerabilities": [
    {
      "vuln_id": "VUL-001",
      "title": "漏洞标题 - 简述路径和问题",
      "type": "information_disclosure",
      "type_zh": "信息泄露",
      "severity": "high",
      "confidence": "confirmed",
      "authenticated": true,
      "target_url": "http://...",
      "description": "详细描述，包含影响分析。",
      "RepairSuggestions": "1. 针对该漏洞的具体修复建议；2. 多条建议用分号分隔。",
      "http_test_commands": [
        {
          "label": "漏洞验证回放命令",
          "command": "python \"d:/vibe_pentest/scripts/http_test.py\" --url \"http://...\" --method GET --show-command --show-summary --include-headers",
          "expected_evidence": "执行后应看到的关键响应证据"
        }
      ],
      "http_interactions": [
        {
          "seq": 1,
          "label": "此交互的说明",
          "request": {"method": "GET", "url": "http://...", "headers": {}, "body": null},
          "response": {"status_code": 200, "headers": {}, "body": "..."}
        }
      ]
    }
  ]
}
```

## report_{timestamp}.json 格式约束

| 字段 | 类型 | 约束 |
|------|------|------|
| `vuln_id` | string | `VUL-NNN` 格式，NNN 从 001 起，按 severity→confidence 排序分配（严重优先） |
| `type` | string | 见下方完整 type 枚举表（共 42 种），不在表中的值将被映射为 `unknown` |
| `type_zh` | string | 由 type 自动映射，同一 type 始终使用相同中文表述 |
| `severity` | string | `critical` > `high` > `medium` > `low` > `info` |
| `confidence` | string | `confirmed`（有完整 HTTP 证据）、`likely`（间接证据）、`potential`（疑似） |
| `authenticated` | boolean | `true` = 需要登录，`false` = 匿名可触发 |
| `http_test_commands` | array | 可选；用于保留可直接复制回放的 `http_test.py` 命令，建议包含 `label`、`command`、`expected_evidence` |
| `http_interactions` | array | 至少 1 条，每条必须包含 request.method、request.url、response.status_code |

## type -> type_zh 漏洞类型完整映射表

与 `scripts/generate_report.py` 中的 `TYPE_ZH_MAP` 保持一致。

| type | type_zh | type | type_zh |
|------|---------|------|---------|
| `sqli` | SQL注入 | `nosqli` | SQL注入 |
| `xss_stored` | XSS注入 | `xss_reflected` | XSS注入 |
| `xss_dom` | XSS注入 | `ssrf` | SSRF |
| `xxe` | XXE注入 | `ssti` | 模板注入 |
| `rce` | 远程代码执行 | `command_injection` | 命令注入 |
| `insecure_deserialization` | 反序列化漏洞 | `crlf_injection` | CRLF注入 |
| `xslt_injection` | 注入攻击 | `el_injection` | 注入攻击 |
| `jndi_injection` | 注入攻击 | `prototype_pollution` | 原型污染 |
| `type_juggling` | 类型混淆 | `request_smuggling` | HTTP走私 |
| `auth_bypass` | 认证绕过 | `idor` | 越权访问 |
| `broken_access_control` | 访问控制缺陷 | `csrf` | CSRF |
| `weak_password` | 弱口令 | `brute_force` | 暴力破解 |
| `lfi` | 文件包含 | `rfi` | 文件包含 |
| `dir_traversal` | 目录穿越 | `file_upload` | 文件上传漏洞 |
| `webshell` | Webshell | | |
| `information_disclosure` | 信息泄露 | `open_redirect` | 开放重定向 |
| `url_redirect` | 开放重定向 | `cookie_security` | Cookie安全问题 |
| `git_exposure` | 信息泄露 | `directory_listing` | 信息泄露 |
| `waf_bypass` | WAF绕过 | `clickjacking` | 点击劫持 |
| `workflow_bypass` | 业务逻辑漏洞 | `race_condition` | 竞争条件 |
| `pricing_manipulation` | 业务逻辑漏洞 | `coupon_abuse` | 业务逻辑漏洞 |
| `subscription_hijack` | 业务逻辑漏洞 | | |
| `unknown` | 未分类 | | |
