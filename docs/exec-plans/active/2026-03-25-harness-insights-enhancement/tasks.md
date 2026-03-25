<!-- verified: 2026-03-25 -->
<!-- scope: skills, docs, scripts -->

# 任务列表

## Batch 1：Phase 1 核心流程加固（3 个任务并行）

### Task 1: exec-plan-runner SKILL.md + progress-log-template.md

**文件：**
- 修改: `skills/exec-plan-runner/SKILL.md`
- 创建: `skills/exec-plan-runner/progress-log-template.md`

**变更说明（来自 spec Phase 1.1 + 1.2 + 1.3 + Phase 2.2 + Phase 3.2）：**

- [ ] **Step 1: 读取当前文件**

  读取 `skills/exec-plan-runner/SKILL.md` 确认现有结构。

- [ ] **Step 2: 在 frontmatter 增加 version 字段**

  将 frontmatter 从：
  ```yaml
  ---
  name: exec-plan-runner
  description: ...
  ---
  ```
  改为：
  ```yaml
  ---
  name: exec-plan-runner
  description: ...
  version: 1.0.0
  ---
  ```

- [ ] **Step 3: 在 Step 1 之前插入 Bootstrap 章节**

  在 `## Step 1: 加载、恢复检测与分析` 之前插入：

  ```markdown
  ## Bootstrap（每次会话开始，无条件执行）

  在执行 Step 1 之前，强制完成以下序列：

  1. 读取 exec-plan 的 `## Session Log` section（如存在，了解上次进度）
  2. `git log --oneline -10`（确认工作树状态）
  3. 运行项目基本健康检查（lint + 核心测试套件）
  4. 若健康检查失败 → 先修复再继续，不在破损基线上工作
  5. 确认恢复点，输出一句话摘要（例："基线健康，从 Batch 2 Task D 恢复"）

  ---
  ```

- [ ] **Step 4: 更新 Step 1 恢复检测逻辑**

  在 Step 1 的"恢复检测"描述中，改为三者交叉验证：

  将：
  ```
  **恢复检测：** 扫描进度标记（`[x]` / `[ ]`）和"当前状态" section
  ```
  改为：
  ```
  **恢复检测：** 读取 Session Log → git log → exec-plan checkbox，三者交叉验证后确定恢复点
  ```

- [ ] **Step 5: 在 Step 2a 子代理 prompt 末尾增加输出粒度控制**

  在 Step 2a 的实现子代理 prompt 模板（`## 要求` section 之后）增加：

  ```markdown
  ## 输出粒度: detailed
  返回完整信息，包含文件列表、关键代码片段、命令输出、推理过程。
  ```

  在 Step 2b 的审查子代理 prompt 模板末尾，增加说明：

  ```markdown
  ## 输出粒度控制
  - 审查通过（无 Issues）时：使用 `concise` 粒度，只返回结论
  - 发现阻塞问题时：使用 `detailed` 粒度，返回完整问题描述和定位

  **concise：** 仅返回结论性信息。省略完整代码、完整命令输出、中间推理过程。
  **detailed：** 返回完整信息，包含文件列表、关键代码片段、命令输出、推理过程。
  ```

  在 Step 3 的验证子代理 prompt 模板末尾，增加：

  ```markdown
  ## 输出粒度: concise
  仅返回结论性信息：命令 + 退出码 + 简短结论。
  ```

- [ ] **Step 6: 更新 Step 2c 为 Session Log + 进度更新**

  将 Step 2c 标题和内容替换为：

  ```markdown
  ### 2c. 更新 Exec-Plan 进度与 Session Log

  每个 batch 完成后立即更新 exec-plan 文件：

  **1. 更新 checkbox 进度（`[x]`）**

  **2. 向 `## Session Log` section 追加一条记录（最新在最上方）：**

  参考模板格式：`skills/exec-plan-runner/progress-log-template.md`

  ```

- [ ] **Step 7: 精简 Escalation 规则**

  将 `## Escalation 规则（停止执行，向用户请示）` section 整体替换为：

  ```markdown
  ## Escalation 规则（唯一触发条件）

  **修复子代理反复失败（3 轮审查修复循环耗尽）且无法定位根因** → 停止执行，向用户请示。

  **无需 Escalate（自主处理）：**
  - 任务描述有歧义 → Agent 自主判断最合理解读
  - 需要引入破坏性变更 → worktree 沙盒已隔离，自主处理
  - exec-plan 前提假设局部不成立 → 记录到 Session Log，继续执行其余任务
  - 实现细节选择（库函数选择、命名等）
  - 可通过重试或换方向解决的临时失败
  - lint 警告修复
  ```

- [ ] **Step 8: 在 Step 5 归档后增加 Step 6 Eval 数据收集**

  在 `## Step 5: 归档` 之后追加：

  ```markdown
  ## Step 6: Eval 数据收集

  归档完成后，自动采集执行指标并写入 exec-plan 文件尾部：

  ```markdown
  <!-- eval: YYYY-MM-DD -->
  <!-- skill: exec-plan-runner -->
  <!-- skill-version: [从 frontmatter version 字段读取] -->
  <!-- project: [从 git remote URL 或目录名推断] -->

  ## Eval 记录
  - 任务完成率: N/N
  - Batch 数: N
  - 修复循环: N 次
  - Escalation: 0
  - 耗时: Nmin
  ```

  然后向用户提问：
  > 快速反馈：
  > 1. 整体效果？ [满意 / 一般 / 不满意]
  > 2. 备注？（可选，直接回车跳过）

  用户跳过时仍写入自动指标，标注 `feedback: skipped`。
  ```

- [ ] **Step 9: 创建 progress-log-template.md**

  创建 `skills/exec-plan-runner/progress-log-template.md`，内容：

  ````markdown
  # Session Log 模板

  每个 batch 完成后，在 exec-plan 文件的 `## Session Log` section 追加一条记录（最新在最上方）。

  ## 使用方式

  在 exec-plan 文件末尾（或 `## 进度` section 之后）添加：

  ```markdown
  ## Session Log
  <!-- 每个 batch 完成后追加一条，最新在最上方 -->

  ### [YYYY-MM-DD HH:MM] Batch N 完成
  - **已完成**: Task A (`path/to/file.py`), Task B (`path/to/other.py`)
  - **遇到的问题**: [描述 + 如何解决，或标注未解决]
  - **已验证假设**: [什么被证实/证伪]
  - **下一步**: Batch N+1，从 Task X 开始
  - **环境状态**: lint ✅ | tests ✅ (N passed) | build ✅
  ```
  ````

- [ ] **Step 10: 验证**

  读取修改后的 `skills/exec-plan-runner/SKILL.md`，确认：
  - frontmatter 含 `version: 1.0.0`
  - Bootstrap 章节存在于 Step 1 之前
  - Step 2c 包含 Session Log 更新指令
  - 实现/审查/验证子代理 prompt 均有输出粒度控制
  - Escalation section 精简为单一条件
  - Step 6 Eval 数据收集章节存在

  读取 `skills/exec-plan-runner/progress-log-template.md`，确认文件存在。

---

### Task 2: systematic-debugging SKILL.md

**文件：**
- 修改: `skills/systematic-debugging/SKILL.md`

**变更说明（来自 spec Phase 1.2 + Phase 3.2）：**

- [ ] **Step 1: 读取当前文件**

  读取 `skills/systematic-debugging/SKILL.md` 确认现有结构。

- [ ] **Step 2: 在 frontmatter 增加 version 字段**

  ```yaml
  ---
  name: systematic-debugging
  description: ...
  version: 1.0.0
  ---
  ```

- [ ] **Step 3: 在"四个阶段"之前插入环境健康检查**

  在 `## 四个阶段（必须按顺序完成）` 之前插入：

  ```markdown
  ## 环境健康检查（调试开始前）

  在进入阶段 1 之前：

  1. 确认当前代码能编译 / 能运行基本测试套件
  2. 若基础测试已有失败（非目标 bug 引起）→ 记录这些已知问题，与目标 bug 区分，避免干扰根因判断
  3. 若无法编译 → 先修复编译错误再开始调试

  **目的：** 确保调试环境基线健康，防止在已有故障干扰下误判根因。

  ---
  ```

- [ ] **Step 4: 在文件末尾追加 Eval 数据收集章节**

  在文件末尾（`## 常见合理化借口` 之后）追加：

  ```markdown
  ---

  ## Eval 数据收集（调试完成后）

  调试成功结束时，写入调用方的 exec-plan 或当前上下文记录：

  ```
  <!-- eval: YYYY-MM-DD -->
  <!-- skill: systematic-debugging -->
  <!-- skill-version: 1.0.0 -->
  - 假设验证轮数: N 轮（每次进入阶段 3 计 1 轮）
  - 修复尝试次数: N 次
  - 是否升级为架构问题: Y/N
  ```

  向用户提问：
  > 快速反馈：
  > 1. 调试效果？ [满意 / 一般 / 不满意]
  > 2. 备注？（可选，直接回车跳过）
  ```

- [ ] **Step 5: 验证**

  读取修改后的文件，确认：
  - frontmatter 含 `version: 1.0.0`
  - 环境健康检查章节存在于四个阶段之前
  - Eval 数据收集章节存在于文件末尾

---

### Task 3: feature-dev SKILL.md

**文件：**
- 修改: `skills/feature-dev/SKILL.md`

**变更说明（来自 spec Phase 2.1 + Phase 3.2）：**

- [ ] **Step 1: 读取当前文件**

  读取 `skills/feature-dev/SKILL.md` 确认现有结构。

- [ ] **Step 2: 在 frontmatter 增加 version 字段**

  ```yaml
  ---
  name: feature-dev
  description: ...
  version: 1.0.0
  ---
  ```

- [ ] **Step 3: 将阶段 6 的强制 Gate 弱化为启动通知**

  将：
  ```markdown
  ## 阶段 6：实现

  **Gate：未经用户明确批准不得开始。**

  - 有 exec-plan → 使用 `exec-plan-runner` skill 执行；exec-plan-runner 会自行建立 worktree 隔离环境并在完成后处理分支收尾，无需 feature-dev 介入
  - 无 exec-plan（简单特性）→ 遵循选定架构直接实现，运行 lint/test 验证
  ```
  改为：
  ```markdown
  ## 阶段 6：实现

  **启动通知（轻量确认，非审批 Gate）：**

  呈现：
  > "Exec-plan 已就绪（N 个任务，预计 M 个 batch）。开始执行？"

  用户确认后进入自主执行。阶段 6-8 为 Agent 闭环，仅在 3 轮修复失败时 escalate。

  - 有 exec-plan → 使用 `exec-plan-runner` skill 执行；exec-plan-runner 会自行建立 worktree 隔离环境并在完成后处理分支收尾，无需 feature-dev 介入
  - 无 exec-plan（简单特性）→ 遵循选定架构直接实现，运行 lint/test 验证
  ```

- [ ] **Step 4: 在阶段 8 之后追加阶段 9 Eval 数据收集**

  在 `## 阶段 8：总结与文档同步` 末尾之后追加：

  ```markdown
  ---

  ## 阶段 9：Eval 数据收集

  文档同步完成后，自动采集指标：

  ```
  <!-- eval: YYYY-MM-DD -->
  <!-- skill: feature-dev -->
  <!-- skill-version: 1.0.0 -->
  - 是否使用 exec-plan: Y/N
  - Gate 等待次数: N（spec 批准 + 方案选择各计 1）
  - 修复循环次数: N
  - Escalation 次数: N
  ```

  向用户提问：
  > 快速反馈：
  > 1. 整体效果？ [满意 / 一般 / 不满意]
  > 2. 备注？（可选，直接回车跳过）
  ```

- [ ] **Step 5: 验证**

  读取修改后的文件，确认：
  - frontmatter 含 `version: 1.0.0`
  - 阶段 6 描述为"启动通知"而非"Gate"
  - 阶段 9 Eval 章节存在

---

## 前置准备（Batch 2 开始前执行）

- [ ] **Pre: 创建 scripts/ 目录**

  ```bash
  mkdir -p /Users/linfee/dev/workspace/ai-skills/power-agent/scripts
  ```

---

## Batch 2：Phase 2 Gate 重构 + 审查自动化（3 个任务并行）

### Task 4: DD-006 创建 + DD-005 状态更新 + index 更新

**文件：**
- 创建: `docs/arch-decisions/DD-006-gate-restructuring.md`
- 修改: `docs/arch-decisions/DD-005-gate-mechanism.md`
- 修改: `docs/arch-decisions/index.md`

- [ ] **Step 1: 读取现有文件**

  读取 `docs/arch-decisions/DD-005-gate-mechanism.md` 和 `docs/arch-decisions/index.md`。

- [ ] **Step 2: 创建 DD-006-gate-restructuring.md**

  内容：

  ```markdown
  <!-- verified: 2026-03-25 -->
  <!-- scope: workflow, skills, gate-mechanism -->
  <!-- status: active -->

  # DD-006: Gate 机制重构

  **状态：** active（supersedes DD-005）
  **日期：** 2026-03-25
  **影响文件：** `skills/feature-dev/SKILL.md`, `skills/exec-plan-runner/SKILL.md`, `docs/workflow.md`, `docs/architecture.md`

  ## 决策

  将 Gate 从"关键决策点人工审批"重构为"规划阶段锁定方向 + 实现阶段 Agent 自主闭环"。

  ## 论据

  1. 方向偏离问题在规划阶段已解决——discuss 产出 spec、writing-plans 产出 exec-plan，方向在此锁定
  2. 破坏性操作由 worktree sandbox 物理隔离，最坏情况是丢弃 worktree
  3. 实现质量由 Agent-to-Agent 审查循环保障，发现问题比解决问题容易

  ## 三道防线模型

  ```
  1. 规划 Gate → 人类锁定方向与架构（discuss/feature-dev 阶段 3-4）
  2. Sandbox 隔离 → worktree 物理限制破坏范围
  3. Agent-to-Agent 审查 → 质量保障（风险分级 + 投票机制）

  Escalation 仅作兜底：审查修复循环耗尽（3轮）后才触发
  ```

  ## Gate 对比

  | Gate 点 | DD-005 | DD-006 |
  |---------|--------|--------|
  | discuss spec 批准 | 强制等待 | **保留** — 规划 Gate |
  | feature-dev 阶段 3 澄清确认 | 强制等待 | **保留** — 规划 Gate |
  | feature-dev 阶段 4 架构选择 | 强制等待 | **保留** — 规划 Gate |
  | feature-dev 阶段 6 实现前 | 强制等待 | **弱化为启动通知** |
  | exec-plan-runner escalation | 歧义/破坏性/3轮失败 | **仅 3 轮失败时触发** |

  ## 影响

  - `feature-dev` 阶段 6：强制 Gate → 轻量启动通知
  - `exec-plan-runner`：Escalation 条件精简，只保留"3 轮修复失败"
  - Agent 在实现阶段有更大自主权，worktree 提供安全兜底
  ```

- [ ] **Step 3: 更新 DD-005 状态为 superseded**

  在 `docs/arch-decisions/DD-005-gate-mechanism.md` 文件顶部或状态行，增加：
  ```
  <!-- status: superseded by DD-006 (2026-03-25) -->
  ```
  并在文件中找到状态描述处（如有"状态："字段）改为 `superseded by DD-006`。

- [ ] **Step 4: 更新 index.md**

  读取 `docs/arch-decisions/index.md` 现有状态体系（`✅ 已验证`、`⚠️ 待验证`、`📋 提议中`），统一状态描述后：
  - 将 DD-005 条目标注为 `superseded by DD-006`（可保留原有 ✅ 符号并追加说明）
  - 追加 DD-006 条目：`DD-006-gate-restructuring.md` — Gate 机制重构，✅ active，2026-03-25
  - 在 index 状态说明处增加 `superseded` 含义说明（如不存在该状态词）

- [ ] **Step 5: 验证**

  确认三个文件均已正确更新，DD-006 路径在 index 中有对应条目。

---

### Task 5: requesting-code-review SKILL.md + risk-classification.md

**文件：**
- 修改: `skills/requesting-code-review/SKILL.md`
- 创建: `skills/requesting-code-review/risk-classification.md`

**变更说明（来自 spec Phase 2.3 + Phase 3.1）：**

- [ ] **Step 1: 读取当前文件**

  读取 `skills/requesting-code-review/SKILL.md`。

- [ ] **Step 2: 在 frontmatter 增加 version 字段**

  ```yaml
  ---
  name: requesting-code-review
  description: ...
  version: 1.0.0
  ---
  ```

- [ ] **Step 3: 在步骤 3 之前插入风险分级章节**

  在 `### 3. 启动审查子代理` 之前插入：

  ```markdown
  ### 2.5. 风险分级

  启动审查子代理前，评估本次变更的风险级别：

  | 级别 | 触发条件 | 审查行为 |
  |------|----------|----------|
  | 低风险 | 文档、测试、格式变更 | 单轮快速审查，通过即继续 |
  | 中风险 | 单模块逻辑变更 | 标准审查（规格符合性 + 代码质量） |
  | 高风险 | 跨模块 API 或数据模型变更 | 双重审查（2 个独立审查子代理） |

  **高风险双重审查规则：**
  - 并行启动 2 个独立审查子代理
  - 两者均通过 → 继续
  - 任一发现阻塞问题 → 进入修复循环（取更严格结论）
  - 所有级别均为 Agent 自主完成，不 escalate 给用户

  详见 `risk-classification.md`。

  ```

- [ ] **Step 4: 创建 risk-classification.md**

  内容：

  ```markdown
  <!-- verified: 2026-03-25 -->
  <!-- scope: code-review -->

  # 风险分级指南

  用于 `requesting-code-review` skill 在启动审查前选择审查策略。

  ## 分级标准

  ### 低风险
  **触发条件：** 变更仅涉及以下类型之一：
  - 文档文件（.md、注释）
  - 测试文件（不涉及被测逻辑变更）
  - 格式化/lint 修复
  - 配置值调整（无结构变更）

  **审查行为：** 启动单个审查子代理，快速审查，通过即继续。

  ### 中风险
  **触发条件：** 变更涉及：
  - 单个模块内的逻辑变更
  - 新增功能（不改变现有 API 接口）
  - Bug 修复（不涉及架构变更）

  **审查行为：** 标准审查，检查规格符合性 + 代码质量。

  ### 高风险
  **触发条件：** 变更涉及：
  - 跨模块的 API 变更
  - 数据模型结构变更
  - 公共接口签名变更
  - 数据库迁移

  **审查行为：** 双重审查（Parallelization-Voting 模式）：
  1. 并行启动 2 个独立审查子代理
  2. 两者结论均为"通过" → 继续
  3. 任一子代理发现阻塞问题 → 视为未通过，进入修复循环
  4. 结论不一致时取更严格结论

  ## 原则

  所有级别均为 Agent 自主完成，不因风险等级 escalate 给用户。
  风险等级影响审查深度，不影响 Agent 自主决策权。
  ```

- [ ] **Step 5: 验证**

  确认 SKILL.md 含 version 字段和风险分级章节，risk-classification.md 存在。

---

### Task 6: harness-engineering-review SKILL.md + 辅助文件

**文件：**
- 修改: `skills/harness-engineering-review/SKILL.md`
- 创建: `skills/harness-engineering-review/golden-principles-template.md`
- 创建: `scripts/scan-antipatterns.sh`（需先创建 `scripts/` 目录）

**变更说明（来自 spec Phase 2.4 + Phase 3.1）：**

- [ ] **Step 1: 读取当前文件**

  读取 `skills/harness-engineering-review/SKILL.md`。

- [ ] **Step 2: 在 frontmatter 增加 version 字段**

  ```yaml
  ---
  name: harness-engineering-review
  description: ...
  version: 1.0.0
  ---
  ```

- [ ] **Step 3: 在第 6 个审查维度之后插入第 7 个维度**

  在 `### 6. 技术债管理` section 之后，`## 审查报告格式` 之前插入：

  ```markdown
  ### 7. 代码模式一致性（Code Pattern Consistency）

  **目标：** 防止 AI 生成代码引入模式漂移，保持代码库风格一致。

  检查项：
  - [ ] 是否有项目专属"黄金原则"列表（golden principles）？
  - [ ] 是否定期检测已知反模式（重复逻辑、不一致命名、过时 API 调用）？
  - [ ] 是否有轻量自动化脚本辅助反模式扫描？

  **工具支持：**
  - `scripts/scan-antipatterns.sh` — 使用 ripgrep 扫描项目反模式，输出 Agent 友好报告
  - `golden-principles-template.md`（本目录）— 项目可定制的黄金原则模板

  **建议方案：**
  - 建立 `golden-principles.md`，记录团队公认的代码模式约定
  - 每次大型 AI 生成后运行 `scan-antipatterns.sh` 检查一致性
  - 在 AGENTS.md 中以指针引用黄金原则（非全文内嵌）

  ```

- [ ] **Step 4: 更新审查报告格式中的总体评分表**

  在审查报告格式的 `| 技术债管理 | ... | ... |` 行之后增加：
  ```markdown
  | 代码模式一致性 | ✅优 / ⚠️需改进 / ❌缺失 | 高/中/低 |
  ```

- [ ] **Step 5: 创建 golden-principles-template.md**

  内容：

  ```markdown
  <!-- verified: 2026-03-25 -->
  <!-- scope: code-quality -->

  # 黄金原则模板

  复制此文件到项目根目录或 `docs/` 下，定制为项目专属规范。

  ## 使用方式

  1. 将此文件复制为 `golden-principles.md`
  2. 根据项目实际情况修改和扩展原则列表
  3. 在 `AGENTS.md` 中以指针引用：`详见 [golden-principles.md](golden-principles.md)`
  4. 定期在 `scan-antipatterns.sh` 中添加新的反模式检测规则

  ## 通用原则（可定制）

  ### 代码组织
  - 优先复用共享工具函数，禁止手写同类 helper（DRY）
  - 单个文件不超过 [X] 行（超出则拆分）
  - 模块依赖方向：[层级 A] → [层级 B] → [层级 C]，禁止反向

  ### 数据处理
  - 所有边界数据必须验证/解析，禁止 YOLO 读取
  - 外部输入统一在 [入口层] 校验

  ### 错误处理
  - 禁止空 catch：`catch(e) {}`
  - 错误必须包含上下文信息

  ### 测试
  - 新功能必须有对应测试
  - 禁止删除失败测试以"通过" CI

  ## 项目专属原则

  （在此添加项目特有规范）
  ```

- [ ] **Step 6: 创建 scan-antipatterns.sh**（scripts/ 目录已在 Batch 2 前置步骤中创建）

  ```bash
  #!/usr/bin/env bash
  # scan-antipatterns.sh — 使用 ripgrep 扫描代码反模式
  # 用法: bash scripts/scan-antipatterns.sh [目录] [--format agent|human]
  # 默认扫描当前目录，输出 Agent 友好格式

  set -euo pipefail

  SCAN_DIR="${1:-.}"
  FORMAT="${2:---format}"
  FORMAT_VALUE="${3:-agent}"

  # 若第二个参数不是 --format，则视为目录
  if [[ "$FORMAT" != "--format" ]]; then
    FORMAT_VALUE="agent"
  fi

  ISSUES=0

  echo "## 反模式扫描报告"
  echo "扫描目录: $SCAN_DIR"
  echo "---"

  # 检测 1: 空 catch 块
  echo "### 1. 空 catch 块"
  if rg -l "catch\s*\([^)]*\)\s*\{\s*\}" "$SCAN_DIR" 2>/dev/null; then
    ISSUES=$((ISSUES + 1))
    echo "⚠️  发现空 catch 块，需要添加错误处理"
  else
    echo "✅ 未发现空 catch 块"
  fi

  # 检测 2: TypeScript 类型抑制
  echo ""
  echo "### 2. TypeScript 类型抑制"
  if rg -l "@ts-ignore|@ts-expect-error|as any" "$SCAN_DIR" 2>/dev/null; then
    ISSUES=$((ISSUES + 1))
    echo "⚠️  发现类型抑制，需要修复类型"
  else
    echo "✅ 未发现类型抑制"
  fi

  # 检测 3: console.log 残留（生产代码）
  echo ""
  echo "### 3. console.log 残留"
  if rg -l "console\.log" --glob "!*.test.*" --glob "!*.spec.*" "$SCAN_DIR" 2>/dev/null; then
    echo "⚠️  发现 console.log，确认是否为调试残留"
  else
    echo "✅ 未发现 console.log 残留"
  fi

  echo ""
  echo "---"
  echo "扫描完成。阻塞性问题: $ISSUES"

  if [[ "$FORMAT_VALUE" == "agent" ]]; then
    if [[ $ISSUES -gt 0 ]]; then
      echo "ACTION_REQUIRED: 修复以上 $ISSUES 个问题后继续"
    else
      echo "ACTION_REQUIRED: none"
    fi
  fi

  exit $ISSUES
  ```

- [ ] **Step 7: 验证**

  确认 SKILL.md 含第 7 个维度和 version 字段，golden-principles-template.md 和 scan-antipatterns.sh 存在。

---

## Batch 3：Phase 2 文档更新 + Phase 3 基础建设（3 个任务并行）

### Task 7: docs/workflow.md + docs/architecture.md

**文件：**
- 修改: `docs/workflow.md`
- 修改: `docs/architecture.md`

**变更说明（来自 spec Phase 2.5）：**

- [ ] **Step 1: 读取两个文件**

  读取 `docs/workflow.md` 和 `docs/architecture.md` 的 Gate 相关章节。

- [ ] **Step 2: 更新 workflow.md 的 Gate 描述**

  找到 workflow.md 中描述 Gate 机制的部分，按 DD-006 更新：
  - 将"feature-dev 阶段 6 实现前必须等待人工批准"改为"feature-dev 阶段 6 为轻量启动通知"
  - 将"exec-plan-runner 歧义/破坏性变更触发 escalation"改为"仅 3 轮修复失败时 escalation"
  - 更新文档顶部 `<!-- verified: -->` 时间戳为 `2026-03-25`

- [ ] **Step 3: 更新 architecture.md 的 Gate 表格**

  找到 architecture.md 中的 Gate 机制表格，同步 DD-006 的变更：
  - 更新阶段 6 前 Gate 描述
  - 更新 escalation 条件
  - 更新文档顶部 `<!-- verified: -->` 时间戳为 `2026-03-25`

- [ ] **Step 4: 验证**

  读取两个文件，确认 Gate 描述已与 DD-006 一致。

---

### Task 8: verification-before-completion SKILL.md

**文件：**
- 修改: `skills/verification-before-completion/SKILL.md`

**变更说明（来自 spec Phase 3.3 + Phase 3.1）：**

- [ ] **Step 1: 读取当前文件**

  读取 `skills/verification-before-completion/SKILL.md`。

- [ ] **Step 2: 在 frontmatter 增加 version 字段**

  ```yaml
  ---
  name: verification-before-completion
  description: ...
  version: 1.0.0
  ---
  ```

- [ ] **Step 3: 在"标准验证序列"之后增加"环境感知验证策略"章节**

  在 `## 标准验证序列` section 之后，`## 红旗 — 立即停止` 之前插入：

  ```markdown
  ## 环境感知验证策略

  验证开始前先检测可用工具，按项目类型选择验证手段：

  | 项目类型 | 基础验证（必须） | 增强验证（工具可用时） |
  |----------|-----------------|----------------------|
  | CLI/库 | lint + unit test + build | 集成测试、示例脚本运行 |
  | API/后端 | lint + unit test + build | curl/httpie 端到端请求、日志检查 |
  | Web UI | lint + unit test + build | 浏览器自动化（截图对比、DOM 断言） |
  | 全栈 | lint + unit test + build | API 验证 + 浏览器验证 |

  **工具检测（验证前）：**
  ```bash
  which curl httpie playwright puppeteer 2>/dev/null || true
  ```

  工具不可用时 → 回退到基础验证，在报告中注明"增强验证不可用（缺少 [工具名]）"。

  ```

- [ ] **Step 4: 验证**

  读取修改后文件，确认 version 字段和环境感知验证章节存在。

---

### Task 9: VERSION + scripts/sync-version.sh

**文件：**
- 创建: `VERSION`（项目根目录）
- 创建: `scripts/sync-version.sh`

**变更说明（来自 spec Phase 3.1）：**

注意：`scripts/` 目录在 Task 6 中已创建。如果 Task 6 尚未完成，先创建目录。

- [ ] **Step 1: 创建 VERSION 文件**

  在项目根目录 `/Users/linfee/dev/workspace/ai-skills/power-agent/VERSION` 创建：

  ```
  1.0.0
  ```

- [ ] **Step 2: 创建 scripts/sync-version.sh**

  使用 python3 内联方式处理 frontmatter（避免 macOS BSD sed 兼容问题）：

  ```bash
  #!/usr/bin/env bash
  # sync-version.sh — 读取 VERSION 文件，批量更新所有 SKILL.md 的 version 字段
  # 用法: bash scripts/sync-version.sh
  # 若 SKILL.md 无 version 字段则追加，有则更新
  # 依赖: python3（系统自带）

  set -euo pipefail

  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  ROOT_DIR="$(dirname "$SCRIPT_DIR")"
  VERSION_FILE="$ROOT_DIR/VERSION"

  if [[ ! -f "$VERSION_FILE" ]]; then
    echo "错误：未找到 VERSION 文件（$VERSION_FILE）" >&2
    exit 1
  fi

  VERSION=$(cat "$VERSION_FILE" | tr -d '[:space:]')

  python3 - "$ROOT_DIR" "$VERSION" <<'PYEOF'
  import sys, re
  from pathlib import Path

  root = Path(sys.argv[1])
  version = sys.argv[2]
  print(f"目标版本: {version}\n")

  updated = 0
  errors = 0

  for skill_file in sorted(root.glob('skills/*/SKILL.md')):
      skill_name = skill_file.parent.name
      try:
          content = skill_file.read_text()
          if not content.startswith('---'):
              raise ValueError("不以 --- 开头，无法处理 frontmatter")
          lines = content.split('\n')
          close_idx = next(
              (i for i in range(1, len(lines)) if lines[i].strip() == '---'),
              None
          )
          if close_idx is None:
              raise ValueError("未找到 frontmatter 结束符 ---")
          fm = lines[1:close_idx]
          rest = lines[close_idx:]
          if any(l.startswith('version:') for l in fm):
              fm = [re.sub(r'^version:.*', f'version: {version}', l) for l in fm]
              action = "更新"
          else:
              fm.append(f'version: {version}')
              action = "追加"
          skill_file.write_text('\n'.join(['---'] + fm + rest))
          print(f"✅ 已{action}: {skill_name} -> {version}")
          updated += 1
      except Exception as e:
          print(f"❌ 失败: {skill_name}: {e}")
          errors += 1

  print(f"\n---\n处理完成：{updated} 个，{errors} 个失败\n")
  if errors:
      sys.exit(1)

  print("版本一致性校验...")
  bad = 0
  for skill_file in sorted(root.glob('skills/*/SKILL.md')):
      m = re.search(r'^version:\s*(.+)$', skill_file.read_text(), re.MULTILINE)
      fv = m.group(1).strip() if m else 'missing'
      if fv != version:
          print(f"❌ {skill_file.parent.name} = {fv}")
          bad += 1
  if bad:
      print(f"校验失败：{bad} 个不一致")
      sys.exit(1)
  print(f"✅ 版本同步完成：所有 SKILL.md = {version}")
  PYEOF
  ```

- [ ] **Step 3: 赋予执行权限**

  ```bash
  chmod +x /Users/linfee/dev/workspace/ai-skills/power-agent/scripts/sync-version.sh
  chmod +x /Users/linfee/dev/workspace/ai-skills/power-agent/scripts/scan-antipatterns.sh
  ```

- [ ] **Step 4: 运行 sync-version.sh 为所有 16 个 SKILL.md 添加 version 字段**

  此步骤统一处理所有 16 个 SKILL.md 的 version 字段，**Task 10 的手工逐个添加可跳过**（由本脚本统一完成）。

  ```bash
  bash /Users/linfee/dev/workspace/ai-skills/power-agent/scripts/sync-version.sh
  ```
  预期输出：16 个 ✅，最后一行"✅ 版本同步完成：所有 SKILL.md = 1.0.0"

- [ ] **Step 5: 验证**

  确认 VERSION 文件和 sync-version.sh 存在，且 Step 4 输出符合预期。

---

## Batch 4：Phase 3 完成（3 个任务并行）

### Task 10: 确认所有 SKILL.md version 字段（由 Task 9 脚本统一完成）

**说明：** Task 9 的 `sync-version.sh` 已对全部 16 个 SKILL.md 执行 version 字段添加/更新。本任务仅做验证确认，不需要手工编辑。

- [ ] **Step 1: 验证全部 16 个 SKILL.md 均含 version 字段**

  ```bash
  grep -l "^version:" /Users/linfee/dev/workspace/ai-skills/power-agent/skills/*/SKILL.md | wc -l
  ```
  预期输出：16

  若未达 16，说明 Task 9 未完成，重新运行 sync-version.sh。

---

### Task 11: docs/eval-framework.md + eval-results 目录

**文件：**
- 创建: `docs/eval-framework.md`
- 创建: `skills/exec-plan-runner/eval-results/.gitkeep`
- 创建: `skills/systematic-debugging/eval-results/.gitkeep`
- 创建: `skills/feature-dev/eval-results/.gitkeep`

- [ ] **Step 1: 创建 docs/eval-framework.md**

  内容：

  ```markdown
  <!-- verified: 2026-03-25 -->
  <!-- scope: eval, metrics, skills -->

  # Eval 框架

  power-agent 轻量评估框架，用于追踪 Skill 执行质量、版本间改进效果与用户满意度。

  ## 设计原则

  - **低摩擦**：Agent 自动采集，用户只需回答 1 个必答题
  - **版本追踪**：每条记录含 skill-version，便于版本间对比
  - **可跳过**：用户可跳过反馈，仍保留自动指标

  ## 评估维度

  | 指标 | 来源 | 自动化 |
  |------|------|--------|
  | 任务完成率 | exec-plan checkbox | 全自动 |
  | 修复循环次数 | 执行过程计数 | 全自动 |
  | Escalation 次数 | 执行过程计数 | 全自动 |
  | Batch 数量 | exec-plan 结构 | 全自动 |
  | 假设验证轮数 | debugging 阶段 3 计数 | 全自动 |
  | 端到端耗时 | 首次工具调用到完成时间差 | 全自动（精确到分钟） |
  | 用户满意度 | 向用户提问 | 人工（可跳过） |

  ## 收集协议

  支持 Eval 收集的 Skills：`exec-plan-runner`、`systematic-debugging`、`feature-dev`

  每次 Skill 执行完成时：
  1. 自动采集上表中的全自动指标
  2. 写入 exec-plan 文件尾部（或当前上下文）
  3. 向用户提问 1 个必答题 + 1 个可选备注
  4. 用户跳过时标注 `feedback: skipped`，仍保存自动指标

  ## Eval 记录格式

  ```markdown
  <!-- eval: YYYY-MM-DD -->
  <!-- skill: [skill-name] -->
  <!-- skill-version: [version] -->
  <!-- project: [project-name] -->
  <!-- task: [任务简述] -->

  ## Eval 记录
  - 任务完成率: N/N
  - Batch 数: N
  - 修复循环: N 次
  - Escalation: N 次
  - 耗时: Nmin

  ## 用户反馈
  - 整体: [满意 / 一般 / 不满意 / skipped]
  - 备注: [内容或 "-"]
  ```

  ## 存储位置

  Eval 记录写入对应 exec-plan 文件尾部。历史记录可在 `skills/[skill-name]/eval-results/` 下归档（手动操作）。

  ## 非交互场景处理

  当 skill 在自动化或非交互上下文中运行时：
  - 默认写入 `feedback: skipped`（不阻塞主流程）
  - 不需要额外等待用户输入
  - 自动指标仍正常写入

  ## 版本追踪规范

  - `skill-version` 从对应 SKILL.md frontmatter 的 `version` 字段读取
  - `project` 从目标项目 git remote URL 或目录名推断
  - 版本升级时更新 `VERSION` 文件并运行 `scripts/sync-version.sh`
  ```

- [ ] **Step 2: 创建 eval-results 目录和 .gitkeep 文件**

  创建三个 `.gitkeep` 文件以保持目录结构：
  - `skills/exec-plan-runner/eval-results/.gitkeep`
  - `skills/systematic-debugging/eval-results/.gitkeep`
  - `skills/feature-dev/eval-results/.gitkeep`

  `.gitkeep` 文件内容为空字符串。

- [ ] **Step 3: 验证**

  确认 eval-framework.md 和三个 .gitkeep 文件均已创建。

---

### Task 12: AGENTS.md + docs/development.md

**文件：**
- 修改: `AGENTS.md`（项目根目录）
- 修改: `docs/development.md`

**变更说明（来自 spec Phase 3.1）：**

- [ ] **Step 1: 读取两个文件**

  读取 `AGENTS.md` 的约束表格和知识库导航部分，读取 `docs/development.md` 的提交流程相关章节。

- [ ] **Step 2: 更新 AGENTS.md 约束表格**

  在 `## 约束（硬规则）` 的表格中追加一行：

  ```markdown
  | 提交前版本同步 | 修改 Skill 内容后提交前：1) 更新 VERSION 2) 运行 `scripts/sync-version.sh` 3) 确认同步完成 |
  ```

- [ ] **Step 3: 更新 docs/development.md 补充版本管理章节**

  在 docs/development.md 中找到或在文件末尾追加"提交流程"或"版本管理"章节：

  ```markdown
  ## 版本管理

  ### Skill 版本机制

  所有 `skills/*/SKILL.md` 的 frontmatter 包含 `version` 字段，与 `VERSION` 文件保持同步。

  ### 提交流程（修改 Skill 内容后）

  1. 修改 `VERSION` 文件中的版本号（语义化版本：`MAJOR.MINOR.PATCH`）
  2. 运行 `bash scripts/sync-version.sh` 同步所有 SKILL.md
  3. 确认输出"✅ 版本同步完成"
  4. 将 VERSION、sync-version.sh 和修改的 SKILL.md 一起提交

  ### 版本号规范

  | 变更类型 | 版本升级 | 示例 |
  |----------|---------|------|
  | 破坏性变更（移除 Gate、重构流程） | MAJOR | 1.0.0 → 2.0.0 |
  | 新增功能（新章节、新机制） | MINOR | 1.0.0 → 1.1.0 |
  | 文字修正、描述优化 | PATCH | 1.0.0 → 1.0.1 |
  ```

- [ ] **Step 4: 验证**

  读取修改后的 AGENTS.md 和 docs/development.md，确认版本管理规则已正确添加。

---

## 全局验证

所有 batch 完成后执行：

- [ ] **GV1: 统计 version 字段**

  运行：
  ```bash
  grep -l "version:" /Users/linfee/dev/workspace/ai-skills/power-agent/skills/*/SKILL.md | wc -l
  ```
  预期输出：16（16 个 SKILL.md 均含 version 字段）

- [ ] **GV2: 运行 sync-version.sh**

  ```bash
  bash /Users/linfee/dev/workspace/ai-skills/power-agent/scripts/sync-version.sh
  ```
  预期输出包含"✅ 版本同步完成"，无报错

- [ ] **GV3: 测试 scan-antipatterns.sh**

  ```bash
  # 测试 1：正常目录 + 有内容 → 能输出分类结果
  bash /Users/linfee/dev/workspace/ai-skills/power-agent/scripts/scan-antipatterns.sh \
    /Users/linfee/dev/workspace/ai-skills/power-agent/skills
  # 预期：输出包含 "## 反模式扫描报告"，每个检测项有 ✅ 或 ⚠️，末尾有 "ACTION_REQUIRED"

  # 测试 2：目录不存在 → 脚本正常退出或提示
  bash /Users/linfee/dev/workspace/ai-skills/power-agent/scripts/scan-antipatterns.sh /nonexistent 2>&1 || true
  # 预期：不崩溃（exit 0 或有错误提示）

  # 测试 3：检查脚本有执行权限
  test -x /Users/linfee/dev/workspace/ai-skills/power-agent/scripts/scan-antipatterns.sh && echo "✅ 有执行权限"
  ```

- [ ] **GV4: 检查 DD 索引完整性**

  读取 `docs/arch-decisions/index.md`，确认 DD-001 到 DD-006 均有条目，DD-005 标注 superseded

- [ ] **GV5: eval-framework.md 存在**

  确认 `docs/eval-framework.md` 文件存在且格式完整

## Session Log
