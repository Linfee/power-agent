---
name: implement
description: 实现明确的开发任务、issue、spec 或 ticket，完成相关证明、适用审查与授权内的状态更新。
---

# Implement

把用户目标或已有任务完成为经过证明的变更。指定 issue/ticket 时读取正文和必要讨论，确认对象、目标、范围、验收及已有决定；完整 issue 可直接实现，不必再建 spec 或 ticket。简单明确的任务直接做，不为形式拆分。只获授权讨论、建议或规划时不实施。

在既定目标与授权内，自主补足不改变结果的实现细节。需要改变目标、范围、验收或风险的未定选择先核实事实，仍无法判断时仅暂停受阻部分并向用户说明；不受阻的工作继续。按真实依赖和写所有权组织独立切片：每位 sub-agent 使用新上下文，获得目标、触达范围、共享约束、验收、证据与允许/禁止动作；冲突文件串行或交单一集成者。完整任务图的调度可使用 `implement-spec`。

按 `proof-oriented-development` 选择与目标匹配的证据：可自动化的行为默认 Red/Green/Refactor，已有失败复用，纯重构与 UI、文档等按实际证据处理；根因不明时按需使用 `diagnosing-bugs`，设计边界有实际问题时使用 `codebase-design`。复用仍有效的证据，只对变化、失败或未解疑点补验；项目明确门禁仍适用。原失败场景与机制是 bug 修复的锚点，不能复跑时说明替代证据和缺失条件。

根据用户要求、风险和不确定性使用 `code-review` 审查需求符合性与工程质量；不要求先 commit，范围包含相关 staged、unstaged 和 untracked 文件。核实反馈，修复本次问题并对受影响部分补验。切片完成不等于整体完成，集成者验证共享出口和组合行为。

仅在授权覆盖具体对象和操作时更新项目 tracker；本地实现许可不等于认领、评论或关闭许可。缺少 tracker 配置不阻塞普通实现或审查；确需 tracker 时按项目入口读取配置，必要时使用 `setup-power-agent`。不自动 commit、建分支或 worktree、merge、push、创建 PR、关闭 issue 或删除 worktree。执行这些动作前核对既有授权与目标；清理还须保护未提交、未推送及他人活跃工作。报告实际结果、证据和未验证面，不把未授权的发布说成实现失败。

## 可选审查包

需要可携带的审查输入时，从实际加载的本 Skill 目录解析 `scripts/review-package`，在明确的目标仓库中运行。它包含范围内的 staged、unstaged 和新文件；不要默认生成无人消费的包。脚本位置与业务仓库分别确定，以下变量须使用已核实的绝对路径与基线值：

```bash
(
  cd "$TARGET_REPO" || exit 1
  "$IMPLEMENT_SKILL_DIR/scripts/review-package" --base "$BASE_SHA" -- src
)
```

`IMPLEMENT_SKILL_DIR` 是实际加载的本 Skill 目录。`--` 后范围相对目标 Git 根，按本次变更选择；`--output` 相对路径按调用目录解析。默认通过相邻的 `review-workspace` 在目标仓库 `.power-agent/review-runs/` 创建私有 scratch；自选仓库内输出必须已被 gitignore 覆盖，脚本拒绝覆盖已有包和危险路径。将包只交给获授权的审查者，不扫描 scratch 或敏感目录寻找额外材料；临时产物不作为持久状态或提交内容。
