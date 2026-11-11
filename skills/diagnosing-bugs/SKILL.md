---
name: diagnosing-bugs
description: 调查原因未明的故障、偶发失败、性能退化或意外行为；修复已明确时不必重启调查。
---

# Diagnosing Bugs

让症状可观察，用有区分力的证据定位原因，再在授权范围内修复或说明确切阻塞。已有项目术语和相关决定可帮助理解调用链；不要把静态可疑点当运行事实。

## 建立反馈

先明确用户观察到的症状、期望结果、环境和触发条件。尽可能复用最贴近原场景、可比较且成本合理的观察：失败测试、HTTP/CLI、浏览器、脱敏重放、好坏版本或配置差分、日志与 trace 都可以。按信息价值收紧输入与范围，但保留真正的故障机制。可运行的红色命令很有用，却不是提出或检验假设的前提；只有脱敏 trace 时也应分析事件链与差分。详见 [building-feedback-loops.md](references/building-feedback-loops.md)。

人必须操作时，可按需复制并调整 [HITL 模板](scripts/hitl-loop.template.sh)，让人执行最小操作并返回非敏感观察；不是调查入口的前提。准备前确认实际交互、超时、终端和可披露内容；不要让脚本收集凭证。不能得到区分性观察时，说明已尝试的方式和能解除缺口的最小条件，继续其他可做的调查。

## 解释与探针

先区分实际观察和候选解释。围绕主要解释提出可证伪预测，用 debugger、定向观测、对照或差分选取能区分它们的探针；控制或记录变量，使观察可归因。按信息价值最小化复现，不规定假设数、实验数或穷尽缩减。关联触发条件、第一处偏离、传播与用户症状；只有预测得到实际观察支持、主要替代解释被区分且因果链足以支持修复边界，才能称为根因。静态代码阅读或相关性本身不够。细节见 [root-cause-tracing.md](references/root-cause-tracing.md)。

临时 instrumentation 只采集必要信号、使用可搜索标识并脱敏；结束时清理无用探针、停止临时运行，必要的安全证据说明保留位置和处置。不得绕过安全控制、扩大权限或执行未授权的生产、破坏性操作；秘密和隐私不进入输出或共享产物。

## 修复与原场景

永久修复应落在产生偏离或拥有不变量的位置；用户授权事故止损时可先缓解，但分别验证和报告缓解与根因修复。适用时用 `proof-oriented-development` 实现回归保护，保留需要的调用链、并发和真实组件交互。原失败场景可安全重跑且覆盖风险时优先复跑；否则说明替代证据保留和省略的条件，区分代码证据与原环境尚未验收。最小复现仅在增加证据价值时重跑。

性能和 flaky 问题需同口径 workload、环境、频率或分布证据，单次绿色不足以证明修复；见 [performance-and-flakiness.md](references/performance-and-flakiness.md)。按需阅读 [condition-based-waiting.md](references/condition-based-waiting.md) 处理异步等待，[defense-in-depth.md](references/defense-in-depth.md) 判断独立防护责任。

报告可复查观察支持或排除了什么、实际修改与验证、剩余不确定性；证据不足时保持假设并指出具体阻塞，不假称根因或修复完成。

来源：融合 mattpocock/skills 的 engineering/diagnosing-bugs 与 Power-Agent 的 systematic-debugging。
