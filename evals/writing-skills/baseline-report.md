# Baseline Report — writing-skills 路由评测基线

日期：2026-08-02 ｜ 评测对象：13 个 `skills/*/SKILL.md` frontmatter description（采集当日版本）｜ judge 模型：会话默认模型 `cpa/kimi-k3`（task 子代理，fresh 上下文）

## 方法

1. `cases.json`（46 条）按 `id` 字典序排序，分配匿名 id `c001`–`c046`（映射存 `scratch/id-mapping.json`），切成 10 批（9 批 × 5 条 + 1 批 × 1 条），每批输入只含匿名 `id` + `input`，judge 看不到 `expected_skill`/`kind`/`note`。
2. 每批起一个 fresh 子代理，prompt 为 `judge-prompt.md` 中 code block 全文（`{CASES}` 替换为该批 JSON），要求逐条独立判断、只输出 `[{"id","chosen"}]`。
3. 完整跑了两轮（rep1：`scratch/batch-01..10.md`；rep2：`scratch/rep2-batch-01..10.md`），用于检验采样稳定性。
4. 匿名 id 经映射还原后与 `expected_skill` 比对（`null` 视为 `"none"`）。

**方法学备注（首轮作废）**：最初一轮直接把 cases.json 原始 id 喂给 judge，而 id 含 expected_skill 与混淆对信息（如 `positive-code-review-1`），造成标注泄露，得到失真的 100% 后作废；匿名化重跑即为本报告数据。该教训已固化进 README 运行方法。

**已知折衷**：每批 ≤5 条共用一次 judge 调用（成本控制），批内输入彼此可见但 prompt 要求独立判断；批间完全隔离。

## 结果

| 指标 | rep1 | rep2 |
|---|---|---|
| overall accuracy | **46/46 = 100%** | **46/46 = 100%** |
| near_miss 正确率 | **12/12 = 100%** | **12/12 = 100%** |
| far_negative 误触发 | 0/8 | 0/8 |
| 混淆对（expected → chosen） | 无 | 无 |
| 漏触发（判成 none） | 无 | 无 |

两轮逐条比对：**零分歧**（46/46 完全一致）。

per-skill recall（positive，每 skill 2 条）：13 个 skill 全部 2/2 = 100%——code-review、dev-docs、dev-docs-maintain、discuss、finishing-a-development-branch、harness-engineering-review、implement、proof-oriented-development、setup-power-agent、systematic-debugging、verification-before-completion、writing-plans、writing-skills。

## 复算方法

```bash
cd evals/writing-skills
python3 - <<'EOF'
import json, re, glob, collections
mapping = json.load(open('scratch/id-mapping.json'))
cases = {c['id']: c for c in json.load(open('cases.json'))}
chosen = {}
for f in sorted(glob.glob('scratch/batch-??.md')):   # rep2 用 scratch/rep2-batch-??.md
    arr = json.loads(re.search(r'```json\n(.*?)\n```', open(f).read(), re.S).group(1))
    for e in arr: chosen[mapping[e['id']]] = e['chosen']
assert set(chosen) == set(cases)
hits, nm_hit, nm_tot = 0, 0, 0
per = collections.defaultdict(lambda: [0, 0])
confusions, false_triggers, misses = [], [], []
for cid, c in cases.items():
    exp = c['expected_skill'] or 'none'
    ok = chosen[cid] == exp
    hits += ok
    if c['kind'] == 'positive':
        per[exp][0] += ok; per[exp][1] += 1
    if c['kind'] == 'near_miss':
        nm_hit += ok; nm_tot += 1
    if not ok:
        if c['kind'] == 'far_negative': false_triggers.append((cid, chosen[cid]))
        elif chosen[cid] != 'none': confusions.append((cid, exp, chosen[cid]))
        else: misses.append(cid)
print(f'overall {hits}/{len(cases)}')
print(f'near_miss {nm_hit}/{nm_tot}')
for s in sorted(per): print(f'recall {s}: {per[s][0]}/{per[s][1]}')
print('confusions:', confusions)
print('false_triggers:', false_triggers)
print('misses:', misses)
EOF
```

该脚本输出本报告全部统计数字（overall、near_miss、per-skill recall、混淆对、误触发、漏触发），对 rep1/rep2 各跑一遍即可逐位复核上文表格。

## 发现

1. **现状 description 在本探针集上达到上限且稳定**：两轮独立运行逐条一致，13 个 skill 的 recall、6 组易混淆对的 near_miss、8 条 far_negative 全部判对。当前 description 未表现出可观测的路由错误。
2. **"Triggers:" 关键词行承担了主要区分度**：description 末尾的触发词列表与用户输入的词汇高度可匹配（如"根因"→systematic-debugging、"exec-plan"→writing-plans）。near_miss 全对说明 judge 在边界案例上主要靠语义句而非仅关键词判定，但关键词行显然降低了区分难度。
3. **静态可观察的词汇重叠对（本次未造成误判，属改造期风险点）**：
   - `implement` ↔ `proof-oriented-development`：都含"实现/验证"语义，靠"是否有现成计划"区分；
   - `dev-docs` ↔ `dev-docs-maintain`：都以 `docs/` 长期知识为对象，且都使用"不要用于裸写文档/执行计划"的否定句式，正面职责（写入 vs 检查/登记）是主要区分点；
   - `code-review` ↔ `verification-before-completion`：都出现在"完成/合并前"语境，区分点是审查对象（代码 vs 证据）；
   - `writing-skills` ↔ `harness-engineering-review`：都含"审查"，区分点是对象粒度（单个 skill vs 整体工作流）；
   - `discuss` ↔ `writing-plans`、`systematic-debugging` ↔ `proof-oriented-development`：靠"结论是否已定/根因是否已明"区分。
4. **上限效应的解读边界**：cases 由与 judge 同族的模型撰写，input 虽不复述 description 原文但仍含触发邻近词汇；100% 不能外推为"description 无改进空间"，只能说明**本探针集对当前模型不构成区分**。
5. **两个 `disable-model-invocation: true` skill（setup-power-agent、harness-engineering-review）被当作普通可路由项参与评测**：judge prompt 未暴露该标志（任务卡规定 13 个 skill 全量参与、每个 ≥2 positive）。因此这两个 skill 的 2/2 recall 衡量的是 description 语义区分度，**不代表运行时路由行为**——真实 harness 中它们只能由人手动触发。它们作为干扰项未造成任何误触发（0/46），但不能外推；后续若评测运行时路由，应把这两个 skill 移出候选或单独评测。
6. **对 P0-2 的使用方式**：description 改造（如四要素格式）后重跑本评测，**100%/100% 是必须守住的回归底线**；同时应扩充更难的探针（不含触发词的转述、对抗性 near_miss、多意图输入、跨模型 judge）才能让评测恢复区分度。

## 数据与产物

- 标注数据：`cases.json`（46 条：positive 26 / near_miss 12 / far_negative 8）。
- judge prompt：`judge-prompt.md`（含逐字 description 列表）。
- 原始记录：`scratch/batch-01..10.md`（rep1）、`scratch/rep2-batch-01..10.md`（rep2）、`scratch/id-mapping.json`、`scratch/batch-*-input.json`。
