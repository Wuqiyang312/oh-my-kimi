---
name: oh-my-kimi
description: |
  使用 Oh My Kimi 插件提供的增强工具进行文件搜索、代码分析和 GitHub 集成。
  当用户需要以下功能时触发：
  (1) 查找文件 - "查找所有 Python 文件"、"搜索某种类型的文件"
  (2) 搜索文件内容 - "搜索包含某内容的文件"、"查找 TODO"
  (3) 分析代码结构 - "分析这个文件"、"统计代码量"、"项目有多大"
  (4) GitHub 分析 - "分析仓库 issues"、"查看 PRs"、"triage github"
  (5) 项目统计 - "项目用了哪些语言"、"代码分布情况"
---

# Oh My Kimi 插件使用指南

Oh My Kimi 提供了一系列增强工具，帮助更高效地进行文件搜索、代码分析和 GitHub 集成。

## 工具概览

| 工具 | 用途 | 典型场景 |
|------|------|----------|
| `smart_glob` | 文件模式匹配查找 | 查找特定类型文件、按目录查找 |
| `smart_grep` | 文件内容搜索 | 查找代码模式、搜索 TODO/FIXME |
| `code_analyze` | Python 代码分析 | 分析文件/目录结构、统计复杂度 |
| `project_stats` | 项目统计 | 代码量统计、语言分布、目录分析 |
| `github_triage` | GitHub 分析 | Issues/PRs 分类统计、活跃度分析 |

## 工具详解

### 1. smart_glob - 文件查找

基于 glob 模式查找文件，支持 `**/*.py` 等高级模式。

**核心参数：**
- `pattern` (必需): 匹配模式，如 `"**/*.py"`, `"src/**/*.ts"`
- `path`: 搜索目录，默认当前工作目录
- `limit`: 结果数量限制，默认 100

**典型用法：**
```json
// 查找所有 Python 文件
{"pattern": "**/*.py"}

// 在 src 目录查找 TypeScript 文件
{"pattern": "**/*.ts", "path": "./src"}

// 查找配置文件，限制 20 个
{"pattern": "*.json", "limit": 20}
```

**适用场景：**
- 批量查找特定类型文件
- 定位代码文件范围后再用 smart_grep 搜索
- 统计某类文件数量

---

### 2. smart_grep - 内容搜索

基于正则表达式搜索文件内容，支持多种输出模式。

**核心参数：**
- `pattern` (必需): 正则表达式模式
- `include`: 文件类型过滤，如 `"*.py"`, `"*.{ts,tsx}"`
- `output_mode`: 输出模式 - `content`(显示匹配行), `files_with_matches`(仅文件路径), `count`(统计数量)
- `head_limit`: 结果数量限制
- `path`: 搜索目录

**典型用法：**
```json
// 查找所有函数定义
{"pattern": "^def ", "include": "*.py", "output_mode": "content"}

// 查找 TODO/FIXME 并统计数量
{"pattern": "TODO|FIXME", "output_mode": "count"}

// 查找类定义，限制 20 个结果
{"pattern": "^class ", "include": "*.py", "head_limit": 20}

// 搜索所有导入语句
{"pattern": "^import |^from ", "include": "*.py", "output_mode": "content"}
```

**适用场景：**
- 查找代码模式（函数、类、导入）
- 搜索 TODO/FIXME/HACK 标记
- 查找特定字符串在哪些文件中
- 统计某模式出现次数

---

### 3. code_analyze - Python 代码分析

使用 AST 分析 Python 代码结构，统计函数、类、导入和复杂度。

**核心参数：**
- `path` (必需): 文件或目录路径
- `include_tests`: 是否包含测试文件，默认 false

**典型用法：**
```json
// 分析单个文件
{"path": "./my_module.py"}

// 分析目录，包含测试文件
{"path": "./src", "include_tests": true}
```

**输出内容：**
- 文件总数、函数总数、类总数
- 每个文件的：函数列表、类列表、导入语句、代码行数
- 平均复杂度、最大复杂度

**适用场景：**
- 了解代码库结构
- 识别复杂度过高的文件
- 统计代码规模
- 代码审查前的概览

---

### 4. project_stats - 项目统计

统计项目代码量和结构，按语言、目录分组。

**核心参数：**
- `path`: 项目目录，默认当前目录
- `exclude`: 排除模式，默认 `"node_modules,__pycache__,.git,venv,.venv,dist,build"`

**典型用法：**
```json
// 分析当前目录
{"path": "."}

// 自定义排除模式
{"path": ".", "exclude": "node_modules,vendor,*.min.js"}
```

**输出内容：**
- 按语言统计：文件数、代码行数
- 按目录统计：文件分布
- 最大文件列表
- 总行数、代码行数、空行数

**适用场景：**
- 了解项目技术栈
- 评估项目规模
- 识别代码分布
- 查找大文件

---

### 5. github_triage - GitHub 分析

分析 GitHub 仓库的 Issues 和 PRs，自动分类和统计。

**核心参数：**
- `repo` (必需): 仓库名称，格式 `"owner/repo"`
- `item_type`: 类型 - `"issues"`, `"prs"`, `"all"`
- `state`: 状态 - `"open"`, `"closed"`, `"all"`
- `output_format`: 输出格式 - `"json"`, `"summary"`

**典型用法：**
```json
// 获取仓库概览
{"repo": "code-yeongyu/oh-my-openagent"}

// 只分析 open 的 issues
{"repo": "owner/repo", "item_type": "issues", "state": "open"}

// 获取详细 JSON 数据
{"repo": "owner/repo", "output_format": "json"}
```

**分类规则：**
- Issues: bug, feature, question, other
- PRs: bugfix, feature, docs, refactor, test, other

**适用场景：**
- 了解开源项目活跃度
- 分析 issue 分布
- 评估贡献者活动
- 项目健康状况检查

---

## 组合使用技巧

### 技巧 1: 先定位范围，再搜索内容
```
1. smart_glob "src/**/*.py" → 获取 Python 文件列表
2. smart_grep "TODO" --include "*.py" → 在这些文件中搜索 TODO
```

### 技巧 2: 代码审查流程
```
1. project_stats "." → 了解项目整体情况
2. code_analyze "./src" → 分析核心代码结构
3. smart_grep "^class |^def " → 查看主要接口
```

### 技巧 3: 查找重复代码
```
smart_grep "some_function_pattern" --output_mode "content"
→ 查看某段代码在哪些文件中重复出现
```

---

## 常见任务速查

| 任务 | 工具 | 参数示例 |
|------|------|----------|
| 找所有测试文件 | smart_glob | `{"pattern": "test_*.py"}` |
| 找未使用的导入 | smart_grep | `{"pattern": "^import |^from ", "include": "*.py"}` |
| 统计代码行数 | project_stats | `{"path": "."}` |
| 找大文件 | project_stats | 查看输出中的 "largest_files" |
| 分析 Python 复杂度 | code_analyze | `{"path": "./src"}` |
| 查看项目活跃度 | github_triage | `{"repo": "owner/repo"}` |

---

## 注意事项

1. **路径处理**: 所有路径都相对于当前工作目录
2. **性能**: 大型项目搜索可能需要较长时间
3. **GitHub 工具**: 需要 `gh` CLI 已登录才能使用 github_triage
4. **正则表达式**: smart_grep 使用 Python re 模块语法
5. **排除规则**: 工具自动排除常见目录（node_modules, __pycache__, .git 等）
