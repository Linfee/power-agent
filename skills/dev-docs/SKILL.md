---
name: dev-docs
description: |-
  开发文档创建 Skill。创建或更新 docs/ 下的开发文档；用户要求写架构文档、决策记录、领域文档或开发文档时触发。
  Triggers: 写文档, 更新文档, 维护 docs, 架构文档, 决策记录, 领域文档, dev-docs.
disable-model-invocation: true
---

# 创建开发文档

在项目的 `docs/` 知识库中创建结构化文档。所有文档服务于一个目标：让 Agent（和工程师）仅凭仓库内容就能理解全局。

---

## 文档类型识别

根据用户输入判断类型，类型不明确时询问：

| 类型            | 关键词                    | 输出位置                                 |
| --------------- | ------------------------- | ---------------------------------------- |
| exec-plan       | 计划/重构/迁移/实现/spec  | → **委派给 `writing-plans` skill**       |
| architecture    | 架构/模块/系统/组件       | `docs/architecture.md` 或 `docs/domain/` |
| adr | 决策/选型/方案/权衡/ADR   | `docs/adr/0001-slug.md`  |
| domain          | 前端/安全/API/数据库/部署 | `docs/domain/[name].md`                  |
| development     | 开发/搭建/环境/命令       | `docs/development.md`                    |
| reference       | 参考/外部/集成/第三方     | `docs/references/[name].md`              |

---

## exec-plan 路径

**识别到 exec-plan 类型时，立即委派给 `writing-plans` skill，不在本 skill 内处理。**

将用户的原始需求和上下文完整传递给 writing-plans。

---

## 其他文档路径

### 不应文档化的内容

以下内容默认不写入 `docs/`：
- 临时讨论结论或一次性调试过程
- 可直接从当前代码推导的信息
- 仅对当前会话有效的执行细节

### 执行流程

1. **预检**
   - 确认 `docs/` 目录存在，`AGENTS.md` 已加载。
   - 仅按需加载最小上下文（目标文档与相关 ADR）。
2. **代码核对**
   - 按主题启动 `explore` 子代理，收集必要证据（关键文件路径、模块边界、数据流）。
3. **优先更新，再新建**
   - 优先更新已有文档；仅在不存在对应文档时新建。
4. **写入最小结构**
   - 普通 docs 文档必须包含元信息：

```markdown
<!-- verified: YYYY-MM-DD -->
<!-- scope: [对应范围] -->
```

   - ADR 不写 `verified` / `scope`；需要表达状态时可写 `<!-- status: accepted | proposed | superseded -->`。

5. **ADR 联动**
   - `adr` 不维护强制索引；编号时扫描 `docs/adr/` 当前最大编号并递增。
   - 仅当新增路径时更新 `AGENTS.md` 导航。

### 输出格式

完成任务后，用便于阅读的 Markdown 小节输出结果，不使用 YAML：

```markdown
## 文档创建结果

状态：DONE / BLOCKED

### 证据
- [diff / file] <file_path>

### 阻塞项
- DOC-xxx：<阻塞原因>

### 非阻塞建议
- <建议内容>

### 下一步
- 动作：proceed / clarify
- 负责人：user / orchestrator
```
