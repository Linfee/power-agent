# Docs 维护 CLI

## 定位与扫描

从当前 Skill 的实际位置解析 `SKILL_DIR`，从用户目标、工作目录与仓库边界解析 `REPO_ROOT`，确认是有效绝对路径。Skill 可以安装在目标仓库外，不能从 `REPO_ROOT` 猜测其位置；只有无法定位或目标有实质歧义时才补充询问。

```bash
SKILL_DIR="/absolute/path/to/installed/skills/dev-docs-maintain"
REPO_ROOT="/absolute/path/to/target-repository"
BUNDLE_DIR="$REPO_ROOT/docs"

python3 "$SKILL_DIR/scripts/bundle_status.py" scan \
  --repo "$REPO_ROOT" --bundle "$BUNDLE_DIR" --format json
```

报告默认写 stdout；需要保存时加 `--output /absolute/path/to/report.json`。`--include-fresh` 包含所有 Concept 详情；`--strict` 在存在候选或 Bundle 问题时返回 1。默认扫描返回 0 不代表没有待处理项，应读取报告。参数完整定义见 [脚本](../scripts/bundle_status.py) 的 `--help`。

## 登记已验证的 Concept

沿用上节路径。以下示例只适用于两篇都已完成同种验证、证据仍覆盖当前内容的情况；可重复 `--concept` 在一个写锁内原子登记。

```bash
python3 "$SKILL_DIR/scripts/bundle_status.py" record \
  --repo "$REPO_ROOT" --bundle "$BUNDLE_DIR" \
  --concept "$BUNDLE_DIR/domain/payment.md" \
  --concept "$BUNDLE_DIR/domain/refund.md" \
  --method semantic --evidence human-review
```

`--method` 为 `semantic`、`executable` 或 `continuity`；前两者的验证要求见 [主文件](../SKILL.md#登记与完成)，`continuity` 的适用条件见 [登记资格](maintenance-policy.md#4-验证登记规则)。可选 `--evidence` 仅接受 `human-review`、`automated-test`、`external-audit`，可重复传入；这是脱敏分类，不承载命令、URL、凭据或原始证据。

## 脚本拒绝时

- 锁冲突：锁文件存在不等于活跃写者；不删锁、不改 ledger，重新扫描后重试。进程结束时操作系统释放 advisory lock。
- 路径错误：核对 repo、Bundle、registry 的真实路径与归属。Bundle/registry 路径中的符号链接组件及 symlink lock 会被拒绝；不以换别名、hardlink 或改锁绕过。详见 [ledger 协议](maintenance-policy.md#ledger-与写锁)。
- Concept 被阻止：修复报告中的 metadata、来源或链接问题，再取得适用验证证据。单条损坏登记与整个 registry 损坏的恢复资格不同，见 [损坏登记](maintenance-policy.md#损坏登记)。

参数或运行错误返回 2。只处理已定位的原因；脚本拒绝不是手工写入 ledger 的授权。
