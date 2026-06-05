<!-- verified: 2026-06-03 -->
<!-- scope: plan-impl-lightweight, scope-check -->

# Lightweight Scope Check Template

在执行任何实现前填写。缺少关键字段时不要启动实现。

```markdown
## Lightweight Scope Check

结论：LIGHTWEIGHT_OK / USE_FULL_RUNNER / ASK_USER
原因：<一句话说明>

### 任务边界
- 目标行为是否明确：yes/no
- allowed_scope 是否明确：yes/no
- forbidden_scope 是否明确：yes/no
- 完成判据是否明确：yes/no
- 验证方式是否明确：yes/no

### 风险检查
- 是否涉及认证/授权/密钥/支付/数据一致性：yes/no
- 是否涉及数据迁移、schema migration 或存储格式：yes/no
- 是否涉及公共 API 大改或架构决策：yes/no
- 是否需要多个实现代理并行：yes/no
- 是否存在共享文件或共享出口冲突风险：yes/no
- 当前工作树是否能区分本次任务边界：yes/no

### 执行建议
- execution_mode：MAIN_AGENT / SINGLE_IMPLEMENTER / NONE
- targeted_verify：<命令或可观察验证方式>
- optional_review：skip / self_review / single_reviewer

### 下一步
- 动作：execute / ask_user / use_full_runner
- 交棒给：orchestrator / plan-impl / user
```

## 判定规则

- 关键边界与验证方式都明确，且风险检查均为低风险：`LIGHTWEIGHT_OK`。
- 目标、范围、完成判据或验证方式缺失：`ASK_USER`。
- 发现高风险、复杂依赖、多代理并行需求或共享改动面不可控：`USE_FULL_RUNNER`。
