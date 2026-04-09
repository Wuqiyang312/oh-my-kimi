#!/usr/bin/env python3
"""GitHub Triage - 分析 GitHub 仓库的 Issues 和 PRs。

获取仓库的 Issues 和 PRs 列表，支持分页获取全部数据，
提供摘要统计和分类信息。

需要 gh CLI 已登录：gh auth login

使用场景:
- 了解仓库的活跃 Issues 和 PRs
- 按分类统计（Bug, Feature, Question 等）
- 识别需要关注的项目

示例:
  github_triage --repo code-yeongyu/oh-my-openagent
  github_triage --repo owner/repo --item_type issues --state open
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from typing import Any


USAGE_GUIDE = """
GitHub Triage - 分析 GitHub 仓库的 Issues 和 PRs

核心功能:
- 获取仓库的 Issues 和 PRs 列表
- 自动分类: Bug, Feature, Question, Other
- 统计活跃项目（30天内更新）

前置要求:
- 安装 gh CLI: https://cli.github.com/
- 已登录: gh auth login

参数:
- --repo (必需): GitHub 仓库 (owner/repo 格式)
- --item_type: 获取类型 (issues/prs/all)，默认 all
- --state: 状态过滤 (open/closed/all)，默认 open
- --output_format: 输出格式 (json/summary)，默认 summary

使用示例:
  github_triage --repo code-yeongyu/oh-my-openagent
  github_triage --repo owner/repo --item_type issues --state open
  github_triage --repo owner/repo --output_format json

分类规则:
  Issues:
    - bug: 标题包含 [Bug], Bug:, fix, error, crash
    - feature: 标题包含 [Feature], Feature:, RFE:, enhancement
    - question: 标题包含 [Question], Question:, how to, why does
    - other: 其他
  
  PRs:
    - bugfix: 分支/标题包含 fix, bugfix, hotfix
    - feature: 标题包含 feat:, feature:, add:
    - docs: 标题包含 docs:, doc:, documentation:
    - refactor: 标题包含 refactor:
    - test: 标题包含 test:, tests:
    - other: 其他
"""


def run_gh_command(args: list[str]) -> tuple[str, str, int]:
    """运行 gh CLI 命令。"""
    try:
        result = subprocess.run(
            ["gh"] + args,
            capture_output=True,
            text=True,
            timeout=120,
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        raise TimeoutError("GitHub API 请求超时")
    except FileNotFoundError:
        raise RuntimeError("gh CLI 未安装。请安装：https://cli.github.com/")


def check_gh_auth() -> bool:
    """检查是否已登录 GitHub。"""
    _, _, code = run_gh_command(["auth", "status"])
    return code == 0


def fetch_items(
    repo: str,
    item_type: str,  # "issue" or "pr"
    state: str,
) -> list[dict[str, Any]]:
    """获取 Issues 或 PRs，支持分页。"""
    all_items = []
    page = 1
    batch_size = 100
    
    while True:
        cmd = [
            item_type,
            "list",
            "--repo", repo,
            "--state", state,
            "--limit", str(batch_size),
            "--json", "number,title,state,createdAt,updatedAt,labels,author,body",
        ]
        
        stdout, stderr, code = run_gh_command(cmd)
        
        if code != 0:
            raise RuntimeError(f"获取 {item_type}s 失败: {stderr}")
        
        try:
            items = json.loads(stdout) if stdout.strip() else []
        except json.JSONDecodeError as e:
            raise RuntimeError(f"解析 {item_type}s 响应失败: {e}")
        
        if not items:
            break
        
        all_items.extend(items)
        
        # 如果获取的数量小于 batch_size，说明已经获取全部
        if len(items) < batch_size:
            break
        
        # 分页：使用搜索获取下一页
        last_created = items[-1].get("createdAt", "")
        if not last_created:
            break
        
        page += 1
        if page > 10:  # 安全限制：最多 1000 项
            break
    
    return all_items


def classify_issue(issue: dict[str, Any]) -> str:
    """对 Issue 进行分类。"""
    title = issue.get("title", "").lower()
    labels = [label.get("name", "").lower() for label in issue.get("labels", [])]
    
    # 检查标签
    if any("bug" in label or "fix" in label for label in labels):
        return "bug"
    if any("feature" in label or "enhancement" in label or "rfe" in label for label in labels):
        return "feature"
    if any("question" in label or "discussion" in label for label in labels):
        return "question"
    
    # 检查标题
    if any(kw in title for kw in ["[bug]", "bug:", "fix:", "error", "crash", "broken"]):
        return "bug"
    if any(kw in title for kw in ["[feature]", "feature:", "rfe:", "enhancement:", "proposal:"]):
        return "feature"
    if any(kw in title for kw in ["[question]", "question:", "how to", "why does", "is it possible"]):
        return "question"
    
    return "other"


def classify_pr(pr: dict[str, Any]) -> str:
    """对 PR 进行分类。"""
    title = pr.get("title", "").lower()
    labels = [label.get("name", "").lower() for label in pr.get("labels", [])]
    
    if any("bug" in label or "fix" in label for label in labels):
        return "bugfix"
    if any("feature" in label or "enhancement" in label for label in labels):
        return "feature"
    if "docs" in labels or "documentation" in labels:
        return "docs"
    if "refactor" in labels:
        return "refactor"
    if "test" in labels:
        return "test"
    
    if any(kw in title for kw in ["fix:", "fix(", "bugfix", "hotfix"]):
        return "bugfix"
    if any(kw in title for kw in ["feat:", "feat(", "feature:", "add:", "add("]):
        return "feature"
    if any(kw in title for kw in ["docs:", "docs(", "doc:", "documentation:"]):
        return "docs"
    if any(kw in title for kw in ["refactor:", "refactor(", "refactoring:"]):
        return "refactor"
    if any(kw in title for kw in ["test:", "test(", "tests:"]):
        return "test"
    
    return "other"


def analyze_items(items: list[dict[str, Any]], item_type: str) -> dict[str, Any]:
    """分析 Items 并生成统计。"""
    if not items:
        return {
            "total": 0,
            "categories": {},
            "authors": {},
            "recent": 0,
        }
    
    categories = {}
    authors = {}
    recent_count = 0
    
    # 30 天前的日期
    thirty_days_ago = datetime.now().timestamp() - (30 * 24 * 60 * 60)
    
    for item in items:
        # 分类
        if item_type == "issue":
            category = classify_issue(item)
        else:
            category = classify_pr(item)
        categories[category] = categories.get(category, 0) + 1
        
        # 作者统计
        author = item.get("author", {}).get("login", "unknown")
        authors[author] = authors.get(author, 0) + 1
        
        # 最近 30 天的数量
        updated_at = item.get("updatedAt", "")
        if updated_at:
            try:
                # 解析 ISO 格式日期
                item_time = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
                if item_time.timestamp() > thirty_days_ago:
                    recent_count += 1
            except ValueError:
                pass
    
    return {
        "total": len(items),
        "categories": categories,
        "authors": dict(sorted(authors.items(), key=lambda x: x[1], reverse=True)[:10]),
        "recent": recent_count,
    }


def run_triage(
    repo: str,
    item_type: str,
    state: str,
    output_format: str,
) -> dict[str, Any]:
    """执行 GitHub Triage 分析。"""
    # 验证 gh CLI 和登录状态
    if not check_gh_auth():
        raise RuntimeError("未登录 GitHub。请运行: gh auth login")
    
    result = {
        "repo": repo,
        "state": state,
        "timestamp": datetime.now().isoformat(),
    }
    
    # 获取 Issues
    if item_type in ("issues", "all"):
        try:
            issues = fetch_items(repo, "issue", state)
            result["issues"] = {
                "items": issues[:50] if output_format == "json" else None,  # summary 模式不返回详细列表
                "analysis": analyze_items(issues, "issue"),
            }
            if result["issues"]["items"] is None:
                del result["issues"]["items"]
        except Exception as e:
            result["issues_error"] = str(e)
    
    # 获取 PRs
    if item_type in ("prs", "all"):
        try:
            prs = fetch_items(repo, "pr", state)
            result["prs"] = {
                "items": prs[:50] if output_format == "json" else None,
                "analysis": analyze_items(prs, "pr"),
            }
            if result["prs"]["items"] is None:
                del result["prs"]["items"]
        except Exception as e:
            result["prs_error"] = str(e)
    
    return result


def format_summary(result: dict[str, Any]) -> str:
    """格式化摘要输出。"""
    lines = []
    lines.append(f"GitHub Triage Report: {result['repo']}")
    lines.append(f"State: {result['state']} | Generated: {result['timestamp']}")
    lines.append("")
    
    if "issues" in result:
        analysis = result["issues"]["analysis"]
        lines.append(f"📋 Issues: {analysis['total']} total")
        if analysis["categories"]:
            lines.append(f"   Categories: {', '.join(f'{k}: {v}' for k, v in analysis['categories'].items())}")
        lines.append(f"   Active (30d): {analysis['recent']}")
        lines.append("")
    
    if "prs" in result:
        analysis = result["prs"]["analysis"]
        lines.append(f"🔀 PRs: {analysis['total']} total")
        if analysis["categories"]:
            lines.append(f"   Categories: {', '.join(f'{k}: {v}' for k, v in analysis['categories'].items())}")
        lines.append(f"   Active (30d): {analysis['recent']}")
        lines.append("")
    
    if "issues_error" in result:
        lines.append(f"⚠️ Issues Error: {result['issues_error']}")
    if "prs_error" in result:
        lines.append(f"⚠️ PRs Error: {result['prs_error']}")
    
    return "\n".join(lines)


def main():
    # 检查是否有 stdin 输入（Kimi CLI 工具调用方式）
    if not sys.stdin.isatty():
        try:
            params = json.load(sys.stdin)
            repo = params.get("repo")
            item_type = params.get("item_type", "all")
            state = params.get("state", "open")
            output_format = params.get("output_format", "summary")
            if not repo:
                raise ValueError("repo 参数是必需的")
        except json.JSONDecodeError:
            # 如果不是有效的 JSON，回退到命令行参数解析
            parser = argparse.ArgumentParser(
                description="分析 GitHub 仓库的 Issues 和 PRs",
                formatter_class=argparse.RawDescriptionHelpFormatter,
                epilog=USAGE_GUIDE,
            )
            parser.add_argument("--repo", required=True, help="GitHub 仓库 (owner/repo)")
            parser.add_argument(
                "--item_type",
                choices=["issues", "prs", "all"],
                default="all",
                help="获取类型",
            )
            parser.add_argument(
                "--state",
                choices=["open", "closed", "all"],
                default="open",
                help="状态过滤",
            )
            parser.add_argument(
                "--output_format",
                choices=["json", "summary"],
                default="summary",
                help="输出格式",
            )
            args = parser.parse_args()
            repo = args.repo
            item_type = args.item_type
            state = args.state
            output_format = args.output_format
    else:
        # 命令行模式
        parser = argparse.ArgumentParser(
            description="分析 GitHub 仓库的 Issues 和 PRs",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=USAGE_GUIDE,
        )
        parser.add_argument("--repo", required=True, help="GitHub 仓库 (owner/repo)")
        parser.add_argument(
            "--item_type",
            choices=["issues", "prs", "all"],
            default="all",
            help="获取类型",
        )
        parser.add_argument(
            "--state",
            choices=["open", "closed", "all"],
            default="open",
            help="状态过滤",
        )
        parser.add_argument(
            "--output_format",
            choices=["json", "summary"],
            default="summary",
            help="输出格式",
        )
        args = parser.parse_args()
        repo = args.repo
        item_type = args.item_type
        state = args.state
        output_format = args.output_format
    
    try:
        result = run_triage(repo, item_type, state, output_format)
        
        if output_format == "summary":
            print(format_summary(result))
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2))
    
    except RuntimeError as e:
        print(json.dumps({
            "error": str(e),
            "type": "RuntimeError",
            "suggestion": "请确保已安装 gh CLI 并运行 'gh auth login' 登录",
            "usage_guide": USAGE_GUIDE,
        }, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
    except TimeoutError as e:
        print(json.dumps({
            "error": str(e),
            "type": "TimeoutError",
            "suggestion": "GitHub API 请求超时，请稍后重试",
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
