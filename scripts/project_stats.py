#!/usr/bin/env python3
"""Project Stats - 统计项目代码量和结构。

按语言、目录分组统计，生成项目概览报告。

使用场景:
- 了解项目整体规模
- 统计各编程语言的代码量
- 识别最大的文件
- 项目健康度评估

示例:
  project_stats --path .
  project_stats --path ./my-project --exclude "node_modules,*.pyc"
"""

import argparse
import json
import os
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


USAGE_GUIDE = """
Project Stats - 统计项目代码量和结构

核心功能:
- 按编程语言统计文件数和代码行数
- 按目录统计代码分布
- 识别项目中最大的文件
- 自动识别 30+ 种编程语言

参数:
- --path: 项目目录路径，默认当前目录
- --exclude: 排除模式，逗号分隔，默认 "node_modules,__pycache__,.git,venv,.venv,dist,build,.idea,.vscode"
- --output_format: 输出格式 (json/summary)，默认 json

使用示例:
  project_stats --path .                           # 分析当前目录
  project_stats --path ./my-project                # 分析指定项目
  project_stats --exclude "node_modules,vendor"    # 自定义排除模式
  project_stats --output_format summary            # 摘要输出

输出字段说明:
  - summary: 总体统计（文件数、行数、语言数）
  - by_language: 按语言分组统计
  - by_directory: 按目录分组统计
  - largest_files: 最大的 10 个文件

支持的语言:
  Python, JavaScript, TypeScript, Java, Go, Rust, C/C++, Ruby, PHP,
  Swift, Kotlin, Scala, HTML, CSS, SCSS, Sass, Shell, SQL, JSON, YAML,
  Markdown, Dockerfile, Vue, Svelte 等
"""


# 文件扩展名到语言的映射
LANGUAGE_MAP = {
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".jsx": "JavaScript",
    ".java": "Java",
    ".go": "Go",
    ".rs": "Rust",
    ".cpp": "C++",
    ".cc": "C++",
    ".cxx": "C++",
    ".c": "C",
    ".h": "C/C++ Header",
    ".hpp": "C++ Header",
    ".rb": "Ruby",
    ".php": "PHP",
    ".swift": "Swift",
    ".kt": "Kotlin",
    ".scala": "Scala",
    ".r": "R",
    ".m": "MATLAB/Objective-C",
    ".sh": "Shell",
    ".bash": "Shell",
    ".zsh": "Shell",
    ".ps1": "PowerShell",
    ".sql": "SQL",
    ".html": "HTML",
    ".htm": "HTML",
    ".css": "CSS",
    ".scss": "SCSS",
    ".sass": "Sass",
    ".less": "Less",
    ".xml": "XML",
    ".json": "JSON",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".toml": "TOML",
    ".ini": "INI",
    ".cfg": "Config",
    ".md": "Markdown",
    ".rst": "reStructuredText",
    ".txt": "Text",
    ".dockerfile": "Dockerfile",
    "dockerfile": "Dockerfile",
    ".vue": "Vue",
    ".svelte": "Svelte",
}


def get_language(file_path: Path) -> str:
    """根据文件扩展名判断语言。"""
    # 特殊处理 Dockerfile
    if file_path.name.lower() == "dockerfile":
        return "Dockerfile"
    if "dockerfile" in file_path.name.lower():
        return "Dockerfile"
    
    ext = file_path.suffix.lower()
    return LANGUAGE_MAP.get(ext, "Other")


def should_exclude(file_path: Path, exclude_patterns: list[str]) -> bool:
    """检查文件是否应该被排除。"""
    path_str = str(file_path)
    name = file_path.name
    
    for pattern in exclude_patterns:
        pattern = pattern.strip()
        if not pattern:
            continue
        
        # 检查文件名匹配
        if fnmatch(name, pattern):
            return True
        
        # 检查路径匹配
        if pattern in path_str:
            return True
    
    return False


def fnmatch(name: str, pattern: str) -> bool:
    """简单的 fnmatch 实现。"""
    import fnmatch as fnmatch_module
    return fnmatch_module.fnmatch(name, pattern)


def count_lines(file_path: Path) -> tuple[int, int, int]:
    """计算文件的行数统计。
    
    返回: (总行数, 代码行数, 空行数)
    """
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
    except Exception:
        return 0, 0, 0
    
    total = len(lines)
    blank = sum(1 for line in lines if not line.strip())
    code = total - blank
    
    return total, code, blank


def analyze_project(path: str, exclude_patterns: list[str]) -> dict[str, Any]:
    """分析项目统计。"""
    base_path = Path(path).resolve()
    
    if not base_path.exists():
        raise FileNotFoundError(f"路径不存在: {path}")
    
    # 统计数据
    stats = {
        "by_language": defaultdict(lambda: {"files": 0, "lines": 0, "code_lines": 0}),
        "by_directory": defaultdict(lambda: {"files": 0, "lines": 0}),
        "total_files": 0,
        "total_lines": 0,
        "total_code_lines": 0,
        "largest_files": [],
    }
    
    files_info = []
    
    # 遍历目录
    for root, dirnames, filenames in os.walk(base_path):
        # 跳过隐藏目录和排除目录
        dirnames[:] = [
            d for d in dirnames
            if not d.startswith(".") and not should_exclude(Path(root) / d, exclude_patterns)
        ]
        
        current_dir = Path(root).relative_to(base_path)
        if str(current_dir) == ".":
            current_dir = ""
        
        for filename in filenames:
            # 跳过隐藏文件
            if filename.startswith("."):
                continue
            
            file_path = Path(root) / filename
            
            # 检查排除模式
            if should_exclude(file_path, exclude_patterns):
                continue
            
            # 跳过二进制文件（简单判断）
            if is_binary(file_path):
                continue
            
            # 统计
            language = get_language(file_path)
            total, code, _ = count_lines(file_path)
            
            if total == 0:
                continue
            
            # 更新语言统计
            stats["by_language"][language]["files"] += 1
            stats["by_language"][language]["lines"] += total
            stats["by_language"][language]["code_lines"] += code
            
            # 更新目录统计
            dir_name = str(current_dir) or "(root)"
            stats["by_directory"][dir_name]["files"] += 1
            stats["by_directory"][dir_name]["lines"] += total
            
            # 更新总计
            stats["total_files"] += 1
            stats["total_lines"] += total
            stats["total_code_lines"] += code
            
            # 保存文件信息（用于找最大文件）
            files_info.append({
                "path": str(file_path.relative_to(base_path)),
                "language": language,
                "lines": total,
            })
    
    # 找出最大的文件
    files_info.sort(key=lambda x: x["lines"], reverse=True)
    stats["largest_files"] = files_info[:10]
    
    # 转换为普通 dict
    result = {
        "path": str(base_path),
        "summary": {
            "total_files": stats["total_files"],
            "total_lines": stats["total_lines"],
            "total_code_lines": stats["total_code_lines"],
            "languages": len(stats["by_language"]),
        },
        "by_language": dict(stats["by_language"]),
        "by_directory": dict(stats["by_directory"]),
        "largest_files": stats["largest_files"],
    }
    
    return result


def is_binary(file_path: Path) -> bool:
    """简单判断文件是否为二进制文件。"""
    binary_extensions = {
        ".exe", ".dll", ".so", ".dylib", ".bin",
        ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".svg",
        ".mp3", ".mp4", ".avi", ".mov", ".wmv",
        ".zip", ".tar", ".gz", ".bz2", ".7z", ".rar",
        ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
        ".db", ".sqlite", ".sqlite3",
        ".o", ".obj", ".a", ".lib",
        ".pyc", ".pyo", ".class",
        ".woff", ".woff2", ".ttf", ".otf", ".eot",
    }
    
    if file_path.suffix.lower() in binary_extensions:
        return True
    
    # 尝试读取前 1024 字节检查是否有 null 字节
    try:
        with open(file_path, "rb") as f:
            chunk = f.read(1024)
            if b"\x00" in chunk:
                return True
    except Exception:
        return True
    
    return False


def format_summary(result: dict[str, Any]) -> str:
    """格式化摘要输出。"""
    lines = []
    lines.append(f"Project Stats: {result['path']}")
    lines.append("")
    
    summary = result["summary"]
    lines.append(f"Summary:")
    lines.append(f"  Files: {summary['total_files']}")
    lines.append(f"  Lines: {summary['total_lines']:,} (code: {summary['total_code_lines']:,})")
    lines.append(f"  Languages: {summary['languages']}")
    lines.append("")
    
    # 按语言统计
    if result["by_language"]:
        lines.append("By Language:")
        sorted_langs = sorted(
            result["by_language"].items(),
            key=lambda x: x[1]["lines"],
            reverse=True,
        )
        for lang, data in sorted_langs[:10]:
            lines.append(f"  {lang}: {data['files']} files, {data['lines']:,} lines")
        lines.append("")
    
    # 最大的文件
    if result["largest_files"]:
        lines.append("Largest Files:")
        for f in result["largest_files"][:5]:
            lines.append(f"  {f['path']}: {f['lines']:,} lines ({f['language']})")
        lines.append("")
    
    return "\n".join(lines)


def main():
    # 检查是否有 stdin 输入（Kimi CLI 工具调用方式）
    if not sys.stdin.isatty():
        try:
            params = json.load(sys.stdin)
            path = params.get("path", ".")
            exclude = params.get("exclude", "node_modules,__pycache__,.git,venv,.venv,dist,build,.idea,.vscode")
            output_format = params.get("output_format", "json")
        except json.JSONDecodeError:
            # 如果不是有效的 JSON，回退到命令行参数解析
            parser = argparse.ArgumentParser(
                description="统计项目代码量和结构",
                formatter_class=argparse.RawDescriptionHelpFormatter,
                epilog=USAGE_GUIDE,
            )
            parser.add_argument("--path", default=".", help="项目目录路径，默认为当前目录")
            parser.add_argument(
                "--exclude",
                default="node_modules,__pycache__,.git,venv,.venv,dist,build,.idea,.vscode",
                help="排除模式，逗号分隔",
            )
            parser.add_argument(
                "--output_format",
                choices=["json", "summary"],
                default="json",
                help="输出格式",
            )
            args = parser.parse_args()
            path = args.path
            exclude = args.exclude
            output_format = args.output_format
    else:
        # 命令行模式
        parser = argparse.ArgumentParser(
            description="统计项目代码量和结构",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=USAGE_GUIDE,
        )
        parser.add_argument("--path", default=".", help="项目目录路径，默认为当前目录")
        parser.add_argument(
            "--exclude",
            default="node_modules,__pycache__,.git,venv,.venv,dist,build,.idea,.vscode",
            help="排除模式，逗号分隔",
        )
        parser.add_argument(
            "--output_format",
            choices=["json", "summary"],
            default="json",
            help="输出格式",
        )
        args = parser.parse_args()
        path = args.path
        exclude = args.exclude
        output_format = args.output_format
    
    exclude_patterns = [p.strip() for p in exclude.split(",")]
    
    try:
        result = analyze_project(path, exclude_patterns)
        
        if output_format == "summary":
            print(format_summary(result))
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2))
    
    except FileNotFoundError as e:
        print(json.dumps({
            "error": str(e),
            "type": "FileNotFoundError",
            "suggestion": "请检查路径是否正确",
            "usage_guide": USAGE_GUIDE,
        }, ensure_ascii=False), file=sys.stderr)
        exit(1)
    except Exception as e:
        print(json.dumps({
            "error": f"统计失败: {e}",
            "type": "Exception",
            "usage_guide": USAGE_GUIDE,
        }, ensure_ascii=False), file=sys.stderr)
        exit(1)


if __name__ == "__main__":
    main()
