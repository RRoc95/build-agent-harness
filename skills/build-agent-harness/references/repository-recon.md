# Repository reconnaissance

Build the harness from observable repository facts. Reconnaissance is complete when another agent could locate the right code, run the relevant checks, and understand the main boundaries without guessing.

## Contents

- [Start with scope and safety](#start-with-scope-and-safety)
- [Collect evidence](#collect-evidence)
- [Recognize real subprojects](#recognize-real-subprojects)
- [Audit a reference repository](#audit-a-reference-repository)
- [Create an evidence map](#create-an-evidence-map)
- [Resolve uncertainty](#resolve-uncertainty)

## Start with scope and safety

1. Resolve the requested target path and its Git top level.
2. Read every instruction file that applies from the filesystem or repository root to the target directory.
3. Capture `git status --short` before editing.
4. Identify user-owned changes and avoid touching them unless they are directly in scope.
5. Confirm whether the request is docs-only, whether a reference repository is supplied, and whether Claude compatibility is requested or already present.

Do not assume the current shell directory is the Git root. A workspace may contain multiple sibling repositories.

## Collect evidence

Search broadly, then read narrowly. Prefer `rg --files` and `rg` for discovery.

| Question | Strong evidence |
| --- | --- |
| What are the build units? | Language/package manifests, workspace files, lockfiles, build scripts |
| How is the project run? | Package scripts, Make targets, task runners, container entrypoints, service launchers |
| How is it tested? | Test configuration, test directories, CI jobs, documented commands confirmed by scripts |
| What is deployed? | Dockerfiles, compose files, deployment manifests, release workflows, infrastructure modules |
| Where does execution enter? | Main modules, CLI definitions, HTTP routers, workers, schedulers, frontend bootstraps |
| What are the boundaries? | Imports, public interfaces, API schemas, database access layers, messaging contracts |
| What is risky? | Authentication, authorization, migrations, concurrency, money, destructive jobs, external integrations |
| What conventions are real? | Representative nearby code, formatter/linter configuration, CI enforcement |
| What changed recently? | Recent commits touching harness, build, test, architecture, or deployment files |

Inspect at least:

- root and subproject manifests;
- package/task scripts and Makefiles;
- CI workflows;
- test configuration and representative tests;
- runtime entry points;
- deployment and environment examples;
- existing `AGENTS.md`, `CLAUDE.md`, `ARCHITECTURE.md`, `PLANS.md`, `docs/`, and repository-local skills;
- recent commits that explain current structure.

Do not copy a command merely because it appears in prose. Confirm it against the executable configuration or run it safely.

If root `PLANS.md` differs from the skill's canonical asset, inspect it only to identify verified project-specific triggers, constraints, or index rules that belong elsewhere. Do not preserve its generic template wording or use it as a reference for the replacement file.

## Recognize real subprojects

A directory merits nested harness documentation when several of these are true:

- it has its own manifest or workspace membership;
- it has independent build, test, lint, or typecheck commands;
- it has a distinct runtime or deployable artifact;
- it owns clear interfaces or data contracts;
- its local constraints differ materially from the repository root;
- contributors can work in it without loading the whole repository model.

A directory does not become a subproject merely because it contains source code, a Dockerfile, generated output, examples, or a vendored dependency.

For monorepos, create a small boundary table before writing:

| Area | Evidence | Build/test boundary | Runtime/deployment boundary | Local instructions needed? |
| --- | --- | --- | --- | --- |
| `path/` | `manifest`, `script`, `workflow` | Describe verified commands | Describe artifact/service | Yes/No with reason |

Use this table as working evidence; do not persist it unless it adds durable value for maintainers.

## Audit a reference repository

When the user supplies a reference repository:

1. Inventory both repositories independently.
2. Compare document responsibilities, nesting, planning lifecycle, quality gates, and compatibility strategy.
3. Extract reusable patterns, not wording.
4. Map every adopted pattern to target-repository evidence.
5. Reject reference details that do not fit the target's language, topology, tooling, or risk profile.

Useful comparisons include:

- which information stays in root instructions;
- when nested instructions appear;
- how architecture documents describe runtime flow and invariants;
- how plans move from active to completed;
- how verification commands are sourced;
- whether agent-specific compatibility files import or duplicate shared guidance.

Never transfer package names, ports, directory names, commands, owners, service boundaries, or deployment assumptions without target evidence.

## Create an evidence map

Before editing, map each intended claim to its source:

| Intended claim | Repository evidence | Destination | Confidence/action |
| --- | --- | --- | --- |
| Test command | `package.json`, `Makefile`, CI job | `AGENTS.md` or verification guide | Verified / run needed |
| Runtime flow | Entrypoint and representative call path | `ARCHITECTURE.md` | Verified / incomplete |
| Coding rule | Formatter, linter, nearby code | Coding standards | Enforced / conventional |
| Review gate | CI or project policy | Code review guide | Required / recommended |

Keep the map in working notes unless the user requests it as a durable artifact.

## Resolve uncertainty

Use this order:

1. Search configuration and code.
2. Inspect CI and recent history.
3. Run a safe discovery or help command.
4. Omit a nonessential claim.
5. Ask one concrete question if the unresolved fact materially changes the harness.

Fail loudly in the delivery report when a command could not be run, an architecture path was sampled rather than exhaustively traced, or a policy has no enforceable repository evidence.
