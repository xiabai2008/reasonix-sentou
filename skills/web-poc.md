---
name: web-poc
description: Web 漏洞检测与 POC 扫描 - 对 Web 服务进行漏洞扫描和 POC 检测
---

# Web 漏洞检测与 POC 扫描

使用 fscan 对 Web 目标进行漏洞检测。

## 使用方式

### 1. 单个 URL 扫描
```
fscan -u http://target.com
```

### 2. URL + 全量 POC
```
fscan -u http://target.com -full
```

### 3. URL 文件批量扫描
```
fscan -uf urls.txt
```

### 4. 指定端口 + POC
```
fscan -h 192.168.1.1 -p 80,443,8080 -full
```

### 5. 禁用 POC（仅端口扫描）
```
fscan -h 192.168.1.1 -nopoc
```

### 6. 指定 POC 名称
```
fscan -u http://target.com -pocname "thinkphp"
```

### 7. 自定义 POC 脚本路径
```
fscan -u http://target.com -pocpath ./pocs
```

### 8. 带 Cookie 扫描
```
fscan -u http://target.com -cookie "session=abc123"
```

## 常用参数

| 参数 | 说明 |
|------|------|
| `-u` | 目标 URL |
| `-uf` | URL 列表文件 |
| `-full` | 全量 POC 扫描 |
| `-pocname` | 指定 POC 名称 |
| `-pocpath` | POC 脚本路径 |
| `-cookie` | HTTP Cookie |
| `-ua` | 自定义 User-Agent |
| `-proxy` | HTTP 代理 |
| `-nopoc` | 禁用 POC |
| `-wt` | Web 超时时间（默认5秒）|

## 工具路径

`C:\Tools\reasonix_sentou\tools\fscan.exe` (已加入 PATH)
