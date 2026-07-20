---
name: bruteforce
description: 弱口令爆破 - 使用 fscan 对常见服务进行弱口令检测（SSH/RDP/MySQL/Redis 等）
---

# 弱口令爆破

使用 fscan 对常见服务进行弱口令检测。

## 使用方式

### 1. 默认爆破（fscan 自动检测开放服务并执行默认字典）
```
fscan -h 192.168.1.1
```

### 2. 指定用户名和密码
```
fscan -h 192.168.1.1 -user root -pwd "123456"
```

### 3. 使用字典文件
```
fscan -h 192.168.1.1 -userf users.txt -pwdf passwords.txt
```

### 4. 追加额外用户名/密码
```
fscan -h 192.168.1.1 -usera admin -pwda "admin,123456,password"
```

### 5. 指定服务端口
```
fscan -h 192.168.1.1 -p 22,3306,6379,3389
```

### 6. 使用 SSH 私钥
```
fscan -h 192.168.1.1 -sshkey id_rsa
```

### 7. 禁用爆破（仅扫描）
```
fscan -h 192.168.1.1 -nobr
```

## 支持爆破的服务

| 服务 | 端口 |
|------|------|
| SSH | 22 |
| RDP | 3389 |
| MySQL | 3306 |
| Redis | 6379 |
| MongoDB | 27017 |
| PostgreSQL | 5432 |
| FTP | 21 |
| SMB | 445 |
| Telnet | 23 |
| Oracle | 1521 |
| 以及其他 20+ 服务 |

## 常用参数

| 参数 | 说明 |
|------|------|
| `-user` | 用户名 |
| `-usera` | 额外用户名，逗号分隔 |
| `-userf` | 用户名字典文件 |
| `-pwd` | 密码 |
| `-pwda` | 额外密码，逗号分隔 |
| `-pwdf` | 密码字典文件 |
| `-upf` | 用户名:密码对文件 |
| `-nobr` | 禁用暴力破解 |
| `-socks5` | SOCKS5 代理 |

## 字典文件推荐位置

`C:\Tools\reasonix_sentou\config\` (可存放自定义字典)

## 工具路径

`C:\Tools\reasonix_sentou\tools\fscan.exe` (已加入 PATH)
