#!/usr/bin/env python3
"""Smart Glob - 基于模式匹配查找文件。

支持 glob 模式如 "**/*.py", "src/**/*.ts" 等。
优先使用 ripgrep (rg) 如果可用，否则使用 Python glob 模块。

使用场景:
- 查找特定类型的文件（如所有 Python 文件）
- 按目录结构查找文件
- 配合 smart_grep 使用先定位文件范围

示例:
  smart_glob "**/*.py"                           # 查找所有 Python 文件
  smart_glob "src/**/*.ts" --path ./project      # 在指定目录查找 TypeScript 文件
  smart_glob "*.md" --limit 10                   # 查找 Markdown 文件，最多 10 个
"""

import argparse
import fnmatch
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


USAGE_GUIDE = """
Smart Glob - 基于模式匹配查找文件

核心功能:
- 支持 glob 模式: **/*.py, src/**/*.ts, *.md
- 优先使用 ripgrep (rg)，回退到 Python 实现
- 自动排除: node_modules, __pycache__, .git 等

参数:
- pattern (必需): 文件匹配模式
- --path: 搜索目录，默认当前目录
- --limit: 返回结果数量限制，默认 100

使用示例:
  smart_glob "**/*.py"                          # 查找所有 Python 文件
  smart_glob "**/*.ts" --path ./src             # 在 src 目录查找 TypeScript 文件
  smart_glob "*.json" --limit 20                # 查找配置文件，限制 20 个

常见模式:
  **/*.py      - 所有 Python 文件
  src/**/*.ts  - src 目录及子目录下的 TypeScript 文件
  test_*.py    - 测试文件
  *.md         - Markdown 文档
  **/README*   - 所有 README 文件
"""


def has_ripgrep() -> bool:
    """检查系统是否安装了 ripgrep (rg)。"""
    try:
        subprocess.run(
            ["rg", "--version"],
            capture_output=True,
            check=True,
            timeout=5,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return False


def glob_with_ripgrep(pattern: str, path: str, limit: int) -> list[str]:
    """使用 ripgrep 的 --files 和 -g 选项进行文件匹配。"""
    cmd = ["rg", "--files", "-g", pattern, path]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode == 0 or result.returncode == 1:  # rg returns 1 when no matches
            files = [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
            if limit > 0:
                files = files[:limit]
            return files
    except subprocess.TimeoutExpired:
        raise TimeoutError("搜索超时（60秒）")
    except Exception as e:
        raise RuntimeError(f"ripgrep 执行失败: {e}")
    
    return []


def glob_with_python(pattern: str, path: str, limit: int) -> list[str]:
    """使用 Python 的 pathlib 和 fnmatch 进行文件匹配。"""
    files = []
    base_path = Path(path).resolve()
    
    # 将 glob 模式转换为 parts
    # **/*.py -> 递归匹配所有 .py 文件
    # src/*.ts -> 匹配 src 目录下的 .ts 文件
    
    if "**" in pattern:
        # 递归模式
        parts = pattern.split("**")
        if len(parts) == 2 and parts[0] == "":
            # **/*.ext 模式
            suffix = parts[1]  # 如 /*.py
            if suffix.startswith("/"):
                suffix = suffix[1:]  # 移除开头的 /
            
            for root, dirnames, filenames in os.walk(base_path):
                # 跳过隐藏目录和常见排除目录
                dirnames[:] = [
                    d for d in dirnames 
                    if not d.startswith(".") and d not in ("node_modules", "__pycache__", "venv", ".venv")
                ]
                
                for filename in filenames:
                    if fnmatch.fnmatch(filename, suffix):
                        full_path = Path(root) / filename
                        files.append(str(full_path))
                        if limit > 0 and len(files) >= limit:
                            return files
    else:
        # 非递归模式
        if "/" in pattern:
            # 包含目录的模式，如 src/*.ts
            dir_part, file_pattern = pattern.rsplit("/", 1)
            search_dir = base_path / dir_part
            if search_dir.exists():
                for item in search_dir.iterdir():
                    if item.is_file() and fnmatch.fnmatch(item.name, file_pattern):
                        files.append(str(item.resolve()))
                        if limit > 0 and len(files) >= limit:
                            return files
        else:
            # 仅文件名模式，如 *.py
            for item in base_path.iterdir():
                if item.is_file() and fnmatch.fnmatch(item.name, pattern):
                    files.append(str(item.resolve()))
                    if limit > 0 and len(files) >= limit:
                        return files
    
    return sorted(files)


def run_glob(pattern: str, path: str, limit: int) -> dict[str, Any]:
    """执行 glob 搜索。"""
    # 规范化路径
    if not path:
        path = os.getcwd()
    path = os.path.abspath(path)
    
    if not os.path.exists(path):
        raise FileNotFoundError(f"路径不存在: {path}")
    
    if not os.path.isdir(path):
        raise NotADirectoryError(f"路径不是目录: {path}")
    
    # 选择搜索方法
    if has_ripgrep():
        try:
            files = glob_with_ripgrep(pattern, path, limit)
            method = "ripgrep"
        except Exception:
            # 如果 ripgrep 失败，回退到 Python 实现
            files = glob_with_python(pattern, path, limit)
            method = "python (fallback)"
    else:
        files = glob_with_python(pattern, path, limit)
        method = "python"
    
    return {
        "pattern": pattern,
        "path": path,
        "method": method,
        "count": len(files),
        "files": files,
    }


def main():
    # 检查是否有 stdin 输入（Kimi CLI 工具调用方式）
    if not sys.stdin.isatty():
        try:
            params = json.load(sys.stdin)
            pattern = params.get("pattern")
            path = params.get("path", ".")
            limit = params.get("limit", 100)
            if not pattern:
                raise ValueError("pattern 参数是必需的")
        except json.JSONDecodeError:
            # 如果不是有效的 JSON，回退到命令行参数解析
            parser = argparse.ArgumentParser(
                description="基于模式匹配查找文件",
                formatter_class=argparse.RawDescriptionHelpFormatter,
                epilog=USAGE_GUIDE,
            )
            parser.add_argument("pattern", help="文件匹配模式，如 '**/*.py'")
            parser.add_argument("--path", default=".", help="搜索目录，默认为当前目录")
            parser.add_argument("--limit", type=int, default=100, help="返回结果数量限制，0 表示无限制")
            args = parser.parse_args()
            pattern = args.pattern
            path = args.path
            limit = args.limit
    else:
        # 命令行模式
        parser = argparse.ArgumentParser(
            description="基于模式匹配查找文件",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=USAGE_GUIDE,
        )
        parser.add_argument("pattern", help="文件匹配模式，如 '**/*.py'")
        parser.add_argument("--path", default=".", help="搜索目录，默认为当前目录")
        parser.add_argument("--limit", type=int, default=100, help="返回结果数量限制，0 表示无限制")
        args = parser.parse_args()
        pattern = args.pattern
        path = args.path
        limit = args.limit
    
    try:
        result = run_glob(pattern, path, limit)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except FileNotFoundError as e:
        print(json.dumps({
            "error": str(e),
            "type": "FileNotFoundError",
            "suggestion": "请检查路径是否正确",
            "usage_guide": USAGE_GUIDE,
        }, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
    except NotADirectoryError as e:
        print(json.dumps({
            "error": str(e),
            "type": "NotADirectoryError",
            "suggestion": "请提供目录路径而非文件路径",
            "usage_guide": USAGE_GUIDE,
        }, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
    except TimeoutError as e:
        print(json.dumps({
            "error": str(e),
            "type": "TimeoutError",
            "suggestion": "请缩小搜索范围或使用更具体的模式",
            "usage_guide": USAGE_GUIDE,
        }, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(json.dumps({
            "error": f"搜索失败: {e}",
            "type": "RuntimeError",
            "usage_guide": USAGE_GUIDE,
        }, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
