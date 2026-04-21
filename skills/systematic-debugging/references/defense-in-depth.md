# 纵深防御验证

## 概述

修复由无效数据引起的 Bug 时，在一个地方添加验证看起来已经足够了。但单个检查可能被不同的代码路径、重构或 mock 绕过。

**核心原则：** 在数据流经的每一层都添加验证。让 Bug 在结构上不可能发生。

## 为什么需要多层防御

单层验证："我们修复了这个 Bug"  
多层防御："我们让这个 Bug 不可能再发生"

不同的层捕获不同的情况：
- 入口验证捕获大多数 Bug
- 业务逻辑捕获边界情况
- 环境守卫防止特定上下文的危险操作
- 调试日志在其他层失效时提供帮助

## 四层防御

### 第一层：入口验证
**目的：** 在 API 边界拒绝明显无效的输入

```typescript
function createProject(name: string, workingDirectory: string) {
  if (!workingDirectory || workingDirectory.trim() === '') {
    throw new Error('workingDirectory 不能为空');
  }
  if (!existsSync(workingDirectory)) {
    throw new Error(`workingDirectory 不存在: ${workingDirectory}`);
  }
  if (!statSync(workingDirectory).isDirectory()) {
    throw new Error(`workingDirectory 不是目录: ${workingDirectory}`);
  }
  // ... 继续执行
}
```

### 第二层：业务逻辑验证
**目的：** 确保数据对该操作有意义

```typescript
function initializeWorkspace(projectDir: string, sessionId: string) {
  if (!projectDir) {
    throw new Error('初始化工作空间需要 projectDir');
  }
  // ... 继续执行
}
```

### 第三层：环境守卫
**目的：** 防止在特定上下文中执行危险操作

```typescript
async function gitInit(directory: string) {
  // 测试环境中，拒绝在临时目录之外执行 git init
  if (process.env.NODE_ENV === 'test') {
    const normalized = normalize(resolve(directory));
    const tmpDir = normalize(resolve(tmpdir()));

    if (!normalized.startsWith(tmpDir)) {
      throw new Error(
        `测试期间拒绝在临时目录之外执行 git init: ${directory}`
      );
    }
  }
  // ... 继续执行
}
```

### 第四层：调试诊断
**目的：** 捕获上下文信息用于排查

```typescript
async function gitInit(directory: string) {
  const stack = new Error().stack;
  logger.debug('即将执行 git init', {
    directory,
    cwd: process.cwd(),
    stack,
  });
  // ... 继续执行
}
```

## 应用模式

发现 Bug 时：

1. **追踪数据流** — 错误值从哪里产生？在哪里被使用？
2. **绘制检查点** — 列出数据流经的所有位置
3. **在每一层添加验证** — 入口、业务、环境、调试
4. **测试每一层** — 尝试绕过第一层，验证第二层能捕获

## 真实案例

**Bug：** 空的 `projectDir` 导致 `git init` 在源码目录执行

**数据流：**
1. 测试初始化 → 空字符串
2. `Project.create(name, '')`
3. `WorkspaceManager.createWorkspace('')`
4. `git init` 在 `process.cwd()` 执行

**添加的四层防御：**
- 第一层：`Project.create()` 验证非空、存在、可写
- 第二层：`WorkspaceManager` 验证 projectDir 非空
- 第三层：`WorktreeManager` 在测试中拒绝在 tmpdir 之外执行 git init
- 第四层：git init 之前记录堆栈跟踪

**结果：** 全部 1847 个测试通过，Bug 不可能再复现

## 关键洞见

四层防御都是必要的。测试过程中，每一层捕获了其他层遗漏的 Bug：
- 不同的代码路径绕过了入口验证
- Mock 绕过了业务逻辑检查
- 不同平台上的边界情况需要环境守卫
- 调试日志识别出了结构性误用

**不要只在一个地方添加验证。** 在每一层都添加检查。
