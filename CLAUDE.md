# Claude Code — 启动说明

> 本仓库是**多 Agent 通用的 AI 渗透作战工作台**：同一份 persona、技能库、经验系统与证据闭环，
> 可被 Claude Code / Codex / OpenCode / Cline / Trae / WorkBuddy 等 Agent 读取使用。

## 请先读取

- **`AGENTS.md`** — 核心作战说明（persona、工具路线、技能路由、安全规则、经验系统）。这是全量权威文档。

## 技能目录

技能位于 `skills/pentest_skills/<name>/SKILL.md`，带标准 YAML frontmatter（`name` + `description`），
与 Anthropic Agent Skills 格式兼容。运行以下命令即可把技能链接/复制到 Claude Code 约定目录：

```bash
python scripts/setup-agent-links.py --agents claude --apply
```

## 本项目在 Claude Code 中的用法

- 你直接读取 `AGENTS.md` 进入"渗透专家"角色。
- 遇到具体漏洞场景时，按需加载 `skills/pentest_skills/<skill>/SKILL.md`（节省 token，勿全量读）。
- 经验沉淀：任务结束后按 `AGENTS.md` 的"经验积累系统"写入 `memory/pentest-experience-NNN.md`。
- 反幻觉铁律：任何结论必须有 `[EVID-<任务>-<NNN>]` 证据号，否则标记 `[UNVERIFIED]`，见 `evidence_pack`。

## 安全边界

- 仅授权目标；扫描前校验 `config/scope.yaml`。
- 高危操作需人工确认；不扫描 `.gov`/`.mil`；不访问 `169.254.169.254`。