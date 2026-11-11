# 本地文件 tracker seed

供 setup 依据项目已有约定生成 `docs/agents/issue-tracker.md`；没有现成位置时由项目选择一个可写、稳定的本地目录，明确如何给文件分配稳定 ID 和定位父子关系。每个条目一个文件，spec/map 可关联子文件；不要求固定目录外形，也不把下载副本或会话待办当另一份状态。

每个条目顶部保存以下独立字段；`Blocked by` 列稳定 ID，无 blocker 时留空：

```text
Kind: spec | implementation | map | decision
State: open | active | done
Blocked by: <stable IDs>
Owner: <coordinator or empty>
Triage: <project role; only for external requests when needed>
```

上述竖线列的是可选值而非要写入的字面字符串；`Kind` 与 `State` 是不同维度，不把分诊角色塞进 `State`。正文保存目标、范围、验收和必要的父项 ID；map/decision 记录实际待解问题和结论。依 `Blocked by` 对应条目状态判断依赖；候选需 `open`、没有未完成 blocker、没有活跃 owner。

同一任务图只有一个协调者写认领、完成和依赖状态；子代理只交付结果。多会话缺少项目已有可靠原子认领能力时串行协调该图；唯一标记加重读不是原子锁，不引入锁服务。实现、证明及组合验收覆盖当前条目后才在获授权时将其设为 `done`；子项完成不自动关闭父 spec/map，未解决目标或其他活跃所有权不得冒领完成。
