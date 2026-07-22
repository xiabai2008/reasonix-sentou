# 破晓本地靶场指南（方案 1：Docker + vulhub）

> 目的：用**真实漏洞环境**验证破晓新增能力（JYso / SSTImap / dalfox / PEASS-ng），
> 而不是只在理论上"装了工具"。所有目标均为本地回环（127.0.0.1 / localhost），
> 已写入 `config/scope.yaml` 白名单，**破晓扫描本地靶机合法合规**。

> 🚀 **嫌逐条敲命令麻烦？** 直接用一键脚本：
> ```powershell
> powershell -ExecutionPolicy Bypass -File start-all-ranges.ps1
> ```
> 它会自动：检查 Docker → 缺 vulhub 就浅克隆 → 起全部靶场（含 DVWA/Juice Shop）→ 逐个校验 scope.yaml → 打印破晓目标清单。
> 加 `-WhatIf` 只看不跑，加 `-SkipDockerImages` 只起 vulhub 靶场。

---

## 0. 前置条件

```powershell
# 1) 安装 Docker Desktop（winget 或官网）
winget install -e --id Docker.DockerDesktop
# 安装后需重启一次，并确认设置里勾选 "Use the WSL 2 based engine"

# 2) 拉取靶场源码（已克隆到 C:/Tools/vulhub）
#    若需重新拉：git clone --depth 1 https://github.com/vulhub/vulhub.git C:/Tools/vulhub

# 3) 验证 Docker 可用
docker --version
docker run --rm hello-world
```

> ⚠️ 重启后首次使用需手动启动 Docker Desktop（系统托盘图标），否则 `docker` 命令会报 daemon 未启动。

---

## 1. 验证清单（新增能力 → 靶场 → 命令）

| 要验证的能力 | 靶场环境 | vulhub 路径 | 暴露端口 | 破晓目标 |
|:--|:--|:--|:--|:--|
| **JYso — JNDI 注入 / log4shell** | Apache Solr + Log4j (CVE-2021-44228) | `log4j/CVE-2021-44228` | 8983 | `http://127.0.0.1:8983` |
| **JYso — fastjson 反序列化** | fastjson 1.2.24 (JNDI) | `fastjson/1.2.24-rce` | 8090 | `http://127.0.0.1:8090` |
| **JYso — Spring4Shell** | Spring Core RCE (CVE-2022-22965) | `spring/CVE-2022-22965` | 8080 | `http://127.0.0.1:8080` |
| **SSTImap — SSTI 自动利用** | Flask SSTI | `flask/ssti` | 8000 | `http://127.0.0.1:8000` |
| **dalfox — XSS 专项扫描** | DVWA（低/中/高难度） | 独立镜像 | 8080 | `http://127.0.0.1:8080` |
| **dalfox + 逻辑漏洞** | OWASP Juice Shop | 独立镜像 | 3000 | `http://127.0.0.1:3000` |
| **PEASS-ng — 提权枚举** | 任意已拿下低权 shell 的 Linux 容器 | Metasploitable / 自建 | — | 在容器内跑 `linpeas.sh` |

---

## 2. 启动命令（逐条复制即可）

### 2.1 log4shell（验证 JYso）
```bash
cd C:/Tools/vulhub/log4j/CVE-2021-44228
docker-compose up -d
# 验证：curl http://127.0.0.1:8983
```

### 2.2 fastjson（验证 JYso 反序列化）
```bash
cd C:/Tools/vulhub/fastjson/1.2.24-rce
docker-compose up -d
# 验证：curl http://127.0.0.1:8090
```

### 2.3 Spring4Shell（验证 JYso 同类链）
```bash
cd C:/Tools/vulhub/spring/CVE-2022-22965
docker-compose up -d
# 验证：curl http://127.0.0.1:8080
```

### 2.4 Flask SSTI（验证 SSTImap）
```bash
cd C:/Tools/vulhub/flask/ssti
docker-compose up -d
# 验证：curl http://127.0.0.1:8000
```

### 2.5 DVWA（验证 dalfox XSS）
```bash
docker run -d -p 8080:80 --name dvwa vulnerables/web-dvwa
# 浏览器打开 http://127.0.0.1:8080 ，默认 admin/password，左下角 Create / Reset DB
# 验证：登录后进入 XSS (Reflected) / XSS (Stored) 模块
```

### 2.6 OWASP Juice Shop（验证 dalfox + 逻辑漏洞）
```bash
docker run -d -p 3000:3000 --name juice bkimminich/juice-shop
# 浏览器打开 http://127.0.0.1:3000
```

### 2.7 PEASS-ng 提权验证（容器内执行）
```bash
# 先拿下一个低权 shell（如通过上面任一 RCE），再在容器里：
curl -L https://github.com/carlospolop/PEASS-ng/releases/latest/download/linpeas.sh -o linpeas.sh
chmod +x linpeas.sh && ./linpeas.sh
# 破晓技能：skills/pentest_skills/privilege-escalation/SKILL.md
```

---

## 3. 让破晓扫靶机

```bash
# 先校验目标在授权范围内（必须返回 [ALLOW]）
python scripts/check-scope.py http://127.0.0.1:8983

# 再让破晓开跑（示例：针对 log4shell 靶机）
reasonix scan http://127.0.0.1:8983

# 专项：用 dalfox 扫 DVWA 的 XSS 点
reasonix run --skill dalfox-xss-scanner --target http://127.0.0.1:8080
```

---

## 4. 收尾

```bash
# 停止并清理所有靶场容器（避免常驻占用资源）
docker stop dvwa juice 2>/dev/null
docker rm dvwa juice 2>/dev/null
cd C:/Tools/vulhub/log4j/CVE-2021-44228 && docker-compose down
# ... 其余目录同理 docker-compose down
```

---

## 5. 备注

- 所有靶机端口发布在 `localhost`，`config/scope.yaml` 已授权 `127.0.0.1` / `localhost` /
  `172.17.0.0/16`（Docker 默认 bridge）。
- 若 `enforce: true` 下仍报 DENY，先跑 `python scripts/check-scope.py <目标>` 排查；
  解析器已修复"列表项行内注释"导致值被污染的 bug（见 commit 记录）。
- 在线靶场（HackTheBox / TryHackMe / picoCTF）作为 Docker 不可用时的备选，
  但需把对应公网 IP / 域名手动加入 `allowed_ips` / `allowed_domains`。
