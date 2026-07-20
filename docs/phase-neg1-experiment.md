# Phase -1 实验：验证破晓分析能力

> 前置条件：`$env:DEEPSEEK_API_KEY = "sk-你的key"`

## 实验 A：让破晓分析已知漏洞（CTF exam-web01）

目标：`ctf_exam_web01/` 是一个 CTF 靶机备份，已知含数据库配置泄露（`backup_extracted/config.php` 含 root/cJvmb!2G）。

```bash
cd C:\Tools\reasonix_sentou
reasonix
```

在交互中输入：

```
分析这个 CTF 靶机的备份文件，告诉我发现了什么风险：

ctf_exam_web01/backup_extracted/config.php 包含数据库配置：
- DB_HOST: 127.0.0.1
- DB_USER: root
- DB_PWD: cJvmb!2G
- DB_NAME: test

另外还有一个 data.sql 文件。请：
1. 列出主要安全风险（标注置信度）
2. 给出验证步骤
3. 估算 CVSS 评分
```

**记录**：
- 是否正确识别了"数据库配置泄露"和"弱口令"？
- 是否给出了可操作的验证步骤？
- `/stats` — 记录缓存命中率、token、费用

---

## 实验 B：破晓 + nuclei 实战

```bash
# 1. 用 nuclei 扫描一个测试目标（例如 DVWA 或 testphp.vulnweb.com）
nuclei -u http://testphp.vulnweb.com -json -o nuclei-results.json

# 2. 在 reasonix 中分析
cd C:\Tools\reasonix_sentou
reasonix
```

交互中输入：

```
以下是 nuclei 扫描结果，请筛选出最值得深入的 Top 5：

[粘贴 nuclei-results.json 关键字段，或直接 cat nuclei-results.json | 粘贴]
```

**记录**：
- 筛选是否合理？
- 是否注意到了误报？
- 下一步建议是否可行？

---

## 实验结果判定

| 场景 | 通过标准 | 下一步 |
|------|---------|--------|
| 正确识别风险 + 可操作建议 + 低幻觉 | ✅ 通过 | 直接用于实战 |
| 部分有价值但需要修正 | ⚠️ 有条件 | 调整 persona 提示词 |
| 编造漏洞、误判严重性 | ❌ 不通过 | 等更强模型或换方案 |

---

## 实验后

```bash
/stats        # 记录费用和命中率
/remember     # 把实验结果记入 pentest-experience-002
```
