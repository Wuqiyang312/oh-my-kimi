#!/usr/bin/env python3
"""Smart Grep - 基于正则表达式搜索文件内容。

支持多种输出模式：content, files_with_matches, count。
优先使用 ripgrep (rg) 如果可用，否则使用 Python re 模块。

使用场景:
- 查找代码中的特定函数或类定义
- 搜索 TODO/FIXME 标记
- 查找特定字符串或模式的用法
- 统计代码中某模式的出现次数

示例:
  smart_grep "def main"                          # 查找 main 函数定义
  smart_grep "TODO|FIXME" --output_mode count    # 统计 TODO/FIXME 数量
  smart_grep "class.*:" --include "*.py" --output_mode content  # 查找类定义并显示内容
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


USAGE_GUIDE = """
Smart Grep - 基于正则表达式搜索文件内容

核心功能:
- 支持正则表达式搜索
- 多种输出模式: content, files_with_matches, count
- 文件类型过滤: --include "*.py"
- 优先使用 ripgrep (rg)，回退到 Python re 模块

参数:
- pattern (必需): 正则表达式搜索模式
- --path: 搜索目录，默认当前目录
- --include: 文件类型过滤，如 "*.py", "*.{ts,tsx}"
- --output_mode: 输出模式
  - content: 显示匹配行内容（含行号）
  - files_with_matches: 仅显示匹配的文件路径（默认）
  - count: 显示每个文件的匹配次数
- --head_limit: 限制输出结果数量，0 表示无限制

使用示例:
  smart_grep "^def " --include "*.py"                          # 查找函数定义
  smart_grep "^class " --include "*.py" --output_mode content  # 查找类定义并显示内容
  smart_grep "TODO|FIXME" --output_mode count                  # 统计 TODO/FIXME 数量
  smart_grep "smart_glob" --include "*.py"                     # 查找特定字符串用法

常见正则模式:
  ^def \\w+:     - 函数定义（Python）
  ^class \\w+:   - 类定义
  TODO|FIXME     - TODO 或 FIXME 标记
  import \\w+:   - 导入语句
  \\bfunction\\b - 单词 "function"
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


def grep_with_ripgrep(
    pattern: str,
    path: str,
    include: str | None,
    output_mode: str,
    head_limit: int,
) -> dict[str, Any]:
    """使用 ripgrep 进行内容搜索。"""
    cmd = ["rg", "--json", "--line-number", "--with-filename"]
    
    if include:
        cmd.extend(["-g", include])
    
    if output_mode == "files_with_matches":
        cmd.append("-l")  # 仅显示文件名
    elif output_mode == "count":
        cmd.append("-c")  # 显示计数
    
    cmd.extend(["-e", pattern, path])
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=60,
    )
    
    if result.returncode not in (0, 1):  # rg returns 1 when no matches, which is OK
        raise RuntimeError(f"ripgrep 错误: {result.stderr}")
    
    if output_mode == "files_with_matches":
        files = [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
        if head_limit > 0:
            files = files[:head_limit]
        return {
            "matches": [{"file": f} for f in files],
            "count": len(files),
        }
    
    elif output_mode == "count":
        counts = {}
        for line in result.stdout.strip().split("\n"):
            if ":" in line:
                file_path, count = line.rsplit(":", 1)
                try:
                    counts[file_path] = int(count)
                except ValueError:
                    pass
        
        matches = [{"file": f, "count": c} for f, c in counts.items()]
        if head_limit > 0:
            matches = matches[:head_limit]
        return {
            "matches": matches,
            "count": len(matches),
        }
    
    else:  # content mode
        matches = []
        
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
            try:
                data = json.loads(line)
                if data.get("type") == "match":
                    match_data = data.get("data", {})
                    file_path = match_data.get("path", {}).get("text", "")
                    line_num = match_data.get("line_number", 0)
                    lines = match_data.get("lines", {})
                    text = lines.get("text", "")
                    
                    matches.append({
                        "file": file_path,
                        "line": line_num,
                        "content": text.rstrip("\n"),
                    })
                    
                    if head_limit > 0 and len(matches) >= head_limit:
                        break
            except json.JSONDecodeError:
                continue
        
        return {
            "matches": matches,
            "count": len(matches),
        }


def should_include_file(file_path: Path, include: str | None) -> bool:
    """检查文件是否符合 include 模式。"""
    if not include:
        return True
    
    # 简单的 glob 匹配
    import fnmatch
    return fnmatch.fnmatch(file_path.name, include)


def grep_with_python(
    pattern: str,
    path: str,
    include: str | None,
    output_mode: str,
    head_limit: int,
) -> dict[str, Any]:
    """使用 Python re 模块进行内容搜索。"""
    try:
        regex = re.compile(pattern)
    except re.error as e:
        raise ValueError(f"无效的正则表达式: {e}")
    
    base_path = Path(path).resolve()
    matches = []
    files_matched = set()
    file_counts = {}
    
    # 限制搜索范围以提高性能
    max_files = 10000
    file_count = 0
    
    for root, dirnames, filenames in os.walk(base_path):
        # 跳过隐藏目录和常见排除目录
        dirnames[:] = [
            d for d in dirnames 
            if not d.startswith(".") and d not in ("node_modules", "__pycache__", "venv", ".venv", ".git")
        ]
        
        for filename in filenames:
            if not should_include_file(Path(filename), include):
                continue
            
            file_count += 1
            if file_count > max_files:
                break
            
            file_path = Path(root) / filename
            
            try:
                # 跳过二进制文件和大文件
                if file_path.stat().st_size > 1024 * 1024:  # 1MB
                    continue
                
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    
                    if output_mode == "files_with_matches":
                        if regex.search(content):
                            files_matched.add(str(file_path))
                            if head_limit > 0 and len(files_matched) >= head_limit:
                                break
                    
                    elif output_mode == "count":
                        count = len(regex.findall(content))
                        if count > 0:
                            file_counts[str(file_path)] = count
                    
                    else:  # content mode
                        for line_num, line in enumerate(content.split("\n"), 1):
                            if regex.search(line):
                                matches.append({
                                    "file": str(file_path),
                                    "line": line_num,
                                    "content": line,
                                })
                                if head_limit > 0 and len(matches) >= head_limit:
                                    break
                        if head_limit > 0 and len(matches) >= head_limit:
                            break
            
            except (IOError, OSError):
                continue
        
        if file_count > max_files:
            break
    
    if output_mode == "files_with_matches":
        files_list = sorted(files_matched)
        if head_limit > 0:
            files_list = files_list[:head_limit]
        return {
            "matches": [{"file": f} for f in files_list],
            "count": len(files_list),
        }
    
    elif output_mode == "count":
        items = [{"file": f, "count": c} for f, c in file_counts.items()]
        if head_limit > 0:
            items = items[:head_limit]
        return {
            "matches": items,
            "count": len(items),
        }
    
    else:  # content mode
        return {
            "matches": matches,
            "count": len(matches),
        }


def run_grep(
    pattern: str,
    path: str,
    include: str | None,
    output_mode: str,
    head_limit: int,
) -> dict[str, Any]:
    """执行 grep 搜索。"""
    # 规范化路径
    if not path:
        path = os.getcwd()
    path = os.path.abspath(path)
    
    if not os.path.exists(path):
        raise FileNotFoundError(f"路径不存在: {path}")
    
    # 选择搜索方法
    if has_ripgrep():
        try:
            result = grep_with_ripgrep(pattern, path, include, output_mode, head_limit)
            result["method"] = "ripgrep"
            result["pattern"] = pattern
            result["path"] = path
            return result
        except Exception:
            # 如果 ripgrep 失败，回退到 Python 实现
            pass
    
    result = grep_with_python(pattern, path, include, output_mode, head_limit)
    result["method"] = "python"
    result["pattern"] = pattern
    result["path"] = path
    return result


def main():
    # 检查是否有 stdin 输入（Kimi CLI 工具调用方式）
    if not sys.stdin.isatty():
        try:
            params = json.load(sys.stdin)
            pattern = params.get("pattern")
            path = params.get("path", ".")
            include = params.get("include")
            output_mode = params.get("output_mode", "files_with_matches")
            head_limit = params.get("head_limit", 0)
            if not pattern:
                raise ValueError("pattern 参数是必需的")
        except json.JSONDecodeError:
            # 如果不是有效的 JSON，回退到命令行参数解析
            parser = argparse.ArgumentParser(
                description="基于正则表达式搜索文件内容",
                formatter_class=argparse.RawDescriptionHelpFormatter,
                epilog=USAGE_GUIDE,
            )
            parser.add_argument("pattern", help="正则表达式搜索模式")
            parser.add_argument("--path", default=".", help="搜索目录，默认为当前目录")
            parser.add_argument("--include", help="文件类型过滤，如 '*.py'")
            parser.add_argument(
                "--output_mode",
                choices=["content", "files_with_matches", "count"],
                default="files_with_matches",
                help="输出模式",
            )
            parser.add_argument("--head_limit", type=int, default=0, help="输出结果数量限制，0 表示无限制")
            args = parser.parse_args()
            pattern = args.pattern
            path = args.path
            include = args.include
            output_mode = args.output_mode
            head_limit = args.head_limit
    else:
        # 命令行模式
        parser = argparse.ArgumentParser(
            description="基于正则表达式搜索文件内容",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=USAGE_GUIDE,
        )
        parser.add_argument("pattern", help="正则表达式搜索模式")
        parser.add_argument("--path", default=".", help="搜索目录，默认为当前目录")
        parser.add_argument("--include", help="文件类型过滤，如 '*.py'")
        parser.add_argument(
            "--output_mode",
            choices=["content", "files_with_matches", "count"],
            default="files_with_matches",
            help="输出模式",
        )
        parser.add_argument("--head_limit", type=int, default=0, help="输出结果数量限制，0 表示无限制")
        args = parser.parse_args()
        pattern = args.pattern
        path = args.path
        include = args.include
        output_mode = args.output_mode
        head_limit = args.head_limit
    
    try:
        result = run_grep(
            pattern,
            path,
            include,
            output_mode,
            head_limit,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except FileNotFoundError as e:
        print(json.dumps({
            "error": str(e),
            "type": "FileNotFoundError",
            "suggestion": "请检查路径是否正确",
            "usage_guide": USAGE_GUIDE,
        }, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(json.dumps({
            "error": str(e),
            "type": "ValueError",
            "suggestion": "请检查正则表达式语法",
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
