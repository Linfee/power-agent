# Output Contract Examples

契约字段见 SKILL.md「输出契约」。这里只演示三种典型结局的填法；字段必须出现，措辞和顺序不必与示例逐字一致。

## 1) DONE — Proof Block accepted

```markdown
## 完成前验证结果

状态：DONE
passed：true
commit_sha：abc1234
verified_at：2026-05-05T07:10:00Z

### Proof Block 审计
- 结论：accepted
- 完整、与声明强相关、可复现，未验证项为无；条件性门槛均未触发（性能影响面 not_applicable：纯文档改动）

### 证据
- proof_block:inline：来源 proof_block，时间 2026-05-05T07:10:00Z，范围目标模块；accepted，验证命令与声明强相关

### 阻塞项
- 无

### 下一步
- 动作：proceed_to_finishing-a-development-branch
```

## 2) DONE — 审计发现缺口，补验后通过

```markdown
## 完成前验证结果

状态：DONE
passed：true
commit_sha：abc1234
verified_at：2026-05-05T07:12:00Z

### Proof Block 审计
- 结论：needs_more_verification → 补验通过
- Proof Block 缺少引用一致性检查，目标约束从任务卡映射；已补跑 rg 检查并通过

### 证据
- proof_block:inline：来源 proof_block，时间 2026-05-05T07:12:00Z，范围变更文件；needs_more_verification，缺引用一致性检查
- rg -n "Proof Block" skills/ docs/：来源 vbc_extra_verification，退出码 0，时间 2026-05-05T07:12:00Z，范围目标模块；补充检查通过

### 阻塞项
- 无

### 下一步
- 动作：proceed_to_finishing-a-development-branch
```

## 3) BLOCKED — 证据过期，HEAD 不匹配

```markdown
## 完成前验证结果

状态：BLOCKED
passed：false
commit_sha：abc1234
verified_at：2026-05-05T07:25:00Z

### Proof Block 审计
- 结论：rejected
- Proof Block 绑定的 commit 与当前 HEAD 不匹配，证据不新鲜

### 证据
- proof_block:inline：来源 proof_block，时间 2026-05-05T07:25:00Z，范围完成声明范围；rejected，证据绑定旧 HEAD

### 阻塞项
- 证据过期：Proof Block 不对应当前 HEAD → 需要动作：重新运行最小相关验证

### 下一步
- 动作：rerun_minimal_verification
```

其他常见 BLOCKED 情形按同一格式填写：`return_to_proof-oriented-development`（缺 Proof Block 或与声明对不上）、`return_to_systematic-debugging`（验证失败且原因不清）、`return_to_writing-plans`（缺验收、证明策略或高风险决策）。
