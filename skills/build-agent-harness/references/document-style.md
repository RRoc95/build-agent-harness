# Harness document style

Use this contract when creating or normalizing `AGENTS.md` and `ARCHITECTURE.md`. It captures the stable document shape shared by the reference harnesses while leaving all project facts, commands, boundaries, and terminology dependent on target-repository evidence.

## Contents

- [Scope of the contract](#scope-of-the-contract)
- [Shared Markdown style](#shared-markdown-style)
- [Root AGENTS.md](#root-agentsmd)
- [Nested AGENTS.md](#nested-agentsmd)
- [ARCHITECTURE.md](#architecturemd)
- [Normalization rules](#normalization-rules)
- [Anti-patterns](#anti-patterns)

## Scope of the contract

The contract standardizes:

- the document title;
- the opening scope statement;
- the semantic order of sections;
- heading-number consistency;
- the separation between current architecture and future work;
- the position of commands, verification, and completion criteria;
- Markdown source layout.

It does not standardize project facts. Never copy a command, package name, port, directory, technology, service, invariant, or runtime path from a reference repository without evidence in the target.

This is a local style contract for full-harness generation and requested normalization, not an OpenAI model requirement. Apply it only to the requested surfaces in a focused update. Preserve verified facts and keep each section as short as its useful content allows; headings are navigation, not a word-count target.

Use the target repository's established human language for prose. Keep machine-audited outline headings in one of the two canonical vocabularies supported by this skill: use the Chinese labels below for Chinese harnesses and their stated English equivalents for other harnesses. Do not freely translate the semantic anchor headings into additional languages, because the deterministic auditor intentionally recognizes Chinese and English only. Match existing numbered or unnumbered `AGENTS.md` headings when they are internally consistent. Use numbered level-two headings in every `ARCHITECTURE.md`.

## Shared Markdown style

Apply these source-format rules to both document types:

1. Start with exactly one level-one title.
2. Follow the title with a short scope paragraph before detailed content. An architecture document may move directly to its first section only when an established repository style already does so.
3. Use level-two headings for the main outline and level-three headings only for subordinate flows or components.
4. Keep one prose paragraph or list item on one source line. Do not manually wrap a sentence across lines merely to satisfy a column width.
5. Put a blank line around headings, lists, tables, and fenced code blocks.
6. Label every code fence, using `bash` for commands and `text` for architecture or directory diagrams.
7. Put paths, commands, identifiers, environment variables, endpoints, and code symbols in backticks.
8. Use short tables for repeated mappings and `text` diagrams for dependency direction or multi-step flows when either is clearer than prose. Do not add decorative diagrams.
9. Prefer concise bullets over dense paragraphs, but do not fragment one rule into several overlapping bullets.
10. End the file with one final newline.

Keep headings descriptive and stable. Avoid conversational headings, questions, release dates, task status, model names, and temporary migration notes.

## Root AGENTS.md

The root file is the repository operating contract. Its title is exactly:

```markdown
# AGENTS.md
```

Immediately state:

- the scope of the file;
- which nested instruction files take precedence;
- that Codex is primary and `CLAUDE.md` imports the same rules when that distinction is useful.

Use this semantic outline:

```markdown
# AGENTS.md

<Repository scope, inheritance, and precedence.>

## 1. 项目定位与目录

## 2. 开始任务前

## 3. 自治与执行边界

## 4. 何时使用 ExecPlan

## 5. 仓库级不变量

## 6. 按需阅读

## 7. 常用命令

## 8. 完成定义
```

An established repository may omit the numeric prefixes or split “自治与执行边界” into separate autonomy and execution-loop sections. It may use close local names such as “项目与目录”, “开始任务”, “完成标准”, or “文档与代码边界”. Preserve that local choice only when the resulting outline remains consistent and contains every semantic anchor.

English equivalents, in order, are: “Project positioning and repository map”, “Before starting”, “Autonomy and execution boundaries”, “When to use an ExecPlan”, “Repository invariants”, “On-demand reading”, “Authoritative commands”, and “Definition of done”.

Section responsibilities:

| Section | Required content |
| --- | --- |
| Project and map | Repository purpose, real project boundaries, and links to nested instructions or architecture |
| Before starting | Applicable instructions, evidence to inspect, worktree safety, and focused reconnaissance |
| Autonomy and execution | Inspect-edit-verify loop, approval boundaries, uncertainty handling, and scope discipline |
| ExecPlan | Concrete triggers and link to the canonical planning contract and local plan index |
| Repository invariants | Cross-project contracts, security or compatibility boundaries, and prohibited shortcuts |
| On-demand reading | Links to architecture, standards, review, verification, plans, and local skills without duplicating them |
| Commands | Verified repository-level commands with working directory and prerequisites where needed |
| Completion | Checkable definition of done, diff review, skipped-check reporting, and documentation synchronization |

Do not open with generic goals such as “write high-quality code”. Do not fold ExecPlan guidance into a directory-map bullet or hide the start-of-task contract inside a broad “working method” section.

## Nested AGENTS.md

A nested file inherits the root and contains only instructions for one meaningful scope. Its title is also exactly:

```markdown
# AGENTS.md
```

The opening paragraph must name the local scope, state that root rules are inherited, and link to the sibling `ARCHITECTURE.md` when the directory is an independent project.

Use this default semantic outline:

```markdown
# AGENTS.md

<Local scope, root inheritance, and architecture link.>

## 1. 子工程定位

## 2. 开始前

## 3. 分层与架构约束

## 4. 关键契约与不变量

## 5. 代码、依赖与安全

## 6. 测试与常用命令

## 7. 完成定义
```

Adapt the middle headings to the domain. A frontend may use “UI 与交互” and “代码与依赖”; a service may use “API、任务与回调”, “数据库与安全”, and “测试要求”. Keep this order:

1. scope and entry points;
2. what to inspect before editing;
3. dependency, layer, and ownership boundaries;
4. domain contracts and high-risk invariants;
5. tests and verified commands;
6. completion criteria.

English equivalents are: “Subproject positioning”, “Before editing”, “Architecture and dependency constraints”, “Domain contracts and high-risk invariants”, “Tests and authoritative commands”, and “Definition of done”. Add further domain-specific headings between the architecture and command sections when needed.

An established concise file may merge adjacent sections, for example “工作入口” may cover scope and start-of-task reading, or “常用命令” may contain tests. It must still retain at least six meaningful level-two sections, keep commands near the end, and finish with completion criteria.

Do not repeat root approval policy, planning prose, or generic engineering guidance unless the local scope changes it. Do not place commands before architecture and contract constraints.

## ARCHITECTURE.md

Every independently buildable or runnable project uses this title shape:

```markdown
# ARCHITECTURE.md — <工程名称>当前架构
```

The wording after the dash may follow repository terminology, for example “管理端架构”, “后端架构”, or “Server 当前架构”. The required invariant is that the title begins with `ARCHITECTURE.md — ` and names the project or system.

Use continuously numbered level-two headings beginning at 1. The exact number of domain-flow sections varies. Prefer this information order:

```markdown
# ARCHITECTURE.md — <工程名称>当前架构

<Scope, evidence basis, and explicit current-state statement.>

## 1. 系统定位与运行边界

## 2. 分层与依赖方向

## 3. 启动与应用生命周期

## 4. <关键运行流程一>

## 5. <关键运行流程二或数据流>

## 6. <数据、API 或外部契约>

## 7. <错误、安全、事务、并发或其他横切边界>

## 8. <关键文件与修改落点>

## 9. 验证
```

Required semantic anchors:

- system purpose and runtime boundary;
- layers, responsibilities, and allowed dependency direction;
- startup, lifecycle, or representative entry-to-I/O flow;
- applicable data, API, event, persistence, or external-service contracts;
- applicable cross-cutting boundaries and failure behavior;
- verification entry points as the final level-two section.

English equivalents for the stable anchors are “System purpose and runtime boundary”, “Layers and dependency direction”, “Startup and application lifecycle” or a representative request/event/job flow, and final “Verification” or “Validation”. Domain-specific middle headings remain evidence-driven.

Keep system position, application composition or layers, and the first representative runtime path near the beginning. When an established architecture is clearer with application composition or routing before the explicit dependency-direction section, preserve that local order; do not move the final verification section.

Use level-three headings for subordinate phases when a flow has multiple stable stages. If level-three headings use numeric prefixes, make them consistent with their parent section.

The final section must be “验证”, “验证入口”, `Verification`, `Validation`, or an equivalent dedicated verification heading. It names authoritative commands and the behavior each check covers; it does not claim that those checks were run during document generation unless they actually were.

Architecture is a current-state map, not a design proposal. Move diagnostics, recommended evolution, future architecture, migration roadmaps, and “next three things to do” into an active ExecPlan or design document. A short note about a verified present limitation is acceptable only when it affects current behavior or change safety.

## Normalization rules

When optimizing an existing harness:

1. Preserve every verified project fact and useful project-specific rule.
2. Normalize the title, opening scope paragraph, section ownership, ordering, and final section.
3. Rename vague headings to the closest semantic anchor.
4. Split overloaded sections when required anchors are hidden; merge only genuinely duplicated sections.
5. Move commands toward the end of `AGENTS.md`.
6. Number every architecture level-two heading sequentially from 1.
7. Move future-state architecture content to the correct planning owner without losing useful information.
8. Remove manual sentence wrapping while leaving tables, code blocks, and intentionally formatted diagrams intact.
9. Recheck links and update them when content moves.
10. Run the harness audit after normalization.

Do not rewrite solely to make wording identical to a reference project. The target should share the document grammar, not another project's voice or facts.

## Anti-patterns

Reject these shapes:

- `# Project Instructions`, `# Admin 架构`, or `# 架构说明` as substitutes for the canonical titles;
- root instructions with only “goal”, “commands”, “workflow”, and “done” sections;
- nested instructions with commands immediately after the scope and no architecture or contract section;
- unnumbered or partially numbered architecture level-two headings;
- architecture documents whose final section is risks, recommendations, diagnosis, or future work;
- copied reference commands or component names;
- paragraphs hard-wrapped in the middle of sentences;
- architecture narratives duplicated in `AGENTS.md`;
- task history, chat transcripts, internal reasoning, or design-process notes committed as harness documentation.
