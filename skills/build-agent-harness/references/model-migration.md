# Model-aware harness migration

Use for an explicitly requested model change or a model-specific regression supported by observed behavior. Keep the shared repository harness durable across models; do not add this entire reference to every AGENTS.md.

## Targets and evidence

The targets are `gpt-6.1-sol` and `gpt-6-astra`. The live official guide positions Sol for complex work at lower cost and Astra for the most demanding work; evaluate that tradeoff on the repository's tasks. Its prompting guidance is a family-wide starting point based on observed Astra behavior. See [source provenance](openai-sources.md).

Keep host and API settings distinct. The verified Codex catalog uses `low` as its default reasoning level and lists `ultra`; the live Sol API page instead documents `medium` as default and `low`, `medium`, `high`, `xhigh`, `max` as supported. The Astra API page lists the same supported efforts. Do not transfer `ultra` or a host default into an API configuration. These facts do not authorize changing the user's effective settings.

There is no inference that Sol and Astra need incompatible repository rules. Start with the same harness and compare them on the same tasks. Keep the chosen model, effort, service tier, toolset and permission mode in the host's configuration or the experiment record, not in generic repository invariants. Preserve explicit user preferences and intentionally pinned fallbacks. Do not change model configuration as part of a documentation-only request.

## Audit the instruction stack

| Observed or documented concern | Candidate harness correction | Evidence to check |
| --- | --- | --- |
| Astra asks for clarification or permission before authorized work | State the outcome, existing authorization and genuine decision boundary; continue independent work | No repeated approval request; the requested artifact is completed |
| Stronger instruction following turns an old skill convention into a blocker | Classify requirements versus recommendations; user scope takes precedence within host permissions; cite any rule causing a pause | The agent applies the correct scope without silently ignoring a real boundary |
| A focused request expands into full harness generation | Select full, focused or audit-only mode explicitly | Only requested surfaces change |
| Detailed output obscures the result | Ask for outcome, changed artifacts, actual validation and residual blocker in concise prose | A reviewer can assess the result without a transcript |
| Testing grows after the required checks pass | Define change-proportional checks and the condition for more testing | Required checks execute; unrelated and unchanged checks are not repeated |
| Work stops after planning or first tool failure | Require completion of authorized work and diagnosis before retry | The loop advances after recoverable failure and distinguishes external blockers |
| Delegation is missing or excessive | Enable it only when permitted and useful; bound task ownership and integration | No overlapping edits, unauthorized agent calls, or unverified merged findings |

The Astra concerns above come from the live GPT-6 guide and the official skill/prompt migration blog. Their occurrence and the value of each correction must still be checked on this workload. For Sol, treat them as evaluation hypotheses rather than documented model characteristics.

## Apply the smallest migration

1. Inventory the active instruction surfaces, requested modes, old model/effort when known, tool contracts and validation commands. Do not replace historical examples or completed plans.
2. Preserve a baseline: old harness on the old model, where available, and old harness on each requested model. Mark unavailable cells as unrun.
3. Identify whether a failure comes from a prompt, instruction conflict, tool/environment problem, repository defect or model capability. Fix the responsible layer within scope; prose cannot supply a missing permission, credential or tool.
4. Change the smallest instruction that addresses the evidenced problem or explicit user requirement. Keep legitimate approval boundaries, output contracts and verification assertions.
5. Compare old versus candidate harness for each target with the same repository snapshot, task and runtime settings. Use [behavioral evaluation](evaluation.md); change reasoning effort or delegation in a separate experiment.
6. Promote a candidate only on observed results. Report unsupported targets, failed checks and unavailable comparisons rather than claiming cross-model optimization from a structural audit.

For a requested refresh without live traces, make source-backed contract and clarity improvements, then label model-level effectiveness as unmeasured. Do not fabricate a performance improvement or require a paid evaluation before delivering the authorized local changes.

## Runtime and context boundaries

This skill builds repository guidance, not an API client. API changes require separate implementation scope. The verified live guide says tool calling for these targets requires Responses; both reject `none` and `minimal`, and reasoning requests do not support `temperature` or `top_p`. Check the current endpoint-specific guide before changing an integration, preserve supported effective effort, and test one parameter change at a time. Do not insert API fields into a repository with no corresponding integration. Caching, async tools, mid-turn steering and context compaction remain host responsibilities unless explicitly requested.

When a task spans sessions or models, retain factual progress, accepted decisions, paths, exact check results, unresolved items and the next action in the existing plan owner. Do not store hidden reasoning or duplicate the transcript. A model change does not cancel prior authorization or restart completed work.

Parallel tool calls and subagent delegation are distinct. Independent read-only checks can be batched when supported. Spawn agents only when allowed by higher-priority instructions and the user's scope, with separate ownership and a final integration check. This reference does not itself enable delegation.
