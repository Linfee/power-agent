<!-- verified: 2026-03-25 -->
<!-- scope: architecture, workflow, skills -->
<!-- status: proposed -->

# Spec: 基于参考文献洞察的 Skill 与工作流增强

## 背景

基于 OpenAI Harness Engineering 和 Anthropic 系列工程博文（共 6 篇）提炼的关键洞察，识别出当前 power-agent 体系的 7 个改进方向。本 spec 将其组织为 3 个递进 Phase 实施。

## 设计决策

### DD-006: Gate 机制重构（supersede DD-005）

**核心变更：** 将 Gate 从"关键决策点人工审批"重构为"规划阶段锁定方向 + 实现阶段 Agent 自主闭环"。

**论据：**

1. 方向偏离问题在规划阶段已解决——discuss 产出 spec、writing-plans 产出 exec-plan，方向在此锁定
2. 破坏性操作由 worktree sandbox 物理隔离，最坏情况是丢弃 worktree
3. 实现质量由 Agent-to-Agent 审查循环保障，发现问题比解决问题容易

**三道防线模型：**

```
1. 规划 Gate → 人类锁定方向与架构（discuss/feature-dev 阶段 3-4）
2. Sandbox 隔离 → worktree 物理限制破坏范围
3. Agent-to-Agent 审查 → 质量保障（风险分级 + 投票机制）

Escalation 仅作兜底：审查修复循环耗尽（3轮）后才触发
```

**Gate 重新划分：**

| Gate | 原 DD-005 | DD-006 |
|------|-----------|--------|
| discuss Step 7（spec 批准） | 保留 | **保留** — 规划 Gate |
| feature-dev 阶段 3（澄清确认） | 保留 | **保留** — 规划 Gate |
| feature-dev 阶段 4（架构选择） | 保留 | **保留** — 规划 Gate |
| feature-dev 阶段 6 前（实现批准） | 强制等待 | **弱化为启动通知** — "Exec-plan 已就绪，开始执行？" |
| exec-plan-runner escalation | 歧义/破坏性变更/3轮失败 | **仅 3 轮审查修复循环耗尽时触发** |

---

## Phase 1：核心流程加固

### 1.1 跨窗口 session progress log

**修改文件：** `skills/exec-plan-runner/SKILL.md`

**变更：** 在 Step 2c 的进度更新中，增加结构化 Session Log 写入协议。写入位置为 exec-plan 文件的 `## Session Log` section（不额外创建文件）。

**新增文件：** `skills/exec-plan-runner/progress-log-template.md`

模板格式：

```markdown
## Session Log
<!-- 每个 batch 完成后追加一条，最新在最上方 -->

### [YYYY-MM-DD HH:MM] Batch N 完成
- **已完成**: Task A (文件列表), Task B (文件列表)
- **遇到的问题**: [描述 + 如何解决，或标注未解决]
- **已验证假设**: [什么被证实/证伪]
- **下一步**: Batch N+1，从 Task X 开始
- **环境状态**: lint ✅ | tests ✅ (N passed) | build ✅
```

恢复模式（Step 1）调整：读取 Session Log → git log → exec-plan checkbox，三者交叉验证后确定恢复点。

### 1.2 会话 bootstrap 标准化

**修改文件：** `skills/exec-plan-runner/SKILL.md`、`skills/systematic-debugging/SKILL.md`

**exec-plan-runner** — 在 Step 1 最前面插入固定 bootstrap 序列：

```
Bootstrap（每次会话开始，无条件执行）：
1. 读 exec-plan 的 Session Log（如有）
2. git log --oneline -10
3. 运行项目基本健康检查（lint + 核心测试套件）
4. 若健康检查失败 → 先修复再继续，不在破损基线上工作
5. 确认恢复点，输出一句话摘要
```

**systematic-debugging** — 阶段 1 前置环境健康检查：先确认当前代码能编译/能跑基本测试，再开始调试，避免在已有其他问题的环境中排查。

### 1.3 子代理返回值粒度控制

**修改文件：** `skills/exec-plan-runner/SKILL.md`

在子代理 prompt 模板中增加 `output_detail` 参数，按阶段选择粒度：

| 子代理类型 | 粒度 | 理由 |
|-----------|------|------|
| 实现子代理 | `detailed` | 需要完整文件列表、测试输出、疑虑描述 |
| 审查子代理 | `concise`（通过时）/ `detailed`（有问题时） | 通过时只需结论 |
| 验证子代理 | `concise` | 只需命令+结论+退出码 |
| explore 子代理 | `concise`（首轮）/ `detailed`（深入时） | 首轮只要文件路径和模块边界 |

子代理 prompt 尾部控制指令：

```
## 输出粒度: concise
仅返回结论性信息。省略完整代码、完整命令输出、中间推理过程。
```

```
## 输出粒度: detailed
返回完整信息，包含文件列表、关键代码片段、命令输出、推理过程。
```

---

## Phase 2：Gate 重构 + 审查自主化 + 熵治理

### 2.0 DD-006 落地

**新增文件：** `docs/arch-decisions/DD-006-gate-restructuring.md`

**修改文件：**
- `docs/arch-decisions/DD-005-gate-mechanism.md` — 状态更新为 `superseded by DD-006`
- `docs/arch-decisions/index.md` — 更新索引

### 2.1 feature-dev 流程调整

**修改文件：** `skills/feature-dev/SKILL.md`

调整后流程：

```
阶段 1-3：上下文 + 探索 + 澄清
  gate ✋ 等待用户确认

阶段 4：架构方案呈现
  gate ✋ 等待用户选择方案

阶段 5：writing-plans 创建 exec-plan

阶段 6 前：轻量确认（启动通知，非审批 Gate）
  > "Exec-plan 已就绪（N 个任务，预计 M 个 batch）。开始执行？"
  用户确认 → 进入自主执行

阶段 6-8：自主执行（实现→审查→文档）
  全程 Agent 闭环，仅 3 轮修复失败时 escalate

最终：呈现完成报告 + finishing-a-development-branch 选项
```

### 2.2 exec-plan-runner escalation 精简

**修改文件：** `skills/exec-plan-runner/SKILL.md`

- 移除 escalation 中的"歧义"和"破坏性变更"触发条件
- 保留唯一 escalation 条件：**修复子代理反复失败（3 轮审查修复循环耗尽）**
- "无需 Escalate"列表扩展：歧义由 Agent 自主判断，破坏性变更由 worktree 隔离

### 2.3 审查自动化分级

**修改文件：** `skills/requesting-code-review/SKILL.md`

**新增文件：** `skills/requesting-code-review/risk-classification.md`

风险分级决定审查深度（所有级别 Agent 自主完成，不 escalate 给人类）：

| 级别 | 条件 | 审查行为 |
|------|------|----------|
| 低风险 | 文档、测试、格式 | 单轮快速审查，通过即继续 |
| 中风险 | 单模块逻辑变更 | 标准审查（规格符合性 + 代码质量） |
| 高风险 | 跨模块 API/数据模型变更 | 双重审查（2 个独立审查子代理，结论一致才通过） |

高风险采用 Parallelization-Voting 模式增加可靠性。两个审查子代理结论不一致时，取更严格的结论（即任一子代理发现阻塞问题则视为未通过，进入修复循环）。

### 2.4 代码模式漂移检测

**修改文件：** `skills/harness-engineering-review/SKILL.md` — 增加第 7 个审查维度"代码模式一致性"

**新增文件：**
- `skills/harness-engineering-review/golden-principles-template.md` — 项目可定制的黄金原则模板
- `scripts/scan-antipatterns.sh` — 轻量 ripgrep 反模式扫描脚本，输出 Agent 友好报告

### 2.5 文档同步

**修改文件：**
- `docs/workflow.md` — Gate 机制描述、反模式列表同步更新
- `docs/architecture.md` — Gate 机制表格同步更新

---

## Phase 3：元层能力建设

### 3.1 版本管理机制

**新增文件：**
- `VERSION` — 项目根目录，全局版本源，纯文本，语义化版本号
- `scripts/sync-version.sh` — 读取 VERSION 批量更新所有 SKILL.md frontmatter 的 `version` 字段；末尾校验所有 SKILL.md 版本一致，不一致则报错退出

**修改文件：**
- 所有 16 个 `skills/*/SKILL.md` — frontmatter 增加 `version` 字段
- `AGENTS.md` — 约束表格增加"提交前版本同步"规则：修改 Skill 内容后提交前必须 1) 更新 VERSION 2) 运行 `scripts/sync-version.sh` 3) 确认同步完成
- `docs/development.md` — 补充提交流程章节，说明版本管理和 sync-version 用法

### 3.2 轻量 Eval 框架

**新增文件：**
- `docs/eval-framework.md` — 评估维度、自动采集指标清单、收集协议、版本追踪规范
- `skills/exec-plan-runner/eval-results/.gitkeep`
- `skills/systematic-debugging/eval-results/.gitkeep`
- `skills/feature-dev/eval-results/.gitkeep`

**修改文件：** `skills/exec-plan-runner/SKILL.md`、`skills/systematic-debugging/SKILL.md`、`skills/feature-dev/SKILL.md` — 各自在完成步骤后追加反馈收集步骤

**收集协议：** Agent 在任务完成后自动采集指标 + 向用户提 1 个必答选择题 + 1 个可选备注：

```
> 执行摘要：6/6 任务完成，2 个 batch，修复循环 1 次，无 escalation。
>
> 快速反馈：
> 1. 整体效果？ [满意 / 一般 / 不满意]
> 2. 备注？（可选，直接回车跳过）
```

用户跳过反馈时仍写入自动指标，标注 `feedback: skipped`。

**自动采集指标：**

| 指标 | 来源 | 自动化程度 |
|------|------|-----------|
| 任务完成率 | exec-plan checkbox | 全自动 |
| 修复循环次数 | 执行过程计数 | 全自动 |
| Escalation 次数 | 执行过程计数 | 全自动 |
| Batch 数量 | exec-plan 结构 | 全自动 |
| 假设验证轮数 | debugging 阶段 3 计数 | 全自动 |
| 端到端耗时 | 首次工具调用到 finishing 时间差（精确到分钟） | 全自动 |
| 用户满意度 | 向用户提问 | 人工（可跳过） |

**Eval 记录格式：**

```markdown
<!-- eval: YYYY-MM-DD -->
<!-- skill: exec-plan-runner -->
<!-- skill-version: 1.2.0 -->
<!-- project: acme-backend -->
<!-- task: 用户认证模块重构 -->

## 自动指标
- 任务完成率: 6/6
- Batch 数: 2
- 修复循环: 1 次
- Escalation: 0
- 耗时: 45min

## 用户反馈
- 整体: 满意
- 备注: -
```

`skill-version` 从 SKILL.md frontmatter 的 `version` 字段读取。`project` 从目标项目 git remote 或目录名推断。

### 3.3 验证能力增强

**修改文件：** `skills/verification-before-completion/SKILL.md` — 增加"环境感知验证策略"章节

按项目类型选择验证手段：

| 项目类型 | 基础验证（必须） | 增强验证（如工具可用） |
|----------|-----------------|----------------------|
| CLI/库 | lint + unit test + build | 集成测试、示例脚本运行 |
| API/后端 | lint + unit test + build | curl/httpie 端到端请求、日志检查 |
| Web UI | lint + unit test + build | 浏览器自动化（截图对比、DOM 断言） |
| 全栈 | lint + unit test + build | API 验证 + 浏览器验证 |

验证开始前检测环境中可用工具（Puppeteer/Playwright、curl/httpie、日志查询工具），不可用时回退基础验证并在报告中注明。不实现具体浏览器集成，预留扩展点。

---

## 全局交付物清单

### 新增文件（11 个）

| 文件 | Phase |
|------|-------|
| `VERSION` | 3 |
| `scripts/sync-version.sh` | 3 |
| `scripts/scan-antipatterns.sh` | 2 |
| `docs/arch-decisions/DD-006-gate-restructuring.md` | 2 |
| `docs/eval-framework.md` | 3 |
| `skills/exec-plan-runner/progress-log-template.md` | 1 |
| `skills/exec-plan-runner/eval-results/.gitkeep` | 3 |
| `skills/systematic-debugging/eval-results/.gitkeep` | 3 |
| `skills/feature-dev/eval-results/.gitkeep` | 3 |
| `skills/requesting-code-review/risk-classification.md` | 2 |
| `skills/harness-engineering-review/golden-principles-template.md` | 2 |

### 修改文件（14+ 个）

| 文件 | Phase | 变更内容 |
|------|-------|----------|
| `skills/exec-plan-runner/SKILL.md` | 1+2+3 | session log + bootstrap + 粒度控制 + escalation 精简 + eval 收集 + version |
| `skills/systematic-debugging/SKILL.md` | 1+3 | bootstrap 前置 + eval 收集 + version |
| `skills/feature-dev/SKILL.md` | 2+3 | 阶段 6 弱化为启动通知 + eval 收集 + version |
| `skills/requesting-code-review/SKILL.md` | 2+3 | 风险分级审查 + version |
| `skills/harness-engineering-review/SKILL.md` | 2+3 | 第 7 维度 + version |
| `skills/verification-before-completion/SKILL.md` | 3 | 环境感知验证 + version |
| 其余 10 个 `skills/*/SKILL.md` | 3 | frontmatter 增加 version 字段 |
| `docs/arch-decisions/DD-005-gate-mechanism.md` | 2 | 状态→superseded |
| `docs/arch-decisions/index.md` | 2 | 更新索引 |
| `docs/workflow.md` | 2 | Gate 描述同步 |
| `docs/architecture.md` | 2 | Gate 表格同步 |
| `docs/development.md` | 3 | 版本管理+提交流程 |
| `AGENTS.md` | 3 | 约束表格+导航指针 |

---

## 测试策略

本项目为 prompt/skill 工程项目，无单元测试。验证方式：

1. **结构验证**：`sync-version.sh` 运行后所有 SKILL.md version 字段一致
2. **脚本验证**：`scan-antipatterns.sh` 在示例目录上正确检测反模式
3. **文档交叉引用**：所有 DD 编号、文件路径指针指向实际存在的文件
4. **Eval 框架验证**：在一次真实 exec-plan-runner 执行后，eval 记录成功写入

---

## 实施顺序

Phase 1 → Phase 2 → Phase 3（Phase 2 依赖 Phase 1 的 session log 机制稳定后再做审查自动化；Phase 3 的版本机制是独立的但放在最后避免中途改 frontmatter 导致 diff 噪音）。
