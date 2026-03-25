#!/usr/bin/env bash
# scan-antipatterns.sh — 使用 ripgrep 扫描代码反模式
# 用法: bash scripts/scan-antipatterns.sh [目录] [--format agent|human]
# 默认扫描当前目录，输出 Agent 友好格式

set -euo pipefail

SCAN_DIR="${1:-.}"
FORMAT_VALUE="agent"

# 解析 --format 参数
for arg in "$@"; do
  case "$arg" in
    --format=*) FORMAT_VALUE="${arg#*=}" ;;
    agent|human) FORMAT_VALUE="$arg" ;;
  esac
done

ISSUES=0

echo "## 反模式扫描报告"
echo "扫描目录: $SCAN_DIR"
echo "---"
echo ""

# 检测 1: 空 catch 块
echo "### 1. 空 catch 块"
RESULT=$(rg -l "catch\s*\([^)]*\)\s*\{\s*\}" "$SCAN_DIR" 2>/dev/null || true)
if [[ -n "$RESULT" ]]; then
  ISSUES=$((ISSUES + 1))
  echo "⚠️  发现文件："
  echo "$RESULT" | sed 's/^/  - /'
  echo "   → 需要添加错误处理逻辑"
else
  echo "✅ 未发现空 catch 块"
fi
echo ""

# 检测 2: TypeScript 类型抑制
echo "### 2. TypeScript 类型抑制（@ts-ignore / as any）"
RESULT=$(rg -l "@ts-ignore|@ts-expect-error|as any" "$SCAN_DIR" 2>/dev/null || true)
if [[ -n "$RESULT" ]]; then
  ISSUES=$((ISSUES + 1))
  echo "⚠️  发现文件："
  echo "$RESULT" | sed 's/^/  - /'
  echo "   → 需要修复类型定义"
else
  echo "✅ 未发现类型抑制"
fi
echo ""

# 检测 3: console.log 残留（排除测试文件）
echo "### 3. console.log 残留（非测试文件）"
RESULT=$(rg -l "console\.log" --glob "!*.test.*" --glob "!*.spec.*" --glob "!*_test.*" "$SCAN_DIR" 2>/dev/null || true)
if [[ -n "$RESULT" ]]; then
  echo "⚠️  发现文件（请确认是否为调试残留）："
  echo "$RESULT" | sed 's/^/  - /'
else
  echo "✅ 未发现 console.log 残留"
fi
echo ""

echo "---"
if [[ $ISSUES -gt 0 ]]; then
  echo "扫描完成。阻塞性问题: $ISSUES"
else
  echo "扫描完成。无阻塞性问题。"
fi
echo ""

if [[ "$FORMAT_VALUE" == "agent" ]]; then
  if [[ $ISSUES -gt 0 ]]; then
    echo "ACTION_REQUIRED: 修复以上 $ISSUES 个问题后继续"
  else
    echo "ACTION_REQUIRED: none"
  fi
fi

exit $ISSUES
