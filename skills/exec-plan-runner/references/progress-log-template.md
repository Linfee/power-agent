<!-- verified: 2026-05-05 -->
<!-- scope: exec-plan-runner, progress-log -->

# Session Log 模板

每个 batch 完成后，在 exec-plan 文件的 `## Session Log` section 追加一条记录（最新在最上方）。

## 使用方式

在 exec-plan 文件末尾（或 `## 进度` section 之后）添加：

```markdown
## Session Log
<!-- 每个 batch 完成后追加一条，最新在最上方 -->

### [YYYY-MM-DD HH:MM] Batch N 完成
- **已完成**: Task A (`path/to/file.py`), Task B (`path/to/other.py`)
- **遇到的问题**: [描述 + 如何解决，或标注未解决]
- **已验证假设**: [什么被证实/证伪]
- **下一步**: Batch N+1，从 Task X 开始
- **环境状态**: lint ✅ | tests ✅ (N passed) | build ✅
```
