# Product Fingerprints - Admin Panel Detection

This file contains 100+ regex patterns for identifying specific admin panel products and systems.

## Generic Admin Indicators

These patterns indicate a generic admin panel or login page:

```regex
<title>.*后台.*</title>              # Contains "backend" in title
<title>.*登录.*</title>              # Contains "login" in title
<title>.*管理.*</title>              # Contains "management" in title
<title>.*控制面板.*</title>          # Contains "control panel"
<title>.*\bLogin\b.*</title>         # English "Login" in title
<title>.*登入.*</title>              # Contains "login" (variant)
<title>.*平台.*</title>              # Contains "platform"
<title>.*admin.*</title>             # Contains "admin"
<title>.*OA协同.*</title>            # Contains "OA collaboration"
<title>.*身份认证平台.*</title>      # Contains "identity auth platform"
<title>.*系统</title>                # Contains "system"
<title>.*低代码.*(平台|中台)</title> # Contains "low-code platform"
<div.*后台.*</div>
<h1.*登录.*</h1>
<h1.*后台.*</h1>
<h2.*登录.*</h2>
<h2.*后台.*</h2>
<button.*登录</button>
<button.*登录系统</button>
<div.*>(\s+)?(账号)?登录(\s+)?</div>
"\b系统登录\b"                       # "System login"
<a.*>忘记密码</a>                    # "Forgot password" link
重新登录                             # "Re-login"
扫码登录                             # "Scan QR to login"
"input-password"
auth.password.*Authorization
```

## Infrastructure & DevOps Tools

### Nacos
```regex
<title>Nacos</title>
```

### Druid (Alibaba Database Connection Pool)
```regex
<title>druid.*</title>
```

### XXL-JOB (Distributed Task Scheduling)
```regex
<title>任务调度中心</title>
```

### Jenkins (CI/CD)
```regex
<title>Sign in \[Jenkins\]</title>
```

### Grafana (Monitoring)
```regex
<title>Grafana</title>
```

### Portainer (Docker Management)
```regex
<title>Portainer</title>
```

### Harbor (Container Registry)
```regex
<title>Harbor</title>
```

### Kubernetes Dashboard
```regex
<title>Kubernetes Dashboard</title>
```

### MinIO Console (Object Storage)
```regex
<title>MinIO Console</title>
```

### nginxWebUI
```regex
<title>nginxWebUI</title>
```

### DSS (Data Sphere Studio)
```regex
<title>DSS</title>
```

### Dubbo Admin
```regex
<title>Dubbo Admin</title>
```

### Kafka Manager
```regex
<title>Kafka Manager</title>
```

### Swagger UI
```regex
swagger-ui.html
```

### GLPI (IT Asset Management)
```regex
<title>身份验证 - GLPI</title>
```

### rConfig (Network Configuration)
```regex
<title>rConfig - Configuration Management</title>
```

## Application Servers

### Oracle WebLogic
```regex
<title>Oracle WebLogic Server Administration Console</title>
Welcome to Weblogic Application Server
```

### JBoss
```regex
<title>JBoss
<title>Welcome to JBoss
```

### GlassFish
```regex
<title>GlassFish
```

## CMS Platforms

### WordPress
```regex
<title>.*WordPress</title>
```

### GeoServer
```regex
<title>GeoServer
```

## Chinese Enterprise Systems

### 万户网络 (Wanhu ezOFFICE)
```regex
<title>万户网络
<title>Wanhu ezOFFICE</title>
```

### 金蝶云 (Kingdee Cloud)
```regex
<title>金蝶云
```

### 致远 (Seeyon/Zhiyuan OA)
```regex
<title>致远
sys/ui/extend/theme/default/style/profile.css
/Scripts/jquery.landray.dialog.js
```

### 泛微 (Weaver OA)
```regex
content="Weaver E-Mobile
<title>泛微云桥e-Bridge</title>
```

### 用友 (Yonyou)
```regex
<title>YONYOU NC</title>
<title>Yonyou UAP</title>
<TITLE>用友U8CRM</TITLE>
<title>用友GRP-U8
<title>U8Cloud</title>
```

### 畅捷通 (Chanjet)
```regex
<TITLE>畅捷通CRM</TITLE>
<title>畅捷通 T+</title>
```

### iOffice
```regex
src=/iOffice/js/iOffice.js
<title>iOffice.net</title>
```

### Jeecg-Boot (Low-Code Platform)
```regex
<title>Jeecg-Boot快速开发平台</title>
<title>Jeecg-Boot 快速开发平台</title>
<title>JeecgBoot 企业级低代码平台</title>
<title>Jeecg-Boot 企业级快速开发平台</title>
<title>Jeecg 快速开发平台</title>
<title>JeecgBoot 企业级快速开发平台</title>
```

### 金和协同 (Jinhe Collaboration)
```regex
金和协同管理平台
```

### 汉得SRM (Hand SRM)
```regex
<title>汉得SRM云平台</title>
```

### 明源地产ERP (Mingyuan Real Estate ERP)
```regex
<title>明源地产ERP</title>
```

### 民政OA (Civil Affairs OA)
```regex
民政OA - v\d+\.\d+
```

### 碧海威L7 (BiHaiWei L7 Router)
```regex
<title>碧海威L7云路由无线运营版</title>
```

## Security Products & VPN

### 深信服 (Sangfor)
```regex
<title>ad.sangfor.com
<title>SANGFOR 数据中心</title>
<title>SANGFOR | NGAF</title>
<title>SANGFOR | AF 
```

### 奇安信VPN (QiAnXin VPN)
```regex
<title>奇安信VPN</title>
```

### 网神SecGate (WangShen SecGate)
```regex
<title>网神SecGate 3600防火墙</title>
```

### MilesightVPN
```regex
<title>MilesightVPN</title>
```

### 明御安全网关 (MingYu Security Gateway)
```regex
<title>明御安全网关</title>
```

### 360新天擎 (360 TianQing)
```regex
<title>360新天擎</title>
```

### 博华网龙 (BoHua WangLong)
```regex
<title>博华网龙信息安全一体机</title>
<title>博华网龙防火墙</title>
```

### FortiManager
```regex
<title>FortiManager
```

### 华测监测预警 (HuaCe Monitoring)
```regex
<span id="sysName">华测监测预警系统2.2</span>
```

## Email & Messaging Systems

### Microsoft Exchange OWA
```regex
<title>Microsoft Exchange - Outlook Web Access</title>
```

### Dahua
```regex
dahuaDefined/headCommon.js
```

## Other Products

### JumpServer (Bastion Host)
```regex
<title>JumpServer</title>
```

### Jira
```regex
<title>System Dashboard - Jira-Test</title>
```

### Confluence
```regex
<title>Log In - Confluence</title>
```

### RabbitMQ
```regex
rabbitmqlogo.svg
```

### 移动系统管理 (Mobile System Management)
```regex
</span>移动系统管理
```

### 孚盟云 (FuMeng Cloud)
```regex
孚盟云 - 用户登录
```

### 智能云网管 (Smart Cloud Network)
```regex
<title>智能云网关注册管理平台</title>
```

### Reporter
```regex
<title>Login @ Reporter</title>
```

### SSO Server (Single Sign-On)
```regex
zz-sso-server-web
```

### Login Logo Pattern
```regex
/images/login_logo@2x.png
```

### Hidden Easter Egg
```regex
你在看什么呢？我写的代码好看吗
```

### Babel Polyfill
```regex
<script src=/cdn/babel-polyfill/polyfill_
```

### URL-based Redirect
```regex
/local/connect_notfound/connect_notfound\.html\?from=
```

## Usage Notes

1. All patterns are case-insensitive unless specified
2. Match against the full HTML response body
3. Multiple pattern matches increase confidence
4. Product-specific patterns have higher confidence than generic patterns
5. Total patterns: 100+
6. Combine with login page indicators and CAPTCHA detection for comprehensive analysis
