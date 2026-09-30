# OpenAI guidance and provenance

Read this when refreshing an OpenAI claim, changing model guidance, or explaining the basis for this skill. Do not load it for every repository edit.

## Verification boundary

Reviewed on 2026-09-30 (Asia/Shanghai). Live official documentation and blogs were fetched after network access was restored. Official repository sources were also read from their default branches and are pinned for reproducibility:

- `openai/codex`: `d42056091aded7feb1d88ac7e83972108b2aa478`, commit timestamp 2026-09-30T07:15:14Z.
- `openai/openai-cookbook`: `2182005bcaf5a5cdd96bb46fb9995d08730e7b91`, commit timestamp 2026-09-29T12:13:15-07:00.

The live GPT-6 guide now covers both requested models. The guessed dedicated `/latest-model/gpt-6.1-sol.md` route returned 404; use the Sol section of the shared guide and its actual model page. The harness blog initially returned 403 but was fetched successfully with a query string. Codex's AGENTS.md and skills URLs redirected to `learn.chatgpt.com`; the linked destinations below were read as Markdown. Live documentation takes precedence over bundled fallback guidance for current product claims.

## Sources used

| Source | Verified scope | Applied here |
| --- | --- | --- |
| [Rethinking skills and prompts for GPT-6 Astra](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra) | Short precise skill descriptions, minimal routers, contextual reading, decision boundaries and completion | Narrow the trigger, load references on demand, define full/focused/audit scope and stop conditions |
| [GPT-6 guide: prompting and migration](https://developers.openai.com/api/docs/guides/latest-model/gpt-6-astra.md) | Family-wide starting prompts based on Astra observations; Sol selection and API migration guidance | Shared core, explicit persistence and authorization continuity, measured model comparisons |
| [GPT-6.1 Sol](https://developers.openai.com/api/docs/models/gpt-6.1-sol.md) and [GPT-6 Astra](https://developers.openai.com/api/docs/models/gpt-6-astra.md) | Exact API IDs and reasoning/tool compatibility | Distinguish host catalog settings from public API settings; avoid copying unsupported parameters |
| [Harness engineering](https://openai.com/index/harness-engineering/) | Short instruction maps, repository knowledge, executable feedback and mechanical boundaries | Conditional references and read-only structural checks; do not copy the article's team-specific merge or delegation policies |
| [Testing Agent Skills Systematically with Evals](https://developers.openai.com/blog/eval-skills) | Traces plus artifacts, explicit/implicit/negative trigger cases, deterministic and rubric checks | Evaluate discovery as well as execution; separate local checks from actual model trials |
| [Evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices.md) | Task-specific evals, representative cases and human-calibrated scoring | Controlled comparisons, held-out cases and failure-driven iteration |
| [AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md.md) and [Build skills](https://learn.chatgpt.com/docs/build-skills.md) | Instruction discovery, skill loading, progressive disclosure and optional metadata | Preserve host hierarchy; use current `.agents/skills` installation paths and precise discovery metadata |
| [Codex model catalog](https://github.com/openai/codex/blob/d42056091aded7feb1d88ac7e83972108b2aa478/codex-rs/models-manager/models.json) | Contains `gpt-6.1-sol` and `gpt-6-astra`; describes Sol as the coding/everyday workhorse and Astra for demanding work | Preserve the requested identifiers; use roles as starting hypotheses for evaluation, not as a forced router |
| [Bundled Astra prompting guidance](https://github.com/openai/codex/blob/d42056091aded7feb1d88ac7e83972108b2aa478/codex-rs/skills/src/assets/samples/openai-docs/references/prompting-guide.md) | Fallback for Astra initiative, instruction following, writing, delegation and testing | Explicit authorization continuity, source attribution for pauses, concise delivery, conditional delegation and bounded verification |
| [Bundled Astra migration guide](https://github.com/openai/codex/blob/d42056091aded7feb1d88ac7e83972108b2aa478/codex-rs/skills/src/assets/samples/openai-docs/references/upgrading-to-gpt-6-astra.md) | Scoped migration and controlled comparisons | Preserve the baseline, separate model/prompt/effort changes, and keep API/runtime migration outside documentation scope |
| [Official skill-creator](https://github.com/openai/codex/blob/d42056091aded7feb1d88ac7e83972108b2aa478/codex-rs/skills/src/assets/samples/skill-creator/SKILL.md) | Precise triggers, capable-agent assumption, risk-proportional specificity, progressive disclosure and script validation | Shorter entrypoint, conditional reference loading, full/focused/audit modes and package validation |
| [Iterating development workflows with Codex](https://github.com/openai/openai-cookbook/blob/2182005bcaf5a5cdd96bb46fb9995d08730e7b91/examples/codex/iterating-development-workflows-with-codex.md) | Repository knowledge and optional workflow conventions | Separate Codex behavior from this project's canonical file and outline conventions |
| [Using PLANS.md for multi-hour problem solving](https://github.com/openai/openai-cookbook/blob/2182005bcaf5a5cdd96bb46fb9995d08730e7b91/articles/codex_exec_plans.md) | Outcome-oriented, self-contained living plans | Preserve the existing canonical asset and plan history; use task-specific evidence for resumption |
| [Build iterative repair loops with Codex](https://github.com/openai/openai-cookbook/blob/2182005bcaf5a5cdd96bb46fb9995d08730e7b91/examples/codex/Build_iterative_repair_loops_with_Codex.ipynb) | Review, focused repair, executable validation, remaining delta and stopping conditions | Retry from observed feedback; stop on success, unchanged failure, an actual blocker or a defined experiment budget |
| [Agent improvement loop](https://github.com/openai/openai-cookbook/blob/2182005bcaf5a5cdd96bb46fb9995d08730e7b91/examples/agents_sdk/agent_improvement_loop.ipynb) | Traces, human feedback, behavior evals and iteration | Add a reusable evaluation protocol; no mandatory HALO, Promptfoo, model API or new dependency |

The catalog establishes Codex source metadata at its revision, not public API defaults or account access. The live guide explicitly presents its prompts as starting points across GPT-6 while attributing the observed behaviors to Astra. Evaluate them on Sol rather than declaring them established Sol traits.

## Refresh policy

Fetch the exact relevant official page before refreshing a model-specific claim. Record the date, source URL/revision, supported claim, and harness decision it changes. Prefer a disclosed official repository fallback when the live page is unavailable. Never silently substitute another model or turn an example's optional gates, tools, or directory layout into a global requirement.

## Local conventions retained

The required full-harness baseline, thin Claude imports, exact AGENTS/ARCHITECTURE outlines, and byte-for-byte canonical PLANS.md are project choices. OpenAI's Cookbook explicitly describes its workflow files as optional conventions, and the ExecPlan article permits customization. This project intentionally retains its existing conventions for compatibility; they are not attributed to GPT-6.1 Sol, GPT-6 Astra, or Codex itself.
