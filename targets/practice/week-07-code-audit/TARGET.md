# Week 7 — 前端代码审计与 JS 逆向

> **靶场**: Juice Shop + 本地 JS 文件 | **工具**: katana, SpiderX, jq, DevTools
> **技能**: `ai-assisted-code-audit`, `js-reverse-bypass`
> **难度**: ⭐⭐⭐⭐ | **预计时间**: 6 小时

## 本周目标

从"黑盒测试"升级到"灰盒测试"——通过分析前端 JS 代码发现 API 端点、权限逻辑、硬编码密钥等。

## 练习任务

### 任务 1: JS 文件收集 (1h)

```bash
# 用 katana 爬取 Juice Shop，收集所有 JS 文件
katana -u http://localhost:3000 -d 3 -jc -ext js -o results/week07_js.txt

# 查看收集到的 JS 文件
cat results/week07_js.txt

# 下载关键 JS 文件到本地分析
mkdir -p targets/practice/week-07-code-audit/js_files
cat results/week07_js.txt | while read url; do
  curl -s "$url" -o "targets/practice/week-07-code-audit/js_files/$(basename $url)"
done
```

### 任务 2: 静态分析 (2h)

打开浏览器 DevTools (`F12` → Sources) 或本地 JS 文件，搜索以下内容：

```javascript
// 搜索关键词 (Ctrl+Shift+F 在 DevTools 中):
"api/"         // API 端点
"token"        // Token 处理
"role"         // 角色判断
"isAdmin"      // 管理员检查
"password"     // 密码逻辑
"secret"       // 密钥
"encrypt"      // 加密函数
"localStorage" // 本地存储
"Cookie"       // Cookie 操作
"fetch("       // API 调用
"axios"        // HTTP 请求库
```

**分析清单**:
1. 找到了多少个 API 端点？
2. 哪些端点需要认证？哪些不需要？
3. 前端如何判断用户是否为管理员？
4. Token 存储在哪里？如何传递？
5. 有没有硬编码的密钥、URL、凭证？

### 任务 3: SourceMap 检测 (1h)

```bash
# 检查每个 JS 文件是否有对应的 .map 文件
cat results/week07_js.txt | while read url; do
  status=$(curl -s -o /dev/null -w "%{http_code}" "$url.map")
  if [ "$status" = "200" ]; then
    echo "[!] SourceMap 泄露: $url.map"
  fi
done

# 如果发现 SourceMap:
# 1. 下载 .map 文件
# 2. 使用工具恢复源码 (见 skills/pentest_skills/ai-assisted-code-audit/SKILL.md)
```

### 任务 4: 前端权限控制分析 (1.5h)

以 Juice Shop 为例：

1. **路由守卫**: 查看 Angular 路由定义，哪些路由有守卫（`canActivate`）？
2. **角色枚举**: 在前端代码中搜索 `admin`、`customer`、`deluxe` 等角色关键字
3. **接口访问控制**: 前端是否在调用管理接口前检查权限？还是完全依赖后端？
4. **隐藏功能**: Score Board 的入口被隐藏了——前端代码中怎么找到的？

### 任务 5: AI 辅助审计 (30min)

```bash
# 将收集到的 JS 文件和发现整理好
# 使用 Reasonix 加载 ai-assisted-code-audit 技能
# 粘贴关键代码片段，让 AI 分析:
# - 安全风险排序 (P0-P4)
# - API 接口清单
# - 权限矩阵
```

## 交付物

```markdown
## JS 文件清单
| 文件 | 大小 | 关键发现 |
|:-----|:-----|:---------|

## API 端点清单
| 端点 | 方法 | 需要认证 | 需要角色 | 功能 |
|:-----|:-----|:---------|:---------|:-----|

## 硬编码发现
| 类型 | 内容 | 文件 | 行号 | 风险 |
|:-----|:-----|:-----|:-----|:-----|

## 权限矩阵
| 功能 | 前端检查 | 后端验证 | 可越权? |
|:-----|:---------|:---------|:--------|

## SourceMap
- [ ] 发现 SourceMap 泄露: _____

## 风险排序 (P0-P4)
- P0: _____
- P1: _____
- P2: _____
```
