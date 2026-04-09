---
name: oh-my-kimi-installer
description: |
  安装和管理 oh-my-kimi 插件及其相关 skills。
  当用户需要以下功能时触发：
  (1) 安装 oh-my-kimi 插件
  (2) 更新 oh-my-kimi 插件
  (3) 重新安装 oh-my-kimi
  (4) 复制 skills 到用户目录
  (5) 安装 oh-my-kimi skills
  (6) 排查 oh-my-kimi 安装问题
---

# Oh My Kimi 插件安装器

帮助用户安装和管理 oh-my-kimi 插件和 skills。

## 功能模块

oh-my-kimi 按功能分为多个 skill 模块：

| Skill | 功能 | 触发场景 |
|-------|------|----------|
| `oh-my-kimi-search` | 文件搜索 | 查找文件、搜索内容 |
| `oh-my-kimi-code` | 代码分析 | 分析代码结构、统计项目 |
| `oh-my-kimi-github` | GitHub 分析 | 分析 Issues/PRs |
| `oh-my-kimi-installer` | 安装管理 | 安装、更新 |
| `oh-my-kimi-remover` | 卸载清理 | 删除、重置 |

## 安装方法

### 方法 1: 安装插件（仅工具）

```bash
# 从 GitHub 安装最新版本
kimi plugin install https://github.com/Wuqiyang312/oh-my-kimi

# 或从本地路径（开发/测试）
cd /path/to/oh-my-kimi
kimi plugin install .
```

### 方法 2: 完整安装（插件 + Skills）

```bash
# 1. 克隆仓库
git clone https://github.com/Wuqiyang312/oh-my-kimi.git
cd oh-my-kimi

# 2. 安装插件
kimi plugin install .

# 3. 安装 skills 到用户目录
./.kimi/skills/oh-my-kimi-installer/scripts/install-skills.sh
```

### 方法 3: 使用安装脚本

```bash
# 自动安装 skills
bash ./.kimi/skills/oh-my-kimi-installer/scripts/install-skills.sh

# 检查现有安装
bash ./.kimi/skills/oh-my-kimi-installer/scripts/install-skills.sh --check

# 查看帮助
bash ./.kimi/skills/oh-my-kimi-installer/scripts/install-skills.sh --help
```

## Skills 安装位置

Kimi Code CLI 按以下优先级搜索 skills：

### 用户级（推荐）
- `~/.kimi/skills/` ⭐ 推荐
- `~/.config/agents/skills/` ⭐ 标准位置
- `~/.claude/skills/`
- `~/.codex/skills/`
- `~/.agents/skills/`

### 项目级
- `./.kimi/skills/`
- `./.agents/skills/`

安装脚本会自动检测已存在的目录并安装到优先级最高的位置。

## 管理插件

### 查看已安装
```bash
# 查看插件
kimi plugin list

# 查看详情
kimi plugin info oh-my-kimi
```

### 更新插件
```bash
# 移除旧版本
kimi plugin remove oh-my-kimi

# 重新安装
kimi plugin install https://github.com/Wuqiyang312/oh-my-kimi
```

### 重新安装（修复问题）
```bash
kimi plugin remove oh-my-kimi
kimi plugin install /path/to/oh-my-kimi
```

## 管理 Skills

### 安装 Skills
```bash
# 运行安装脚本
./.kimi/skills/oh-my-kimi-installer/scripts/install-skills.sh
```

脚本功能：
- ✅ 自动检测目标目录
- ✅ 检查现有安装
- ✅ 支持覆盖确认
- ✅ 显示安装进度

### 检查安装状态
```bash
./.kimi/skills/oh-my-kimi-installer/scripts/install-skills.sh --check
```

### 卸载 Skills
```bash
./.kimi/skills/oh-my-kimi-installer/scripts/install-skills.sh --uninstall
```

或参考 `oh-my-kimi-remover` skill 获取详细卸载指导。

## 故障排除

### 插件不生效
1. 检查安装：`kimi plugin list`
2. 重新安装
3. 重启 Kimi CLI

### Skills 不触发
1. 检查安装位置：运行 `--check`
2. 确认 skills 名称正确
3. 重启 Kimi CLI

### 工具调用失败
1. 检查脚本权限：`ls -la scripts/`
2. 验证 Python：`python3 --version`
3. 查看错误日志

## 验证安装

```bash
# 验证插件
echo '{"path": "."}' | python3 scripts/code_analyze.py

# 验证 skills 安装
./.kimi/skills/oh-my-kimi-installer/scripts/install-skills.sh --check
```

## 工具清单

| 工具 | 功能 | 所属 Skill |
|------|------|------------|
| `smart_glob` | 文件模式匹配查找 | oh-my-kimi-search |
| `smart_grep` | 文件内容搜索 | oh-my-kimi-search |
| `code_analyze` | Python 代码结构分析 | oh-my-kimi-code |
| `project_stats` | 项目统计 | oh-my-kimi-code |
| `github_triage` | GitHub Issues/PRs 分析 | oh-my-kimi-github |
