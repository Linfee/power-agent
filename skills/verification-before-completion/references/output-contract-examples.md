# Output Contract Examples

## 1) 通过

```yaml
status: 通过
evidence:
  - type: 测试
    command: pnpm test --filter auth
    exit_code: 0
    timestamp: 2026-04-21T07:10:00Z
    scope: 目标模块
    summary: auth 模块相关用例全部通过
blocking_issues: []
advisories:
  - 建议在合并前补一次全量回归测试
next_action:
  owner: 代理
  action: 可以声称完成
```

## 2) 部分通过

```yaml
status: 部分通过
evidence:
  - type: 检查
    command: pnpm lint
    exit_code: 0
    timestamp: 2026-04-21T07:12:00Z
    scope: 全仓库
    summary: lint 通过
blocking_issues:
  - code: 范围不匹配
    message: 当前仅有 lint 证据，无法直接证明修复行为
    required_action: 运行覆盖声明行为的测试
advisories:
  - 可先跑目标模块测试，再决定是否补全量测试
next_action:
  owner: 代理
  action: 补充与声明相关的行为验证
```

## 3) 阻塞

```yaml
status: 阻塞
evidence: []
blocking_issues:
  - code: 无证据
    message: 未发现本轮验证记录
    required_action: 先执行验证并记录证据
advisories:
  - 若为纯文档变更，可提供人工核对记录作为证据
next_action:
  owner: 代理
  action: 执行最小充分验证后重新评估
```
