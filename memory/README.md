# Reasonix 经验记忆库

`memory/` 用来保存渗透任务后的经验沉淀。它不是普通日志目录，而是 Reasonix 下次启动和分析相似目标时可以参考的长期记忆层。

## 目录结构

```text
memory/
├── README.md
├── pentest-experience-001.md
├── attack-chains.yaml
├── cost-stats.csv
└── templates/
    ├── pentest-experience-template.md
    └── attack-chain-template.yaml
```

## 记录原则

每次任务结束后，优先新增一个 `pentest-experience-NNN.md` 文件。编号按已有文件递增，例如已有 `pentest-experience-001.md`，下一次写 `pentest-experience-002.md`。

经验记录要包含：

- 目标概况
- 授权范围
- 技术栈和资产特征
- 成功手法
- 失败记录
- 关键口令或关键线索
- 工具链效果
- 攻击链
- 成本与缓存数据
- 可沉淀到 `AGENTS.md` 或 `SKILL.md` 的方法

## 使用方式

遇到相似目标时，Reasonix 应先检索本目录：

```text
EyouCMS / ThinkPHP / Flask / JWT / Webpack / SourceMap / 内网弱口令
```

如果经验多次复用，应升级到：

- `AGENTS.md` 的常见任务速查
- 对应 `skills/pentest_skills/*/SKILL.md`
- `skills/references/*`

## 成本记录

任务结束后在 Reasonix 中执行：

```text
/stats
```

把结果追加到 `cost-stats.csv`，用于长期分析 DeepSeek prefix-cache 的真实收益。

## 攻击链记录

跨漏洞组合写入 `attack-chains.yaml`。例如：

```text
目录遍历 → 配置泄露 → 数据库弱口令 → WebShell
JWT 低权限账号 → API 越权 → 横向读取用户数据
SourceMap 泄露 → 接口发现 → 权限矩阵分析 → BOLA
```

攻击链记录越清晰，Reasonix 后续越容易复用相似路径。
