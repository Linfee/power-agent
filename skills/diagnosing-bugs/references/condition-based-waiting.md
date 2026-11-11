# 基于条件的等待

固定延迟只能表明时间经过，不能证明异步工作已经完成。需要结果就等待真实结果；需要验证时间契约，就控制或测量该时间契约。

## 选择等待方式

- 优先复用宿主或测试框架的等待断言、事件订阅和完成 promise；在触发动作前建立订阅，避免错过事件。
- 防抖、节流、重试间隔等时间行为优先使用框架支持的可控时钟，并推进到契约规定的时点。测试真实调度时记录时钟、负载和允许误差。
- 只有缺少合适的事件或等待能力时才轮询。按状态变化速度、查询成本、可接受延迟与总时间预算选择间隔，不使用统一频率。
- 等待应有有界超时和明确失败信息；框架已有超时能力时直接复用。取消或超时后释放本次订阅、计时器等资源。

## 等待真实条件

```typescript
// 固定延迟无法证明结果已到达。
await new Promise(resolve => setTimeout(resolve, 50));
expect(getResult()).toBeDefined();

// 优先使用项目测试框架已有的等待断言。
// 以下 waitFor 示意缺少框架能力时的轮询，预算由调用场景提供。
await waitFor(() => getResult(), '操作结果', { timeoutMs, pollIntervalMs });
```

条件应对应当前操作的可观察结果，例如指定请求的完成事件、目标状态、所需条目数或已落盘的文件。每次检查读取新状态；事件历史中已有的同名事件不能证明本次操作完成，必要时按请求 ID 或序号关联。

## 轮询示例

下例针对同步、低成本的本地读取。`undefined` 表示尚未就绪；`0`、空字符串等可以是有效结果。超时约束等待调度，不能中断阻塞的 getter；网络查询应使用自身的超时或取消机制。

```typescript
async function waitFor<T>(
  condition: () => T | undefined,
  description: string,
  options: { timeoutMs: number; pollIntervalMs: number }
): Promise<T> {
  const { timeoutMs, pollIntervalMs } = options;
  if (!Number.isFinite(timeoutMs) || timeoutMs < 0 ||
      !Number.isFinite(pollIntervalMs) || pollIntervalMs <= 0) {
    throw new RangeError('等待预算须为有限非负数，轮询间隔须为有限正数');
  }
  const deadline = performance.now() + timeoutMs;

  while (true) {
    const result = condition();
    if (result !== undefined) return result;

    const remainingMs = deadline - performance.now();
    if (remainingMs <= 0) {
      throw new Error(`等待 ${description} 超时（${timeoutMs}ms）`);
    }
    await new Promise(resolve =>
      setTimeout(resolve, Math.min(pollIntervalMs, remainingMs))
    );
  }
}
```

## 核对结果

等待通过只证明所观察条件出现。仍须断言用户关心的输出与副作用；不稳定性修复需要与风险相称的可比较样本，不能从一次通过推导“消除了所有竞态”。

当目标是等到两次事件发生时，应按事件数量等待。仅当目标确实是检查某段时间窗口内的行为，才等待或推进该窗口，并说明时间依据与预期观察。
