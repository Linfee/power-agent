# Stress Scenarios — writing-skills

用于验证本 Skill 的行为边界。格式：输入 → 无 Skill 易错行为 → 期望行为 → 验收点。

## 场景：新建一个只需要手动触发的工具型 Skill

- 输入：用户要求新建一个"初始化项目配置"类 Skill，明确说"我手动跑就行"。
- 易错行为：默认 model-invoked，写长 Triggers 列表，常驻上下文。
- 期望行为：判定为 user-invoked（`disable-model-invocation: true`），description 改为面向人类的一句话摘要，并在 `AGENTS.md` 速查表登记。
- 验收点：frontmatter 含 `disable-model-invocation: true`；description 无触发词列表；AGENTS.md 有新条目。

## 场景：给现有 Skill 加规则

- 输入：用户说"这个 skill 再补一条：验证前要检查 X"。
- 易错行为：直接追加，不检查是否与现有内容重复、是否有可删的旧规则。
- 期望行为：先定位该规则的含义是否已存在（单一事实源）；加入新规则时顺手做 no-op 测试和沉积检查，删掉失效内容。
- 验收点：同一含义只在一处；被删内容在交付说明中列出；不是纯增量 diff。

## 场景：description 堆同义触发词

- 输入：审查一个 description 为"需求讨论、需求分析、PRD 细化、产品讨论时使用"的 Skill。
- 易错行为：认为触发词越多越好，全部保留。
- 期望行为：识别为同一触发分支的同义重复，收敛为真正不同的分支；确认前置词承担主要触发工作。
- 验收点：修改后的 description 中每个触发词对应一个可区分的触发分支。
