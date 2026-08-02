# evals/writing-skills — Skill 路由评测基线

## 目的

测量 power-agent 全仓 13 个 skill 的 `SKILL.md` description 的**触发质量**：模型只看到 name + description 列表时，对给定用户输入是否选对 skill（或正确地不选）。这是 writing-skills P0-2 description 改造的对比基准，同时暴露边界模糊的 description 对。

评测对象是 description，不是 skill 本体；judge 只拿到 name + description，拿不到 SKILL.md 正文。

## 文件

- `cases.json` — 标注数据集（46 条）。
- `judge-prompt.md` — 固化的 judge prompt 全文（含逐字 description 列表）。**改动 judge 逻辑必须先改这里。**
- `baseline-report.md` — 基线结果与分析（含 judge 原始记录的复算方法）。
- `scratch/` — judge 原始输出（每批一个文件），是报告数字的复算依据；不进交付物，可随时重建。

## cases.json 格式

JSON 数组，每条：

```json
{
  "id": "near-miss-discuss-vs-writing-plans-1",
  "input": "（真实用户口吻的一句话，中文为主）",
  "expected_skill": "discuss 或 null",
  "kind": "positive | near_miss | far_negative",
  "note": "标注理由；near_miss 必须写明与哪个近邻 skill 的边界"
}
```

- `positive`：应触发某 skill；每个 skill ≥2 条（13 × 2 = 26）。
- `near_miss`：落在两个易混淆 skill 的边界上，`expected_skill` 是真正正确的一侧（≥10 条，覆盖 6 组易混淆对：discuss↔writing-plans、implement↔proof-oriented-development、code-review↔verification-before-completion、dev-docs↔dev-docs-maintain、systematic-debugging↔proof-oriented-development、writing-skills↔harness-engineering-review）。
- `far_negative`：明显不应触发任何 skill（纯代码提问、一次性命令、闲聊），`expected_skill = null`（≥8 条）。

positive 的 input 不复述 description 原文，否则测不出泛化只测出抄词。

## 运行方法（如何重跑）

1. **准备批次**：把 `cases.json` 按 `id` 字典序排序，为每条分配匿名 id（`c001`、`c002`、…），再顺序切成每批 ≤5 条。每批构造 JSON，每条只含匿名 `id` 与 `input`。**必须匿名化**——cases.json 的原始 id 含 expected_skill 和混淆对信息，直接喂给 judge 会泄露标注（首轮基线曾因此得到失真的 100%，已作废重跑）。映射关系由排序规则确定，复算时按同一规则还原。
2. **逐批 judge**：每批起一个 fresh 上下文的子代理，prompt = `judge-prompt.md` 中 code block 的全文，把 `{CASES}` 替换为该批 JSON。要求 judge 逐条独立判断、互不影响。
   - judge 模型：基线使用会话默认模型（baseline-report.md 中注明具体模型）；重跑时应与所对比的报告使用同一模型。
3. **收集原始输出**：每批的完整原始返回存入 `scratch/batch-NN.md`。
4. **复算统计**：对每条 case 比较 `chosen` 与 `expected_skill`（`null` 视为 `"none"`），按下方判定规则汇总，更新报告。

## 判定规则

- **命中**：judge 输出的 `chosen` == `expected_skill`（far_negative 期望 `"none"`）。
- **混淆对**：`chosen` 与 `expected_skill` 都非 none 且不同，记录 `(expected → chosen)`。
- **误触发**：far_negative 被判成某个 skill。
- **漏触发**：positive/near_miss 被判成 none。
- 汇总指标：overall accuracy、per-skill recall（仅 positive）、near_miss 单独正确率、混淆对清单、误触发清单。

## 已知折衷

- 为控制成本每批 ≤5 条 case 共用一次 judge 调用，批内输入彼此可见；已通过 prompt 要求逐条独立判断。批间完全隔离（fresh 子代理）。
- 单次运行存在采样随机性；基线报告中的数字可由 `cases.json` + `scratch/` 原始记录精确复算，但重跑不保证逐位相同。
- 两个 `disable-model-invocation: true` 的 skill（setup-power-agent、harness-engineering-review）按任务要求与其他 11 个一样参与评测，judge 不知道该标志；其结果衡量的是 description 语义区分度，不代表运行时路由行为。
