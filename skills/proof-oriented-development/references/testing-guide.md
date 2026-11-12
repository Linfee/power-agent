# 行为测试与替身

设计测试、选择观察边界或隔离方式时使用。反面案例见 [testing-anti-patterns.md](testing-anti-patterns.md)。

## 测什么

好测试通过稳定的调用入口或真实副作用验证用户、调用者依赖的行为，描述做什么而不是如何实现；无关内部重构不应使它失败。围绕一个清晰行为组织测试，允许多个相关断言；期望来自规格、已知结果或独立事实，而不是重算被测实现。

例如 checkout 返回确认结果可验证可见行为；只断言内部 `paymentService.process` 被调用通常不能证明结账成功。但付款调用次数、消息顺序或持久化结果若是契约，也可以直接断言。优先从公开接口观察；当数据持久性或外部副作用本身是契约时，检查数据库或其他真实副作用同样有价值。

```typescript
// 行为：调用者能完成结账；内部支付实现可以更换。
test("user can checkout with valid cart", async () => {
  const cart = createCart();
  cart.add(product);
  const result = await checkout(cart, paymentMethod);
  expect(result.status).toBe("confirmed");
});

// 通常过于关注内部过程：调用过支付服务不等于结账成功。
test("checkout calls paymentService.process", async () => {
  const payment = fakePaymentService();
  await checkout(cart, payment);
  expect(payment.process).toHaveBeenCalledWith(cart.total);
});
```

第二个断言在「只能扣一次」或调用参数本身是外部契约时可能有价值，但还要验证结账的结果；不要把偶然的内部调用结构当作业务契约。

优先从接口验证数据能否被使用，而不只是验证实现碰过数据库：

```typescript
// 只查存储，可能遗漏读取接口的行为。
await createUser({ name: "Alice" });
expect(await db.query("SELECT * FROM users WHERE name = ?", ["Alice"])).toBeDefined();

// 从调用者入口创建并取回。
const user = await createUser({ name: "Alice" });
const retrieved = await getUser(user.id);
expect(retrieved.name).toBe("Alice");
```

如果持久化本身或跨进程重启后的可用性是契约，直接观察存储或重启后的结果也有意义，不能因它不是返回值就一概排除。

期望应独立于实现。测试中用同样的 `reduce` 计算 expected 会复制相同错误；已知输入与独立的结果才能发现求和缺陷：

```typescript
// BAD: 期望值按与实现相同的方式计算。
test("calculateTotal sums line items", () => {
  const items = [{ price: 10 }, { price: 5 }];
  const expected = items.reduce((sum, item) => sum + item.price, 0);
  expect(calculateTotal(items)).toBe(expected);
});

// GOOD: 15 是独立的已知结果。
test("calculateTotal sums line items", () => {
  expect(calculateTotal([{ price: 10 }, { price: 5 }])).toBe(15);
});
```

## 测试切入边界

从用户目标、契约和故障机制选择可观察入口：可以是模块接口、协议、原场景或副作用。回归须保留导致缺陷的调用链、并发或组件交互；过浅的通过不能证明缺陷修复。没有理想入口时利用现有边界或等价观察并说明缺失条件，不为测试方便硬造公开接口，也无需预先逐个向用户确认。

可自动化的行为变更默认在每个有意义的纵向切片中先观察相关失败，再实现、变绿；重构留到 review 阶段，在行为覆盖更完整时进行。既有失败、绿色行为重构及不能机械自动化的例外按主文件处理；不规定每轮恰好一个测试。

例如新增订单折扣，不要先写满普通折扣、过期、叠加、退款等所有测试，再猜测接口做完整实现。先让「有效折扣使订单总额从 100 降到 90」穿过调用入口并通过；根据真实接口和这个周期发现的约束，再验证过期或叠加等下一项行为。每次反馈帮助确定测试是否处在正确层次，也让失败更容易归因。若需求和接口已经清楚，一组相关断言可同轮进行；关键是不要在尚未验证重要假设时堆积整套想象出来的接口。

## 何时隔离

依据副作用和真实契约选择替身：外部 API、数据库、文件系统、时间、随机数或自己拥有的远程组件都可能需要隔离；进程内确定性协作优先真实对象。必要时也可替换昂贵、不可达或不稳定的内部依赖，但不能替换掉正要验证的交互。替身只能证明它保留的行为，真实协议或集成风险须另有相应证据。

优先复用已有接口和组装方式；有真实运行边界或消费者需要时，传入外部依赖或用表达业务操作的窄接口收敛协议处理。不要只为了方便 mock 加公开 wrapper、通用 fetcher 或多态层，也不要将一切内部对象强制注入。

### 替身和接口示例

对外部付款服务，可以将已存在的客户端在组装时传入，让测试用可控响应覆盖成功与失败，而不向真实账户收费：

```typescript
function processPayment(order, paymentClient) {
  return paymentClient.charge(order.total);
}

test("returns the payment result", async () => {
  const paymentClient = {
    charge: async amount => ({ status: amount === 90 ? "paid" : "rejected" }),
  };
  expect(await processPayment({ total: 90 }, paymentClient))
    .toEqual({ status: "paid" });
});
```

若函数内部每次直接创建 `new StripeClient(process.env.STRIPE_KEY)`，测试既难控制响应，也可能意外访问真实服务。是否抽出依赖仍取决于真实组装和生命周期，而非每个函数都要注入。测试替身模拟的只是其声明的响应；另用适当的协议或集成验证确认真实服务契约。

确需收敛多个外部操作时，业务命名的窄接口通常比要求所有测试解析 URL 和请求体的通用 fetcher 更容易理解：

```typescript
const api = {
  getUser: id => fetch(`/users/${id}`),
  getOrders: userId => fetch(`/users/${userId}/orders`),
  createOrder: data => fetch('/orders', { method: 'POST', body: data }),
};
```

这样每个替身可以只返回对应操作的结构，测试也能看出操作意图。相反，让 fake 的单个 `fetch(endpoint, options)` 通过条件分支模拟整个服务，容易重建另一套实现。这里不是要求为所有 `fetch` 添加 wrapper：已有 SDK 或直接调用更简单且满足真实边界时就复用它。
