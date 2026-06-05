<!-- verified: 2026-05-05 -->
<!-- scope: verification-before-completion, examples -->

# Output Contract Examples

## 1) DONE — Proof Block accepted

```markdown
## 完成前验证结果

状态：DONE
commit_sha：abc1234
passed：true
verified_at：2026-05-05T07:10:00Z

### Proof Block 审计
- 是否提供：是
- 完整性：完整
- 相关性：强相关
- 可复现性：可复现
- 未验证项影响：无影响
- 结论：accepted

### 证据
- [proof_block_audit] proof_block:inline
  - source：proof_block
  - exit code：not_applicable
  - 时间：2026-05-05T07:10:00Z
  - 范围：目标模块
  - 摘要：accepted；Proof Block 完整、验证命令与声明强相关，未验证项为无

### 阻塞项
- 无

### 非阻塞建议
- 合并前可按风险补一次全量回归

### 下一步
- 负责人：代理
- 动作：proceed_to_finishing-a-development-branch
```

## 2) DONE — Proof Block + extra verification

```markdown
## 完成前验证结果

状态：DONE
commit_sha：abc1234
passed：true
verified_at：2026-05-05T07:12:00Z

### Proof Block 审计
- 是否提供：是
- 完整性：部分
- 相关性：强相关
- 可复现性：部分可复现
- 未验证项影响：可接受
- 结论：needs_more_verification

### 证据
- [proof_block_audit] proof_block:inline
  - source：proof_block
  - exit code：not_applicable
  - 时间：2026-05-05T07:12:00Z
  - 范围：变更文件
  - 摘要：needs_more_verification；Proof Block 缺少引用一致性检查，目标约束从任务卡映射
- [检查] rg -n "Proof Block 审计" skills/verification-before-completion
  - source：vbc_extra_verification
  - exit code：0
  - 时间：2026-05-05T07:12:00Z
  - 范围：目标模块
  - 摘要：补充契约字段检查通过

### 阻塞项
- 无

### 非阻塞建议
- 无

### 下一步
- 负责人：代理
- 动作：proceed_to_finishing-a-development-branch
```

## 3) PARTIAL — Proof Block has non-core gaps

```markdown
## 完成前验证结果

状态：PARTIAL
commit_sha：abc1234
passed：false
verified_at：2026-05-05T07:15:00Z

### Proof Block 审计
- 是否提供：是
- 完整性：部分
- 相关性：强相关
- 可复现性：可复现
- 未验证项影响：可接受
- 结论：needs_more_verification

### 证据
- [proof_block_audit] proof_block:inline
  - source：proof_block
  - exit code：not_applicable
  - 时间：2026-05-05T07:15:00Z
  - 范围：目标模块
  - 摘要：needs_more_verification；目标测试通过，但未覆盖非核心浏览器路径

### 阻塞项
- [Proof Block 不足] 当前证据未覆盖非核心浏览器路径
  - 需要动作：按风险决定是否补浏览器验证

### 非阻塞建议
- 若该路径属于发布前验收，应补最小浏览器验证

### 下一步
- 负责人：代理
- 动作：rerun_minimal_verification
```

## 4) BLOCKED — Missing Proof Block or equivalent evidence

```markdown
## 完成前验证结果

状态：BLOCKED
commit_sha：abc1234
passed：false
verified_at：2026-05-05T07:18:00Z

### Proof Block 审计
- 是否提供：否
- 完整性：缺失
- 相关性：不匹配
- 可复现性：不可复现
- 未验证项影响：阻塞
- 结论：rejected

### 证据
- [proof_block_audit] proof_block:inline
  - source：proof_block
  - exit code：not_applicable
  - 时间：2026-05-05T07:18:00Z
  - 范围：完成声明范围
  - 摘要：rejected；实现声明缺少 Proof Block 或等价证据块

### 阻塞项
- [Proof Block 不足] 实现代理只声明完成，未提供可复现证明
  - 需要动作：回到 proof-oriented-development 补 Proof Block

### 非阻塞建议
- 无

### 下一步
- 负责人：代理
- 动作：return_to_proof-oriented-development
```

## 5) BLOCKED — Verification failed with unclear cause

```markdown
## 完成前验证结果

状态：BLOCKED
commit_sha：abc1234
passed：false
verified_at：2026-05-05T07:20:00Z

### Proof Block 审计
- 是否提供：是
- 完整性：完整
- 相关性：强相关
- 可复现性：可复现
- 未验证项影响：阻塞
- 结论：accepted

### 证据
- [proof_block_audit] proof_block:inline
  - source：proof_block
  - exit code：not_applicable
  - 时间：2026-05-05T07:20:00Z
  - 范围：目标模块
  - 摘要：accepted；Proof Block 完整，但运行结果为 FAIL
- [测试] pnpm test --filter auth
  - source：proof_block
  - exit code：1
  - 时间：2026-05-05T07:20:00Z
  - 范围：目标模块
  - 摘要：目标测试失败，失败原因不清

### 阻塞项
- [检查失败] 目标验证失败且原因不清
  - 需要动作：回到 systematic-debugging 建立根因证据

### 非阻塞建议
- 无

### 下一步
- 负责人：代理
- 动作：return_to_systematic-debugging
```

## 6) BLOCKED — Missing plan proof strategy

```markdown
## 完成前验证结果

状态：BLOCKED
commit_sha：abc1234
passed：false
verified_at：2026-05-05T07:22:00Z

### Proof Block 审计
- 是否提供：是
- 完整性：部分
- 相关性：强相关
- 可复现性：部分可复现
- 未验证项影响：阻塞
- 结论：needs_more_verification

### 证据
- [proof_block_audit] proof_block:inline
  - source：proof_block
  - exit code：not_applicable
  - 时间：2026-05-05T07:22:00Z
  - 范围：公共 API 改动
  - 摘要：needs_more_verification；任务涉及公共 API 语义变化，但计划缺少证明策略和高风险决策

### 阻塞项
- [计划缺口] 缺少公共 API 语义变化的证明策略和验收口径
  - 需要动作：回到 writing-plans 补范围、验收和证明策略

### 非阻塞建议
- 无

### 下一步
- 负责人：代理
- 动作：return_to_writing-plans
```

## 7) BLOCKED — Stale evidence or HEAD mismatch

```markdown
## 完成前验证结果

状态：BLOCKED
commit_sha：abc1234
passed：false
verified_at：2026-05-05T07:25:00Z

### Proof Block 审计
- 是否提供：是
- 完整性：完整
- 相关性：强相关
- 可复现性：可复现
- 未验证项影响：无影响
- 结论：rejected

### 证据
- [proof_block_audit] proof_block:inline
  - source：proof_block
  - exit code：not_applicable
  - 时间：2026-05-05T07:25:00Z
  - 范围：完成声明范围
  - 摘要：rejected；Proof Block 绑定的 commit 与当前 HEAD 不匹配

### 阻塞项
- [证据过期] Proof Block 或验证记录不对应当前 HEAD
  - 需要动作：重新运行最小相关验证

### 非阻塞建议
- 无

### 下一步
- 负责人：代理
- 动作：rerun_minimal_verification
```
