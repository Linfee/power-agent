<!-- verified: 2026-03-20 -->
<!-- scope: system-design -->

# Harness Engineering 体系设计

基于 OpenAI Harness Engineering 实践构建的 Agent 驱动开发体系。核心理念：**人类掌舵，Agent 执行**——人类的职责是设计意图、构建反馈循环，Agent 负责执行闭环。

**原始参考：** [Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/) — Ryan Lopopolo, OpenAI, Feb 11, 2026

---

## 设计哲学

### 三个核心原则

**1. 仓库即唯一真相来源（Repo as SSOT）**
所有知识必须版本化、存储在仓库中。Agent 看不到的东西等同于不存在。架构决策写在 Slack 里、口头约定的规范、只存在聊天记录中的"为什么这样设计"——这些信息对 Agent 而言完全不可见。

**2. 目录式上下文（Context as Map, Not Encyclopedia）**
`AGENTS.md` 控制在 ~150 行，是一张**地图**而非百科全书。具体知识下沉到 `docs/` 的结构化文件中。当所有事情都标为重要，就没有什么重要。

**3. 机械化约束优于 Prompt 啰嗦**
核心规范靠 Linter/Test 强制执行，而非在 Prompt 中写 50 条"你应该如何写代码"。Linter 错误信息对 Agent 友好，含直接可执行的修复建议。

---

## 知识库结构

```
docs/
├── harness-engineering.md       # 本文档：体系设计与参考
├── design-decisions/            # 设计决策记录
│   └── index.md                 # 决策索引（带验证状态）
└── exec-plans/                  # 执行计划
    ├── active/                  # 进行中
    └── completed/               # 已归档
```

扩展目录（按项目需要裁剪）：

```
docs/
├── architecture.md              # 系统架构：模块划分、层级依赖、数据流
├── development.md               # 开发指南：环境搭建、构建命令、调试
├── domain/                      # 领域专项文档（前端/安全/API 等）
│   └── [domain-name].md
└── references/                  # 外部参考（llms.txt 等）
```

**文档元信息（所有文档必须包含）：**
```markdown
<!-- verified: YYYY-MM-DD -->
<!-- scope: [architecture|frontend|backend|security|...] -->
<!-- status: accepted | proposed | superseded -->  <!-- 仅设计决策 -->
```

---

## 体系组件

### Commands（引导式工作流）

Commands 是高层级工作流编排器，定义人与 Agent 协作的**交互协议**。

#### `/feature-dev` — 功能开发

八阶段引导式开发流程，确保在动手写代码之前充分理解问题：

| 阶段 | 目标 | 关键动作 |
|------|------|----------|
| 1. 发现 | 理解要构建什么 | 加载 AGENTS.md 和相关 docs/，澄清需求 |
| 2. 代码库探索 | 理解现有代码和模式 | 并行启动 2-3 个 `explore` 子代理 |
| 3. 澄清性问题 | 填补空白，解决歧义 | 分批提问，附带推荐方案和理由 |
| 4. 架构设计 | 设计多个实现方案 | 并行启动 2-3 个 `code-architect` 子代理 |
| 5. 规划（按需） | 创建可追踪的执行计划 | `>5 文件变更` 时创建 exec-plan |
| 6. 实现 | 构建功能 | exec-plan → `exec-plan-runner`；简单特性直接实现 |
| 7. 质量审查 | 确保代码质量 | 并行 3 个 `code-reviewer` 子代理 |
| 8. 总结与文档同步 | 知识回流 | 更新 architecture.md / design-decisions/ |

**关键设计决策：** 用户在**阶段 4** 选定架构方案后才开始实现；实现前必须等待明确的用户批准（阶段 6）。

#### `/pr-discuss` — 需求讨论（已由 `discuss` skill 升级）

不写代码，专注于分析和讨论。适合在开始功能开发前评估可行性。推荐直接使用 `discuss` skill 获得完整的设计探索能力。

---

### Skills（专项能力）

Skills 是可复用的专项执行单元，被 Commands 或直接调用。

#### `discuss` — 需求探索与设计讨论

在实现之前，通过结构化对话将模糊需求变为经过评审的 spec 文档。融合了 brainstorming 设计探索工作流。

**核心能力：**
- **HARD-GATE**：spec 批准前绝不写代码
- **分批提问**：无依赖的问题合并同批，有顺序依赖的拆分多批（不强制一问一答）
- **强制 2-3 方案对比**：每次都呈现方案权衡与推荐
- **Spec 双重 gate**：自动 reviewer（`tech-plan-reviewer`）审查 + 用户确认
- **Visual Companion**：可选浏览器伴侣，展示线框图/架构图/设计对比
- **规模检查**：自动识别过大需求并建议拆分为子项目

**输出：** `docs/specs/YYYY-MM-DD-<topic>.md`（已通过审查，status: accepted）

**交棒：** 完成后建议 `/feature-dev [topic]`；如果架构已足够清晰可直接用 `writing-plans` skill 创建实现计划

#### `init-harness-engineering` — 项目初始化

为新项目（或已有项目）建立完整的 Harness Engineering 知识体系。

**四个执行阶段：**

```
Phase 1: 项目扫描    → 并行 2-3 个 explore 子代理
Phase 2: 构建 docs/  → 按扫描结果裁剪，创建必要文档
Phase 3: 生成 AGENTS.md → 目录式结构，≤150 行
Phase 4: 验证        → 检查行数、指针有效性、命令可执行性
```

**触发场景：**
- 新项目第一次接入 Agent 工作流
- 已有项目文档散乱，需要重组为 Harness 结构
- AGENTS.md 过大（>200行），需要拆分

#### `dev-docs` — 开发文档管理

识别文档类型并路由到对应流程。收到 exec-plan 请求时委派给 `writing-plans` skill；其他类型直接创建。

| 类型 | 触发关键词 | 处理方式 |
|------|-----------|---------|
| exec-plan | 计划/重构/迁移/实现/spec | → **委派给 `writing-plans` skill** |
| architecture | 架构/模块/系统/组件 | `docs/architecture.md` 或 `docs/domain/` |
| design-decision | 决策/选型/方案/权衡/DD | `docs/design-decisions/DD-NNN-title.md` |
| domain | 前端/安全/API/数据库 | `docs/domain/[name].md` |
| development | 开发/搭建/环境/命令 | `docs/development.md` |
| reference | 参考/外部/集成/第三方 | `docs/references/[name].md` |

非 exec-plan 文档：启动 `explore` 子代理分析相关代码 → 按模板撰写 → 更新 `AGENTS.md` 导航。

#### `writing-plans` — 实现计划创建

将设计或 spec 拆解为 **agent 可直接执行的细粒度任务**（TDD 结构，含完整代码片段和精确命令）。由 `dev-docs` 委派或直接调用。

| 规模 | 输出 |
|------|------|
| 小任务（单模块） | 单文件 `docs/exec-plans/active/YYYY-MM-DD-title.md` |
| 大需求（跨多模块） | 目录 `docs/exec-plans/active/YYYY-MM-DD-title/`（README + design + tasks + decisions） |

任务粒度：TDD 结构（写测试→验证失败→实现→验证通过→commit），每步 2-5 分钟，含完整代码和可执行命令。

**计划审查循环：** 写完后 dispatch `tech-plan-reviewer` 子代理审查（最多 3 轮）。

**执行交棒：** 审查通过后建议 `exec-plan-runner`（推荐）或内联执行。

#### `dev-docs-maintain` — 文档维护（Doc Gardening）

定期扫描 docs/ 知识库，对照代码现状识别过期内容并修复。

**健康检查维度：**

| 检查项 | 阈值 |
|--------|------|
| AGENTS.md 行数 | ≤ 200 行 |
| 文档新鲜度（verified 时间戳） | >30天 → ⚠️，>90天 → ❌ |
| 导航指针有效性 | 必须指向实际存在的文件 |

**修复优先级：**
- **P0**（立即修复）：错误命令、不存在的模块引用——会直接误导 Agent
- **P1**（当次修复）：新增模块未记录、新约定未文档化
- **P2**（记录 TODO）：格式不统一、缺少 Mermaid 图

**建议运行时机：** 每次重大功能完成后、exec-plan 归档时。

#### `exec-plan-runner` — 执行计划驱动实现

自主执行 exec-plans/active/ 中的计划。**主代理只做规划编排，绝不自己写代码；所有实现由一次性子代理完成。**

**核心机制：**

```
Step 1: 加载 exec-plan → 依赖分析 → 划分 batch
Step 2: 逐批并行启动实现子代理（每任务一个，最多 3 并行）
        子代理必须使用 test-driven-development skill
Step 3: 批次后并行启动代码审查子代理（规格符合性 + 代码质量两阶段）
Step 4: 有问题 → 启动新修复子代理（不重用旧子代理）
Step 5: 更新 exec-plan 进度
Step 6: 循环直到完成 → 启动验证子代理（verification-before-completion skill）
```

**恢复模式：** 有已完成标记（`[x]`）时，先验证已完成产出有效，再从中断点继续。

**Escalation（停止，向用户请示）：**
- 任务歧义且解读差异 ≥ 2x
- 需要 exec-plan 未预期的破坏性变更
- 修复子代理反复失败（3 轮）
- exec-plan 前提假设不成立

#### `systematic-debugging` — 系统化调试

遇到 bug、测试失败或意外行为时使用。四阶段流程，在修复前找到根本原因。

**铁律：** 没有根本原因调查就没有修复。3+ 次修复失败 → 质疑架构，不要继续修症状。

| 阶段 | 核心动作 |
|------|---------|
| 1. 根本原因 | 读错误信息、稳定复现、检查最近变更、多组件系统添加诊断、追踪数据流 |
| 2. 模式分析 | 找同类工作代码、完整阅读参考实现、列出所有差异 |
| 3. 假设验证 | 形成单一假设、最小化测试、确认或证伪 |
| 4. 实现 | 先写失败测试（TDD）、单一修复、验证通过 |

**支撑文件（skill 目录中可用）：** `root-cause-tracing.md`、`condition-based-waiting.md`、`defense-in-depth.md`、`find-polluter.sh`

#### `harness-engineering-review` — 实践审查

审查项目是否符合 Harness Engineering 最佳实践，输出评分和改进建议。

**六个审查维度：**

| 维度 | 核心问题 |
|------|----------|
| AGENTS.md 结构 | 是否超过 150 行？是否堆砌了百科全书式内容？ |
| Agent 可见性 | 重要决策是否在仓库中版本化？ |
| 约束机制化 | 规范是靠 Linter/Test 还是靠 Prompt 口头约定？ |
| 反馈循环质量 | Agent 能否自运行应用、捕获错误、验证修复？ |
| 知识维护 | 是否有机制防止文档腐化？ |
| 技术债管理 | 是否有"黄金原则"防止模式漂移？ |

---

## 标准工作流

### 新项目接入

```
/init-harness-engineering [关注点]
    ↓
parallel: explore × 2-3（扫描项目结构）
    ↓
构建 docs/ 知识库
    ↓
生成 AGENTS.md（目录式，≤150行）
    ↓
验证（行数、指针、命令可执行性）
```

### 功能开发生命周期

```
discuss skill [需求]        ← 可选：设计探索，产出经过审查的 spec
    ↓（spec 批准后）
/feature-dev [功能描述]
    ├── Phase 1-3: 理解与澄清（人类确认）
    ├── Phase 4: 架构设计（人类选方案）
    ├── Phase 5: exec-plan 创建（dev-docs skill）
    ├── Phase 6: exec-plan-runner 执行
    ├── Phase 7: 代码审查（code-reviewer × 3）
    └── Phase 8: 文档同步（dev-docs-maintain skill）
```

### 调试路径

```
遇到 bug / 测试失败 / 意外行为
    ↓
systematic-debugging skill
    ├── 阶段 1-3: 根本原因调查（不允许跳过）
    └── 阶段 4: 实现修复
        ├── test-driven-development skill（先写失败测试）
        └── verification-before-completion skill（验证修复）
```

### 文档维护循环

```
重大功能完成 / exec-plan 归档
    ↓
/dev-docs-maintain [聚焦范围]
    ├── 健康检查（结构完整性 + 新鲜度）
    ├── 代码对照验证（explore 子代理）
    ├── P0/P1 修复
    └── 归档已完成的 exec-plan
```

---

## 设计决策记录格式

```markdown
<!-- verified: YYYY-MM-DD -->
<!-- scope: [涉及范围] -->
<!-- status: accepted | proposed | superseded -->

# DD-NNN: [决策标题]

## 背景
[为什么需要做这个决策？当前痛点是什么？]

## 约束
[必须满足的硬性条件]

## 方案对比
| 方案 | 优势 | 劣势 | 复杂度 |
|------|------|------|--------|
| A: ... | ... | ... | S/M/L |
| B: ... | ... | ... | S/M/L |

## 决定
[选择了哪个方案，为什么]

## 后果
[这个决策带来的影响和需要注意的事项]
```

---

## 反模式识别

| 反模式 | 问题 | 正确做法 |
|--------|------|----------|
| 巨型 AGENTS.md | 上下文拥挤，重点丢失，极易腐化 | 目录式 AGENTS.md + docs/ 分层 |
| 口头架构决策 | Agent 不可见，新成员无法入职 | 每次重大决策后立即写入 docs/ |
| Prompt 规范啰嗦 | Agent 难以执行，无验证机制 | 转化为 Linter 规则 + 测试 |
| 跳过文档同步 | 文档腐化，误导后续 Agent | Phase 8 强制文档同步 |
| 并行有依赖的任务 | 产生冲突，结果不可预期 | exec-plan-runner 依赖分析 |
| 未验证就声称完成 | 产生 AI slop | 验证原则：未运行命令不得声称通过 |

---

## 快速参考

| 场景 | 使用 |
|------|------|
| 新项目建立知识体系 | `init-harness-engineering` skill |
| 讨论需求可行性 | `discuss` skill |
| 开发新功能 | `/feature-dev [功能描述]` |
| 创建实现计划（exec-plan） | `writing-plans` skill（或通过 `dev-docs` 委派） |
| 创建架构/决策等其他文档 | `dev-docs` skill |
| 执行已有 exec-plan | `exec-plan-runner` skill |
| 遇到 bug / 测试失败 | `systematic-debugging` skill |
| 维护/更新文档 | `dev-docs-maintain` skill |
| 审查项目 Harness 实践 | `harness-engineering-review` skill |
