# 工作机制与 Skill 协调

本文档描述 power-agent 的完整工作机制：各 Skill 的职责边界、产出物、以及它们之间如何协调。

---

## 核心设计原则

**Skill 是执行单元，人类是决策者。** 每个 Skill 只做一件事，通过明确的输入/输出协议与其他 Skill 协作。Agent 在关键 gate 点停下来等待人类决策，绝不在批准前推进。

**产出物是协调介质。** Skill 之间不直接调用彼此——它们通过写入仓库文件来"传话"：spec 文档、exec-plan 文件、代码、docs/ 文档。下一个 Skill 读取这些产出物作为输入。

---

## 完整工作流图

```
┌─────────────────────────────────────────────────────────┐
│                    需求阶段                             │
│                                                         │
│   discuss skill                                         │
│   输入：模糊需求                                           │
│   产出：docs/specs/YYYY-MM-DD-<topic>.md                 │
│   gate：spec 经 spec-reviewer 审查 + 用户批准              │
└─────────────────────┬───────────────────────────────────┘
                      │ spec 文档（或用户直接描述功能）
                      ▼
┌─────────────────────────────────────────────────────────┐
│                 功能开发阶段                               │
│                                                         │
│   feature-dev skill（薄编排层）                            │
│   ├── 阶段 1-3：上下文 + 探索 + 澄清                        │
│   │   工具：explore 子代理 × 2-3（并行）                    │
│   │   gate：所有关键问题得到回答                             │
│   │                                                     │
│   ├── 阶段 4：架构设计                                     │
│   │   工具：code-architect 子代理 × 2-3（并行）             │
│   │   gate：用户选定方案 ✋                                 │
│   │                                                     │
│   ├── 阶段 5：规划（>5 文件时）                             │
│   │   → writing-plans skill                             │
│   │                                                     │
│   ├── 阶段 6：实现                                        │
│   │   gate：用户明确批准 ✋                                 │
│   │   → exec-plan-runner skill                          │
│   │                                                     │
│   ├── 阶段 7：质量审查                                     │
│   │   → requesting-code-review skill                    │
│   │                                                     │
│   └── 阶段 8：文档同步                                     │
│       → dev-docs-maintain skill                         │
└─────────────────────────────────────────────────────────┘

调试路径（独立入口）：
   systematic-debugging skill
       └── → test-driven-development skill
               └── → verification-before-completion skill
```

---

## 各 Skill 详解

### discuss — 设计探索

**触发：** 需求模糊、有多种可行方案、风险较高的架构决策。

**输入：** 用户的文字描述（任意格式）

**核心流程：**
1. 批量澄清问题（按主题分批，不一问一答）
2. 强制呈现 2-3 个方案对比，含权衡和推荐
3. 产出 spec 草稿
4. 启动 `tech-plan-reviewer` 子代理审查（最多 3 轮）
5. 用户确认 → spec 状态标记为 `accepted`

**产出：** `docs/specs/YYYY-MM-DD-<topic>.md`

**交棒给：** `feature-dev` skill 或 `writing-plans` skill（如果架构已足够清晰）

**不做：** 不写任何代码，不创建 exec-plan。spec 未批准前的任何实现动作均被 HARD-GATE 阻止。

---

### feature-dev — 功能开发编排

**触发：** 开始开发一个新功能。

**输入：** 功能描述（字符串）或已批准的 spec 文档路径

**本 Skill 不执行任何具体工作** —— 它只是编排层，负责：
- 确定当前处于哪个阶段
- 在 gate 点等待人类决策
- 将具体工作委派给对应 Skill

**阶段协调逻辑：**

```
已有 spec 文档？
├── 是 → 加载 spec，跳过阶段 1 直接到阶段 2
└── 否 → 阶段 1：加载 AGENTS.md + 相关 docs，澄清需求

阶段 2：并行 explore 子代理（理解现有代码）
阶段 3：澄清性问题（分批）

gate ✋ 阶段 3 结束后等待用户确认

阶段 4：并行 code-architect 子代理 → 呈现方案对比

gate ✋ 等待用户选择方案

预估变更 > 5 个文件？
├── 是 → 阶段 5：writing-plans skill 创建 exec-plan
└── 否 → 跳过阶段 5

gate ✋ 阶段 6 开始前等待用户明确批准

阶段 6：exec-plan-runner skill（或直接实现）
阶段 7：requesting-code-review skill
阶段 8：dev-docs-maintain skill
```

**关键设计决策：** 两个人工 gate（选方案、批准实现）是故意的强制停顿，防止 Agent 在没有人类确认的情况下推进到破坏性操作。

---

### writing-plans — 实现计划创建

**触发：** `feature-dev` 阶段 5 委派，或用户直接要求创建 exec-plan，或 `dev-docs` skill 路由。

**输入：** spec 文档 + 选定的架构方案 + 已有的代码库上下文

**核心流程：**
1. 读取 spec 和相关代码文件（利用 `feature-dev` 阶段 2 已建立的上下文）
2. 拆解为 TDD 结构任务（每步 2-5 分钟）
3. 每个任务包含：完整代码片段 + 精确命令 + 验证步骤
4. 启动 `tech-plan-reviewer` 子代理审查（最多 3 轮）
5. 提供执行选项（推荐 `exec-plan-runner`）

**产出：**
- 小任务：`docs/exec-plans/active/YYYY-MM-DD-title.md`
- 大需求：`docs/exec-plans/active/YYYY-MM-DD-title/`（含 README + design + tasks）

**任务格式（每个任务）：**
```markdown
### Task N: [任务名称]

**目标：** [一句话说明]

**测试（先写）：**
```[lang]
[完整测试代码]
```

**实现：**
```[lang]
[完整实现代码]
```

**验证：**
```bash
[可执行命令]
```
```

**交棒给：** `exec-plan-runner` skill

---

### exec-plan-runner — 计划执行

**触发：** 有已创建的 exec-plan，需要执行。

**输入：** `docs/exec-plans/active/` 中的计划文件

**核心架构：主代理只做编排，绝不自己写代码。**

```
Step 1: 读取 exec-plan → 分析任务依赖关系
Step 2: 划分 batch（可并行的任务一批）
Step 3: 每个 batch：
        a) 并行启动实现子代理（每任务一个，最多 3 并发）
           子代理使用 test-driven-development skill
        b) 等待所有子代理返回
        c) 并行启动审查子代理（两阶段）：
           - 规格符合性审查（spec-reviewer-prompt.md）
           - 代码质量审查（code-quality-reviewer-prompt.md）
        d) 发现问题 → 启动新修复子代理（不重用旧子代理）
Step 4: 更新 exec-plan 进度标记
Step 5: 循环 Step 3-4 直到所有任务完成
Step 6: 启动验证子代理（verification-before-completion skill）
```

**子代理是一次性的：** 主代理不与同一子代理进行多轮对话。每次需要修复都启动一个新的子代理，将问题描述和上下文完整传入。

**并行调度规则：**
- 修改同一文件的任务 → 有依赖，串行
- 操作不同模块且无数据依赖 → 可并行（最多 3 并发）
- 不确定时 → 视为有依赖（安全优先）

**恢复模式：** exec-plan 中有 `[x]` 标记时，先验证已完成产出有效，再从中断点继续。

**Escalation（停止，等待人类）：**
- 任务歧义且解读差异 ≥ 2x
- 需要 exec-plan 未预期的破坏性变更
- 修复子代理反复失败（3 轮）

---

### dev-docs — 文档路由器

**触发：** 需要创建任何类型的 docs/ 文档。

**核心逻辑：识别类型 → 路由。**

```
用户请求
├── exec-plan 类型（计划/重构/迁移/实现）
│   └── 委派给 writing-plans skill，原始需求完整传递
└── 其他类型 → 直接处理
    ├── architecture → docs/architecture.md 或 docs/domain/
    ├── arch-decision → docs/arch-decisions/DD-NNN-title.md
    ├── domain → docs/domain/[name].md
    ├── development → docs/development.md
    └── reference → docs/references/[name].md
```

非 exec-plan 文档流程：
1. 启动 `explore` 子代理分析相关代码
2. 按模板撰写文档（含 `<!-- verified: YYYY-MM-DD -->` 元信息）
3. 更新 AGENTS.md 导航指针

**关键职责：** dev-docs 确保文档类型路由正确，但不重复 writing-plans 的计划创建逻辑。

---

### systematic-debugging — 系统化调试

**触发：** 遇到 bug、测试失败、意外行为。独立入口，不经过 feature-dev。

**铁律：** 没有根本原因分析就没有修复。随机尝试修复是反模式。

**四阶段协调：**

```
阶段 1：根本原因调查（必须完成才能继续）
├── 读错误信息（完整，含堆栈）
├── 稳定复现（不可复现 → 收集更多数据）
├── 检查最近变更（git diff、新依赖）
└── 多组件系统：在每层边界添加诊断日志，一次运行收集数据

阶段 2：模式分析
├── 找同类正常工作的代码
└── 列出工作代码与损坏代码的所有差异

阶段 3：假设验证
├── 形成单一具体假设（写下来）
└── 最小化测试（一次一个变量）

阶段 4：实现修复
├── → test-driven-development skill（先写失败测试）
├── 单一修复（不捆绑重构）
└── → verification-before-completion skill（验证）

失败次数 ≥ 3？
└── 停止，质疑架构，不要继续修症状
```

**支撑文件：**
- `root-cause-tracing.md` — 向后追踪调用栈定位原始触发器
- `condition-based-waiting.md` + `condition-based-waiting-example.ts` — 替换任意超时
- `defense-in-depth.md` — 在根本原因之上多层防御
- `find-polluter.sh` — 定位测试污染来源

---

### test-driven-development — TDD 执行

**触发：** 实现任何功能前（由 exec-plan-runner 子代理或 systematic-debugging 触发）。

**流程：**
```
RED：写一个失败的测试（针对要实现的行为）
     ↓ 运行验证失败（不跳过这步）
GREEN：写最少的代码让测试通过
     ↓ 运行验证通过
REFACTOR：清理，保持测试通过
     ↓ commit
```

**与 exec-plan-runner 的协调：** exec-plan-runner 的实现子代理接收到任务时，任务描述中包含完整的测试代码（writing-plans 已写好），子代理直接从 RED 阶段开始。

**反模式参考：** `testing-anti-patterns.md`（5 类常见 TDD 反模式）

---

### requesting-code-review — 代码审查编排

**触发：** feature-dev 阶段 7（实现完成后），或手动发起审查。

**流程：**
1. 收集代码变更上下文（diff、相关文件、功能背景）
2. 启动 `code-reviewer` 子代理（按 `code-reviewer.md` 模板）
3. 汇总发现，按严重程度分级（P0/P1/P2）
4. 呈现给用户，等待处理决策

**与 exec-plan-runner 的区别：** exec-plan-runner 内部有自己的代码审查循环（规格符合性 + 代码质量），针对每个 batch 的实现。`requesting-code-review` 是面向整个功能的全量代码审查，发生在实现完成之后。

---

### verification-before-completion — 完成前验证

**触发：** 任何声称"完成"之前，由 systematic-debugging 阶段 4 或 exec-plan-runner 最终步骤触发。

**核心规则：**
- 没有运行验证命令 → 不得声称测试通过
- 没有截图/输出 → 不得声称 UI 正常
- 没有 lint 输出 → 不得声称无错误
- 验证必须是新鲜的（本次 session 运行的），不接受"之前运行过"

**与其他 Skill 的关系：** 这是工作流的最终 gate，任何 Skill 在声称完成时都应触发此 Skill 的原则（即便不显式调用，也应遵循其规则）。

---

### dispatching-parallel-agents — 并行调度

**触发：** 有 2 个以上相互独立、无共享状态的任务需要同时处理。

**调度规则：**
```
任务 A 和任务 B 相互独立？
├── 是（不同文件、不同模块、无数据依赖）→ 并行启动
└── 否（共享文件、有顺序依赖）→ 串行

并发上限：3 个（超过分批排队）
```

**与 exec-plan-runner 的区别：** exec-plan-runner 内联了并行调度逻辑（专用于 exec-plan 执行上下文）。`dispatching-parallel-agents` 是通用的并行调度 Skill，用于 exec-plan 之外的场景（如 feature-dev 阶段 2 并行探索、阶段 4 并行架构设计）。

---

### dev-docs-maintain — 文档维护

**触发：** 重大功能完成后，或 exec-plan 归档时（feature-dev 阶段 8）。

**健康检查维度：**
```
结构完整性：
├── AGENTS.md 行数 ≤ 200
├── 所有导航指针指向实际存在的文件
└── exec-plans/completed 已归档完成的计划

新鲜度（verified 时间戳）：
├── > 30 天 → ⚠️ 需要验证
└── > 90 天 → ❌ 需要修复

内容准确性（对照代码）：
└── 启动 explore 子代理验证文档描述与代码现状是否一致
```

**修复优先级：**
- **P0**（立即）：错误命令、不存在的模块引用
- **P1**（当次）：新增模块未记录、新约定未文档化
- **P2**（记录 TODO）：格式不统一、缺少图表

---

### init-harness-engineering — 项目初始化

**触发：** 新项目首次接入，或已有项目文档混乱需要重组。

**流程：**
```
Phase 1: 并行 explore 子代理 × 2-3，扫描项目结构
         ├── 技术栈、框架、构建工具
         ├── 现有文档（README、CHANGELOG、注释）
         └── 代码结构、模块边界、测试方式

Phase 2: 构建 docs/ 知识库
         按项目复杂度裁剪，创建必要文档

Phase 3: 生成 AGENTS.md
         精简结构，≤ 200 行，指针指向 docs/

Phase 4: 验证
         行数检查 + 指针有效性 + 命令可执行性
```

**产出：** 结构化的 `docs/` 目录 + `AGENTS.md`，建立完整的 Harness Engineering 知识体系。

---

### harness-engineering-review — 实践审查

**触发：** 需要评估项目 Agent 工作流质量，或作为定期健康检查。

**六个审查维度：**

| 维度 | 核心问题 |
|------|----------|
| AGENTS.md 结构 | 是否 ≤ 200 行？是否是目录而非百科全书？ |
| Agent 可见性 | 重要决策是否在仓库中版本化？ |
| 约束机制化 | 规范靠 Linter/Test 还是 Prompt 口头约定？ |
| 反馈循环质量 | Agent 能否自运行应用、捕获错误、验证修复？ |
| 知识维护 | 是否有机制防止文档腐化？ |
| 技术债管理 | 是否有"黄金原则"防止模式漂移？ |

---

## 产出物流转图

```
用户需求
    │
    ▼
docs/specs/*.md          ← discuss 产出
    │
    ▼
docs/exec-plans/active/  ← writing-plans 产出
    │
    ▼
代码变更（git diff）      ← exec-plan-runner 子代理产出
    │
    ▼
代码审查发现              ← requesting-code-review 产出
    │
    ▼
docs/ 更新               ← dev-docs-maintain 产出
    │
    ▼
docs/exec-plans/completed/ ← 归档
```

---

## 反模式

| 反模式 | 问题 | 正确做法 |
|--------|------|----------|
| 跳过 discuss，直接 feature-dev | 架构决策不充分，执行中反复返工 | 复杂需求先用 discuss |
| feature-dev 不等人工确认就推进 | Agent 在不正确方向上浪费资源 | 两个 gate（选方案、批准实现）必须停顿 |
| exec-plan-runner 主代理自己写代码 | 上下文污染，无法有效追踪 | 主代理只编排，所有实现交给子代理 |
| 重用子代理修复问题 | 子代理带着错误上下文继续工作 | 每次修复启动新子代理，完整传入问题描述 |
| 随机修复 bug | 掩盖根本原因，制造新问题 | systematic-debugging 四阶段，先找根因 |
| 未运行命令就声称完成 | AI 幻觉，产出 AI slop | verification-before-completion 的证据优先原则 |
| AGENTS.md 写成百科全书 | 上下文臃肿，重点丢失 | 精简 AGENTS.md + docs/ 分层 |
