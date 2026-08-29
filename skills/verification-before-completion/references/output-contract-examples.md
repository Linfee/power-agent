# Output Contract Examples

字段以 SKILL.md「输出」为准。这里只演示填法。

## 1) DONE

```markdown
## 完成前验证结果

状态：DONE
passed：true
commit_sha：abc1234
verified_at：2026-05-05T07:10:00Z

### 证据
- pytest tests/test_foo.py：退出码 0，覆盖目标行为

### 未验证 / 阻塞
- 无
```

## 2) BLOCKED

```markdown
## 完成前验证结果

状态：BLOCKED
passed：false
commit_sha：abc1234
verified_at：2026-05-05T07:25:00Z

### 证据
- 声称已测，但没有可复查的命令输出

### 未验证 / 阻塞
- 缺与完成声明对应的新鲜验证结果
```
