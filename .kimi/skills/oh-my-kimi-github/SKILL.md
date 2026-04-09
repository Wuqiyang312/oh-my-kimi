---
name: oh-my-kimi-github
description: |
  使用 Oh My Kimi 插件分析 GitHub 仓库。
  当用户需要以下功能时触发：
  (1) 分析仓库 Issues - "查看这个仓库的 issues"
  (2) 分析 PRs - "查看这个项目的 PR"
  (3) 项目活跃度 - "这个项目活跃吗"
  (4) Issues 分类统计 - "有多少 bug 待修复"
  (5) GitHub 仓库分析 - "分析 GitHub 仓库"
---

# Oh My Kimi - GitHub 分析

专注于 GitHub 仓库分析的 triage 工具。

## 工具概览

| 工具 | 用途 | 典型场景 |
|------|------|----------|
| `github_triage` | Issues/PRs 分类统计 | 仓库活跃度分析、问题分类、贡献统计 |

---

## github_triage - GitHub 仓库分析

分析 GitHub 仓库的 Issues 和 PRs，自动分类和统计。

### 核心参数
- `repo` (必需): 仓库名称，格式 `"owner/repo"`
- `item_type`: 类型
  - `"issues"`: 仅分析 Issues
  - `"prs"`: 仅分析 PRs
  - `"all"`: 两者都分析（默认）
- `state`: 状态过滤
  - `"open"`: 仅开放的（默认）
  - `"closed"`: 仅关闭的
  - `"all"`: 所有状态
- `output_format`: 输出格式
  - `"summary"`: 摘要格式（默认）
  - `"json"`: 详细 JSON 数据

### 典型用法
```json
// 获取仓库概览
{"repo": "code-yeongyu/oh-my-openagent"}

// 只分析 open 的 issues
{"repo": "owner/repo", "item_type": "issues", "state": "open"}

// 获取详细 JSON 数据
{"repo": "owner/repo", "output_format": "json"}

// 分析所有状态的 PRs
{"repo": "owner/repo", "item_type": "prs", "state": "all"}
```

### 输出内容

#### Summary 模式
- **Issues 统计**: 总数、bug 数量、feature 数量、question 数量
- **PRs 统计**: 总数、各类型 PR 数量（bugfix, feature, docs 等）
- **最近活动**: 最新的 Issues 和 PRs
- **贡献者**: 活跃贡献者统计

#### JSON 模式
- 完整的 Issues/PRs 列表
- 每个项目的标题、作者、状态、标签、创建时间
- 分类信息

### 自动分类规则

**Issues 分类**:
- `bug`: 标签包含 "bug", "error", "crash"
- `feature`: 标签包含 "feature", "enhancement"
- `question`: 标签包含 "question", "help"
- `other`: 其他类型

**PRs 分类**:
- `bugfix`: 标题包含 "fix", "bug", "patch"
- `feature`: 标题包含 "feat", "feature", "add"
- `docs`: 标题包含 "doc", "readme", "wiki"
- `refactor`: 标题包含 "refactor", "clean"
- `test`: 标题包含 "test", "spec"
- `other`: 其他类型

### 适用场景
- 了解开源项目活跃度
- 分析 issue 分布（bug vs feature）
- 评估贡献者活动
- 项目健康状况检查
- 选择依赖前的项目评估
- 维护者工作负载评估

---

## 使用技巧

### 技巧 1: 项目健康度快速检查
```
github_triage {"repo": "owner/repo"}
→ 查看 open issues/PRs 数量和分布
```

### 技巧 2: Bug 修复进度分析
```
github_triage {"repo": "owner/repo", "item_type": "issues", "state": "all", "output_format": "json"}
→ 对比 open/closed bug 比例
```

### 技巧 3: 贡献活跃度评估
```
github_triage {"repo": "owner/repo", "item_type": "prs", "state": "all"}
→ 查看 PR 合并率和响应速度
```

---

## 常见任务速查

| 任务 | 参数示例 |
|------|----------|
| 仓库概览 | `{"repo": "owner/repo"}` |
| 查看待修复 Bug | `{"repo": "owner/repo", "item_type": "issues"}` |
| 查看活跃 PR | `{"repo": "owner/repo", "item_type": "prs"}` |
| 历史数据分析 | `{"repo": "owner/repo", "state": "all"}` |
| 获取原始数据 | `{"repo": "owner/repo", "output_format": "json"}` |

---

## 注意事项

1. **依赖 gh CLI**: 需要 `gh` CLI 已登录才能使用
   - 安装: `brew install gh` 或 `apt install gh`
   - 登录: `gh auth login`

2. **权限**: 私有仓库需要有访问权限

3. **API 限制**: 受 GitHub API 速率限制影响

4. **数据实时性**: 获取的是当前时刻的数据快照

5. **标签识别**: 分类基于标签和标题关键词，可能不完全准确
