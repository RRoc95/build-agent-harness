# Harness blueprint

Design the harness as a layered operating system for repository work: short instructions are always available, detailed context is linked, plans preserve long-running state, and executable helpers validate what can be checked mechanically.

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

Codex combines applicable instruction files from the repository root toward the working directory, with closer instructions taking precedence. Keep the combined chain small. The audit helper defaults to a 32 KiB combined limit; override `--max-agent-bytes` when repository configuration uses a different value, and re-check current official guidance before relying on the exact default.

## Select the document set

Install the root harness entry points, including the canonical `PLANS.md`. Select optional documents by demonstrated repository need rather than creating them merely to complete a template.

| Document | Create or retain when | Avoid when |
| --- | --- | --- |
| Root `AGENTS.md` | Agent work is expected in the repository | Almost never; this is the harness entry point |
| Nested `AGENTS.md` | A real subproject has materially different commands or constraints | It would only repeat root guidance |
| `ARCHITECTURE.md` | Runtime flow, boundaries, contracts, or risks need durable explanation | The directory is trivial and self-evident |
| Root `PLANS.md` | Every repository | It differs from the canonical skill asset |
| `docs/exec-plans/` | Active/completed plan history is useful | It would hold only empty ceremony |
| Coding standards | Verified code conventions exceed a short root summary | It would be generic language advice |
| Code review guide | Review gates, severity, or domain checks need definition | Existing project policy already owns the topic |
| Verification guide | Multiple change types have different authoritative checks | One short command is sufficient in `AGENTS.md` |
| Local skill | A repeated workflow has a precise trigger and benefits from helpers or detailed context | It is one-off guidance or a renamed document |
| `CLAUDE.md` | Claude compatibility is requested or already part of the repository | Codex-only scope with no existing Claude surface |

Except for the fixed root `PLANS.md`, preserve an existing filename and structure when it already has a clear canonical role. Avoid creating case or spelling variants that compete with it.

## Root AGENTS.md

The root file is a concise operating guide, not a full handbook. Include only what agents repeatedly need.

Recommended outline:

1. **Purpose and success** — what correct work in this repository means.
2. **Repository map** — real subprojects and where deeper guidance lives.
3. **Authoritative commands** — setup, focused test, broader test, lint, typecheck, build, and run commands that were verified.
4. **Global constraints** — boundaries, generated files, security-sensitive areas, compatibility promises, and prohibited changes.
5. **Working method** — inspect, make surgical changes, validate by risk, review the diff.
6. **Definition of done** — checkable completion and reporting requirements.
7. **Links** — architecture, planning, standards, review, verification, and local skills.

Write imperatively and precisely. State working directories for commands in monorepos. Distinguish required checks from optional or expensive checks. Name missing prerequisites rather than hiding them.

Keep out:

- architecture narratives already owned elsewhere;
- exhaustive directory trees;
- generic exhortations such as “write clean code”;
- commands that were guessed or copied only from another repository;
- large examples needed only for rare workflows;
- transient task status or chat history.

## Nested AGENTS.md

Create nested instructions only at meaningful boundaries. The nested file inherits root guidance, so include only local information and explicit exceptions.

Recommended outline:

1. Scope of the subproject.
2. Local map and entry points.
3. Local setup/build/test/lint/typecheck/run commands.
4. Architecture and contract invariants.
5. High-risk areas and prohibited shortcuts.
6. Local definition of done and links.

Do not restate root rules unless the local file changes or sharpens them. If two sibling projects share extensive detail, move that detail to a common linked guide instead of copying it.

Use `AGENTS.override.md` only when the repository already relies on the override mechanism or the user explicitly requests it. Do not turn temporary overrides into a second permanent policy layer.

## Architecture documents

Place an `ARCHITECTURE.md` at the root or subproject boundary it describes. Present the current system as current fact and label proposed changes explicitly.

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

## Repository-local skills

Use `.agents/skills/<skill-name>/SKILL.md` when a repeated workflow needs a precise trigger, conditional detail, or executable helper. Follow progressive disclosure:

1. Put a specific trigger and short capability summary in frontmatter.
2. Keep the main workflow concise.
3. Move deep reference material to `references/`.
4. Put deterministic, reusable operations in `scripts/`.
5. Test every added script and validate skill metadata.

Do not create a skill for a single task, a generic policy, or content better owned by `AGENTS.md` or a quality guide.

## Claude compatibility

Keep Codex instructions canonical. For thin Claude compatibility, a root `CLAUDE.md` can contain:

```markdown
@AGENTS.md
```

Use the equivalent relative import at nested boundaries when needed. Add Claude-specific text only for a real behavioral difference; do not duplicate the full instruction body.

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
