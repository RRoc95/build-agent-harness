#!/usr/bin/env python3
"""Read-only inventory plus structural and style validation for agent harnesses."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple
from urllib.parse import unquote, urlsplit


DEFAULT_MAX_AGENT_BYTES = 32 * 1024
CANONICAL_PLANS_PATH = (
    Path(__file__).resolve().parent.parent / "assets" / "PLANS.md"
)

IGNORED_DIRECTORIES = {
    ".git",
    ".hg",
    ".idea",
    ".mypy_cache",
    ".next",
    ".nuxt",
    ".pytest_cache",
    ".ruff_cache",
    ".svn",
    ".tox",
    ".turbo",
    ".venv",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "target",
    "vendor",
    "venv",
}

MANIFEST_NAMES = {
    "Cargo.toml",
    "CMakeLists.txt",
    "Gemfile",
    "Makefile",
    "Package.swift",
    "WORKSPACE",
    "build.gradle",
    "build.gradle.kts",
    "composer.json",
    "deno.json",
    "deno.jsonc",
    "go.mod",
    "go.work",
    "meson.build",
    "mix.exs",
    "package.json",
    "pom.xml",
    "pyproject.toml",
    "requirements.txt",
    "settings.gradle",
    "settings.gradle.kts",
}

HARNESS_BASENAMES = {
    "AGENTS.md",
    "AGENTS.override.md",
    "ARCHITECTURE.md",
    "CLAUDE.md",
    "PLANS.md",
}

QUALITY_DOC_NAMES = {
    "code-review.md",
    "coding-standards.md",
    "verification-guide.md",
}

SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FENCE_RE = re.compile(r"^[ \t]{0,3}(`{3,}|~{3,})")
HEADING_RE = re.compile(r"^(#{1,6})[ \t]+(.+?)[ \t]*$")
NUMBERED_SECTION_RE = re.compile(r"^(\d+)\.[ \t]+(.+)$")
LIST_ITEM_RE = re.compile(r"^[ \t]{0,3}(?:[-*+]|\d+[.)])[ \t]+")
LINK_RE = re.compile(r"!?\[[^\]\n]*\]\(([^)\n]+)\)")
FRONTMATTER_KEY_RE = re.compile(r"^([A-Za-z][A-Za-z0-9_-]*):(?:\s*(.*))?$")
CLAUDE_IMPORT_RE = re.compile(r"^\s*@([^\s]+)\s*$")
ARCHITECTURE_TITLE_RE = re.compile(r"^ARCHITECTURE\.md — \S.*$")
COMPLETION_HEADING_RE = re.compile(
    r"(完成|交付|definition[ \t]+of[ \t]+done|completion|done)",
    re.IGNORECASE,
)
VERIFICATION_HEADING_RE = re.compile(
    r"(验证|校验|verification|validation|verify)", re.IGNORECASE
)
FINAL_VERIFICATION_HEADING_RE = re.compile(
    r"^(?:验证(?:入口|指南|方式)?|校验|"
    r"(?:verification|validation)(?:[ \t]+(?:entry|entry[ \t]+points|guide))?)$",
    re.IGNORECASE,
)
FUTURE_ARCHITECTURE_HEADING_RE = re.compile(
    r"(当前问题诊断|建议.*演进|演进方向|未来(?:架构|设计|形态|工作)|"
    r"后续(?:计划|工作)|下一步|路线图|值得继续推进|recommended[ \t]+evolution|"
    r"future[ \t]+(?:architecture|design|work)|follow-up|planned[ \t]+changes?|"
    r"roadmap|proposed[ \t]+(?:architecture|design)|next[ \t]+(?:steps|priorities))",
    re.IGNORECASE,
)

ROOT_AGENTS_SECTIONS = (
    (
        "project positioning and repository map",
        re.compile(
            r"(项目.*(?:定位|目录|地图)|仓库地图|repository[ \t]+map|"
            r"project[ \t]+(?:map|positioning|overview))",
            re.IGNORECASE,
        ),
    ),
    (
        "before-start guidance",
        re.compile(
            r"(开始(?:任务)?前?|任务前|before[ \t]+(?:starting|work)|getting[ \t]+started)",
            re.IGNORECASE,
        ),
    ),
    (
        "autonomy and execution boundaries",
        re.compile(
            r"(自治|审批|执行(?:边界|闭环|流程)|工作方式|autonomy|approval|"
            r"execution[ \t]+(?:boundary|loop)|working[ \t]+method)",
            re.IGNORECASE,
        ),
    ),
    (
        "ExecPlan triggers",
        re.compile(r"exec[ \t-]*plans?", re.IGNORECASE),
    ),
    (
        "repository invariants",
        re.compile(
            r"(仓库.*不变量|跨.*不变量|全局.*约束|repository[ \t]+invariants?|"
            r"global[ \t]+constraints?)",
            re.IGNORECASE,
        ),
    ),
    (
        "on-demand documentation",
        re.compile(
            r"(按需阅读|文档与代码边界|文档(?:导航|索引|边界)|"
            r"on-demand[ \t]+reading|documentation[ \t]+(?:map|boundaries|index))",
            re.IGNORECASE,
        ),
    ),
    (
        "authoritative commands",
        re.compile(
            r"(常用命令|权威验证|验证命令|commands?|verification[ \t]+commands?)",
            re.IGNORECASE,
        ),
    ),
    (
        "completion criteria",
        COMPLETION_HEADING_RE,
    ),
)

NESTED_AGENTS_SECTIONS = (
    (
        "subproject scope and entry points",
        re.compile(
            r"(子工程定位|项目定位|工作入口|范围与入口|范围与结构|scope|"
            r"entry[ \t]+points?|project[ \t]+positioning)",
            re.IGNORECASE,
        ),
    ),
    (
        "before-editing guidance",
        re.compile(
            r"(开始前|开始任务|工作入口|阅读顺序|范围与入口|before|"
            r"getting[ \t]+started|read[ \t]+first)",
            re.IGNORECASE,
        ),
    ),
    (
        "architecture and dependency constraints",
        re.compile(
            r"(架构|分层|职责边界|实现约束|组件约束|不变量|结构|architecture|"
            r"layers?|dependency|boundaries|constraints?|invariants?)",
            re.IGNORECASE,
        ),
    ),
    (
        "domain contracts and high-risk invariants",
        re.compile(
            r"(关键契约|认证与错误|API.*(?:任务|回调)|开放平台|数据库与安全|"
            r"UI.*交互|代码与依赖|运行不变量|必须保持.*不变量|组件约束|"
            r"迁移与安全|高风险|domain[ \t]+contracts?|contracts?|security|"
            r"authentication|error[ \t]+boundaries)",
            re.IGNORECASE,
        ),
    ),
    (
        "tests and authoritative commands",
        re.compile(
            r"(常用命令|本地命令|测试|验证|commands?|tests?|verification)",
            re.IGNORECASE,
        ),
    ),
    (
        "completion criteria",
        COMPLETION_HEADING_RE,
    ),
)

ARCHITECTURE_SECTIONS = (
    (
        "system purpose and runtime boundary",
        re.compile(
            r"(系统定位|系统角色|技术栈与运行边界|边界与职责|项目定位|"
            r"system[ \t]+(?:purpose|role|positioning|boundary)|runtime[ \t]+boundary)",
            re.IGNORECASE,
        ),
    ),
    (
        "layers and dependency direction",
        re.compile(
            r"(分层|依赖方向|源码结构|应用组合|运行结构|顶层架构|模块关系|"
            r"layers?|dependency[ \t]+direction|source[ \t]+layout|"
            r"application[ \t]+composition)",
            re.IGNORECASE,
        ),
    ),
    (
        "startup, lifecycle, or representative runtime flow",
        re.compile(
            r"(启动|生命周期|路由|数据流|运行流程|进程生命周期|startup|"
            r"lifecycle|routing|data[ \t]+flow|runtime[ \t]+flow|"
            r"(?:request|event|job|execution|representative)[ \t]+flow)",
            re.IGNORECASE,
        ),
    ),
    (
        "verification",
        VERIFICATION_HEADING_RE,
    ),
)


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Inventory or validate repository agent harness structure and style "
            "without modifying it."
        )
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Repository path; a containing Git root is used when available.",
    )
    parser.add_argument(
        "--max-agent-bytes",
        type=positive_int,
        default=DEFAULT_MAX_AGENT_BYTES,
        help="Maximum combined bytes for an applicable AGENTS instruction chain.",
    )

    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("inventory", "validate"):
        command = commands.add_parser(name)
        command.add_argument(
            "--json", action="store_true", help="Emit machine-readable JSON."
        )
        command.add_argument(
            "--project-boundary",
            action="append",
            default=[],
            metavar="PATH",
            help=(
                "Repository-relative independently buildable or runnable project "
                "boundary; repeat for multiple projects."
            ),
        )
    return parser.parse_args(argv)


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return parsed


def run_git(path: Path, *arguments: str) -> Optional[str]:
    completed = subprocess.run(
        ["git", "-C", str(path), *arguments],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    if completed.returncode != 0:
        return None
    return completed.stdout.rstrip("\n")


def resolve_repository(path_value: str) -> Tuple[Path, Optional[Path]]:
    requested = Path(path_value).expanduser().resolve()
    if not requested.exists():
        raise ValueError(f"repository path does not exist: {requested}")
    if not requested.is_dir():
        raise ValueError(f"repository path is not a directory: {requested}")

    git_root_value = run_git(requested, "rev-parse", "--show-toplevel")
    if git_root_value:
        git_root = Path(git_root_value).resolve()
        return git_root, git_root
    return requested, None


def normalize_project_boundaries(root: Path, values: Sequence[str]) -> List[str]:
    normalized = set()
    for value in values:
        candidate = (root / value).resolve()
        try:
            candidate.relative_to(root)
        except ValueError as exc:
            raise ValueError(
                f"project boundary escapes repository root: {value}"
            ) from exc
        if not candidate.is_dir():
            raise ValueError(f"project boundary is not a directory: {value}")
        normalized.add(relative(candidate, root))
    return sorted(normalized)


def iter_files(root: Path) -> Iterable[Path]:
    for current, directory_names, file_names in os.walk(
        root, topdown=True, followlinks=False
    ):
        current_path = Path(current)
        retained_directories = []
        for name in directory_names:
            candidate = current_path / name
            if name in IGNORED_DIRECTORIES or candidate.is_symlink():
                continue
            retained_directories.append(name)
        directory_names[:] = sorted(retained_directories)

        for name in sorted(file_names):
            candidate = current_path / name
            if candidate.is_file():
                yield candidate


def relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def is_manifest(path: Path) -> bool:
    return (
        path.name in MANIFEST_NAMES
        or path.suffix in {".csproj", ".fsproj", ".sln", ".vbproj"}
    )


def is_exec_plan(path: Path, root: Path) -> bool:
    parts = path.relative_to(root).parts
    return (
        path.suffix.lower() == ".md"
        and len(parts) >= 3
        and parts[0] == "docs"
        and parts[1] == "exec-plans"
    )


def is_project_skill(path: Path, root: Path) -> bool:
    parts = path.relative_to(root).parts
    return (
        path.name == "SKILL.md"
        and len(parts) >= 4
        and parts[0] == ".agents"
        and parts[1] == "skills"
    )


def is_quality_doc(path: Path, root: Path) -> bool:
    parts = path.relative_to(root).parts
    return "docs" in parts[:-1] and path.name.lower() in QUALITY_DOC_NAMES


def is_harness_file(path: Path, root: Path) -> bool:
    return (
        path.name in HARNESS_BASENAMES
        or is_exec_plan(path, root)
        or is_project_skill(path, root)
        or is_quality_doc(path, root)
    )


def file_record(path: Path, root: Path) -> Dict[str, Any]:
    return {"path": relative(path, root), "bytes": path.stat().st_size}


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def plans_template_status(root: Path) -> Dict[str, Any]:
    if not CANONICAL_PLANS_PATH.is_file():
        raise RuntimeError(
            f"canonical PLANS.md asset does not exist: {CANONICAL_PLANS_PATH}"
        )

    canonical_content = CANONICAL_PLANS_PATH.read_bytes()
    target = root / "PLANS.md"
    target_content = target.read_bytes() if target.is_file() else None
    return {
        "status": (
            "missing"
            if target_content is None
            else "matches"
            if target_content == canonical_content
            else "differs"
        ),
        "canonical_sha256": sha256_bytes(canonical_content),
        "target_sha256": (
            sha256_bytes(target_content) if target_content is not None else None
        ),
    }


def claude_skill_links(root: Path) -> List[Dict[str, Any]]:
    links_root = root / ".claude" / "skills"
    if not links_root.exists() and not links_root.is_symlink():
        return []

    entries: List[Dict[str, Any]] = []
    if links_root.is_symlink():
        candidates = [links_root]
    else:
        candidates = list(links_root.rglob("*"))

    for candidate in sorted(candidates, key=lambda item: item.as_posix()):
        if not candidate.is_symlink():
            continue
        entries.append(
            {
                "path": relative(candidate, root),
                "target": os.readlink(candidate),
                "broken": not candidate.exists(),
            }
        )
    return entries


def build_inventory(root: Path, git_root: Optional[Path]) -> Dict[str, Any]:
    files = list(iter_files(root))
    manifests = [path for path in files if is_manifest(path)]
    agent_files = [
        path for path in files if path.name in {"AGENTS.md", "AGENTS.override.md"}
    ]
    architecture_files = [path for path in files if path.name == "ARCHITECTURE.md"]
    claude_files = [path for path in files if path.name == "CLAUDE.md"]
    project_skills = [path for path in files if is_project_skill(path, root)]
    exec_plans = [path for path in files if is_exec_plan(path, root)]
    harness_files = [path for path in files if is_harness_file(path, root)]

    subprojects: Dict[str, List[str]] = {}
    for manifest in manifests:
        parent = relative(manifest.parent, root)
        subprojects.setdefault(parent, []).append(manifest.name)

    agent_directories = {relative(path.parent, root) for path in agent_files}
    manifest_directories = set(subprojects)
    nested_project_boundaries = sorted(
        (agent_directories & manifest_directories) - {"."}
    )
    project_boundaries = nested_project_boundaries
    if (
        not nested_project_boundaries
        and "." in agent_directories
        and "." in manifest_directories
    ):
        project_boundaries = ["."]

    status_output = run_git(root, "status", "--short") if git_root else None
    head = run_git(root, "rev-parse", "--short", "HEAD") if git_root else None

    return {
        "root": str(root),
        "git_root": str(git_root) if git_root else None,
        "git_head": head,
        "git_status": status_output.splitlines() if status_output else [],
        "manifests": [relative(path, root) for path in manifests],
        "subproject_candidates": [
            {"path": path, "manifests": sorted(names)}
            for path, names in sorted(subprojects.items())
        ],
        "project_boundaries": project_boundaries,
        "harness_files": [file_record(path, root) for path in harness_files],
        "agent_files": [file_record(path, root) for path in agent_files],
        "architecture_files": [relative(path, root) for path in architecture_files],
        "claude_files": [relative(path, root) for path in claude_files],
        "project_skills": [relative(path, root) for path in project_skills],
        "exec_plans": [relative(path, root) for path in exec_plans],
        "plans_template": plans_template_status(root),
        "claude_skill_links": claude_skill_links(root),
    }


def finding(
    code: str, message: str, path: Optional[str] = None, line: Optional[int] = None
) -> Dict[str, Any]:
    result: Dict[str, Any] = {"code": code, "message": message}
    if path is not None:
        result["path"] = path
    if line is not None:
        result["line"] = line
    return result


def read_markdown(path: Path, root: Path, errors: List[Dict[str, Any]]) -> Optional[str]:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        errors.append(
            finding(
                "invalid-utf8",
                "harness Markdown must be valid UTF-8",
                relative(path, root),
            )
        )
    except OSError as exc:
        errors.append(
            finding("unreadable-file", str(exc), relative(path, root))
        )
    return None


def check_fences(
    path: Path, root: Path, text: str, errors: List[Dict[str, Any]]
) -> None:
    open_fence: Optional[Tuple[str, int, int]] = None
    for line_number, line in enumerate(text.splitlines(), start=1):
        match = FENCE_RE.match(line)
        if not match:
            continue
        marker = match.group(1)
        marker_type = marker[0]
        marker_length = len(marker)
        if open_fence is None:
            open_fence = (marker_type, marker_length, line_number)
        elif marker_type == open_fence[0] and marker_length >= open_fence[1]:
            open_fence = None

    if open_fence is not None:
        errors.append(
            finding(
                "unclosed-fence",
                "Markdown code fence is not closed",
                relative(path, root),
                open_fence[2],
            )
        )


def check_fence_labels(
    path: Path, root: Path, text: str, errors: List[Dict[str, Any]]
) -> None:
    open_fence: Optional[Tuple[str, int]] = None

    for line_number, line in enumerate(text.splitlines(), start=1):
        match = FENCE_RE.match(line)
        if not match:
            continue
        marker = match.group(1)
        marker_type = marker[0]
        marker_length = len(marker)
        if open_fence is None:
            if not line[match.end() :].strip():
                errors.append(
                    finding(
                        "unlabeled-code-fence",
                        "AGENTS.md and ARCHITECTURE.md code fences need a language label",
                        relative(path, root),
                        line_number,
                    )
                )
            open_fence = (marker_type, marker_length)
        elif marker_type == open_fence[0] and marker_length >= open_fence[1]:
            open_fence = None


def markdown_headings(text: str) -> List[Dict[str, Any]]:
    headings: List[Dict[str, Any]] = []
    open_fence: Optional[Tuple[str, int]] = None

    for line_number, line in enumerate(text.splitlines(), start=1):
        fence_match = FENCE_RE.match(line)
        if fence_match:
            marker = fence_match.group(1)
            marker_type = marker[0]
            marker_length = len(marker)
            if open_fence is None:
                open_fence = (marker_type, marker_length)
            elif marker_type == open_fence[0] and marker_length >= open_fence[1]:
                open_fence = None
            continue
        if open_fence is not None:
            continue

        heading_match = HEADING_RE.match(line)
        if not heading_match:
            continue
        title = re.sub(r"[ \t]+#+[ \t]*$", "", heading_match.group(2).strip())
        headings.append(
            {
                "level": len(heading_match.group(1)),
                "title": title,
                "line": line_number,
            }
        )
    return headings


def section_number(title: str) -> Optional[int]:
    match = NUMBERED_SECTION_RE.match(title)
    return int(match.group(1)) if match else None


def section_title(title: str) -> str:
    match = NUMBERED_SECTION_RE.match(title)
    return match.group(2).strip() if match else title.strip()


def has_opening_scope_paragraph(
    text: str, title_line: int, first_section_line: int
) -> bool:
    lines = text.splitlines()
    open_fence: Optional[Tuple[str, int]] = None
    in_html_comment = False

    for line in lines[title_line : first_section_line - 1]:
        fence_match = FENCE_RE.match(line)
        if fence_match:
            marker = fence_match.group(1)
            marker_type = marker[0]
            marker_length = len(marker)
            if open_fence is None:
                open_fence = (marker_type, marker_length)
            elif marker_type == open_fence[0] and marker_length >= open_fence[1]:
                open_fence = None
            continue
        if open_fence is not None:
            continue

        if in_html_comment:
            closing = line.find("-->")
            if closing == -1:
                continue
            line = line[closing + 3 :]
            in_html_comment = False
        while "<!--" in line:
            opening = line.find("<!--")
            closing = line.find("-->", opening + 4)
            if closing == -1:
                line = line[:opening]
                in_html_comment = True
                break
            line = line[:opening] + line[closing + 3 :]

        stripped = line.strip()
        if not stripped:
            continue
        if (
            stripped.startswith(("#", "-", "*", "+", ">", "|", "```", "~~~"))
            or stripped.startswith("<!--")
            or re.match(r"^\d+[.)][ \t]+", stripped)
        ):
            continue
        return True
    return False


def is_plain_prose_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if (
        stripped.startswith(("#", "-", "*", "+", ">", "|", "```", "~~~"))
        or stripped.startswith("<!--")
        or stripped.endswith("-->")
        or re.match(r"^\d+[.)][ \t]+", stripped)
        or re.fullmatch(r"[-*_]{3,}", stripped)
    ):
        return False
    return True


def check_manual_prose_wrapping(
    path: Path, root: Path, text: str, errors: List[Dict[str, Any]]
) -> None:
    open_fence: Optional[Tuple[str, int]] = None
    in_html_comment = False
    previous_plain = False
    previous_list_item = False

    for line_number, line in enumerate(text.splitlines(), start=1):
        fence_match = FENCE_RE.match(line)
        if fence_match:
            marker = fence_match.group(1)
            marker_type = marker[0]
            marker_length = len(marker)
            if open_fence is None:
                open_fence = (marker_type, marker_length)
            elif marker_type == open_fence[0] and marker_length >= open_fence[1]:
                open_fence = None
            previous_plain = False
            previous_list_item = False
            continue
        if open_fence is not None:
            previous_plain = False
            previous_list_item = False
            continue

        if in_html_comment:
            closing = line.find("-->")
            if closing == -1:
                previous_plain = False
                previous_list_item = False
                continue
            line = line[closing + 3 :]
            in_html_comment = False
        while "<!--" in line:
            opening = line.find("<!--")
            closing = line.find("-->", opening + 4)
            if closing == -1:
                line = line[:opening]
                in_html_comment = True
                break
            line = line[:opening] + line[closing + 3 :]

        current_plain = is_plain_prose_line(line)
        if current_plain and (previous_plain or previous_list_item):
            errors.append(
                finding(
                    "manual-prose-wrapping",
                    "keep each prose paragraph or list item on one source line; "
                    "this content appears manually wrapped",
                    relative(path, root),
                    line_number,
                )
            )
            return
        previous_plain = current_plain
        previous_list_item = bool(LIST_ITEM_RE.match(line))


def semantic_section_positions(
    headings: Sequence[Dict[str, Any]],
    required_sections: Sequence[Tuple[str, re.Pattern[str]]],
    path: Path,
    root: Path,
    error_code: str,
    errors: List[Dict[str, Any]],
) -> Optional[List[int]]:
    titles = [section_title(item["title"]) for item in headings]
    positions: List[int] = []
    missing = False

    for label, pattern in required_sections:
        matches = [index for index, title in enumerate(titles) if pattern.search(title)]
        if not matches:
            errors.append(
                finding(
                    error_code,
                    f"missing required semantic section: {label}",
                    relative(path, root),
                )
            )
            missing = True
            continue
        positions.append(matches[-1] if label == "completion criteria" else matches[0])

    return None if missing else positions


def check_optional_section_numbering(
    headings: Sequence[Dict[str, Any]],
    path: Path,
    root: Path,
    errors: List[Dict[str, Any]],
) -> None:
    numbers = [section_number(item["title"]) for item in headings]
    numbered_count = sum(number is not None for number in numbers)
    if numbered_count == 0:
        return
    if numbered_count != len(numbers):
        first_unnumbered = next(
            item for item, number in zip(headings, numbers) if number is None
        )
        errors.append(
            finding(
                "mixed-agents-section-numbering",
                "AGENTS.md level-two sections must be either all numbered or all unnumbered",
                relative(path, root),
                first_unnumbered["line"],
            )
        )
        return

    expected = list(range(1, len(numbers) + 1))
    if numbers != expected:
        errors.append(
            finding(
                "nonsequential-agents-sections",
                "numbered AGENTS.md level-two sections must be sequential from 1",
                relative(path, root),
                headings[0]["line"] if headings else None,
            )
        )


def check_agents_style(
    path: Path, root: Path, text: str, errors: List[Dict[str, Any]]
) -> None:
    headings = markdown_headings(text)
    h1_headings = [item for item in headings if item["level"] == 1]
    h2_headings = [item for item in headings if item["level"] == 2]
    relative_path = relative(path, root)

    canonical_title = (
        len(h1_headings) == 1 and h1_headings[0]["title"] == "AGENTS.md"
    )
    if not canonical_title:
        errors.append(
            finding(
                "noncanonical-agents-title",
                "AGENTS.md must contain exactly one level-one title: # AGENTS.md",
                relative_path,
                h1_headings[0]["line"] if h1_headings else 1,
            )
        )
    elif not text.splitlines() or text.splitlines()[0] != "# AGENTS.md":
        errors.append(
            finding(
                "agents-title-not-first",
                "AGENTS.md must start on line 1 with exactly '# AGENTS.md'",
                relative_path,
                1,
            )
        )

    if h1_headings and not has_opening_scope_paragraph(
        text,
        h1_headings[0]["line"],
        h2_headings[0]["line"] if h2_headings else len(text.splitlines()) + 1,
    ):
        errors.append(
            finding(
                "missing-agents-intro",
                "AGENTS.md needs a short scope and inheritance paragraph after its title",
                relative_path,
                h1_headings[0]["line"],
            )
        )

    is_root = path.parent == root
    minimum_sections = 8 if is_root else 6
    if len(h2_headings) < minimum_sections:
        errors.append(
            finding(
                "too-few-agents-sections",
                f"{'root' if is_root else 'nested'} AGENTS.md needs at least "
                f"{minimum_sections} meaningful level-two sections; found "
                f"{len(h2_headings)}",
                relative_path,
            )
        )

    check_optional_section_numbering(h2_headings, path, root, errors)
    positions = semantic_section_positions(
        h2_headings,
        ROOT_AGENTS_SECTIONS if is_root else NESTED_AGENTS_SECTIONS,
        path,
        root,
        "missing-agents-section",
        errors,
    )
    if positions is not None and positions != sorted(positions):
        errors.append(
            finding(
                "agents-section-order",
                "AGENTS.md semantic sections are not in the canonical order",
                relative_path,
            )
        )

    if h2_headings and not COMPLETION_HEADING_RE.search(
        section_title(h2_headings[-1]["title"])
    ):
        errors.append(
            finding(
                "agents-final-section-not-completion",
                "the final AGENTS.md level-two section must define completion criteria",
                relative_path,
                h2_headings[-1]["line"],
            )
        )

    command_pattern = (
        ROOT_AGENTS_SECTIONS[-2][1] if is_root else NESTED_AGENTS_SECTIONS[-2][1]
    )
    command_positions = [
        index
        for index, item in enumerate(h2_headings)
        if command_pattern.search(section_title(item["title"]))
    ]
    if command_positions and command_positions[0] < max(0, len(h2_headings) - 3):
        errors.append(
            finding(
                "agents-commands-too-early",
                "tests and commands belong near the end of AGENTS.md",
                relative_path,
                h2_headings[command_positions[0]]["line"],
            )
        )

    check_manual_prose_wrapping(path, root, text, errors)
    check_fence_labels(path, root, text, errors)


def check_architecture_style(
    path: Path, root: Path, text: str, errors: List[Dict[str, Any]]
) -> None:
    headings = markdown_headings(text)
    h1_headings = [item for item in headings if item["level"] == 1]
    h2_headings = [item for item in headings if item["level"] == 2]
    relative_path = relative(path, root)

    canonical_title = (
        len(h1_headings) == 1
        and ARCHITECTURE_TITLE_RE.fullmatch(h1_headings[0]["title"]) is not None
    )
    if not canonical_title:
        errors.append(
            finding(
                "noncanonical-architecture-title",
                "ARCHITECTURE.md must contain exactly one title shaped "
                "'# ARCHITECTURE.md — <project architecture>'",
                relative_path,
                h1_headings[0]["line"] if h1_headings else 1,
            )
        )
    elif (
        not text.splitlines()
        or text.splitlines()[0] != f"# {h1_headings[0]['title']}"
    ):
        errors.append(
            finding(
                "architecture-title-not-first",
                "ARCHITECTURE.md must start on line 1 with its canonical title",
                relative_path,
                1,
            )
        )

    if len(h2_headings) < 5:
        errors.append(
            finding(
                "too-few-architecture-sections",
                "ARCHITECTURE.md needs at least five meaningful level-two sections",
                relative_path,
            )
        )

    numbers = [section_number(item["title"]) for item in h2_headings]
    if any(number is None for number in numbers):
        first_unnumbered = next(
            item for item, number in zip(h2_headings, numbers) if number is None
        )
        errors.append(
            finding(
                "unnumbered-architecture-sections",
                "every architecture level-two section must be numbered",
                relative_path,
                first_unnumbered["line"],
            )
        )
    elif numbers != list(range(1, len(numbers) + 1)):
        errors.append(
            finding(
                "nonsequential-architecture-sections",
                "architecture level-two sections must be sequential from 1",
                relative_path,
                h2_headings[0]["line"] if h2_headings else None,
            )
        )

    positions = semantic_section_positions(
        h2_headings,
        ARCHITECTURE_SECTIONS,
        path,
        root,
        "missing-architecture-section",
        errors,
    )
    if positions is not None and positions != sorted(positions):
        errors.append(
            finding(
                "architecture-section-order",
                "architecture semantic sections are not in the canonical order",
                relative_path,
            )
        )

    if h2_headings and not FINAL_VERIFICATION_HEADING_RE.fullmatch(
        section_title(h2_headings[-1]["title"])
    ):
        errors.append(
            finding(
                "architecture-final-section-not-verification",
                "the final architecture level-two section must be a dedicated verification section",
                relative_path,
                h2_headings[-1]["line"],
            )
        )

    for item in h2_headings:
        if FUTURE_ARCHITECTURE_HEADING_RE.search(section_title(item["title"])):
            errors.append(
                finding(
                    "architecture-mixes-future-design",
                    "current-state architecture must move diagnosis, recommendations, "
                    "and future evolution to an ExecPlan or design document",
                    relative_path,
                    item["line"],
                )
            )

    check_manual_prose_wrapping(path, root, text, errors)
    check_fence_labels(path, root, text, errors)


def extract_link_target(raw_target: str) -> str:
    stripped = raw_target.strip()
    if stripped.startswith("<"):
        closing = stripped.find(">")
        if closing != -1:
            return stripped[1:closing]
    return stripped.split(maxsplit=1)[0].strip("'\"")


def check_links(
    path: Path,
    root: Path,
    text: str,
    errors: List[Dict[str, Any]],
    warnings: List[Dict[str, Any]],
) -> None:
    for line_number, line in enumerate(text.splitlines(), start=1):
        for match in LINK_RE.finditer(line):
            target = extract_link_target(match.group(1))
            if not target or target.startswith("#"):
                continue
            if any(
                token in target
                for token in ("{{", "}}", "${", "*", "YYYY-MM-DD")
            ):
                continue

            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc:
                continue
            link_path = unquote(parsed.path)
            if not link_path:
                continue
            if link_path.startswith("/"):
                warnings.append(
                    finding(
                        "absolute-local-link",
                        f"absolute local link is not portable: {target}",
                        relative(path, root),
                        line_number,
                    )
                )
                continue

            resolved = (path.parent / link_path).resolve()
            if not resolved.exists():
                errors.append(
                    finding(
                        "broken-local-link",
                        f"local link target does not exist: {target}",
                        relative(path, root),
                        line_number,
                    )
                )


def parse_frontmatter(text: str) -> Tuple[Optional[Dict[str, str]], Optional[str]]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, "missing opening YAML frontmatter delimiter"

    closing_index: Optional[int] = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            closing_index = index
            break
    if closing_index is None:
        return None, "missing closing YAML frontmatter delimiter"

    fields: Dict[str, str] = {}
    for line in lines[1:closing_index]:
        if not line or line[0].isspace() or line.lstrip().startswith("#"):
            continue
        match = FRONTMATTER_KEY_RE.match(line)
        if match:
            fields[match.group(1)] = (match.group(2) or "").strip().strip("'\"")
    return fields, None


def check_skill(
    path: Path,
    root: Path,
    text: str,
    errors: List[Dict[str, Any]],
    warnings: List[Dict[str, Any]],
) -> None:
    fields, parse_error = parse_frontmatter(text)
    relative_path = relative(path, root)
    if parse_error:
        errors.append(finding("invalid-skill-frontmatter", parse_error, relative_path, 1))
        return

    assert fields is not None
    for required in ("name", "description"):
        if not fields.get(required):
            errors.append(
                finding(
                    "missing-skill-field",
                    f"skill frontmatter requires a non-empty {required}",
                    relative_path,
                    1,
                )
            )

    name = fields.get("name", "")
    if name and not SKILL_NAME_RE.fullmatch(name):
        errors.append(
            finding(
                "invalid-skill-name",
                "skill name must use lowercase letters, digits, and single hyphens",
                relative_path,
                1,
            )
        )
    if name and name != path.parent.name:
        errors.append(
            finding(
                "skill-directory-mismatch",
                f"skill name {name!r} does not match directory {path.parent.name!r}",
                relative_path,
                1,
            )
        )

    extra_fields = sorted(set(fields) - {"name", "description"})
    if extra_fields:
        warnings.append(
            finding(
                "extra-skill-frontmatter",
                "review nonstandard top-level skill fields: " + ", ".join(extra_fields),
                relative_path,
                1,
            )
        )


def check_claude_imports(
    path: Path, root: Path, text: str, errors: List[Dict[str, Any]]
) -> None:
    for line_number, line in enumerate(text.splitlines(), start=1):
        match = CLAUDE_IMPORT_RE.match(line)
        if not match:
            continue
        target = match.group(1).strip("<>")
        if urlsplit(target).scheme:
            continue
        target_path = target.split("#", 1)[0]
        if target_path and not (path.parent / target_path).resolve().exists():
            errors.append(
                finding(
                    "broken-claude-import",
                    f"Claude import target does not exist: {target}",
                    relative(path, root),
                    line_number,
                )
            )


def claude_imports_target(path: Path, text: str, expected: Path) -> bool:
    expected_resolved = expected.resolve()
    for line in text.splitlines():
        match = CLAUDE_IMPORT_RE.match(line)
        if not match:
            continue
        target = match.group(1).strip("<>")
        if urlsplit(target).scheme:
            continue
        target_path = target.split("#", 1)[0]
        if target_path and (path.parent / target_path).resolve() == expected_resolved:
            return True
    return False


def check_harness_baseline(
    root: Path,
    inventory: Dict[str, Any],
    markdown_texts: Dict[Path, str],
    errors: List[Dict[str, Any]],
) -> None:
    agent_paths = [root / item["path"] for item in inventory["agent_files"]]
    agent_directories = {root}
    agent_directories.update(path.parent for path in agent_paths)
    project_directories = {
        root if path == "." else root / path
        for path in inventory["project_boundaries"]
    }
    required_directories = agent_directories | project_directories
    for directory in sorted(required_directories, key=lambda item: item.as_posix()):
        override = directory / "AGENTS.override.md"
        standard = directory / "AGENTS.md"
        effective = override if override.is_file() else standard
        claude = directory / "CLAUDE.md"
        claude_relative = relative(claude, root)

        if (
            directory != root
            and directory in project_directories
            and not effective.is_file()
        ):
            errors.append(
                finding(
                    "missing-project-agents",
                    "project boundary does not contain AGENTS.md or AGENTS.override.md",
                    relative(standard, root),
                )
            )

        if directory in project_directories:
            architecture = directory / "ARCHITECTURE.md"
            architecture_relative = relative(architecture, root)
        else:
            architecture = None
            architecture_relative = None

        if architecture is not None and not architecture.is_file():
            errors.append(
                finding(
                    "missing-project-architecture",
                    f"missing architecture file for project boundary "
                    f"{relative(directory, root)}",
                    architecture_relative,
                )
            )

        if not claude.is_file():
            errors.append(
                finding(
                    (
                        "missing-root-claude"
                        if directory == root
                        else "missing-boundary-claude"
                    ),
                    f"missing Claude compatibility file for {relative(effective, root)}",
                    claude_relative,
                )
            )
            continue

        text = markdown_texts.get(claude)
        if text is not None and not claude_imports_target(claude, text, effective):
            errors.append(
                finding(
                    "missing-agents-import",
                    f"Claude compatibility file must import {effective.name}",
                    claude_relative,
                )
            )


def instruction_chain(
    root: Path, target_directory: Path
) -> List[Path]:
    chain: List[Path] = []
    relative_parts = target_directory.relative_to(root).parts
    directories = [root]
    current = root
    for part in relative_parts:
        current = current / part
        directories.append(current)

    for directory in directories:
        override = directory / "AGENTS.override.md"
        standard = directory / "AGENTS.md"
        if override.is_file():
            chain.append(override)
        elif standard.is_file():
            chain.append(standard)
    return chain


def check_instruction_chains(
    root: Path,
    inventory: Dict[str, Any],
    max_bytes: int,
    errors: List[Dict[str, Any]],
    warnings: List[Dict[str, Any]],
) -> Dict[str, Any]:
    agent_paths = [root / item["path"] for item in inventory["agent_files"]]
    directories = sorted({path.parent for path in agent_paths}, key=lambda item: item.as_posix())
    checked_chains = set()
    maximum = {"bytes": 0, "files": []}

    for directory in directories:
        standard = directory / "AGENTS.md"
        override = directory / "AGENTS.override.md"
        if standard.is_file() and override.is_file():
            warnings.append(
                finding(
                    "shadowed-agents-file",
                    "AGENTS.override.md shadows AGENTS.md in this directory",
                    relative(override, root),
                )
            )

        chain = instruction_chain(root, directory)
        signature = tuple(str(path) for path in chain)
        if signature in checked_chains:
            continue
        checked_chains.add(signature)
        total_bytes = sum(path.stat().st_size for path in chain)
        chain_files = [relative(path, root) for path in chain]
        if total_bytes > maximum["bytes"]:
            maximum = {"bytes": total_bytes, "files": chain_files}
        if total_bytes > max_bytes:
            errors.append(
                finding(
                    "agent-chain-too-large",
                    f"instruction chain uses {total_bytes} bytes; limit is {max_bytes}: "
                    + " -> ".join(chain_files),
                    chain_files[-1] if chain_files else None,
                )
            )
    return maximum


def validate(
    root: Path, inventory: Dict[str, Any], max_agent_bytes: int
) -> Dict[str, Any]:
    errors: List[Dict[str, Any]] = []
    warnings: List[Dict[str, Any]] = []

    if not (root / "AGENTS.md").is_file():
        errors.append(
            finding(
                "missing-root-agents",
                "repository root does not contain the canonical AGENTS.md",
                "AGENTS.md",
            )
        )

    markdown_texts: Dict[Path, str] = {}
    plans_template = inventory["plans_template"]
    if plans_template["status"] == "missing":
        errors.append(
            finding(
                "missing-canonical-plans",
                "repository root does not contain the canonical PLANS.md; "
                f"expected SHA-256 {plans_template['canonical_sha256']}",
                "PLANS.md",
            )
        )
    elif plans_template["status"] == "differs":
        errors.append(
            finding(
                "noncanonical-plans",
                "root PLANS.md differs from the canonical template; "
                f"target SHA-256 {plans_template['target_sha256']}, "
                f"canonical SHA-256 {plans_template['canonical_sha256']}",
                "PLANS.md",
            )
        )

    if inventory["git_status"]:
        warnings.append(
            finding(
                "dirty-worktree",
                f"Git worktree has {len(inventory['git_status'])} changed path(s); preserve user changes",
            )
        )

    for item in inventory["harness_files"]:
        path = root / item["path"]
        text = read_markdown(path, root, errors)
        if text is None:
            continue
        markdown_texts[path] = text
        if text and not text.endswith("\n"):
            errors.append(
                finding(
                    "missing-final-newline",
                    "harness text file must end with a newline",
                    item["path"],
                )
            )
        check_fences(path, root, text, errors)
        check_links(path, root, text, errors, warnings)
        if path.name == "AGENTS.md":
            check_agents_style(path, root, text, errors)
        elif path.name == "ARCHITECTURE.md":
            check_architecture_style(path, root, text, errors)
        if is_project_skill(path, root):
            check_skill(path, root, text, errors, warnings)
        if path.name == "CLAUDE.md":
            check_claude_imports(path, root, text, errors)

    check_harness_baseline(root, inventory, markdown_texts, errors)

    for item in inventory["claude_skill_links"]:
        if item["broken"]:
            errors.append(
                finding(
                    "broken-claude-skill-link",
                    f"Claude skill symlink target does not exist: {item['target']}",
                    item["path"],
                )
            )

    exec_plans_root = root / "docs" / "exec-plans"
    if exec_plans_root.is_dir() and not (exec_plans_root / "README.md").is_file():
        errors.append(
            finding(
                "missing-exec-plan-index",
                "docs/exec-plans exists without README.md",
                "docs/exec-plans/README.md",
            )
        )

    maximum_chain = check_instruction_chains(
        root, inventory, max_agent_bytes, errors, warnings
    )

    return {
        "root": str(root),
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "summary": {
            "harness_files": len(inventory["harness_files"]),
            "agent_files": len(inventory["agent_files"]),
            "architecture_files": len(inventory["architecture_files"]),
            "claude_files": len(inventory["claude_files"]),
            "project_boundaries": len(inventory["project_boundaries"]),
            "project_skills": len(inventory["project_skills"]),
            "exec_plans": len(inventory["exec_plans"]),
            "plans_template_status": plans_template["status"],
            "plans_template_sha256": plans_template["canonical_sha256"],
            "maximum_agent_chain_bytes": maximum_chain["bytes"],
            "maximum_agent_chain_files": maximum_chain["files"],
            "max_agent_bytes": max_agent_bytes,
        },
    }


def print_list(title: str, values: Sequence[str]) -> None:
    print(f"{title} ({len(values)}):")
    if values:
        for value in values:
            print(f"  - {value}")
    else:
        print("  - none")


def print_inventory(inventory: Dict[str, Any]) -> None:
    print(f"Repository: {inventory['root']}")
    if inventory["git_root"]:
        print(f"Git: {inventory['git_head'] or 'unborn HEAD'}")
        print(
            "Worktree: "
            + (
                f"{len(inventory['git_status'])} changed path(s)"
                if inventory["git_status"]
                else "clean"
            )
        )
    else:
        print("Git: not detected")

    print_list("Manifests", inventory["manifests"])
    print_list(
        "Harness files", [item["path"] for item in inventory["harness_files"]]
    )
    print_list("Agent instructions", [item["path"] for item in inventory["agent_files"]])
    print_list("Project boundaries", inventory["project_boundaries"])
    if inventory["explicit_project_boundaries"]:
        print_list(
            "Explicit project boundaries",
            inventory["explicit_project_boundaries"],
        )
    print_list("Architecture documents", inventory["architecture_files"])
    print_list("Claude compatibility files", inventory["claude_files"])
    print_list("Repository skills", inventory["project_skills"])
    print_list("Execution-plan files", inventory["exec_plans"])
    plans_template = inventory["plans_template"]
    print(
        "Canonical PLANS.md: "
        f"{plans_template['status']} "
        f"(canonical SHA-256 {plans_template['canonical_sha256']}, "
        f"target SHA-256 {plans_template['target_sha256'] or 'missing'})"
    )


def format_finding(item: Dict[str, Any]) -> str:
    location = item.get("path", "")
    if item.get("line") is not None:
        location += f":{item['line']}"
    prefix = f"{location}: " if location else ""
    return f"{prefix}{item['message']} [{item['code']}]"


def print_validation(result: Dict[str, Any]) -> None:
    print(f"Validation: {'PASS' if result['ok'] else 'FAIL'}")
    print(f"Repository: {result['root']}")
    summary = result["summary"]
    print(
        "Summary: "
        f"{summary['harness_files']} harness file(s), "
        f"{summary['agent_files']} AGENTS file(s), "
        f"{summary['architecture_files']} architecture file(s), "
        f"{summary['claude_files']} Claude file(s), "
        f"{summary['project_boundaries']} project boundary/boundaries, "
        f"PLANS.md {summary['plans_template_status']}, "
        f"maximum instruction chain {summary['maximum_agent_chain_bytes']}/"
        f"{summary['max_agent_bytes']} bytes"
    )

    if result["errors"]:
        print("Errors:")
        for item in result["errors"]:
            print(f"  - {format_finding(item)}")
    if result["warnings"]:
        print("Warnings:")
        for item in result["warnings"]:
            print(f"  - {format_finding(item)}")


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    try:
        root, git_root = resolve_repository(args.root)
        inventory = build_inventory(root, git_root)
        explicit_boundaries = normalize_project_boundaries(
            root, args.project_boundary
        )
        inventory["inferred_project_boundaries"] = inventory[
            "project_boundaries"
        ]
        inventory["explicit_project_boundaries"] = explicit_boundaries
        inventory["project_boundaries"] = sorted(
            set(inventory["project_boundaries"]) | set(explicit_boundaries)
        )
        if args.command == "inventory":
            if args.json:
                print(json.dumps(inventory, ensure_ascii=False, indent=2))
            else:
                print_inventory(inventory)
            return 0

        result = validate(root, inventory, args.max_agent_bytes)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print_validation(result)
        return 0 if result["ok"] else 1
    except (OSError, RuntimeError, ValueError) as exc:
        if getattr(args, "json", False):
            print(
                json.dumps(
                    {"ok": False, "runtime_error": str(exc)},
                    ensure_ascii=False,
                    indent=2,
                )
            )
        else:
            print(f"harness audit failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
