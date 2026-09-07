# 独立审查 Brief

此文件可单独派给 reviewer，附上已可得的需求、范围、diff 或工作树、已有验证、先前 finding 与修复增量。缺少材料时先判断是否影响结论，再索取最小必要上下文。遵守委派的读写边界；独立复核者不参与实现。

以有效需求和契约判断应有行为，以当前 diff、相关 staged / unstaged / untracked 文件、受影响调用路径与适用运行证据判断实际行为。旧结论和“已验证”的口头声明只是待核验主张；冲突不能靠现有实现覆盖需求。

检查需求遗漏、边界/状态/错误语义、安全与数据、维护性及验证是否覆盖实际风险。重要性看出错后果，实现风险看当前代码与证据中的不确定性，不按文件或 API 标签定级。风格偏好、猜测或已由工具强制的项目不构成 finding。

修复复核检查原问题、增量与受影响路径；若实质改变范围、验收、公共契约、数据、权限、安全、并发或迁移边界，按新范围重审。

交付说明审查范围。每个 finding 给出 file:line、diff hunk 或命令输出，并说明触发条件、影响和需改变的行为；严重度按核验影响定为严重、重要或轻微，不因另一 reviewer 定级更高就升级。无 blocker 且证据覆盖需求与风险才判通过；材料不足则报告缺口，非阻塞建议与开放问题说明依据。

## Review Assets

如有 Review Assets，只有在下列信任边界全部成立时才能读取或采信：

- 未解析的 run root 必须恰好是当前仓库 `.power-agent/review-runs/<run-id>`；它及每个父路径都不是 symlink、是目录，解析后仍恰好是该目录。普通仓库目录不得伪装为 run root。
- 未解析和解析后的 manifest 路径都必须恰好等于该 root 的 `review-assets.md`。
- 只读取 manifest 明确点名、位于同一 root `assets/` 下的普通文件；拒绝绝对路径、空路径段、`.`、`..`、symlink 与解析后逃出 `assets/` 的路径。
- 每个资产的 scope 必须匹配当前审查目标及适用的 `paths` / finding，freshness 必须匹配当前审查依据，source 可追溯，sensitivity 获得当前授权（省略时仅 `normal`）。

没有 manifest 时不扫描 `.power-agent`、`review-runs` 或 `assets`。元数据无效、过期或无法比较时，只报告证据缺口，绝不扩扫寻找替代物。
