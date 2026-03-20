# 测试反模式

**加载时机：** 编写或修改测试、添加 mock、或想在生产代码中添加仅供测试用的方法时。

## 概述

测试必须验证真实行为，而非 mock 的行为。Mock 是隔离的手段，不是被测试的对象。

**核心原则：** 测试代码的行为，而不是 mock 的行为。

**严格执行 TDD 可以预防这些反模式。**

## 铁律

```
1. 绝不测试 mock 的行为
2. 绝不在生产类中添加仅供测试用的方法
3. 绝不在不理解依赖的情况下添加 mock
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
  问：「我是在测试真实组件行为还是只在验证 mock 存在？」

  如果是验证 mock 存在：
    停止——删除该断言或取消 mock

  改为测试真实行为
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
- 测试因为错误的原因通过，或者莫名奇妙地失败

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
  2. 问：「这个测试依赖其中任何副作用吗？」
  3. 问：「我完全理解这个测试需要什么吗？」

  如果依赖副作用：
    在更底层 mock（实际慢/外部的操作）
    或使用保留必要行为的测试替身
    不要 mock 测试所依赖的高层方法

  如果不确定测试依赖什么：
    先用真实实现运行测试
    观察实际需要发生什么
    然后在正确的层级添加最小化 mock

  警告信号：
    - 「mock 这个以防万一」
    - 「这可能很慢，最好 mock 掉」
    - 不理解依赖链就添加 mock
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
- **测试通过但集成失败** — mock 不完整，真实 API 完整
- **虚假的信心** — 测试对真实行为毫无证明

**铁律：** mock 完整的数据结构（与现实中存在的完全一致），而不仅仅是当前测试用到的字段。

**修复方案：**
```typescript
// ✅ 正确：镜像真实 API 的完整性
const mockResponse = {
  status: 'success',
  data: { userId: '123', name: 'Alice' },
  metadata: { requestId: 'req-789', timestamp: 1234567890 }
  // 真实 API 返回的所有字段
};
```

### 门控检查

```
在创建 mock 响应之前：
  检查：「真实 API 响应包含哪些字段？」

  行动：
    1. 查阅实际 API 响应文档或示例
    2. 包含系统下游可能消费的所有字段
    3. 验证 mock 与真实响应 schema 完全匹配

  关键：
    如果你在创建 mock，你必须理解整个结构
    不完整的 mock 在代码依赖遗漏字段时静默失败

  不确定时：包含所有文档记录的字段
```

## 反模式 5：测试是事后补丁

**违规写法：**
```
✅ 实现完成
❌ 没有写测试
「可以测试了」
```

**为什么错误：**
- 测试是实现的一部分，不是可选的后续工作
- TDD 本可以在实现过程中发现问题
- 没有测试就不能声称完成

**修复方案：**
```
TDD 循环：
1. 写失败的测试
2. 实现让测试通过
3. 重构
4. 然后才能声称完成
```

## 当 Mock 变得过于复杂时

**警告信号：**
- Mock 配置比测试逻辑更长
- Mock 了所有东西才能让测试通过
- Mock 缺少真实组件有的方法
- Mock 变化时测试就崩溃

**应该问的问题：** 「这里真的需要 mock 吗？」

**考虑：** 使用真实组件的集成测试往往比复杂的 mock 更简单

## TDD 如何预防这些反模式

**TDD 为什么有效：**
1. **先写测试** → 迫使你思考你究竟在测试什么
2. **看到失败** → 确认测试在测试真实行为，而不是 mock
3. **最小化实现** → 不会出现仅供测试用的方法
4. **真实依赖** → 你在 mock 之前就能看到测试真正需要什么

**如果你在测试 mock 的行为，说明你违反了 TDD** — 你在没有看到测试对真实代码失败之前就添加了 mock。

## 快速参考

| 反模式 | 修复方案 |
|--------|---------|
| 断言 mock 元素 | 测试真实组件或取消 mock |
| 生产代码中的测试专用方法 | 移到测试工具中 |
| 不理解就 mock | 先理解依赖，最小化 mock |
| 不完整的 mock | 完整镜像真实 API |
| 测试是事后补丁 | TDD——先写测试 |
| 过于复杂的 mock | 考虑集成测试 |

## 红色警报

- 断言检查 `*-mock` 测试 ID
- 方法只在测试文件中被调用
- Mock 配置占测试的 >50%
- 删除 mock 时测试崩溃
- 无法解释为什么需要 mock
- 「为了安全」而 mock

## 结论

**Mock 是隔离的工具，不是被测试的对象。**

如果 TDD 揭示你在测试 mock 的行为，说明你走错了方向。

修复：测试真实行为，或质疑为什么要 mock。
