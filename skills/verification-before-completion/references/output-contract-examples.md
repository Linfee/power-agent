<!-- verified: 2026-05-05 -->
<!-- scope: verification-before-completion, examples -->

# Output Contract Examples

## 1) DONE

```markdown
## 完成前验证结果

状态：DONE
commit_sha：abc1234
passed：true
verified_at：2026-05-05T07:10:00Z

### 证据
- [测试] pnpm test --filter auth
  - exit code：0
  - 时间：2026-05-05T07:10:00Z
  - 范围：目标模块
  - 摘要：auth 模块相关用例全部通过

### 阻塞项
- 无

### 非阻塞建议
- 合并前可按风险补一次全量回归

### 下一步
- 负责人：代理
- 动作：可以声称完成，并可将 verification_evidence 交给分支收尾
```

## 2) PARTIAL

```markdown
## 完成前验证结果

状态：PARTIAL
commit_sha：abc1234
passed：false
verified_at：2026-05-05T07:12:00Z

### 证据
- [检查] pnpm lint
  - exit code：0
  - 时间：2026-05-05T07:12:00Z
  - 范围：全仓库
  - 摘要：lint 通过，但没有覆盖声明行为

### 阻塞项
- [范围不匹配] 当前仅有 lint 证据，无法直接证明修复行为
  - 需要动作：运行覆盖声明行为的目标测试

### 非阻塞建议
- 可先跑目标模块测试，再决定是否补全量测试

### 下一步
- 负责人：代理
- 动作：补充与声明相关的行为验证
```

## 3) BLOCKED

```markdown
## 完成前验证结果

状态：BLOCKED
commit_sha：未提供
passed：false
verified_at：未提供

### 证据
- 无

### 阻塞项
- [无证据] 未发现本轮验证记录
  - 需要动作：先执行验证并记录证据

### 非阻塞建议
- 若为纯文档变更，可提供人工核对记录作为证据

### 下一步
- 负责人：代理
- 动作：执行最小充分验证后重新评估
```
