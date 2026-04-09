#!/bin/bash
# Oh My Kimi Skills 安装脚本
# 将项目中的 skills 复制到用户级 skills 目录

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
SOURCE_SKILLS_DIR="$PROJECT_ROOT/.kimi/skills"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 可能的用户级 skills 目录
USER_SKILL_DIRS=(
    "$HOME/.kimi/skills"
    "$HOME/.config/agents/skills"
    "$HOME/.claude/skills"
    "$HOME/.codex/skills"
    "$HOME/.agents/skills"
)

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 检查目录是否存在 oh-my-kimi-* skills
has_oh_my_kimi_skills() {
    local dir="$1"
    if [ ! -d "$dir" ]; then
        return 1
    fi
    for skill in "$dir"/oh-my-kimi-*; do
        if [ -e "$skill" ]; then
            return 0
        fi
    done
    return 1
}

# 获取目标目录（优先级最高的已存在目录，或默认创建第一个）
get_target_dir() {
    # 优先返回已存在的目录
    for dir in "${USER_SKILL_DIRS[@]}"; do
        if [ -d "$dir" ]; then
            echo "$dir"
            return
        fi
    done
    # 如果没有存在的，返回默认位置
    echo "${USER_SKILL_DIRS[0]}"
}

# 复制 skill
copy_skill() {
    local source="$1"
    local target="$2"
    local skill_name=$(basename "$source")
    
    if [ -d "$target/$skill_name" ]; then
        print_warning "覆盖已存在的: $skill_name"
        read -p "是否覆盖? [Y/n] " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]] && [ ! -z "$REPLY" ]; then
            print_info "跳过: $skill_name"
            return
        fi
        rm -rf "$target/$skill_name"
    fi
    
    cp -r "$source" "$target/"
    print_success "已安装: $skill_name"
}

# 主函数
main() {
    echo "🚀 Oh My Kimi Skills 安装器"
    echo "============================"
    echo ""
    
    # 检查源目录
    if [ ! -d "$SOURCE_SKILLS_DIR" ]; then
        print_error "源目录不存在: $SOURCE_SKILLS_DIR"
        exit 1
    fi
    
    # 查找所有 oh-my-kimi-* skills
    local skills=()
    for skill in "$SOURCE_SKILLS_DIR"/oh-my-kimi-*; do
        if [ -d "$skill" ]; then
            skills+=("$skill")
        fi
    done
    
    if [ ${#skills[@]} -eq 0 ]; then
        print_error "未找到 oh-my-kimi-* skills"
        exit 1
    fi
    
    print_info "发现 ${#skills[@]} 个 skills:"
    for skill in "${skills[@]}"; do
        echo "  - $(basename "$skill")"
    done
    echo ""
    
    # 选择目标目录
    local target_dir=$(get_target_dir)
    
    # 显示现有安装
    print_info "检查现有安装..."
    local found_existing=false
    for dir in "${USER_SKILL_DIRS[@]}"; do
        if has_oh_my_kimi_skills "$dir"; then
            print_warning "在以下位置发现已安装的 skills:"
            ls -1 "$dir"/oh-my-kimi-* 2>/dev/null | while read skill; do
                echo "  - $skill"
            done
            found_existing=true
            break
        fi
    done
    
    if [ "$found_existing" = false ]; then
        print_info "未发现现有安装"
    fi
    echo ""
    
    # 确认目标目录
    echo "目标目录: $target_dir"
    if [ ! -d "$target_dir" ]; then
        read -p "目录不存在，是否创建? [Y/n] " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Nn]$ ]]; then
            print_error "安装取消"
            exit 1
        fi
        mkdir -p "$target_dir"
        print_success "创建目录: $target_dir"
    fi
    echo ""
    
    # 复制所有 skills
    print_info "开始安装..."
    for skill in "${skills[@]}"; do
        copy_skill "$skill" "$target_dir"
    done
    
    echo ""
    echo "============================"
    print_success "安装完成！"
    echo ""
    echo "已安装到: $target_dir"
    echo ""
    echo "安装的 skills:"
    ls -1 "$target_dir"/oh-my-kimi-* 2>/dev/null | while read skill; do
        echo "  ✓ $(basename "$skill")"
    done
    echo ""
    echo "提示: 重启 Kimi CLI 以加载新的 skills"
}

# 处理命令行参数
case "${1:-}" in
    --check)
        # 仅检查现有安装
        print_info "检查 oh-my-kimi skills 安装状态..."
        for dir in "${USER_SKILL_DIRS[@]}"; do
            if has_oh_my_kimi_skills "$dir"; then
                echo ""
                echo "📁 $dir:"
                ls -1 "$dir"/oh-my-kimi-* 2>/dev/null | while read skill; do
                    echo "  ✓ $(basename "$skill")"
                done
            fi
        done
        ;;
    --uninstall)
        # 卸载
        print_info "卸载 oh-my-kimi skills..."
        for dir in "${USER_SKILL_DIRS[@]}"; do
            if has_oh_my_kimi_skills "$dir"; then
                print_warning "删除: $dir/oh-my-kimi-*"
                rm -rf "$dir"/oh-my-kimi-*
            fi
        done
        print_success "卸载完成"
        ;;
    --help|-h)
        echo "Oh My Kimi Skills 安装器"
        echo ""
        echo "用法: $0 [选项]"
        echo ""
        echo "选项:"
        echo "  (无)        安装 skills 到用户目录"
        echo "  --check     检查现有安装"
        echo "  --uninstall 卸载所有 oh-my-kimi skills"
        echo "  --help      显示帮助"
        ;;
    *)
        main
        ;;
esac
