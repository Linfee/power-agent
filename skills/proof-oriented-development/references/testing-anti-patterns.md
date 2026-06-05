# 测试与证明反模式

**加载时机：** 编写或修改测试、添加 mock、设计 Proof Block，或想在生产代码中添加仅供测试用的方法时。

## 概述

Proof Block 必须证明真实行为，而不是证明 mock、脚手架或测试替身本身能工作。Mock 是隔离的手段，不是被证明的对象。

**核心原则：** 证明真实行为，而不是证明测试装置。

strict TDD 能暴露很多反模式，但 proof-oriented development 不要求默认 strict TDD。disciplined test-after、targeted command、characterization case 或 golden diff 也可以成为有效证明，只要它们低成本、可复现、与任务强相关。

## 铁律

```
1. 绝不测试 mock 的行为
2. 绝不在生产类中添加仅供测试用的方法
3. 绝不在不理解依赖的情况下添加 mock
4. 绝不把未运行、不可复现或与任务弱相关的检查写成 Proof Block
```

## 反模式 1：测试 Mock 的行为

**违规写法：**
```typescript
// ❌ 错误：测试的是 mock 是否存在
test('渲染侧边栏', () => {
  render(<Page />);
  expect(screen.getByTestId('sidebar-mock')).toBeInTheDocument();
});
```

**为什么错误：**
- 你在验证 mock 能工作，而不是组件能工作
- mock 存在时测试通过，不存在时测试失败
- 对真实行为毫无反映

**修复方案：**
```typescript
// ✅ 正确：测试真实组件，或不要 mock 它
test('渲染侧边栏', () => {
  render(<Page />);  // 不要 mock 侧边栏
  expect(screen.getByRole('navigation')).toBeInTheDocument();
});

// 如果必须 mock 侧边栏以便隔离：
// 不要断言 mock 本身——测试侧边栏存在时 Page 的行为
```

### 门控检查

```
在断言任何 mock 元素之前：
  问：「我是在证明真实行为还是只在验证 mock 存在？」

  如果是验证 mock 存在：
    停止——删除该断言或取消 mock

  改为证明真实行为
```

## 反模式 2：在生产代码中添加仅供测试用的方法

**违规写法：**
```typescript
// ❌ 错误：destroy() 只在测试中使用
class Session {
  async destroy() {  // 看起来像生产 API！
    await this._workspaceManager?.destroyWorkspace(this.id);
    // ... 清理
  }
}

// 在测试中
afterEach(() => session.destroy());
```

**为什么错误：**
- 生产类被测试专用代码污染
- 在生产环境中被意外调用有风险
- 违反 YAGNI 和关注点分离
- 混淆了对象生命周期与实体生命周期

**修复方案：**
```typescript
// ✅ 正确：测试工具负责测试清理
// Session 没有 destroy()——在生产中它是无状态的

// 在 test-utils/ 中
export async function cleanupSession(session: Session) {
  const workspace = session.getWorkspaceInfo();
  if (workspace) {
    await workspaceManager.destroyWorkspace(workspace.id);
  }
}

// 在测试中
afterEach(() => cleanupSession(session));
```

### 门控检查

```
在向生产类添加任何方法之前：
  问：「这个方法只被测试用到吗？」

  如果是：
    停止——不要添加
    放到测试工具中

  问：「这个类拥有该资源的生命周期吗？」

  如果不是：
    停止——这个方法放错了类
```

## 反模式 3：不理解依赖就添加 Mock

**违规写法：**
```typescript
// ❌ 错误：Mock 破坏了测试逻辑
test('检测重复的服务器', () => {
  // Mock 阻止了测试依赖的配置写入！
  vi.mock('ToolCatalog', () => ({
    discoverAndCacheTools: vi.fn().mockResolvedValue(undefined)
  }));

  await addServer(config);
  await addServer(config);  // 应该抛出——但不会！
});
```

**为什么错误：**
- 被 mock 的方法有测试依赖的副作用（写入配置）
- 为了「安全」过度 mock 破坏了实际行为
- 测试因为错误的原因通过，或者莫名其妙地失败

**修复方案：**
```typescript
// ✅ 正确：在正确的层级 mock
test('检测重复的服务器', () => {
  // Mock 慢的部分，保留测试需要的行为
  vi.mock('MCPServerManager'); // 只 mock 慢的服务器启动

  await addServer(config);  // 配置被写入
  await addServer(config);  // 重复被检测 ✓
});
```

### 门控检查

```
在 mock 任何方法之前：
  停止——先不要 mock

  1. 问：「这个真实方法有哪些副作用？」
  2. 问：「这个 proof 依赖其中任何副作用吗？」
  3. 问：「我完全理解这个 proof 需要什么吗？」

  如果依赖副作用：
    在更底层 mock（实际慢/外部的操作）
    或使用保留必要行为的测试替身
    不要 mock proof 所依赖的高层方法

  如果不确定 proof 依赖什么：
    先用真实实现运行最小验证
    观察实际需要发生什么
    然后在正确的层级添加最小化 mock
```

## 反模式 4：不完整的 Mock

**违规写法：**
```typescript
// ❌ 错误：不完整的 mock——只有你认为需要的字段
const mockResponse = {
  status: 'success',
  data: { userId: '123', name: 'Alice' }
  // 缺少：下游代码使用的 metadata
};

// 之后：当代码访问 response.metadata.requestId 时崩溃
```

**为什么错误：**
- **不完整的 mock 隐藏了结构假设** — 你只 mock 了你知道的字段
- **下游代码可能依赖你没有包含的字段** — 静默失败
- **proof 通过但集成失败** — mock 不完整，真实 API 完整
- **虚假的信心** — proof 对真实行为毫无证明

**铁律：** mock 完整的数据结构（与现实中存在的完全一致），而不仅仅是当前 proof 用到的字段。

## 反模式 5：无纪律的事后补测

**违规写法：**
```
✅ 实现完成
❌ 没有目标约束
❌ 没有验收标准
❌ 没有运行命令或关键输出
「可以测试了」
```

**为什么错误：**
- proof 是实现交付的一部分，不是可选的后续装饰
- 没有可复现证明就不能声称完成
- 事后为了覆盖率补的测试容易与真实任务弱相关

**允许的 disciplined test-after：**
```
1. 实现前明确目标约束和验收标准
2. 做最小实现
3. 运行与任务强相关的最小验证
4. 在 Proof Block 中记录命令、结果、风险和未验证项
5. 然后才能声称当前增量完成
```

## 当 Mock 变得过于复杂时

**警告信号：**
- Mock 配置比 proof 逻辑更长
- Mock 了所有东西才能让验证通过
- Mock 缺少真实组件有的方法
- Mock 变化时 proof 就崩溃

**应该问的问题：** 「这里真的需要 mock 吗？」

**考虑：** 使用真实组件的集成验证、characterization case 或 golden diff 往往比复杂 mock 更简单。

## strict TDD 的位置

strict TDD 仍然有效，但它只是用户明确要求时的证明路径之一：

1. **先写失败测试** → 迫使你思考究竟要证明什么
2. **看到失败** → 确认证明针对真实代码，而不是 mock
3. **最小化实现** → 避免仅供测试用的方法
4. **重构后复验** → 保持行为证明稳定

如果用户没有明确要求 strict TDD，不要把高风险或复杂任务自动升级为 Red → Green → Refactor；应提高 Proof Block 的强度，例如增加目标测试、局部回归、日志、截图、CI 或 reviewer 可复查路径。

## 快速参考

| 反模式 | 修复方案 |
|--------|---------|
| 断言 mock 元素 | 证明真实组件行为或取消 mock |
| 生产代码中的测试专用方法 | 移到测试工具中 |
| 不理解就 mock | 先理解依赖，最小化 mock |
| 不完整的 mock | 完整镜像真实 API |
| 无纪律的事后补测 | 先定义 proof plan，再运行最小相关验证 |
| 过于复杂的 mock | 考虑集成验证、characterization 或 golden diff |

## 红色警报

- 断言检查 `*-mock` 测试 ID
- 方法只在测试文件中被调用
- Mock 配置占 proof 的 >50%
- 删除 mock 时验证崩溃
- 无法解释为什么需要 mock
- 「为了安全」而 mock
- Proof Block 写了 PASS，但没有命令、输出或可复查路径

## 结论

**Mock 是隔离的工具，不是被证明的对象。**

Proof Block 的目标是让 reviewer 或用户能够低成本复现并信任当前增量。修复测试反模式时，优先证明真实行为；如果 proof 只能证明 mock 或测试装置，说明方向错了。
