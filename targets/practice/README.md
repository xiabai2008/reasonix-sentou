# Reasonix 实战训练计划 — 8 周从入门到攻击链

> **目标**: 每周 4-6 小时，8 周后独立完成完整的渗透测试攻击链。
> **配套**: 靶场环境（`targets/docker-compose.yml`）、59 个漏洞技能、20+ 工具

## 核心原则

1. **先练后看** — 先自己尝试，再对照 EXPECTED.md 复盘
2. **AI 辅助** — 每阶段用 `ai-pentest-orchestrator.py` 生成分析报告
3. **经验沉淀** — 每周写 NOTES.md，重要发现升级到 `memory/pentest-experience-NNN.md`
4. **循序渐进** — 难度递增：信息收集 → 单漏洞 → 多漏洞 → 攻击链

## 8 周路线图

```
Week 1-2      Week 3-4       Week 5-6       Week 7          Week 8
信息收集       SQLi + XSS     文件上传+认证  前端审计+JWT    综合攻击链
  │              │              │              │              │
recon ──────→ vuln-scan ──→ exploitation → code-audit → full-chain
subfinder      sqlmap          upload          SourceMap      串联利用
httpx          dalfox          brute.py        JWT 越权       报告生成
naabu          nuclei          ffuf            API 分析       AI 研判
```

## 每周标准流程

```
1. 阅读 TARGET.md     → 理解本周目标、靶场、工具
2. 启动对应靶场       → .\targets\start-ranges.ps1
3. 自主练习 (2-3h)    → 记录过程到 NOTES.md
4. AI 辅助分析 (30min) → python scripts/ai-pentest-orchestrator.py
5. 对照 EXPECTED.md   → 复盘差距，记录踩坑
6. 沉淀经验            → 更新 memory/pentest-experience-NNN.md
```

## 评分标准

| 等级 | 标准 |
|:-----|:-----|
| ⭐ 入门 | 能使用工具完成基础扫描和检测 |
| ⭐⭐ 熟练 | 能独立完成漏洞验证和利用 |
| ⭐⭐⭐ 精通 | 能绕过 WAF、构造自定义 Payload |
| ⭐⭐⭐⭐ 专家 | 能串联多漏洞形成攻击链，编写利用脚本 |

## 建议学习节奏

- 在校学生: 每晚 1 小时 + 周末集中 2 小时
- 带团队: 每周五下午集中练习 + 周日晚复盘
