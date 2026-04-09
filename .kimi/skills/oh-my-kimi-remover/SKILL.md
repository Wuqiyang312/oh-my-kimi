---
name: oh-my-kimi-remover
description: |
  卸载和清理 oh-my-kimi 插件及其 skills。
  当用户需要以下功能时触发：
  (1) 删除 oh-my-kimi 插件
  (2) 卸载 oh-my-kimi
  (3) 清理 oh-my-kimi 相关文件
  (4) 完全移除 oh-my-kimi
  (5) 重置 oh-my-kimi 安装
---

# Oh My Kimi 卸载器

帮助用户完全卸载 oh-my-kimi 插件和相关资源。

## 卸载方式

### 方式 1: 仅移除插件（保留 skills）

```bash
# 移除 Kimi CLI 插件
kimi plugin remove oh-my-kimi
```

### 方式 2: 完全卸载（插件 + skills）

```bash
# 1. 移除插件
kimi plugin remove oh-my-kimi

# 2. 移除用户级 skills
rm -rf ~/.kimi/skills/oh-my-kimi-*

# 3. 检查其他可能位置
rm -rf ~/.config/agents/skills/oh-my-kimi-*
rm -rf ~/.claude/skills/oh-my-kimi-*
rm -rf ~/.codex/skills/oh-my-kimi-*
rm -rf ~/.agents/skills/oh-my-kimi-*
```

### 方式 3: 清理项目级 skills

```bash
# 如果项目中有安装 skills
rm -rf ./.kimi/skills/oh-my-kimi-*
rm -rf ./.agents/skills/oh-my-kimi-*
```

## 检查残留

### 检查已安装插件
```bash
kimi plugin list | grep oh-my-kimi
```

### 检查用户级 skills
```bash
# 检查所有可能的目录
ls -la ~/.kimi/skills/ | grep oh-my-kimi
ls -la ~/.config/agents/skills/ 2>/dev/null | grep oh-my-kimi
ls -la ~/.claude/skills/ 2>/dev/null | grep oh-my-kimi
ls -la ~/.agents/skills/ 2>/dev/null | grep oh-my-kimi
```

### 检查项目级 skills
```bash
ls -la ./.kimi/skills/ 2>/dev/null | grep oh-my-kimi
ls -la ./.agents/skills/ 2>/dev/null | grep oh-my-kimi
```

## 清理脚本

### 一键卸载脚本

```bash
#!/bin/bash
# uninstall-oh-my-kimi.sh

echo "🧹 开始卸载 oh-my-kimi..."

# 移除插件
if kimi plugin list | grep -q "oh-my-kimi"; then
    echo "📦 移除 Kimi 插件..."
    kimi plugin remove oh-my-kimi
fi

# 清理 skills
echo "🗑️  清理 skills..."
for dir in \
    "$HOME/.kimi/skills" \
    "$HOME/.config/agents/skills" \
    "$HOME/.claude/skills" \
    "$HOME/.codex/skills" \
    "$HOME/.agents/skills" \
    "./.kimi/skills" \
    "./.agents/skills"
do
    if [ -d "$dir" ]; then
        for skill in "$dir"/oh-my-kimi-*; do
            if [ -e "$skill" ]; then
                echo "  删除: $skill"
                rm -rf "$skill"
            fi
        done
    fi
done

echo "✅ 卸载完成！"
echo ""
echo "验证:"
kimi plugin list | grep oh-my-kimi || echo "插件已移除"
```

## 故障排除

### 卸载后仍能使用
如果卸载后插件功能仍然可用：
1. 检查是否有多个安装位置
2. 重启 Kimi CLI
3. 检查是否有缓存

### 权限问题
```bash
# 使用 sudo 如果需要
sudo rm -rf /path/to/skills
```

### 部分功能残留
```bash
# 查找所有相关文件
find ~ -name "*oh-my-kimi*" -type d 2>/dev/null
find ~ -name "*oh-my-kimi*" -type f 2>/dev/null
```

## 重新安装

卸载后如需重新安装：

```bash
# 从 GitHub 安装
kimi plugin install https://github.com/Wuqiyang312/oh-my-kimi
```

或参考 `oh-my-kimi-installer` skill 获取详细安装指导。
