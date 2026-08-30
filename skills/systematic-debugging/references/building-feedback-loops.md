# 构造可区分的反馈循环

反馈循环的作用是快速判断目标症状是否出现，以及一次探针是否改变了它。它不等同于失败测试，也不要求所有问题都能在本地运行。

## 选择 observation boundary

优先复用最贴近真实症状、成本最低且能重复观察的边界：

1. 在正确 seam 上已有或可构造的失败测试；
2. 对开发服务执行 curl / HTTP 请求并断言响应或副作用；
3. CLI + 固定 fixture，对 stdout、exit code、文件或数据结果做精确比较；
4. Headless browser，观察 DOM、console、network 或用户可见状态；
5. 重放已脱敏的请求、消息、事件或 trace；
6. 只启动必要组件的 throwaway harness；
7. property、fuzz 或 stress loop，用频率和输入缩小不稳定症状；
8. 已知好坏版本、配置或数据集之间的 bisection / differential loop；
9. 生产或外部系统的日志、trace、事件 ID、快照与真实副作用差分；
10. 最后才使用结构化 HITL，由人执行最小动作并返回同口径观察。

顺序是启发式，不是固定菜单。选择能最大幅度降低当前不确定性、且不越过安全和授权边界的方法。

## 收紧 loop

已有 loop 后继续检查：

- **精确**：断言用户报告的症状，不以“没崩溃”或退出码 0 替代业务结果；
- **可区分**：结果能支持或排除至少一个当前解释；
- **可重复**：记录命令或 observation boundary、输入、环境和前置条件；
- **稳定**：固定或记录时间、随机种子、并发、依赖和外部状态；
- **快速**：缓存无关初始化、缩小输入和组件，但不切断真实失败机制；
- **安全**：脱敏敏感值，不为调试扩大权限或改变生产安全语义。

本地不可运行时，“收紧”可以表现为提高 trace 关联度、保留同一事件链、获取可比较的成功/失败 artifact，而非强造本地失败测试。

## 最小复现

最小化用于缩小假设空间。逐次移除输入、调用者、配置、数据和步骤，每次都用同一 loop 复验。完成判据是：每个剩余元素都对症状 load-bearing；再移除任一元素都会让症状消失或无法被观察。

记录 minimal 保留和省略了什么，并映射到 original。minimal 是诊断工具，original 是修复后的真实验证锚点。

## 竞争解释与探针

高歧义时使用以下轻量记录；不要求固定候选数量：

| explanation | prediction | probe | observation | verdict |
|---|---|---|---|---|
| 若 X 是原因 | 改变 Y 后症状应消失或增强 | 只改变 Y | 实际结果 | supported / weakened / rejected |

一次 probe 只改变一个与 prediction 相关的变量。没有可证伪 prediction 的解释仍是猜测；日志数量增加但不能区分解释，不算进展。

## Flaky 与性能

Flaky 的目标是获得可比较的复现率，而非一次干净失败。记录失败频率、样本条件和受控变量；stress、并行或 sleep 只能作为探针，并需说明它们如何改变系统。单次绿色不能证明根因或修复。

性能问题先定义同 workload、环境、指标和测量边界的 baseline。profile、query plan 或 bisect 用于区分原因；功能正确不能替代性能证据。详细约束见 `performance-and-flakiness.md`。

## 临时 instrumentation

只有现有观测无法区分解释时才增加 instrumentation，并让每个观测点对应一个 prediction。使用唯一、可搜索的 tag，例如 `[DEBUG-a4f2]`，控制采集范围并脱敏。

调查终止前按 tag 或明确路径清理。只要本轮创建过临时产物，无论最终删除还是保留，都逐项记录位置或标识、敏感性/安全影响、`removed | retained` disposition、保留原因（仅 retained）、责任人和处置验证。没有创建时省略该字段，不为证明 `not_applicable` 额外扫描工作区。

## 无法建立有效 loop

明确列出已经尝试的 observation boundary 和失败原因。请求能真正解除缺口的最小条件，例如环境访问、脱敏 HAR/trace/core dump、带时间戳的录屏，或新增最小生产观测的专项授权。没有区分性 observation boundary 时如实报告仍在调查中，或在调查动作受阻时停下说明缺口，不要靠代码阅读直接升级为根因。
