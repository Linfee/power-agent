---
name: verification-before-completion
description: |-
  在声称工作完成之前使用，核验“完成声明”是否有本轮可验证证据支撑。
  通过结构化输出返回验证结论；不固定 lint/test/build 菜单，按任务类型选择最小充分验证。
  Triggers: 验证完成, 完成前验证, 声称通过, verification.
version: 1.2.0
---

# 完成前验证

在任何“已完成 / 已修复 / 已通过”声明前，先完成证据核验。

---

## verification-before-completion

完成前验证 Skill（completion verifier），负责：
- 判断完成声明是否被验证证据支持
- 输出可被编排层消费的结构化结论
- 在证据不足时明确阻塞原因与下一步动作

---

## Objective

### 做什么
- 对“声明”执行证据核验，而不是复述信心判断
- 要求证据与本轮改动范围相关，且为新鲜运行结果
- 输出统一 contract：`status / evidence / blocking_issues / advisories / next_action`

### 不做什么
- 不把 `lint → test → build` 写成唯一流程
- 不在主 Skill 中内嵌工具探测命令和长命令菜单
- 不替代 `requesting-code-review` 的审查职责
- 不替代 `dev-docs-maintain` 的文档维护职责

---

## Context & Tools

### 最小输入
- 本轮声明内容（宣称“完成了什么”）
- 本轮改动范围（文件或模块）
- 最近验证记录（命令、退出码、时间戳、摘要）
- 任务类型（代码实现 / 配置变更 / 文档变更）

缺失信息按需读取，不预加载大段上下文。

### 参考资料
- 验证路径建议：`references/verification-playbook.md`
- 输出协议示例：`references/output-contract-examples.md`

---

## Constraints & Format

### 核验约束
- 没有证据，`status` 不能是 `DONE`
- 证据过期或与改动范围不匹配时，必须标记阻塞
- 只要存在阻塞项，不得给出”可以声称完成”的结论

### 输出 contract（必须遵循）
```yaml
status: DONE | PARTIAL | BLOCKED
commit_sha: string  # 验证时 HEAD commit sha，供下游分支收尾 skill 消费
evidence:
  - type: 测试 | 检查 | 构建 | 人工核对 | 其他
    command: string
    exit_code: integer
    timestamp: string
    scope: 变更文件 | 目标模块 | 全仓库
    summary: string
blocking_issues:
  - code: 无证据 | 证据过期 | 检查失败 | 范围不匹配
    message: string
    required_action: string
advisories:
  - string
next_action:
  owner: 代理 | 用户
  action: string
```

### 判定规则
- `status=DONE`：至少一条相关且成功的证据，且 `blocking_issues=[]`
- `status=PARTIAL`：有证据但不完整，或存在非致命缺口
- `status=BLOCKED`：无证据、证据失败、或证据与声明不匹配

### 编排层消费规则
- 仅当 `status=DONE` 且 `blocking_issues` 为空时，允许声称完成
- 当 `status=PARTIAL|BLOCKED` 时，必须按 `next_action` 继续执行
