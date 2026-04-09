# GitHub Triage Skill

用于分析 GitHub 仓库的 Issues 和 PRs 的 Skill。

## 触发条件

当用户提到以下关键词时触发：
- "triage github"
- "分析 github issues"
- "查看仓库 issues"
- "github 分类"
- "分析 PRs"

## 使用方式

使用 `github_triage` 工具获取仓库的 Issues 和 PRs 信息：

```json
{
  "repo": "owner/repo",
  "item_type": "all",
  "state": "open",
  "output_format": "summary"
}
```

## 分析流程

1. **获取数据**
   - 使用 `github_triage` 工具获取 Issues/PRs 列表
   - 支持按状态过滤：open, closed, all

2. **分类分析**
   - Issues 分类：bug, feature, question, other
   - PRs 分类：bugfix, feature, docs, refactor, test, other

3. **生成报告**
   - 统计总数和分类数量
   - 识别最近活跃的项目（30天内更新）
   - 列出主要贡献者

## 输出格式

### Summary 模式
```
GitHub Triage Report: owner/repo
State: open | Generated: 2024-01-15T10:30:00

📋 Issues: 42 total
   Categories: bug: 15, feature: 20, question: 5, other: 2
   Active (30d): 18

🔀 PRs: 12 total
   Categories: bugfix: 5, feature: 4, docs: 2, other: 1
   Active (30d): 8
```

### 分析维度

1. **数量统计**
   - 总数
   - 按分类统计
   - 近期活跃度（30天）

2. **作者统计**
   - 最活跃的作者
   - 贡献分布

3. **状态分析**
   - Open vs Closed 比例
   - 解决速度估算

## 注意事项

- 需要 gh CLI 已登录
- API 有速率限制，大型仓库可能需要较长时间
- 默认只获取 open 状态的 items

## 示例对话

**用户**: 帮我分析一下这个仓库的 issues

**助手**: 我来帮你分析仓库的 Issues 和 PRs。请提供仓库名称（格式：owner/repo）。

**用户**: code-yeongyu/oh-my-openagent

**助手**: [使用 github_triage 工具获取数据并展示分析结果]
