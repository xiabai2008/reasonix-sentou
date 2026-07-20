---
name: report-gen
description: 报告生成 - 将 fscan 扫描结果转换为格式化报告，方便输出和归档
---

# 报告生成

将 fscan 扫描结果以不同格式输出，便于整理和分析。

## 输出格式

### 1. TXT 格式（默认）
```
fscan -h 192.168.1.0/24 -f txt -o result.txt
```

### 2. JSON 格式（便于程序解析）
```
fscan -h 192.168.1.0/24 -f json -o result.json
```

### 3. CSV 格式（可导入 Excel）
```
fscan -h 192.168.1.0/24 -f csv -o result.csv
```

### 4. 静默模式（减少输出干扰）
```
fscan -h 192.168.1.0/24 -silent -f json -o result.json
```

### 5. 仅将结果写入文件（不显示到控制台）
```
fscan -h 192.168.1.0/24 -silent -o result.txt
```

## 输出文件管理

建议将扫描结果统一保存到工作目录：

```
project/
├── result.txt       # 扫描结果
├── result.json      # JSON 格式结果
├── targets.txt      # 目标列表
└── fscan_debug.log  # 调试日志（-debug 时生成）
```

## 扫描结果解读

fscan 输出包含：

| 类型 | 说明 |
|------|------|
| `[+]` | 成功/开放信息 |
| `[-]` | 失败/错误信息 |
| `[*]` | 进度/状态信息 |
| 端口开放 | `192.168.1.1:3306 open` |
| 服务识别 | `192.168.1.1:3306 MySQL 5.7` |
| 弱口令 | `mysql://root:root@192.168.1.1:3306` |
| 漏洞 | `[+] poc-go thinksphp-lang-rce` |

## 工具路径

`C:\Tools\reasonix_sentou\tools\fscan.exe` (已加入 PATH)
