---
name: intel-gather
description: 信息收集 - 目标资产发现、子域名枚举、端口开放探测等侦查手段
---

# 信息收集

渗透测试前期信息收集阶段的方法和工具使用。

## 1. 存活探测（ICMP/ARP）

使用 fscan 的 ICMP 模式快速发现存活主机：

```
# 仅进行存活探测
fscan -h 192.168.1.0/24 -nobr -nopoc -np

# 禁用 ping 的 TCP 补充探测
fscan -h 192.168.1.0/24 -nobr -nopoc -ntp
```

## 2. 端口扫描

```
# 快速扫描常见端口
fscan -h 192.168.1.1/24 -nobr -nopoc

# 全端口扫描（使用自定义端口列表）
fscan -h 192.168.1.1 -p 1-65535 -t 1000
```

## 3. 服务识别

fscan 自动识别开放端口上的服务类型：

```
# 自动识别 + 详细输出
fscan -h 192.168.1.1 -debug
```

## 4. DNS 日志记录

```
fscan -h target.com -dns
```

## 5. 资产信息（通过配置信息）

`C:\Tools\reasonix_sentou\config\` 目录可存放：

| 文件 | 用途 |
|------|------|
| `targets.txt` | 目标 IP/域名列表 |
| `passwords.txt` | 常见弱口令字典 |
| `users.txt` | 常见用户名字典 |
| `ports.txt` | 自定义端口列表 |

## 信息收集 checklist

- [ ] 目标 IP 存活探测
- [ ] 开放端口与服务识别
- [ ] 操作系统指纹识别
- [ ] Web 中间件/框架识别（fscan 自动检测）
- [ ] 域名/DNS 信息
- [ ] 旁站/C 段资产

## 工具路径

`C:\Tools\reasonix_sentou\tools\fscan.exe` (已加入 PATH)
