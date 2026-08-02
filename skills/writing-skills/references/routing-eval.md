# Routing Eval — 路由评测格式与方法

description 触发改动的验证格式，随本 Skill 分发：任何项目可据此为自己的 Skill 集建评测集。

## 测什么

模型只看到 name + description 列表时，对给定用户输入是否选对 Skill（或正确地不选）。评测对象是 description，不是 Skill 本体。

## cases 格式

JSON 数组，每条：

```json
{
  "id": "discuss-positive-1",
  "input": "（真实用户口吻的一句话）",
  "expected_skill": "discuss 或 null",
  "kind": "positive | near_miss | far_negative",
  "note": "标注理由；near_miss 必须写明与哪个近邻 Skill 的边界"
}
```

分布要求：

- `positive`：每个 Skill ≥2 条。input 不复述 description 原文，否则测不出泛化只测出抄词。
- `near_miss` ≥10 条：落在两个易混淆 Skill 的边界上，`expected_skill` 是真正正确的一侧。
- `far_negative` ≥8 条：明显不应触发任何 Skill 的输入（纯代码提问、一次性命令、闲聊），`expected_skill = null`。

## 运行方法

1. **匿名化**：cases 按 id 字典序排序后重新分配匿名 id（`c001`、`c002`、…），judge 只看到匿名 id + input。原始 id 含 expected 与混淆对信息，直接喂给 judge 会泄露标注（power-agent 首轮基线曾因此得到失真的 100%，作废重跑）。
2. **judge**：每批 ≤5 条起一个 fresh 上下文子代理。固化 judge prompt：给出全部 Skill 的 name + description 逐字列表，要求逐条独立判断、互不影响，只输出 `[{"id","chosen"}]`。重跑对比时使用同一 judge 模型。
3. **判定**：`chosen == expected`（`null` 视为 `"none"`）为命中。汇总 overall accuracy、per-skill recall（仅 positive）、near_miss 单独正确率、混淆对（expected 与 chosen 都非 none 且不同）、误触发（far_negative 被判成某 Skill）、漏触发（positive/near_miss 被判 none）。
4. **复算**：保留每批 judge 原始输出；报告中的每个统计数字都必须能由 cases + 原始记录精确复算，复算脚本覆盖报告展示的全部指标。

## 已知边界

- **上限效应**：judge 与 cases 同族模型、input 含触发邻近词汇时，100% 不能外推为"description 无改进空间"，只说明本探针集对当前模型不构成区分。description 改造后重跑须守住上一轮成绩作为回归底线；持续补充更难的探针（不含触发词的转述、对抗性 near_miss、多意图输入、跨模型 judge）才能恢复区分度。
- **user-invoked Skill**：对模型不可见，其用例只衡量 description 语义区分度，不代表运行时路由；要评测运行时路由时把它们移出候选或单独处理。

## 与调用方式改动的关系

本评测不管 invocation mode：调用方式改变的是模型能否看到 description，靠 frontmatter 与项目 Skill 索引的一致性核对（见 `SKILL.md` 验证步），不在此格式覆盖范围内。
