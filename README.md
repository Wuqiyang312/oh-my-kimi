# Oh My Kimi

为 Kimi Code CLI 提供的增强插件，源自 [oh-my-opencode](https://github.com/code-yeongyu/oh-my-openagent) 的功能迁移。

## 功能

### 🔍 文件搜索
- **smart_glob** - 基于模式匹配查找文件
  - 支持 `**/*.py`, `src/**/*.ts` 等 glob 模式
  - 优先使用 ripgrep (rg)，自动回退到 Python 实现
  - 自动排除 node_modules, __pycache__ 等目录

- **smart_grep** - 基于正则表达式搜索文件内容
  - 支持多种输出模式：content, files_with_matches, count
  - 文件类型过滤（如 `--include "*.py"`）
  - 优先使用 ripgrep (rg)，自动回退到 Python re 模块

### 📊 代码分析
- **code_analyze** - 分析 Python 代码结构
  - 使用 Python AST 模块解析代码
  - 统计函数、类、导入、复杂度
  - 计算代码行数（总行数、代码行数、空行数）

- **project_stats** - 统计项目代码量和结构
  - 按编程语言统计文件数和代码行数
  - 按目录统计代码分布
  - 识别项目中最大的文件
  - 支持 30+ 种编程语言

### 🔗 GitHub 集成
- **github_triage** - 分析 GitHub 仓库的 Issues 和 PRs
  - 自动分类：Bug, Feature, Question, Other
  - 统计活跃项目（30天内更新）
  - 支持分页获取大量数据

## 安装

```bash
kimi plugin install /path/to/oh-my-kimi
```

或者直接从 Git 仓库安装：

```bash
kimi plugin install https://github.com/yourusername/oh-my-kimi.git
```

## 依赖

- Python 3.9+
- 可选：ripgrep (rg) - 用于增强文件搜索性能
- 可选：GitHub CLI (gh) - 用于 GitHub 相关功能

### 安装依赖

```bash
# Ubuntu/Debian
sudo apt install ripgrep gh

# macOS
brew install ripgrep gh

# Arch Linux
sudo pacman -S ripgrep github-cli
```

## 使用

安装后，Kimi CLI 会自动识别插件中的工具，你可以在对话中直接使用：

### 文件搜索
- "查找项目中所有的 Python 文件"
- "搜索所有包含 'TODO' 的文件"
- "在 src 目录下查找所有 TypeScript 文件"

### 代码分析
- "分析这个 Python 文件的结构"
- "统计项目的代码量和语言分布"
- "找出项目中最大的文件"

### GitHub 集成
- "分析 code-yeongyu/oh-my-openagent 仓库的 issues"
- "查看这个仓库有多少个 open 的 PRs"
- "帮我分类一下这些 issues"

## 插件结构

```
oh-my-kimi/
├── plugin.json                 # 插件配置（必需）
├── README.md                   # 说明文档
├── .kimi/
│   └── skills/
│       └── github-triage.md    # Skill 提示词
└── scripts/                    # 工具脚本
    ├── smart_glob.py           # 文件模式搜索
    ├── smart_grep.py           # 文件内容搜索
    ├── github_triage.py        # GitHub 分析
    ├── code_analyze.py         # 代码结构分析
    └── project_stats.py        # 项目统计
```

## 工具使用指南

### smart_glob

```bash
# 查找所有 Python 文件
python3 scripts/smart_glob.py "**/*.py"

# 在指定目录查找 TypeScript 文件
python3 scripts/smart_glob.py "**/*.ts" --path ./src

# 限制结果数量
python3 scripts/smart_glob.py "*.md" --limit 20
```

### smart_grep

```bash
# 查找函数定义
python3 scripts/smart_grep.py "^def " --include "*.py"

# 查找类定义并显示内容
python3 scripts/smart_grep.py "^class " --include "*.py" --output_mode content

# 统计 TODO/FIXME 数量
python3 scripts/smart_grep.py "TODO|FIXME" --output_mode count

# 限制输出数量
python3 scripts/smart_grep.py "import" --head_limit 50
```

### github_triage

```bash
# 分析仓库（需要 gh CLI 已登录）
python3 scripts/github_triage.py --repo code-yeongyu/oh-my-openagent

# 只分析 issues
python3 scripts/github_triage.py --repo owner/repo --item_type issues

# 包含 closed 状态的 items
python3 scripts/github_triage.py --repo owner/repo --state all

# JSON 输出
python3 scripts/github_triage.py --repo owner/repo --output_format json
```

### code_analyze

```bash
# 分析单个文件
python3 scripts/code_analyze.py --path ./my_script.py

# 分析目录（包含测试文件）
python3 scripts/code_analyze.py --path ./src --include_tests

# 查看摘要
python3 scripts/code_analyze.py --path . | jq '.summary'
```

### project_stats

```bash
# 分析当前目录
python3 scripts/project_stats.py --path .

# 自定义排除模式
python3 scripts/project_stats.py --path . --exclude "node_modules,vendor"

# 摘要输出
python3 scripts/project_stats.py --path . --output_format summary
```

## 错误处理

所有工具在使用错误时会返回详细的使用说明，包括：
- 错误类型和描述
- 解决建议
- 完整的使用指南

示例错误输出：
```json
{
  "error": "路径不存在: /invalid/path",
  "type": "FileNotFoundError",
  "suggestion": "请检查路径是否正确",
  "usage_guide": "..."
}
```

## 与 oh-my-opencode 的关系

本插件将 oh-my-opencode 的部分工具功能迁移到 Kimi CLI 插件格式：

| 原 oh-my-opencode 功能 | Oh My Kimi 对应工具 |
|------------------------|---------------------|
| glob 工具 | smart_glob |
| grep 工具 | smart_grep |
| github-triage Skill | github_triage |
| AST 分析 | code_analyze |
| 项目统计 | project_stats |

**注意**：本插件不包含 oh-my-opencode 的 Agent 系统和 Hooks。

## 插件规范

符合 [Kimi Code CLI 插件规范](https://moonshotai.github.io/kimi-cli/zh/customization/plugins.html)

## License

MIT
