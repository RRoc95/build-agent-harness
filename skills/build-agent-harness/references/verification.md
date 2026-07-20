# Harness verification

Verify documentation structure, document style, and the claims the harness makes. Mechanical checks catch broken wiring and format drift; repository commands establish behavioral truth.

## Contents

- [Verification levels](#verification-levels)
- [Run the audit helper](#run-the-audit-helper)
- [Verify documented claims](#verify-documented-claims)
- [Review compatibility and scope](#review-compatibility-and-scope)
- [Handle findings](#handle-findings)
- [Report evidence](#report-evidence)

## Verification levels

Use four levels:

1. **Inventory** — confirm the tool sees the Git root, subproject manifests, instruction files, architecture files, plans, skills, compatibility files, and canonical `PLANS.md` status.
2. **Structure and style** — check the required root files, project architecture boundaries, canonical AGENTS and architecture titles, semantic section anchors, heading numbering, final sections, the `PLANS.md` asset hash, local links, Markdown fences, skill frontmatter, Claude imports, symlinks, plan indexes, and instruction-chain size.
3. **Claims** — verify commands, paths, runtime descriptions, and policies against repository evidence and safe execution.
4. **Scope** — inspect the final diff and status for accidental application, configuration, generated, or historical changes.

Passing the structure-and-style helper is necessary but not sufficient.

## Run the audit helper

Human-readable inventory:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/build-agent-harness/scripts/harness_audit.py" \
  --root /path/to/repository inventory
```

Structured inventory:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/build-agent-harness/scripts/harness_audit.py" \
  --root /path/to/repository inventory --json
```

Structural validation:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/build-agent-harness/scripts/harness_audit.py" \
  --root /path/to/repository validate \
  --project-boundary path/to/frontend \
  --project-boundary path/to/backend
```

Repeat `--project-boundary` for every independent project identified during reconnaissance; use `.` for a single project at the root and exclude a pure aggregation root. This explicit list makes missing `AGENTS.md`, `CLAUDE.md`, and `ARCHITECTURE.md` detectable even when a project initially has no harness files. Use `--json` for machine-readable results. Override `--max-agent-bytes` when the repository has an explicit Codex instruction budget different from the helper's default.

Exit codes:

- `0`: inventory completed or validation found no errors;
- `1`: structure or document-style validation errors were found;
- `2`: invalid input or a runtime failure prevented the audit.

Warnings do not change the exit code. Read them: they usually identify portability or maintainability risks that require human judgment.

The helper is read-only. It deliberately does not generate files, replace a noncanonical `PLANS.md`, repair links, reformat documents, or execute project commands. Validation treats missing root `AGENTS.md`, root `CLAUDE.md`, or canonical `PLANS.md` as errors; every directory with effective agent instructions must also contain sibling Claude compatibility. It validates standard `AGENTS.md` and `ARCHITECTURE.md` files against [document-style.md](document-style.md), conservatively infers project boundaries from manifests colocated with agent instructions, and requires architecture there, while repository reconnaissance remains authoritative for ambiguous layouts. Inventory reports `missing`, `matches`, or `differs` plus the canonical and target SHA-256 values when available.

## Verify documented claims

For each newly added or changed claim, use the strongest available evidence.

| Claim | Minimum evidence | Strong verification |
| --- | --- | --- |
| Setup/install command | Manifest or task definition | Safe execution in a clean or existing environment |
| Test/lint/typecheck/build command | Script, config, or CI job | Run the narrow command and record result |
| Runtime entrypoint | Executable configuration and source | Trace a representative path |
| Architecture boundary | Imports, interfaces, schemas, ownership | Inspect callers and tests across the boundary |
| Coding rule | Tool configuration or consistent code | Run the enforcing tool or cite convention status |
| Review requirement | Project policy or CI enforcement | Confirm branch/review automation when accessible |
| Deployment statement | Deployment config or workflow | Validate config or dry-run when safe and authorized |

Do not run destructive commands, production operations, migrations against shared data, or broad external actions solely to validate documentation.

For docs-only changes, run application suites only when needed to confirm a documented command or behavioral statement. Markdown, links, command sources, and diff scope are normally the primary checks.

## Review compatibility and scope

Check the final state manually:

- Root `AGENTS.md` contains repository-wide instructions and links, not copied detail.
- Root and nested `AGENTS.md` use the canonical title, expose the required semantic anchors in the expected order, keep commands near the end, and finish with completion criteria.
- Root `CLAUDE.md` imports root `AGENTS.md`.
- Nested `AGENTS.md` files contain only local differences and inherit root rules cleanly.
- Every root or nested `AGENTS.md` boundary has sibling `CLAUDE.md` importing the effective local instruction file.
- Every independently buildable or runnable project boundary has `ARCHITECTURE.md`; a pure aggregation root may intentionally omit it.
- Architecture files use the `ARCHITECTURE.md — …` title shape, continuously numbered level-two sections, and a final verification section.
- Architecture statements describe current code; future changes, diagnoses, and evolution recommendations are planned separately.
- Root `PLANS.md` is byte-for-byte identical to the skill's canonical asset; project-specific rules live in `AGENTS.md` or the execution-plan index.
- Exec-plan indexes point to real files and completed history was preserved.
- Coding, review, and verification guides use repository-specific evidence.
- Local skills have valid names, meaningful descriptions, and tested scripts.
- `CLAUDE.md` imports resolve and shared guidance has one canonical owner.
- No Cursor-specific files were added or managed.
- No application source, dependency, runtime configuration, deployment, hook, MCP, generated, or unrelated file changed.

Inspect:

```bash
git status --short
git diff --check
git diff --stat
git diff -- path/to/in-scope/files
```

Adapt the commands for untracked files and non-Git targets. Read the actual files, because `git diff` alone does not show untracked content.

## Handle findings

Classify each finding before changing anything:

- **Error:** broken structure or a claim known to be wrong. Fix before delivery when in scope.
- **Warning:** plausible risk requiring judgment, such as an absolute local link or a dirty worktree. Resolve or report.
- **Unverified:** a claim lacks enough evidence. Remove it, qualify it, or ask one focused question if material.
- **Out of scope:** an existing repository problem unrelated to the harness change. Do not repair it silently; report only if relevant.

When the reference repository and target disagree, keep the target behavior and document why the pattern was not transferred if that decision matters.

A missing or differing root `PLANS.md` is a structural error, not a style preference. Preserve any valid project-specific policy in its proper owner, then replace the whole file from the canonical asset and rerun validation.

## Report evidence

The final report should state:

1. Which files were created or updated.
2. Which repository facts shaped the harness.
3. Exact validation commands and whether each passed, failed, or was skipped.
4. Structural errors and warnings that remain.
5. The canonical `PLANS.md` match status and SHA-256 when planning files changed.
6. Any claim that was sampled rather than exhaustively verified.
7. Confirmation that protected and unrelated files were untouched.

Do not say “all checks passed” when only the structure-and-style helper ran. Name the layer that passed.
