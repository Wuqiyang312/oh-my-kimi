---
name: oh-my-kimi-installer
description: |
  安装和管理 oh-my-kimi 插件及其相关 skills。
  当用户需要安装、更新、重新安装或排查 oh-my-kimi 插件问题时使用。
  支持本地路径安装和 GitHub 仓库安装。
---

# Oh My Kimi 插件安装器

帮助用户安装和管理 oh-my-kimi 插件。

## 功能模块

oh-my-kimi 插件按功能分为多个 skill 模块：

| Skill | 功能 | 触发场景 |
|-------|------|----------|
| `oh-my-kimi-search` | 文件搜索 | 查找文件、搜索内容 |
| `oh-my-kimi-code` | 代码分析 | 分析代码结构、统计项目 |
| `oh-my-kimi-github` | GitHub 分析 | 分析 Issues/PRs |
| `oh-my-kimi-installer` | 安装管理 | 安装、更新、故障排除 |

## 安装方法

### 方法 1: 从本地路径安装（开发/测试）

```bash
# 进入插件目录
cd /path/to/oh-my-kimi

# 安装插件
kimi plugin install .
```

### 方法 2: 从 GitHub 安装（推荐）

```bash
# 安装最新版本
kimi plugin install https://github.com/Wuqiyang312/oh-my-kimi

# 或指定分支
kimi plugin install https://github.com/Wuqiyang312/oh-my-kimi/tree/main
```

## 管理插件

### 查看已安装插件
```bash
kimi plugin list
```

### 查看插件详情
```bash
kimi plugin info oh-my-kimi
```

### 更新插件
```bash
# 先移除旧版本
kimi plugin remove oh-my-kimi

# 重新安装
kimi plugin install https://github.com/Wuqiyang312/oh-my-kimi
```

### 重新安装（修复问题）
```bash
kimi plugin remove oh-my-kimi
kimi plugin install /path/to/oh-my-kimi
```

## 故障排除

### 插件命令不生效
1. 检查插件是否已安装：`kimi plugin list`
2. 重新安装插件
3. 重启 Kimi CLI

### 工具调用失败
1. 检查脚本权限：`ls -la scripts/`
2. 验证 Python 环境：`python3 --version`
3. 查看插件日志检查错误

### 更新后问题
1. 完全移除插件：`kimi plugin remove oh-my-kimi`
2. 清理缓存（如有）
3. 重新安装

## 验证安装

安装完成后，测试以下功能：

```bash
# 测试代码分析
echo '{"path": "."}' | python3 scripts/code_analyze.py

# 测试文件搜索
echo '{"pattern": "*.py"}' | python3 scripts/smart_glob.py

# 测试项目统计
echo '{"path": "."}' | python3 scripts/project_stats.py
```

## 工具清单

插件安装后会包含以下工具：

| 工具 | 功能 | 所属 Skill |
|------|------|------------|
| `smart_glob` | 基于模式匹配查找文件 | oh-my-kimi-search |
| `smart_grep` | 基于正则表达式搜索文件内容 | oh-my-kimi-search |
| `code_analyze` | 分析 Python 代码结构 | oh-my-kimi-code |
| `project_stats` | 统计项目代码量和结构 | oh-my-kimi-code |
| `github_triage` | 分析 GitHub 仓库 Issues 和 PRs | oh-my-kimi-github |
