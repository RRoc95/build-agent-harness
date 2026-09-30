# Harness blueprint

Design the harness as a layered operating system for repository work: short instructions are always available, project architecture is explicit, Claude imports the Codex-first rules, plans preserve long-running state, and executable helpers validate what can be checked mechanically.

This blueprint applies to full-harness creation or optimization. For a focused request, use only the relevant parts and preserve its scope. Required filenames, canonical PLANS.md, Claude imports, and document grammar below are this skill's established conventions; Codex does not require this complete document set. See [OpenAI sources](openai-sources.md) for that distinction.

## Contents

- [Design principles](#design-principles)
- [Select the document set](#select-the-document-set)
- [Root AGENTS.md](#root-agentsmd)
- [Nested AGENTS.md](#nested-agentsmd)
- [Architecture documents](#architecture-documents)
- [Planning system](#planning-system)
- [Quality guides](#quality-guides)
- [Repository-local skills](#repository-local-skills)
- [Claude compatibility](#claude-compatibility)
- [Size, duplication, and maintenance](#size-duplication-and-maintenance)

## Design principles

Apply these principles in order:

1. **Verified facts over plausible guidance.** Commands, paths, boundaries, and policies must have repository evidence.
2. **Minimum useful context.** Put only durable, frequently needed instructions in always-loaded files.
3. **Nearest scope wins.** Keep repository-wide rules at the root and local exceptions beside the relevant subproject.
4. **One canonical owner.** Link to architecture, planning, or quality detail instead of duplicating it.
5. **Checkable completion.** Define success using exact commands, observable outputs, or explicit review checks.
6. **Progressive disclosure.** Move detailed or situational workflows into linked documents or skills.
7. **Model-agnostic durability.** Describe the repository and its workflow, not prompt tricks for a specific model release.
8. **Authorization continuity.** Repository guidance supports the user's request within host permissions. Do not add an approval gate to already-authorized local work or reinterpret an example workflow as binding policy.
9. **Measured improvement.** When optimizing behavior, connect a trace or observed failure to one rule change and a relevant check. A longer instruction file or a passing style audit is not evidence of better model performance.

Codex combines applicable instruction files from the repository root toward the working directory, with closer instructions taking precedence. Keep the combined chain small. The audit helper defaults to a 32 KiB combined limit; override `--max-agent-bytes` when repository configuration uses a different value, and re-check current official guidance before relying on the exact default.

## Select the document set

Install the three required repository-root entry points: `AGENTS.md`, `CLAUDE.md`, and the canonical `PLANS.md`. Then identify independently buildable or runnable projects and require `ARCHITECTURE.md` at each of those boundaries.

| Document | Create or retain when | Avoid when |
| --- | --- | --- |
| Root `AGENTS.md` | Agent work is expected in the repository | Almost never; this is the harness entry point |
| Root `ARCHITECTURE.md` | The repository root is itself an independently buildable or runnable project | The root only aggregates nested projects |
| Root `CLAUDE.md` | Every create or optimize request | Never duplicate `AGENTS.md`; import it |
| Nested `AGENTS.md` | A real subproject has materially different commands or constraints | It would only repeat root guidance |
| Nested `ARCHITECTURE.md` | The directory is an independently buildable or runnable project | The directory only scopes instructions and is not a project boundary |
| Nested `CLAUDE.md` | Every directory that receives nested `AGENTS.md` | Never duplicate the sibling instructions |
| Root `PLANS.md` | Every repository | It differs from the canonical skill asset |
| `docs/exec-plans/` | Active/completed plan history is useful | It would hold only empty ceremony |
| Coding standards | Verified code conventions exceed a short root summary | It would be generic language advice |
| Code review guide | Review gates, severity, or domain checks need definition | Existing project policy already owns the topic |
| Verification guide | Multiple change types have different authoritative checks | One short command is sufficient in `AGENTS.md` |
| Local skill | A repeated workflow has a precise trigger and benefits from helpers or detailed context | It is one-off guidance or a renamed document |

Except for the fixed root `PLANS.md`, preserve an existing filename, location, and canonical ownership when they already have clear roles. Normalize `AGENTS.md` and `ARCHITECTURE.md` structure against [document-style.md](document-style.md); for other documents, retain a useful existing structure unless the request requires a change. Avoid creating case or spelling variants that compete with an existing owner.

A non-audit run is incomplete until the three repository-root files exist. Every root or nested instruction boundary pairs `AGENTS.md` with `CLAUDE.md`; every independent project boundary adds `ARCHITECTURE.md`. A pure aggregation root therefore has `AGENTS.md`, `CLAUDE.md`, and `PLANS.md`, while its frontend and backend project directories each have all three local harness documents.

## Root AGENTS.md

The root file is a concise operating guide, not a full handbook. Include only what agents repeatedly need.

Follow the mandatory title, semantic section order, numbering rules, and source layout in [document-style.md](document-style.md). The root outline must expose repository positioning and map, start-of-task reading, autonomy and execution boundaries, ExecPlan triggers, repository invariants, on-demand documentation, authoritative commands, and completion criteria in that order.

Write imperatively and precisely. State working directories for commands in monorepos. Distinguish required checks from optional or expensive checks. Name missing prerequisites rather than hiding them.

For autonomy guidance, state when the agent should act, what truly requires input, how it can finish independent work, and what proves completion. An unresolved optional preference should not stop the workflow. Make these rules concrete and scoped instead of copying an entire model system prompt. See [model migration](model-migration.md) for the Sol/Astra migration procedure.

Keep out:

- architecture narratives already owned elsewhere;
- exhaustive directory trees;
- generic exhortations such as “write clean code”;
- commands that were guessed or copied only from another repository;
- large examples needed only for rare workflows;
- transient task status or chat history.

## Nested AGENTS.md

Create nested instructions only at meaningful boundaries. The nested file inherits root guidance, so include only local information and explicit exceptions.

Follow the nested outline in [document-style.md](document-style.md): scope and entry points, before-editing evidence, architecture and dependency boundaries, domain contracts and risks, tests and authoritative commands, then local completion criteria. Domain-specific sections may expand the middle of the outline; commands stay near the end.

Do not restate root rules unless the local file changes or sharpens them. If two sibling projects share extensive detail, move that detail to a common linked guide instead of copying it.

Use `AGENTS.override.md` only when the repository already relies on the override mechanism or the user explicitly requests it. Do not turn temporary overrides into a second permanent policy layer.

## Architecture documents

Place an `ARCHITECTURE.md` at every independently buildable or runnable project boundary. This includes the repository root for a single-project repository, but excludes a pure aggregation root whose deployable projects live in child directories. Present the current system as current fact and move proposed changes to an ExecPlan or explicit design document. A small project still gets a short architecture document that states its scope, entrypoint or artifact, dependency shape, and verification surface without inventing complexity.

Use the mandatory title and continuously numbered level-two outline in [document-style.md](document-style.md). End with a verification section. Architecture documents describe the current system; move proposed changes, diagnoses, evolution recommendations, and roadmaps to an ExecPlan or explicit design document.

Useful sections:

- purpose and system boundary;
- source layout with responsibilities;
- runtime paths from entrypoint through core logic to I/O;
- public APIs, schemas, events, database, and external-service contracts;
- dependency direction and ownership boundaries;
- cross-cutting behavior such as authentication, authorization, errors, observability, configuration, and transactions;
- test architecture and deployment shape;
- invariants, failure modes, and change-risk hotspots;
- links to deeper design records when they exist.

Prefer one or two small diagrams only when they clarify a multi-step flow or hierarchy better than prose. Keep diagrams consistent with verified code. Do not manufacture component relationships to make a diagram look complete.

Architecture documentation should answer:

- Where does a request, job, or event enter?
- Which layer owns validation and business rules?
- Where does I/O occur?
- Which contracts must remain backward compatible?
- What must be tested when a boundary changes?

## Planning system

Install the planning contract in every repository. Create individual ExecPlans for work that is multi-session, cross-component, migration-heavy, ambiguous, or difficult to verify in one step.

### Root PLANS.md

Copy [the canonical PLANS.md asset](../assets/PLANS.md) to the repository root byte-for-byte. Do not generate, summarize, translate, date, or tailor it. The canonical file already defines when to use an ExecPlan, its required sections, active/completed lifecycle, autonomy and approval boundaries, validation evidence, and recovery expectations.

Before replacing an existing noncanonical file, identify verified project-specific content. Move plan triggers and repository constraints to root `AGENTS.md`; move index or local lifecycle details to `docs/exec-plans/README.md`. Discard duplicated generic advice and stale project decoration. Do not move hidden reasoning or chat history.

The standard template is mandatory even for repositories whose current work is small. It establishes the contract for future complex work without requiring an ExecPlan for every task.

### docs/exec-plans

When a plan lifecycle is useful, prefer:

```text
docs/exec-plans/
├── README.md
├── active/
└── completed/
```

Retain an existing taxonomy. Add a category such as `tech-debt/` only when the repository has a real workflow for it.

The README should explain the lifecycle and index tracked plans with status and links. Use a stable filename convention such as `YYYY-MM-DD-short-title.md` when the repository has none.

Never rewrite completed plans to match a new template. Completed plans are historical records; edit them only for an explicitly requested factual correction or broken-link repair. When moving a plan to `completed/`, update its outcome and the index in the same change.

## Quality guides

### Coding standards

Document repository-specific, evidenced conventions:

- language and framework versions;
- formatter, linter, typechecker, and generated-code rules;
- module boundaries and dependency direction;
- naming and API conventions visible in code or configuration;
- error, logging, security, database, concurrency, and compatibility rules;
- testing expectations by change type;
- examples only when they come from representative project code.

Separate enforced rules from conventions. Do not write a generic language tutorial.

### Code review guide

Define how to assess correctness and communicate findings:

- review goals and evidence expectations;
- severity levels tied to concrete impact;
- correctness, security, data, compatibility, concurrency, performance, and maintainability checks relevant to the project;
- test adequacy and documentation checks;
- generated files and migration review;
- expected finding format: impact, trigger, evidence, and actionable fix direction;
- how to report clean reviews and residual risk.

Keep style preferences below correctness and enforceable project rules. Require narrow line references for actionable findings.

### Verification guide

Create a change-type matrix that maps changes to authoritative checks. Include prerequisites, working directory, exact command, expected signal, and when a check may be skipped.

Typical rows include:

- documentation only;
- backend unit or integration change;
- frontend logic or UI change;
- schema or migration change;
- API or event contract change;
- dependency or build change;
- deployment or infrastructure change.

Use repository commands, not generic placeholders. Explain layered escalation from focused checks to broader suites. Require skipped checks and environmental blockers to be reported explicitly.

Include the success signal and stop condition: passing required checks ends validation unless a new change, failure, or unresolved concern justifies more. For services or UI behavior, name the functional request or interaction that proves readiness; a PID, open port, or generated file alone is insufficient. Keep environment prerequisites separate from application defects and avoid blanket full-suite requirements for low-impact documentation edits.

## Repository-local skills

Use `.agents/skills/<skill-name>/SKILL.md` when a repeated workflow needs a precise trigger, conditional detail, or executable helper. Follow progressive disclosure:

1. Put a specific trigger and short capability summary in frontmatter.
2. Keep the main workflow concise.
3. Move deep reference material to `references/`.
4. Put deterministic, reusable operations in `scripts/`.
5. Test every added script and validate skill metadata.

Do not create a skill for a single task, a generic policy, or content better owned by `AGENTS.md` or a quality guide.

## Claude compatibility

Keep Codex instructions canonical. The required root `CLAUDE.md` contains:

```markdown
@AGENTS.md
```

Create the same thin file beside every nested `AGENTS.md`. Because the import target is a sibling, `@AGENTS.md` remains the expected content at each boundary. Add Claude-specific text only for a verified behavioral difference; preserve such existing rules, but do not duplicate the shared instruction body.

If repository-local skills are shared through `.claude/skills/`, preserve the project's existing convention. Symlink or import only when the target tool supports it and the user requested compatibility. Verify every target and avoid two independently maintained copies.

Do not generate Cursor rules as part of Claude compatibility.

## Size, duplication, and maintenance

After editing:

1. Trace instruction precedence from root to each nested boundary.
2. Remove duplicated commands or policies unless the closer file intentionally overrides them.
3. Check the combined instruction size against the repository's configured budget.
4. Confirm every linked detail has one canonical owner.
5. Confirm current facts and future plans are visibly separated.
6. Confirm new commands are backed by configuration and, when practical, execution.
7. Confirm no completed plan history or unrelated documentation was rewritten.

Prefer deleting redundant prose over compressing it into dense, ambiguous instructions.
