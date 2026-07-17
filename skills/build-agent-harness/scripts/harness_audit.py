#!/usr/bin/env python3
"""Read-only inventory and structural validation for repository agent harnesses."""

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
LINK_RE = re.compile(r"!?\[[^\]\n]*\]\(([^)\n]+)\)")
FRONTMATTER_KEY_RE = re.compile(r"^([A-Za-z][A-Za-z0-9_-]*):(?:\s*(.*))?$")
CLAUDE_IMPORT_RE = re.compile(r"^\s*@([^\s]+)\s*$")


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inventory or validate a repository agent harness without modifying it."
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
    claude_files = [path for path in files if path.name == "CLAUDE.md"]
    project_skills = [path for path in files if is_project_skill(path, root)]
    exec_plans = [path for path in files if is_exec_plan(path, root)]
    harness_files = [path for path in files if is_harness_file(path, root)]

    subprojects: Dict[str, List[str]] = {}
    for manifest in manifests:
        parent = relative(manifest.parent, root)
        subprojects.setdefault(parent, []).append(manifest.name)

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
        "harness_files": [file_record(path, root) for path in harness_files],
        "agent_files": [file_record(path, root) for path in agent_files],
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
        if is_project_skill(path, root):
            check_skill(path, root, text, errors, warnings)
        if path.name == "CLAUDE.md":
            check_claude_imports(path, root, text, errors)

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
