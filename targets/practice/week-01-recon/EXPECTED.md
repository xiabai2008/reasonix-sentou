# Week 1 — 预期发现

> ⚠️ **练习完成后再看！** 先自己做完 `TARGET.md` 中的任务，再来对照。

## DVWA (localhost:8080)

### 技术栈
- Web Server: Apache/2.4.x
- 语言: PHP (X-Powered-By: PHP/5.x 或 7.x)
- 数据库: MySQL 5.7 (从报错或 setup 页面推断)
- 关键路径:
  - `/setup.php` — 数据库初始化页面
  - `/vulnerabilities/` — 漏洞练习目录
  - `/config/` — 配置文件目录（可能可读）
  - `/phpinfo.php` — PHP 信息页面
  - `/robots.txt` — 通常包含敏感路径提示

### 信息收集亮点
- `httpx -tech-detect` 会识别出 PHP
- robots.txt 可能包含 `/vulnerabilities/` 等路径
- 响应头中的 Server 字段暴露 Apache 版本
- setup.php 页面不需要认证即可访问（首次安装时）

## Juice Shop (localhost:3000)

### 技术栈
- 框架: Angular (SPA, 单页应用)
- 运行时: Node.js + Express
- 前端特征:
  - 所有内容通过 JavaScript 动态渲染
  - 查看网页源码几乎看不到有用内容
  - API 请求通过 `/api/` 路径

### 信息收集要点
- 这是一个 **SPA**，传统目录爆破效果很差
- 应关注 `/api/` 路径和前端 JS 文件
- `/robots.txt` 包含有趣路径
- `/ftp/` 目录可能暴露文件
- 需要分析 Angular 打包后的 JS 文件找 API 端点

## 常见遗漏

| 遗漏项 | 为什么重要 |
|:-------|:----------|
| robots.txt | 开发者常在此列出不想被搜索引擎索引的路径 |
| sitemap.xml | 可能包含站点结构线索 |
| 响应头 Server/X-Powered-By | 直接暴露版本，匹配已知 CVE |
| favicon.ico 哈希 | 可指纹识别 CMS 类型 |
| 错误页面信息 | 500/404 页面常泄露框架版本 |
