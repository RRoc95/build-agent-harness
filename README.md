# Build Agent Harness

面向 Codex、兼容 Claude Code 的仓库级 harness skill：基于工程证据创建、优化或审计 agent 指令，支持向 GPT-6.1 Sol / GPT-6 Astra 迁移。

## 中文

### 工作方式

- **完整创建或优化**：生成根 `AGENTS.md`、薄 `CLAUDE.md` 和标准 `PLANS.md`；为独立工程补齐指令和 `ARCHITECTURE.md`，按需建立验证指南与执行计划。
- **局部修改**：只调整指定指令、命令或模型迁移规则，保留用户改动与计划历史。
- **只读审计**：报告缺失、冲突和过时规则，不修改目标仓库。

根入口保持精简，参考资料按任务加载。持续完成已授权工作，明确真正需要确认的边界；验证范围随改动风险确定，通过必要检查后结束。

完整模式下的文档标题、章节顺序、Claude 导入和标准 `PLANS.md` 是本项目保留的约定，并非 OpenAI 对所有仓库的强制要求。

### GPT-6.1 Sol / GPT-6 Astra 迁移

依据 2026-09-30 核验的 OpenAI 官方博客和在线文档：

- 缩短 skill 描述，收窄触发条件，按需读取参考文档。
- 审查旧规则造成的重复确认、提前停顿、过度测试和范围扩张。
- 两个模型共用稳定的仓库约束；运行时模型、推理强度与权限由宿主配置管理。
- 区分 Codex 模型目录与公开 API 参数。例如，Codex 目录中的 `ultra` 不应直接写入这两个模型的 API 请求。
- 用相同任务、起始仓库和运行设置比较旧/新 harness，记录实际结果；结构校验不能替代模型评测。

详见[模型迁移指南](skills/build-agent-harness/references/model-migration.md)、[行为评估方案](skills/build-agent-harness/references/evaluation.md)和[官方来源及适用范围](skills/build-agent-harness/references/openai-sources.md)。本仓库提供评估案例与协议，未附带两种模型的性能提升结论。

### 安装到 Codex

按当前官方文档，用户级本地 skill 放在 `~/.agents/skills`：

```bash
git clone https://github.com/RRoc95/build-agent-harness.git
mkdir -p "$HOME/.agents/skills/build-agent-harness"
cp -R build-agent-harness/skills/build-agent-harness/. \
  "$HOME/.agents/skills/build-agent-harness/"
```

团队仓库可以使用 `.agents/skills/build-agent-harness/`。升级时备份自己的修改并整体替换旧 skill，避免残留旧规则。若之前安装在 `~/.codex/skills`，迁移时检查重复安装；实际加载路径以宿主版本为准。列表未刷新时重启 Codex。

### 使用

```text
$build-agent-harness 为当前工程创建完整 harness，兼容 Claude Code。
$build-agent-harness 仅优化现有指令以适配 GPT-6.1 Sol 和 GPT-6 Astra，保留既有文档结构。
$build-agent-harness 只读审计当前 harness 的冲突、过时命令和不必要的确认步骤。
```

### 只读审计

以下命令从本仓库根目录运行；已安装版本可使用对应安装路径中的脚本。

```bash
python3 skills/build-agent-harness/scripts/harness_audit.py \
  --root /path/to/repository inventory

python3 skills/build-agent-harness/scripts/harness_audit.py \
  --root /path/to/repository validate \
  --project-boundary admin --project-boundary server
```

独立根工程使用 `--project-boundary .`，纯聚合根不列入。`validate` 检查完整基线的文档结构、格式、链接、Claude 导入、指令链大小和标准计划；局部任务中的既有基线缺口应单独报告。

维护本 skill 时运行包检查与脚本回归测试，无需模型调用或额外 Python 依赖：

```bash
python3 skills/build-agent-harness/scripts/harness_audit.py validate-skill \
  --skill-dir skills/build-agent-harness
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

审计器不会生成或修复文件。校验退出码：`0` 通过，`1` 发现错误，`2` 输入或运行错误；可加 `--json`。包检查只覆盖基础 frontmatter、Markdown 编码、换行、围栏和本地链接路径，不验证完整 YAML、UI 元数据或模型效果，详见[验证范围](skills/build-agent-harness/references/verification.md)。

### 标准 PLANS.md

完整模式下，目标根 `PLANS.md` 与 [canonical asset](skills/build-agent-harness/assets/PLANS.md) 字节一致。项目自己的触发条件和工作约束放在 `AGENTS.md`，生命周期说明放在 `docs/exec-plans/README.md`。局部修改不会自动重写计划文件。

### 主要官方依据

- [Rethinking skills and prompts for GPT-6 Astra](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra)
- [GPT-6 提示与迁移指南](https://developers.openai.com/api/docs/guides/latest-model/gpt-6-astra.md)
- [Harness engineering](https://openai.com/index/harness-engineering/)
- [Testing Agent Skills Systematically with Evals](https://developers.openai.com/blog/eval-skills)

完整来源、核验日期、固定 Git 提交和本项目约定的区别见[来源清单](skills/build-agent-harness/references/openai-sources.md)。

## English

A Codex-first skill for creating, improving or auditing repository agent guidance from verified project facts, with thin Claude compatibility.

Full runs install the established AGENTS/CLAUDE/ARCHITECTURE baseline and canonical PLANS.md. Focused changes stay within requested surfaces; audit-only runs do not write. These file and outline conventions belong to this project, not to OpenAI's model requirements.

The GPT-6.1 Sol / GPT-6 Astra refresh uses live official guidance reviewed on 2026-09-30: precise discovery, progressive disclosure, authorization continuity, explicit completion, proportionate verification and conditional delegation. Keep durable instructions shared and compare models with fixed tasks and settings. This repository does not claim measured model improvements.

### Install and invoke

Use the installation commands above for `~/.agents/skills/build-agent-harness`; use `.agents/skills/build-agent-harness` for repository-local discovery. Preserve local customizations when replacing an older installation and check for duplicates in legacy locations. Restart Codex if discovery does not refresh.

```text
$build-agent-harness Audit and optimize this repository's harness.
$build-agent-harness Update only the existing model-migration guidance.
```

### Maintenance

Run `validate-skill` and the standard-library regression suite using the commands above. The package validator checks Markdown and basic entrypoint metadata without applying repository baseline rules. It does not validate runtime behavior or model quality.

See the [migration guide](skills/build-agent-harness/references/model-migration.md), [evaluation protocol](skills/build-agent-harness/references/evaluation.md), and [official source ledger](skills/build-agent-harness/references/openai-sources.md).

### License

MIT
