---
name: build-agent-harness
description: Create, optimize, or audit a complete Codex-first, Claude-compatible repository agent harness from verified project facts. Ensures root AGENTS.md, CLAUDE.md, and the canonical project-independent PLANS.md, plus consistently formatted ARCHITECTURE.md at every independently buildable or runnable project boundary; normalizes existing AGENTS.md and architecture documents to the stable harness style, adds scoped quality or planning guidance when appropriate, and can use a reference repository as a pattern without copying its facts.
---

# Build Agent Harness

Build a small, layered repository harness that helps coding agents inspect, change, and verify the project reliably. Treat the target repository as the source of truth and use reference repositories only as pattern libraries.

## Operating contract

- Default to automatic execution: inspect, decide, edit, validate, and report.
- Ask one focused question only when an unresolved choice materially changes scope, architecture, compatibility, or verification.
- Keep the task documentation-only unless the user explicitly requests broader changes. Do not change application code, dependencies, runtime configuration, deployment, hooks, MCP configuration, or generated artifacts.
- Preserve user changes, completed plan history, and existing repository conventions. Never overwrite facts with assumptions.
- Treat root `AGENTS.md`, root `CLAUDE.md`, and root `PLANS.md` as the required repository baseline for every create or optimize request. Require `ARCHITECTURE.md` at every independently buildable or runnable project boundary, including the root only when the root itself is such a project. An audit-only request reports missing files without creating them.
- Treat [document-style.md](references/document-style.md) as the mandatory format contract for every created or optimized `AGENTS.md` and `ARCHITECTURE.md`. Preserve verified facts while normalizing titles, semantic section order, numbering, source layout, and final sections.
- Install [PLANS.md](assets/PLANS.md) at every repository root byte-for-byte. Never customize, translate, shorten, date, or add project facts to this canonical file.
- Use Codex as the primary agent. Always provide thin Claude compatibility through imports from the applicable `AGENTS.md`; do not duplicate shared instructions or add Cursor-specific files.
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

Before editing, classify the root and each candidate boundary in working notes as `aggregation`, `independent project`, or `instruction-only scope`. Record the repository-relative paths of every independent project; use those exact paths during final validation. Do not persist the classification unless it adds durable value.

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

Treat a missing root `CLAUDE.md` as a harness defect. Every directory with effective `AGENTS.md` or `AGENTS.override.md` must have a sibling `CLAUDE.md`. Separately, every independently buildable or runnable project must have an `ARCHITECTURE.md` at that project boundary. A repository aggregation root does not need architecture merely because it owns repository-wide instructions. Preserve verified existing content, but do not let optional-document heuristics omit required files.

Separate current behavior from aspirations. A future design belongs in an explicit plan, not in architecture text presented as current fact.

### 4. Install the baseline and choose scoped extensions

Read [harness-blueprint.md](references/harness-blueprint.md) and [document-style.md](references/document-style.md). Install the required baseline first, then select additional documents by repository need instead of generating every possible guide.

Use these defaults:

- Root `AGENTS.md` for durable repository-wide navigation, commands, constraints, and completion criteria.
- Root `CLAUDE.md` containing `@AGENTS.md`. Keep Codex instructions canonical.
- Root `PLANS.md` in every repository, copied unchanged from [assets/PLANS.md](assets/PLANS.md). Add `docs/exec-plans/` when the repository tracks active or completed ExecPlans.
- Root `ARCHITECTURE.md` only when the repository root is itself one independently buildable or runnable project. Omit it at a pure aggregation root.
- At every directory selected for nested agent guidance, create or maintain sibling `AGENTS.md` and `CLAUDE.md`; the Claude file imports the effective sibling agent instruction file.
- At every independently meaningful subproject, require `AGENTS.md`, `CLAUDE.md`, and `ARCHITECTURE.md` together.
- Coding standards, code review, and verification guides when those concerns require more detail than root instructions can carry.
- Repository-local skills only for repeated, deterministic workflows that benefit from progressive disclosure or executable helpers.

Keep root instructions concise. Put global facts at the root, local facts near the affected code, and detailed explanations in linked documents. Avoid model-version prompt tricks and generic advice that cannot be checked in the repository.

Do not finish a create or optimize request while any required repository or project file is missing. If architecture evidence is incomplete, write only the verified portion, mark the uncertainty, and report the sampling limit instead of skipping a required project document.

For an existing harness, normalize `AGENTS.md` and `ARCHITECTURE.md` even when their facts are correct but their document grammar has drifted. The common grammar is part of the deliverable: canonical titles, recognizable semantic anchors, consistent heading numbering, commands and completion near the end of agent instructions, and verification as the final architecture section. Do not preserve a divergent outline merely because it predates this skill.

### 5. Make surgical edits

Use the repository's naming, language, tone, and index conventions. Prefer updating canonical documents over creating competing sources of truth.

- Copy the canonical `PLANS.md` asset; do not generate or hand-edit its contents. After copying, require a byte-for-byte comparison with the asset.
- Build each `ARCHITECTURE.md` from current repository evidence and the mandatory format contract. Cover the boundary, responsibilities, representative runtime flow, contracts, dependency direction, verification surface, and change-risk hotspots that can be verified. Keep proposed designs out of current-state architecture and move them to an ExecPlan or explicit design document.
- Normalize each root and nested `AGENTS.md` to the contract's scope-first outline. Keep repository commands near the end and completion criteria last; retain domain-specific middle sections where they add verified local guidance.
- Create a new root or nested `CLAUDE.md` as exactly `@AGENTS.md` plus a final newline. When an existing Claude file contains verified Claude-only rules, preserve them and add the applicable `AGENTS.md` import instead of copying shared guidance.
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
  --root /path/to/repository validate \
  --project-boundary path/to/frontend \
  --project-boundary path/to/backend
```

Pass one `--project-boundary` for every independently buildable or runnable project identified during reconnaissance. Use `--project-boundary .` for a single project rooted at the repository root. Omit the aggregation root when its projects live below it. Use `--json` in automation. The audit checks structure and document style and is read-only; it does not prove that documented commands are correct.

Also:

1. Run the narrowest authoritative commands needed to verify newly documented claims.
2. Confirm root `AGENTS.md`, `CLAUDE.md`, and canonical `PLANS.md` exist; confirm every directory with effective agent instructions has a sibling Claude import and every independently buildable or runnable project has `ARCHITECTURE.md`.
3. Check canonical titles, semantic section order, heading-number consistency, architecture current-state boundaries, final sections, Markdown links, instruction precedence, final newlines, local skill metadata, and Claude imports.
4. Review the complete diff and status to confirm only requested harness files changed.
5. State every skipped or unavailable check explicitly.

Do not run broad application tests merely because documentation changed. Run them when needed to verify a command or behavioral claim introduced by the documentation.

### 7. Report the result

Lead with the outcome. Explicitly confirm Claude compatibility at each instruction boundary, architecture at each independent project boundary, and format normalization against the document-style contract. If an aggregation root intentionally has no `ARCHITECTURE.md`, say so. Then list created or updated files, important design decisions, exact validation commands and results, skipped checks, remaining uncertainty, and confirmation that protected application/configuration files were untouched.

## Current OpenAI guidance

Use the `openai-docs` skill when exact, current Codex behavior or OpenAI recommendations materially affect the design. Prefer durable principles in the harness and avoid hard-coding volatile model-specific claims.
