---
name: build-agent-harness
description: Create or optimize repository agent harness documentation from verified project facts, including installing the canonical project-independent PLANS.md unchanged. Use when asked to generate, migrate, audit, or improve AGENTS.md, Claude compatibility, ARCHITECTURE.md, PLANS.md, coding, review, or verification guides, exec-plan structures, or repository-local agent skills, including work patterned after a reference repository.
---

# Build Agent Harness

Build a small, layered repository harness that helps coding agents inspect, change, and verify the project reliably. Treat the target repository as the source of truth and use reference repositories only as pattern libraries.

## Operating contract

- Default to automatic execution: inspect, decide, edit, validate, and report.
- Ask one focused question only when an unresolved choice materially changes scope, architecture, compatibility, or verification.
- Keep the task documentation-only unless the user explicitly requests broader changes. Do not change application code, dependencies, runtime configuration, deployment, hooks, MCP configuration, or generated artifacts.
- Preserve user changes, completed plan history, and existing repository conventions. Never overwrite facts with assumptions.
- Install [PLANS.md](assets/PLANS.md) at every repository root byte-for-byte. Never customize, translate, shorten, date, or add project facts to this canonical file.
- Use Codex as the primary agent. Add or retain thin Claude compatibility only when requested or already present. Do not add or manage Cursor-specific files.
- Do not persist chat transcripts, internal reasoning, or design-process specifications unless the user explicitly requests a durable design artifact.

## Workflow

### 1. Establish scope and repository state

Resolve the target Git root, applicable instruction chain, worktree status, and whether the request is to create a harness or optimize an existing one.

Read [repository-recon.md](references/repository-recon.md), then run:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/build-agent-harness/scripts/harness_audit.py" \
  --root /path/to/repository inventory
```

Use `inventory --json` when structured output helps. Treat a dirty worktree as user-owned state: preserve it and work around it unless an in-scope file conflicts with the requested edit.

### 2. Build an evidence-backed project model

Inspect manifests, scripts, CI workflows, tests, entry points, deployment files, documentation, and recent commits. Identify subprojects only when they have a meaningful build, test, runtime, or deployment boundary.

For every command, path, architecture statement, and invariant that will enter the harness, record its repository evidence. If a fact cannot be verified, research further, omit it, or surface the uncertainty; do not invent a plausible value.

When a reference repository is supplied, compare structure and responsibility rather than copying wording or project facts. Target-repository evidence always wins.

### 3. Audit the existing harness

Read every applicable root and nested instruction file plus existing architecture, planning, quality, verification, and local-skill documentation. Classify findings as:

- missing;
- duplicated;
- stale or conflicting;
- unverifiable;
- misplaced between root and nested scope;
- oversized for always-loaded context.

Treat a missing or noncanonical root `PLANS.md` as a harness defect. Before replacing a differing file, preserve any verified project-specific rules in their proper canonical owner: use `AGENTS.md` for triggers and constraints, or `docs/exec-plans/README.md` for the local plan index and lifecycle. Do not rewrite existing active or completed ExecPlans merely because the template changed.

Separate current behavior from aspirations. A future design belongs in an explicit plan, not in architecture text presented as current fact.

### 4. Choose the minimum useful document set

Read [harness-blueprint.md](references/harness-blueprint.md). Select documents by repository need instead of generating every possible file.

Use these defaults:

- Root `AGENTS.md` for durable repository-wide navigation, commands, constraints, and completion criteria.
- Nested `AGENTS.md` only for independently meaningful subprojects or areas whose local rules differ.
- `ARCHITECTURE.md` near a subproject when its runtime path, boundaries, contracts, or risks need explanation.
- Root `PLANS.md` in every repository, copied unchanged from [assets/PLANS.md](assets/PLANS.md). Add `docs/exec-plans/` when the repository tracks active or completed ExecPlans.
- Coding standards, code review, and verification guides when those concerns require more detail than root instructions can carry.
- Repository-local skills only for repeated, deterministic workflows that benefit from progressive disclosure or executable helpers.
- Thin `CLAUDE.md` imports when Claude compatibility is in scope; keep shared instructions canonical in `AGENTS.md`.

Keep root instructions concise. Put global facts at the root, local facts near the affected code, and detailed explanations in linked documents. Avoid model-version prompt tricks and generic advice that cannot be checked in the repository.

### 5. Make surgical edits

Use the repository's naming, language, tone, and index conventions. Prefer updating canonical documents over creating competing sources of truth.

- Copy the canonical `PLANS.md` asset; do not generate or hand-edit its contents. After copying, require a byte-for-byte comparison with the asset.
- Preserve valid content and completed execution plans.
- Keep commands copy-pasteable and state their working directory and prerequisites when needed.
- Link to detail instead of duplicating it across files.
- Mark generated or inferred examples clearly; never present them as verified commands.
- Update exec-plan indexes when adding or moving plans.
- Add a local skill only when its trigger, workflow, and validation can be stated precisely.

Use the installed asset directly:

```bash
cp "${CODEX_HOME:-$HOME/.codex}/skills/build-agent-harness/assets/PLANS.md" \
  /path/to/repository/PLANS.md
cmp -s "${CODEX_HOME:-$HOME/.codex}/skills/build-agent-harness/assets/PLANS.md" \
  /path/to/repository/PLANS.md
```

### 6. Validate by risk

Read [verification.md](references/verification.md), then run:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/build-agent-harness/scripts/harness_audit.py" \
  --root /path/to/repository validate
```

Use `validate --json` in automation. The audit is structural and read-only; it does not prove that documented commands are correct.

Also:

1. Run the narrowest authoritative commands needed to verify newly documented claims.
2. Check Markdown links, instruction precedence, final newlines, local skill metadata, and Claude imports.
3. Review the complete diff and status to confirm only requested harness files changed.
4. State every skipped or unavailable check explicitly.

Do not run broad application tests merely because documentation changed. Run them when needed to verify a command or behavioral claim introduced by the documentation.

### 7. Report the result

Lead with the outcome. List created or updated files, important design decisions, exact validation commands and results, skipped checks, remaining uncertainty, and confirmation that protected application/configuration files were untouched.

## Current OpenAI guidance

Use the `openai-docs` skill when exact, current Codex behavior or OpenAI recommendations materially affect the design. Prefer durable principles in the harness and avoid hard-coding volatile model-specific claims.
