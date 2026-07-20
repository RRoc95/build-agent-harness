# Build Agent Harness

面向 Codex、兼容 Claude Code 的仓库级 agent harness skill：基于真实工程证据生成或优化完整 harness，并安装不可项目化修改的标准 `PLANS.md`。

## 中文

### 主要能力

- 调研 Git 根目录、真实子工程、清单、脚本、CI、测试、入口和部署边界。
- 生成精简的根 `AGENTS.md`，并只在真实子工程边界创建嵌套 `AGENTS.md`；新建和优化时统一标题、章节语义、顺序和收尾结构。
- 为每个可独立构建或运行的工程强制补齐 `ARCHITECTURE.md`；统一采用 `ARCHITECTURE.md — …` 标题、连续编号章节和最终“验证”章节，纯聚合根不创建该文档。
- 始终生成薄 `CLAUDE.md`，通过 `@AGENTS.md` 复用 Codex 主指令；不复制共享规则。
- 按工程需要补充 Coding Standards、Code Review 和 Verification Guide。
- 建立 `docs/exec-plans/` 生命周期，同时保留既有 active/completed 历史。
- 从 skill 资产原样安装统一 `PLANS.md`，并通过 SHA-256 检查缺失或漂移。
- 以 Codex 为主并默认兼容 Claude Code。
- 提供只读 `harness_audit.py`，检查必需根文档、AGENTS/ARCHITECTURE 格式契约、每个 AGENTS 边界的 Claude 文件、独立工程架构、Markdown、链接、skill 元数据、指令链大小和标准 `PLANS.md`。

### 仓库结构

```text
.
├── README.md
├── LICENSE
└── skills/
    └── build-agent-harness/
        ├── SKILL.md
        ├── agents/openai.yaml
        ├── assets/PLANS.md
        ├── references/
        └── scripts/harness_audit.py
```

### 安装到 Codex

```bash
git clone https://github.com/RRoc95/build-agent-harness.git
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills/build-agent-harness"
cp -R build-agent-harness/skills/build-agent-harness/. \
  "${CODEX_HOME:-$HOME/.codex}/skills/build-agent-harness/"
```

更新已有安装时，请整体替换目标 skill 目录，不要与旧版本合并。若 Codex 没有立即刷新 skill 列表，新建任务或重启 Codex。

### 使用

```text
$build-agent-harness 为当前工程生成符合 OpenAI 最佳实践的 agent harness，兼容 Claude Code
```

```text
$build-agent-harness 参照 /path/to/reference-repository 优化当前工程已有的 harness 文档
```

### 只读审计

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/build-agent-harness/scripts/harness_audit.py" \
  --root /path/to/repository inventory

python3 "${CODEX_HOME:-$HOME/.codex}/skills/build-agent-harness/scripts/harness_audit.py" \
  --root /path/to/repository validate \
  --project-boundary admin \
  --project-boundary server
```

审计器不会生成或修复文件。`validate` 的退出码为：

- `0`：结构与格式校验通过；
- `1`：发现结构或格式错误；
- `2`：输入或运行环境错误。

### 标准 PLANS.md

每个目标工程的根 `PLANS.md` 必须与 `skills/build-agent-harness/assets/PLANS.md` 完全一致。项目自己的计划触发条件和工作约束应放在 `AGENTS.md`，计划索引和本地生命周期说明应放在 `docs/exec-plans/README.md`。

### 设计依据

- [Using PLANS.md for multi-hour problem solving](https://developers.openai.com/cookbook/articles/codex_exec_plans)
- [GPT-5.6 prompt engineering guidance](https://developers.openai.com/api/docs/guides/prompt-engineering#coding)
- [Prompting best practices](https://developers.openai.com/api/docs/guides/latest-model#prompting-best-practices)

## English

`build-agent-harness` is a Codex-first skill for creating or improving repository agent harness documentation from verified project facts.

It can:

- create concise root and nested `AGENTS.md` files with a stable title, semantic outline, ordering, and completion shape;
- require consistently formatted, evidence-backed `ARCHITECTURE.md` at independently buildable or runnable project boundaries while leaving pure aggregation roots architecture-free;
- always create thin root and nested `CLAUDE.md` imports while keeping `AGENTS.md` canonical;
- create coding, review, verification, and execution-plan documentation;
- install one canonical, project-independent `PLANS.md`;
- preserve existing execution-plan history and user changes;
- provide Claude Code compatibility by default;
- audit harness structure and document style without modifying the repository.

### Install

```bash
git clone https://github.com/RRoc95/build-agent-harness.git
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills/build-agent-harness"
cp -R build-agent-harness/skills/build-agent-harness/. \
  "${CODEX_HOME:-$HOME/.codex}/skills/build-agent-harness/"
```

Replace the destination skill directory as a whole when upgrading. Start a new Codex task or restart Codex if skill discovery does not refresh immediately.

### Invoke

```text
$build-agent-harness Audit and optimize the agent harness for this repository.
```

### License

MIT
