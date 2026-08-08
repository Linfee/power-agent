---
name: writing-skills
description: |-
  Skill 维护 Skill。创建、修改、审查或优化 Skill 与触发描述；用户要求写 skill、改 skill 或 review skill 时触发。
  Triggers: 创建 skill, 修改 skill, skill 设计, prompt 契约, skill review.
---

# Writing Skills

Skill 是可复用工作流，不是一次性经验记录。修改 Skill 时先明确目标行为、直接 consumer 与输出契约，再以最小必要改动保持它们一致。

**根美德：过程可预测。** Skill 的存在是为了从随机系统中榨出确定性——目标是每次运行走同样的流程，不是产出同样的结果。本 Skill 的所有规则都服务这一点。

按下方四步流程工作即可自足完成；`references/criteria.md` 是判据完整版（成本模型、机制、示例）——只在判据分歧、切分/合并决策、no-op 裁决时按需读对应节。

---

## Objective

### 做什么
- 创建或修改 `skills/<name>/SKILL.md`。
- 维护 Skill 与 references、docs、项目路由文件（如 AGENTS.md / CLAUDE.md）之间的触发和交接契约。
- 优化 description 与调用方式，使触发准确且上下文成本合理。

### 不做什么
- 不把项目一次性约定伪装成通用 Skill。
- 不为能用脚本、lint 或 schema 机械化的规则只写 prompt。
- 不在 Skill 中隐藏破坏性命令或平台私有假设。
- 不把长篇背景故事写进 `SKILL.md`。

---

## 流程

### 1. 定位

先定位，再动手，分两种情况：

- **新建**：定义**行为缺口**——没有这个 Skill 时 Agent 会犯什么错。写清触发场景（用户说什么、任务处于什么阶段）、目标行为（Agent 读完应做出什么不同决策）、输出契约（下游消费哪些字段）。
- **修改**：读取当前 `SKILL.md`、相关 `references/`、调用方 Skill 和 docs，诊断**文本病灶**——既有 Skill 文字自身的退化，按下方「判据速查：五失败模式」逐行诊断，不同病不同药，不裸精简；同时确认行为缺口仍然成立。

行为缺口是没有 Skill 时 Agent 犯的错；五失败模式是 Skill 文字自身的病灶——两者别混。

完成判据：能写清要建/要修什么，以及明确不做什么——新建不堆预测性规则，修改不顺手重写整套风格。

### 2. 改动

每条一句话判据；拿不准判据含义时读 criteria.md 对应节。

- **description 只服务触发**：触发词前置；一个触发分支只写一次（“需求讨论 / 需求分析 / PRD 细化”是同义重复，保留真正不同的分支）；删掉正文已有的身份复述。用词是“你想要这个 Skill 时自己实际会说的词”；“要严谨”“全面”这类弱词是 no-op，换强词。长度硬上限约 110 token、目标 ~100——description 常驻上下文，超出的部分每轮都在付 load；超限先删同义触发词与身份复述，不动用于/不用于边界信息。
- **调用方式二选一**：model-invoked（默认）付 context load——只有三个理由值这笔钱：模型需要自主触达、别的 Skill 需要按名调用、它是自治工作流链路的一环。user-invoked（`disable-model-invocation: true`）零 context load 但付 cognitive load——人得记得它存在，description 改写成面向人类的一句话摘要，并登记到项目的人维护 Skill 索引（power-agent 仓：`AGENTS.md` 速查表）。依赖方向：user-invoked 可以调用 model-invoked，反之禁止。
- **渐进披露**：所有使用路径都需要的内容内联，只有部分路径用到的下沉 `references/`。有步骤的 Skill 别让长篇引用埋没步骤；无步骤的扁平 Skill 全是引用是合法安排，不要硬造步骤；指针后的材料模型够不到时，先锐化指针措辞，失败了才回拉内联。
- **步骤带完成判据**：可检查、重要处穷尽（“每个改动过的文件都已核对”，而不是“产出变更清单”）。防提前交卷：先锐化判据；判据不可再锐化、且实际观察到 rush，才按 sequence 切分——只有子代理派发或 user-invoked 交接才藏得住后续步骤，inline 的 model-invoked 调用什么都清不掉。
- **切分与合并**：合法时机只有 by invocation（出现应自主触发的独立触发词，或另一个 Skill 必须按名够到它）和 by sequence（藏后续步骤）；每次切分都花一种负载。合并两个串行 Skill 会把前者的后续步骤暴露给当前步骤——合并前先检查两段各自的完成判据是否够硬。
- **纪律防御只补真实逃逸**：直接界定行为缺口或现有契约的基础规则可直接写；仅当真实会话、review finding、正常交付或事故材料可指认 Agent 的实际回避模式时，才新增额外防御。防御写明可观察条件和替代动作；无证据不做预测性堆叠。

完成判据：每处改动能归属到诊断出的缺口或病灶；只动最小必要文件。

### 3. 核对

- **description 改动** → 核对 frontmatter、项目路由载体和直接调用方的触发语义一致；没有直接证据时，不把“触发更准”写成事实。power-agent 仓运行 `scripts/check-description-length.py` 校验长度上限，其他项目人工估算。
- **行为改动** → 读取相关 `SKILL.md`、references、调用方和 docs，确认目标、约束、输入/输出契约没有冲突或遗漏。
- **调用方式改动** → 核对 frontmatter 标志与项目 Skill 索引（人维护的速查表/登记处）一致；power-agent 仓运行 `scripts/check-invocation-consistency.sh`，其他项目人工核对。
- **no-op 裁决**：不能表达当前行为、约束或直接 consumer 需要的文字就是 no-op，删除而不改写。
- **成本边界**：优化以整条 Skill 链的 context/cognitive load 为准，不按单文件行数。

完成判据：改动后的契约、索引和直接引用一致；主张区分已观察事实与推断。

### 4. 同步

- **契约优先**：跨 Skill 交接明确上游输入字段、下游输出字段、状态枚举、缺失字段时如何降级或阻塞。上游模板和下游 prompt 对同一任务卡的要求不同时，先修契约，不靠执行时临时解释。
- **路由一致**：新增、删除、改名 Skill 或改动触发词时，grep 全仓对该 Skill 的引用（项目的路由载体：如 AGENTS.md、docs、其他 Skill 的引用段），逐处同步——路由信息撒谎比没有路由更糟。
- **配套同步**：frontmatter、插件 manifest 和相关 docs 按需更新。

完成判据：grep 无残留旧引用；契约两侧字段一致。

---

## 判据速查：五失败模式

审查既有 Skill 时先诊断得了哪种病，再选配对解药；判定拿不准或需要示例时读 criteria.md §7。

| 失败模式 | 一句话症状 | 解药 |
|---|---|---|
| **no-op** | 相对模型默认行为什么都没改变；弱词也算 | 整句删除，不改写；弱词换强词 |
| **duplication** | 同一含义多处存在 | 单一事实源；重复 token 是刻意的，重复含义才是病 |
| **sediment** | 只加不删，失效规则堆积 | 每次修改做逐行相关性检查 |
| **sprawl** | 每行都活、都独特，但总长失控 | 阶梯下沉 + 切分，不是压缩文字 |
| **negation** | “不要 X”反而让 X 更可用 | 正面表述；硬护栏例外配对替代动作 |

伴随判据 **co-location**：同一概念的定义、规则、警告同居一个标题下；散落在两个以上标题下就是碎片化。

---

## 完成前检查

- [ ] description 触发词合规：前置、无同义重复、无身份复述；长度 ≤ 约 110 token（目标 ~100）。
- [ ] 调用方式命中三个付费理由之一；user-invoked 已登记项目 Skill 索引，并已核对 frontmatter 与索引一致。
- [ ] 正文的每条规则都表达当前行为、约束或直接 consumer 需要；否定式禁令都是无法正面表述的硬护栏，且配对替代动作。
- [ ] 流程步骤都有可检查的完成判据。
- [ ] `SKILL.md` 无 TODO、TBD、占位路径或旧 Skill 名残留；references 路径真实存在。
- [ ] 上下游契约字段一致；全仓对该 Skill 的引用已同步。
- [ ] frontmatter / manifest / docs 已按需同步。

---

## 报告

按三态报告：`DONE / DONE_WITH_CONCERNS / BLOCKED`。变更附证据；风险如实写，没有就不写。
