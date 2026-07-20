# http_test.py — 纯 Python HTTP 发包工具完整用法

## 概述

`http_test.py` 是 vibe-pentest 渗透测试中**唯一推荐使用的 HTTP 发包工具**。

- 基于 `httpx` 的纯 Python 实现，无外部二进制依赖
- 智能 Body 编码（自动推断 charset、form URL-encode、JSON、二进制）
- 连接探针（DNS / TCP / TLS 独立计时）
- 响应体过滤和瘦身（正则过滤 + 行/字节截断），显著减少 Token 消耗
- 重复请求 + 聚合统计（盲注 / 时序测试）
- 自动字符集检测和响应解码

**依赖**：`pip install httpx charset-normalizer`

**位置**：`{SKILL_ROOT}/scripts/http_test.py`

---

## 快速开始

### 基础 GET 请求
```bash
python {SKILL_ROOT}/scripts/http_test.py \
  --url "http://target.com/path" \
  --method GET \
  --show-command \
  --show-summary \
  --include-headers \
  --response-max-lines 80
```

### POST JSON 数据
```bash
python {SKILL_ROOT}/scripts/http_test.py \
  --url "http://target.com/api/endpoint" \
  --method POST \
  --data '{"key":"value"}' \
  --headers '{"Content-Type":"application/json"}' \
  --show-command \
  --show-summary \
  --include-headers \
  --response-max-lines 80
```

### POST 表单数据
```bash
python {SKILL_ROOT}/scripts/http_test.py \
  --url "http://target.com/login" \
  --method POST \
  --data "username=admin&password=test123" \
  --show-command \
  --show-summary \
  --include-headers \
  --response-max-lines 80
```

---

## 参数速查表

### 请求控制

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--url` | string | (必填) | 目标URL |
| `--method` | string | `GET` | HTTP方法：GET/POST/PUT/DELETE/PATCH/OPTIONS/HEAD |
| `--data` | string | `""` | 请求体；JSON字符串 / form数据 / `@file` 加载文件 / `@-` 从stdin读取 |
| `--headers` | object/string | `""` | 请求头，支持 JSON 字典 `{"Key":"Val"}` 或 `"Key: Val"` 字符串 |
| `--cookies` | string | `""` | Cookie字符串：`"PHPSESSID=xxx; token=yyy"` |
| `--user-agent` | string | `""` | 自定义 User-Agent |
| `--proxy` | string | `""` | 代理地址：`http://127.0.0.1:8080` 或 `socks5://127.0.0.1:1080` |
| `--timeout` | float | `60` | 超时秒数（支持小数） |
| `--follow-redirects` | bool | `false` | 跟随 HTTP 重定向 |
| `--allow-insecure` | bool | `false` | 忽略 TLS 证书错误（verify=False） |
| `--auto-encode-url` | bool | `false` | URL 特殊字符自动编码 |

### 响应输出控制

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--show-command` | bool | `true` | 输出请求概览（方法/URL/Headers/Body） |
| `--show-summary` | bool | `true` | 输出性能指标（DNS/TCP/TLS/TTFB/Total/Speed） |
| `--include-headers` | bool | `true` | 输出响应头（状态行+所有Header） |
| `--verbose-output` | bool | `false` | 输出额外调试信息 |
| `--debug` | bool | `false` | Body 编码处理细节 |
| `--response-encoding` | string | `""` | 强制响应解码字符集（如 `gbk`、`shift_jis`） |
| `--download` | string | `""` | 响应体保存到本地文件，支持 `{i}` 序号占位符 |

### 响应体过滤（Token 优化核心功能）

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--response-filter` | regex | `""` | 正则过滤响应体（默认按行匹配） |
| `--response-filter-mode` | string | `line` | 过滤模式：`line`(按行)/`multiline`(跨行块)/`full`(全文DOTALL) |
| `--response-filter-invert` | bool | `false` | 反向过滤：输出不匹配的行（剔除HTML噪音） |
| `--response-filter-ignore-case` | bool | `false` | 正则忽略大小写（等价 `(?i)`） |
| `--response-max-lines` | int | `0` | stdout最多输出行数（0=不限制） |
| `--response-max-bytes` | int | `0` | stdout UTF-8字节上限（0=不限制） |
| `--response-preview-lines` | int | `5` | filter 零命中时的预览行数 |
| `--response-context-lines` | int | `0` | line模式命中行上下各保留N行上下文（类似 grep -C） |

### 高级功能

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--repeat` | int | `1` | 重复请求次数（≥1） |
| `--delay` | float | `0` | 重复请求间隔秒数（支持小数） |
| `--additional-args` | string | `""` | httpx.Client额外选项：`"http2=true cert=/path/cert.pem verify=false max_redirects=5"` |

---

## 渗透测试场景模板

### 场景1: 基础信息探测（GET，完整输出）

```bash
python {SKILL_ROOT}/scripts/http_test.py \
  --url "TARGET_URL" \
  --method GET \
  --show-command \
  --show-summary \
  --include-headers \
  --response-max-lines 80
```

### 场景2: SQL 注入测试（POST，错误过滤）

```bash
python {SKILL_ROOT}/scripts/http_test.py \
  --url "TARGET_URL" \
  --method POST \
  --data "id=1' OR '1'='1" \
  --headers '{"Content-Type":"application/x-www-form-urlencoded"}' \
  --response-filter '(?i)(error|exception|syntax|mysql|sql|database|warning|debug|trace|stack|fatal|ora-|sqlstate|postgresql)' \
  --response-filter-mode line \
  --response-context-lines 2 \
  --response-max-lines 40 \
  --show-command \
  --show-summary \
  --include-headers
```

### 场景3: XSS 测试（payload 回显检测）

```bash
python {SKILL_ROOT}/scripts/http_test.py \
  --url "TARGET_URL" \
  --method GET \
  --data "search=<script>alert('xss_test')</script>" \
  --response-filter '<script>alert' \
  --response-filter-mode full \
  --response-max-lines 20 \
  --show-command \
  --include-headers
```

### 场景4: 时间盲注（重复+延迟+聚合统计）

```bash
python {SKILL_ROOT}/scripts/http_test.py \
  --url "TARGET_URL" \
  --method GET \
  --repeat 5 \
  --delay 0.5 \
  --show-summary \
  --response-max-lines 0
```

### 场景5: 认证测试（带Cookie）

```bash
python {SKILL_ROOT}/scripts/http_test.py \
  --url "TARGET_URL" \
  --method GET \
  --cookies "PHPSESSID=xxx; token=yyy" \
  --show-command \
  --show-summary \
  --include-headers \
  --response-max-lines 80
```

### 场景6: SSRF 内网探测（快速超时+错误过滤）

```bash
python {SKILL_ROOT}/scripts/http_test.py \
  --url "http://127.0.0.1:6379/" \
  --method GET \
  --timeout 5 \
  --response-filter '(?i)(redis|connection|refused|timeout|error)' \
  --response-filter-mode line \
  --show-summary \
  --include-headers
```

### 场景7: 文件上传测试（@file 加载二进制）

```bash
python {SKILL_ROOT}/scripts/http_test.py \
  --url "TARGET_URL/upload" \
  --method POST \
  --data @shell.php \
  --headers '{"Content-Type":"multipart/form-data"}' \
  --show-command \
  --show-summary \
  --include-headers \
  --response-max-lines 40
```

### 场景8: 路径穿越/LFI 测试（响应内容提取）

```bash
python {SKILL_ROOT}/scripts/http_test.py \
  --url "TARGET_URL/download?file=../../etc/passwd" \
  --method GET \
  --response-filter '(?i)(root:|nobody:|daemon:|bin:.*:bin/bash)' \
  --response-filter-mode line \
  --response-context-lines 1 \
  --show-command \
  --show-summary \
  --include-headers
```

### 场景9: IDOR 越权测试（两账号对比）

```bash
# 账号A请求
python {SKILL_ROOT}/scripts/http_test.py \
  --url "TARGET_URL/api/user/1001/profile" \
  --method GET \
  --cookies "session=COOKIE_USER_A" \
  --show-command \
  --show-summary \
  --include-headers \
  --response-max-lines 80

# 账号B请求（用A的资源ID）
python {SKILL_ROOT}/scripts/http_test.py \
  --url "TARGET_URL/api/user/1001/profile" \
  --method GET \
  --cookies "session=COOKIE_USER_B" \
  --show-command \
  --show-summary \
  --include-headers \
  --response-max-lines 80
```

### 场景10: API 参数篡改（JSON body 变体）

```bash
# 基线请求
python {SKILL_ROOT}/scripts/http_test.py \
  --url "TARGET_URL/api/order" \
  --method POST \
  --data '{"user_id":1,"role":"user"}' \
  --headers '{"Content-Type":"application/json"}' \
  --show-command --show-summary --include-headers --response-max-lines 80

# 变体请求（提权尝试）
python {SKILL_ROOT}/scripts/http_test.py \
  --url "TARGET_URL/api/order" \
  --method POST \
  --data '{"user_id":1,"role":"admin"}' \
  --headers '{"Content-Type":"application/json"}' \
  --show-command --show-summary --include-headers --response-max-lines 80
```

### 场景11: 指纹识别（提取 Server/技术栈信息）

```bash
python {SKILL_ROOT}/scripts/http_test.py \
  --url "TARGET_URL" \
  --method GET \
  --include-headers \
  --response-filter '(?i)(server:|x-powered-by:|x-aspnet|generator|apache|nginx|iis|tomcat|jetty|spring|django|laravel|wordpress|php)' \
  --response-filter-mode line \
  --response-context-lines 0 \
  --show-summary
```

### 场景12: 竞争条件测试（高并发短间隔）

```bash
python {SKILL_ROOT}/scripts/http_test.py \
  --url "TARGET_URL/api/redeem-coupon" \
  --method POST \
  --data '{"coupon_code":"TEST001","user_id":1}' \
  --headers '{"Content-Type":"application/json"}' \
  --repeat 10 \
  --delay 0.05 \
  --show-summary \
  --response-max-lines 5
```

---

## 响应过滤最佳实践

### 原则：永远不要让整页 HTML 进入上下文

```bash
# ❌ 错误：整页HTML灌入上下文，浪费Token
python http_test.py --url "http://target.com/page" --method GET

# ✅ 正确：限制行数 + 关键词过滤
python http_test.py --url "http://target.com/page" --method GET \
  --response-max-lines 80 \
  --response-filter '(?i)(error|warning|version|token|password|admin|debug|exception|trace)'
```

### 常用过滤正则模板

| 用途 | 正则模式 |
|------|---------|
| SQL注入错误 | `'(?i)(error\|syntax\|mysql\|sql\|warning\|ora-\|sqlstate\|postgresql\|debug\|trace\|fatal\|exception)'` |
| XSS回显 | `'<script'` 或 `'(?i)(alert\|onerror\|onload\|onclick\|eval)'` |
| 信息泄露 | `'(?i)(password\|api_key\|token\|secret\|private\|internal\|admin\|root:\|.git)'` |
| 技术栈指纹 | `'(?i)(server:\|x-powered-by:\|generator\|apache\|nginx\|iis\|tomcat\|php\|django\|spring)'` |
| SSRF内网探测 | `'(?i)(redis\|connection\|refused\|timeout\|banner\|welcome\|ubuntu\|debian\|centos)'` |
| 文件包含 | `'(?i)(root:\|<?php\|\[extensions\]\|daemon:\|nobody:\|boot.ini\|bin/bash)'` |
| 认证绕过 | `'(?i)(welcome\|dashboard\|admin\|profile\|success\|authorized\|200 OK.*content-length: [1-9])'` |

### 无过滤结果的处理

当 `--response-filter` 零命中时，工具会自动输出前 `--response-preview-lines` 行（默认5行）作为预览，帮助判断是否需要调整正则。输出会标记 `[body] no regex match; showing preview:`.

### 二进制/大响应处理

- 使用 `--download output.bin` 将响应体保存到本地文件
- 使用 `--response-max-lines 3` 只摘要输出
- 多次请求时用 `--download "run-{i}.bin"` 自动序号区分
