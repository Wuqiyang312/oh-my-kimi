#!/usr/bin/env python3
"""Code Analyze - 分析 Python 代码结构。

使用 Python AST 模块解析代码，统计函数、类、导入、复杂度等信息。

使用场景:
- 了解代码文件的结构
- 统计函数、类、导入数量
- 评估代码复杂度

示例:
  code_analyze --path ./my_script.py
  code_analyze --path ./src --include_tests
"""

import argparse
import ast
import json
import os
import sys
from pathlib import Path
from typing import Any


USAGE_GUIDE = """
Code Analyze - 分析 Python 代码结构

核心功能:
- 使用 Python AST 模块解析代码
- 统计函数、类、导入、赋值语句数量
- 检测 docstring 和代码复杂度
- 计算代码行数（总行数、代码行数、空行数）

参数:
- --path (必需): Python 文件或目录路径
- --include_tests: 包含测试文件 (test_*.py, *_test.py)

使用示例:
  code_analyze --path ./my_script.py           # 分析单个文件
  code_analyze --path ./src --include_tests    # 分析目录（包含测试文件）
  code_analyze --path . | jq '.summary'        # 分析当前目录并查看摘要

输出字段说明:
  - lines.total: 总行数
  - lines.code: 代码行数（非空非注释）
  - lines.blank: 空行数
  - functions: 函数列表（含参数数量、是否有 docstring）
  - classes: 类列表（含基类、方法数量）
  - imports: 导入列表
  - complexity_score: 复杂度评分（函数数 + 类数 + 分支复杂度）
"""


class CodeAnalyzer(ast.NodeVisitor):
    """AST 访问者，用于分析 Python 代码。"""
    
    def __init__(self):
        self.functions = []
        self.classes = []
        self.imports = []
        self.assignments = 0
        self.complexity = 0
    
    def visit_FunctionDef(self, node):
        """访问函数定义。"""
        func_info = {
            "name": node.name,
            "line": node.lineno,
            "args": len(node.args.args),
            "docstring": ast.get_docstring(node) is not None,
        }
        self.functions.append(func_info)
        self.complexity += 1  # 简单的复杂度计算
        self.generic_visit(node)
    
    def visit_AsyncFunctionDef(self, node):
        """访问异步函数定义。"""
        func_info = {
            "name": node.name,
            "line": node.lineno,
            "args": len(node.args.args),
            "async": True,
            "docstring": ast.get_docstring(node) is not None,
        }
        self.functions.append(func_info)
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        """访问类定义。"""
        class_info = {
            "name": node.name,
            "line": node.lineno,
            "bases": [self._get_name(base) for base in node.bases],
            "methods": len([n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]),
            "docstring": ast.get_docstring(node) is not None,
        }
        self.classes.append(class_info)
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_Import(self, node):
        """访问导入语句。"""
        for alias in node.names:
            self.imports.append({
                "name": alias.name,
                "alias": alias.asname,
                "line": node.lineno,
                "type": "import",
            })
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        """访问 from ... import 语句。"""
        module = node.module or ""
        for alias in node.names:
            self.imports.append({
                "name": f"{module}.{alias.name}" if module else alias.name,
                "alias": alias.asname,
                "line": node.lineno,
                "type": "from",
                "module": module,
            })
        self.generic_visit(node)
    
    def visit_Assign(self, node):
        """访问赋值语句。"""
        self.assignments += 1
        self.generic_visit(node)
    
    def _get_name(self, node) -> str:
        """获取节点名称。"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        return str(node)


def analyze_file(file_path: str) -> dict[str, Any]:
    """分析单个 Python 文件。"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
    except Exception as e:
        return {"error": f"读取文件失败: {e}"}
    
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        return {"error": f"解析失败: {e}"}
    
    analyzer = CodeAnalyzer()
    analyzer.visit(tree)
    
    # 计算代码行数
    lines = source.split("\n")
    code_lines = len([l for l in lines if l.strip() and not l.strip().startswith("#")])
    total_lines = len(lines)
    
    # 检查模块级 docstring
    has_module_docstring = ast.get_docstring(tree) is not None
    
    return {
        "file": file_path,
        "lines": {
            "total": total_lines,
            "code": code_lines,
            "blank": len([l for l in lines if not l.strip()]),
            "comment": len([l for l in lines if l.strip().startswith("#")]),
        },
        "functions": analyzer.functions,
        "classes": analyzer.classes,
        "imports": analyzer.imports,
        "assignments": analyzer.assignments,
        "docstring": has_module_docstring,
        "complexity_score": analyzer.complexity + len(analyzer.functions) + len(analyzer.classes),
    }


def analyze_directory(dir_path: str, include_tests: bool) -> dict[str, Any]:
    """分析整个目录。"""
    files = []
    errors = []
    
    for root, dirnames, filenames in os.walk(dir_path):
        # 跳过排除目录
        dirnames[:] = [
            d for d in dirnames
            if not d.startswith(".") and d not in ("__pycache__", "node_modules", "venv", ".venv")
        ]
        
        for filename in filenames:
            if not filename.endswith(".py"):
                continue
            
            # 跳过测试文件（如果不需要）
            if not include_tests:
                if filename.startswith("test_") or filename.endswith("_test.py"):
                    continue
            
            file_path = os.path.join(root, filename)
            result = analyze_file(file_path)
            
            if "error" in result:
                errors.append({"file": file_path, "error": result["error"]})
            else:
                files.append(result)
    
    # 汇总统计
    total_lines = sum(f["lines"]["total"] for f in files)
    code_lines = sum(f["lines"]["code"] for f in files)
    total_functions = sum(len(f["functions"]) for f in files)
    total_classes = sum(len(f["classes"]) for f in files)
    total_imports = sum(len(f["imports"]) for f in files)
    
    return {
        "path": dir_path,
        "files_analyzed": len(files),
        "errors": errors,
        "summary": {
            "total_lines": total_lines,
            "code_lines": code_lines,
            "functions": total_functions,
            "classes": total_classes,
            "imports": total_imports,
        },
        "files": files,
    }


def is_test_file(file_path: str) -> bool:
    """检查是否为测试文件。"""
    name = os.path.basename(file_path)
    return name.startswith("test_") or name.endswith("_test.py")


def run_analysis(path: str, include_tests: bool) -> dict[str, Any]:
    """执行代码分析。"""
    if not os.path.exists(path):
        raise FileNotFoundError(f"路径不存在: {path}")
    
    if os.path.isfile(path):
        # 单文件分析
        if not path.endswith(".py"):
            raise ValueError(f"不是 Python 文件: {path}")
        
        result = analyze_file(path)
        if "error" in result:
            raise RuntimeError(result["error"])
        return result
    
    else:
        # 目录分析
        return analyze_directory(path, include_tests)


def main():
    parser = argparse.ArgumentParser(
        description="分析 Python 代码结构",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=USAGE_GUIDE,
    )
    parser.add_argument("--path", required=True, help="Python 文件或目录路径")
    parser.add_argument(
        "--include_tests",
        action="store_true",
        help="包含测试文件 (test_*.py, *_test.py)",
    )
    
    args = parser.parse_args()
    
    try:
        result = run_analysis(args.path, args.include_tests)
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
            "suggestion": "请提供 .py 文件或包含 Python 文件的目录",
            "usage_guide": USAGE_GUIDE,
        }, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
    except RuntimeError as e:
        print(json.dumps({
            "error": str(e),
            "type": "RuntimeError",
            "usage_guide": USAGE_GUIDE,
        }, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(json.dumps({
            "error": f"分析失败: {e}",
            "type": "Exception",
            "usage_guide": USAGE_GUIDE,
        }, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
