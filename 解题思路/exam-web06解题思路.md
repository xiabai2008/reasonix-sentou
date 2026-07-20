# exam-web06 解题思路

## 题目信息

| 项目 | 内容 |
|------|------|
| 题目名称 | exam-web06 |
| 分值 | 100.0 |
| 难度 | 容易 |
| 目标 | 183.129.189.62:21313 (映射到 10.3.4.143:10006) |
| 最终 Flag | `flag{c7b416d513d2815e427a23bdf3438302}` |

## 解题过程

---

### 第 1 步：信息收集 — 识别技术栈

访问 `http://183.129.189.62:21313/`，首页只有登录和注册链接。

HTTP 响应头关键信息：
```
Server: Werkzeug/2.0.3 Python/3.9.24
```

**Flask 应用！** 首页内容：`<a href='/login'>登录</a> | <a href='/register'>注册</a>`

---

### 第 2 步：注册并登录

注册账号 `hzrtest2/test123`，登录后获取 Flask session cookie：
```
session=eyJ1c2VyX2lkIjoxNTR9.alYW2w.cxSoByS9LmFchftUuRvCmIG0KM0
```

解码 session：`{"user_id": 154}`

登录后首页显示：
```
已登录，当前用户ID: 154 | 查看我的信息 | 退出
```

---

### 第 3 步：发现 IDOR 漏洞

`/info` 页面显示当前用户信息。测试 `id` 参数：
- `/info?id=2` → 显示 test1 的信息（不是自己的！）
- `/info?id=3` → 显示 test2 的信息

**IDOR 漏洞确认！** 可以通过修改 `id` 参数查看任意用户信息。

---

### 第 4 步：扫描用户 ID 寻找 flag

批量扫描 ID 1-154，未发现 flag。大部分用户的私密信息都是 "普通用户 xxx 的私密信息"。

同时发现了 admin 用户（ID=6），并爆破出密码 `admin:admin123`，但 admin 也是普通用户，没有特殊权限。

---

### 第 5 步：扩大扫描范围 — 找到 flag！

尝试高 ID 值，在 ID=10086 找到 flag：

```
ID: 10086
用户名: zhaowendao
私密信息: Flag: flag{c7b416d513d2815e427a23bdf3438302}
```

---

## 漏洞成因

应用在 `/info` 端点直接使用用户可控的 `id` 参数查询数据库，没有验证请求者是否有权限查看目标用户信息：

```python
@app.route('/info')
def info():
    user_id = request.args.get('id', session.get('user_id'))
    user = db.execute('SELECT * FROM users WHERE id = ?', (int(user_id),)).fetchone()
    return render_template('info.html', user=user)
```

虽然 `id` 参数做了整数校验（防止 SQL 注入），但没有做**授权校验** — 任何登录用户都可以查看其他用户的私密信息。

## 关键教训

1. **IDOR 扫描范围要够大** — 不能只扫低 ID，flag 可能藏在任意 ID（本题是 10086）
2. **常见高 ID 值值得优先测试** — 999, 1000, 9999, 10086, 8888 等
3. **Flask session 可解码但不可伪造** — 没有密钥就无法修改 session，不要在破解密钥上浪费时间
4. **admin 弱口令（admin:admin123）虽然是突破口，但本题核心是 IDOR**

## 踩坑记录

| 尝试 | 结果 | 结论 |
|------|------|------|
| SSTI（用户名注入 `{{7*7}}`） | 不执行，原样显示 | 用户名未通过 Jinja2 渲染 |
| SQL 注入（id 参数） | "无效的用户ID" | id 参数有整数校验 |
| SQL 注入（登录/注册） | 参数化查询，注入无效 | 后端使用了参数化查询 |
| Flask session 伪造 | 签名验证严格 | 无法在没有密钥的情况下伪造 |
| 爆破 admin 密码 | admin:admin123 | admin 只是普通用户，无额外权限 |
| 扫描 ID 1-154 | 无 flag | flag 在高 ID (10086) |
