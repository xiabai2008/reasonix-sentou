# 贡献指南

感谢你对 **DawnForge（破晓）** 的兴趣！这是一个多 Agent 通用的 AI 渗透作战工作台。
请遵守以下规范，让协作更顺畅。

## 行为准则

- 本项目**仅用于授权目标**。任何涉及未授权扫描、爆破、利用的贡献/示例将不被接受。
- 不提交敏感数据：靶场凭据、真实目标 IP、扫描结果、报告、证据一律不入库。
- 尊重第三方版权：字典与改编技能需保留原始版权声明。

## 如何提交

1. Fork 仓库，从 `master` 切分支。
2. 遵循目录约定（见下）。
3. 提交信息使用 Conventional Commits，如 `feat:`, `fix:`, `docs:`。
4. 开 PR 前先跑 `python scripts/health-check.py` 确认环境健康。
5. PR 描述说明改动动机与验证方式。

## 目录与新增约定

| 新增内容 | 放置位置 |
|:---------|:---------|
| 新漏洞技能 | `skills/pentest_skills/<name>/SKILL.md`（带 YAML frontmatter）|
| 新工具 | `config/tools-manifest.json` 登记 + `bin/` 快捷入口 |
| 新经验 | `memory/pentest-experience-NNN.md`，并 `python scripts/exp-add.py` 入索引 |
| 新脚本 | `scripts/` |
| 新配置模板 | `templates/agent-configs/` |

## 技能命名规范

- 目录名 = 小写连字符，如 `sqli-sql-injection`。
- `SKILL.md` 顶部必须有 `name` 与 `description` 两个 frontmatter 字段。
- description 用英文写（多 Agent 兼容性），正文可为中英混合。

## 测试

- 无自动化测试套件时，至少提供手动验证命令。
- 涉及证据闭环的改动，用 mock 数据跑通 `harvest → archive → report`。

## 问题反馈

- Bug：开 issue，附复现步骤与工具版本。
- 安全漏洞：见 `SECURITY.md`，请走私有上报，勿公开。