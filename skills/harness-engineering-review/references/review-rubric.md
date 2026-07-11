# 审查 Rubric

七个维度的检查项、反模式与判据。供 `harness-engineering-review` skill 执行时参考。

---

## 1. AGENTS.md 结构（Context Management）

**检查项**
- AGENTS.md 是否存在且可导航（≤200 行）
- 是否包含：项目类型、构建/测试命令、关键路径指针
- 指针是否有效（文件实际存在）

**反模式**
- AGENTS.md 超过 400 行，内嵌大量实现细节
- 把完整规范写进 AGENTS.md 而非用指针引用
- 导航指针指向已删除或重命名的文件

**判据**
- 优：≤200 行，指针全部有效，命令可直接执行
- 需改进：存在失效指针或命令过时
- 缺失：无 AGENTS.md 或内容为空

---

## 2. Agent 可见性（Agent Legibility）

**检查项**
- 关键约束是否对 Agent 可见（在 AGENTS.md 或 docs/ 中有明确说明）
- 禁止行为是否有明确边界（不做什么）
- 输出 contract 是否有定义

**反模式**
- 约束只存在于口头约定或 PR 描述中
- Skill 只说"做什么"，不说"不做什么"
- 没有输出格式定义，编排层无法消费

**判据**
- 优：约束可机器读取，输出 contract 有 schema
- 需改进：约束存在但仅为自然语言描述
- 缺失：无约束定义

---

## 3. 约束机制化（Enforced Architecture & Taste）

**检查项**
- 关键规则是否有 harness/tooling 兜底（lint、CI、hook）
- 是否存在只靠 prompt 文本约束的高风险规则
- 破坏性操作是否有确认机制

**反模式**
- "禁止 as any"只写在 AGENTS.md，没有 tsconfig/eslint 规则
- 未验证不得声称完成——仅靠 prompt，无 CI 门禁
- 破坏性 git 命令无二次确认

**判据**
- 优：P0 规则有工具层兜底
- 需改进：P0 规则仅靠 prompt
- 缺失：无任何机制化约束

---

## 4. 反馈循环质量（Feedback Loop）

**检查项**
- 是否有可运行的测试套件
- CI 是否在 PR 前自动运行
- 失败信息是否足够定位根因

**反模式**
- 测试存在但不在 CI 中运行
- 测试只覆盖 happy path
- 错误信息只有 "failed"，无上下文

**判据**
- 优：CI 覆盖、失败可定位、覆盖率有基线
- 需改进：测试存在但 CI 未接入
- 缺失：无测试或无 CI

---

## 5. 知识维护（Documentation Gardening）

**检查项**
- 是否通过 scanner 结合 `.okf/verification.json` 与项目 `freshness` policy 判定核心文档的验证状态
- 没有可信 verification ledger 时，是否明确判定为 `unverified`，而不是向 Concept metadata 写回验证结果
- 文档内容是否与代码现状一致

**反模式**
- 在 Concept metadata 中读写 `verified` 时间戳以替代 verification ledger
- 没有可信 ledger 却将文档当作 `fresh` 或已验证
- 未完成语义核对就通过 `record` 伪造验证状态
- 架构图与实际目录结构不符

**判据**
- 优：核心文档的 scanner 状态为 `fresh`，且内容与代码一致
- 需改进：存在 `due` 或 `dirty` 文档，但已有明确的核对或修复计划
- 缺失：没有可信 ledger，状态为 `unverified`，或存在未解决的 `blocked` 文档

---

## 6. 技术债管理（Garbage Collection）

**检查项**
- 是否有已知技术债的追踪机制（TODO、issue、exec-plan）
- 废弃代码是否有清理计划
- 依赖是否有过期风险

**反模式**
- TODO 注释无 owner 和日期
- 废弃模块保留超过 2 个版本周期
- 依赖版本锁定在有已知漏洞的版本

**判据**
- 优：技术债有追踪、有优先级、有负责人
- 需改进：有追踪但无优先级或负责人
- 缺失：无追踪机制

---

## 7. 代码模式一致性（Code Pattern Consistency）

**检查项**
- 同类操作是否使用统一模式（错误处理、数据访问、API 响应格式）
- 是否有 lint/formatter 配置并在 CI 中执行
- 新代码是否遵循既有约定

**反模式**
- 同一仓库中混用多种错误处理风格
- formatter 配置存在但未在 CI 中强制
- 新功能引入与既有模式不一致的抽象

**判据**
- 优：lint+formatter 在 CI 中强制，模式统一
- 需改进：有配置但未强制，或存在局部不一致
- 缺失：无 lint/formatter，模式混乱
