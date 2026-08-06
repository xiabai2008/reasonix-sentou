# DawnForge 经验记忆库

> **每一位使用者拥有属于自己的私有经验库。仓库只提交通用骨架，不包含任何个人经验内容。**

`memory/` 用来保存渗透任务后的经验沉淀。它是 DawnForge 下次启动和分析相似目标时可以参考的长期记忆层。

## 设计原则：经验是私有的

每个人的使用场景、目标、目标环境都不同，因此**经验库是个人资产**：

- 仓库中**只保留通用模板**（`templates/`）与说明文档（`README.md`）。
- `pentest-experience-NNN.md`、`attack-chains.yaml`、`cost-stats.csv`、`experiences-index.yaml` 等**个人经验文件已被 `.gitignore` 忽略，永远不会提交到开源仓库**。
- 克隆仓库后，你会得到一份干净的骨架，从第一次实战开始建立属于你自己的经验库。

## 目录结构

```text
memory/
├── README.md               说明文档（入库）
└── templates/              通用模板（入库，所有用户的起点）
    ├── pentest-experience-template.md
    └── attack-chain-template.yaml

# 以下为本地私有内容，不会入库（.gitignore 已忽略）：
#   pentest-experience-001.md ...
#   attack-chains.yaml
#   cost-stats.csv
#   experiences-index.yaml
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

遇到相似目标时，DawnForge 应先检索本地经验库：

```text
EyouCMS / ThinkPHP / Flask / JWT / Webpack / SourceMap / 内网弱口令
```

如果经验多次复用，应升级到（这些是通用方法论，可以提交到仓库供社区共享）：

- `AGENTS.md` 的常见任务速查
- 对应 `skills/pentest_skills/*/SKILL.md`
- `skills/references/*`

## 成本记录

任务结束后在 DawnForge 中执行：

```text
/stats
```

把结果追加到 `cost-stats.csv`（本地私有），用于长期分析 DeepSeek prefix-cache 的真实收益。

## 攻击链记录

跨漏洞组合写入 `attack-chains.yaml`（本地私有）。例如：

```text
目录遍历 → 配置泄露 → 数据库弱口令 → WebShell
JWT 低权限账号 → API 越权 → 横向读取用户数据
SourceMap 泄露 → 接口发现 → 权限矩阵分析 → BOLA
```

通用、可复现的攻击链模式可提炼后提交到 `memory/templates/` 或 `AGENTS.md`，让社区受益；涉及具体目标、凭据、扫描结果的细节一律留在本地。