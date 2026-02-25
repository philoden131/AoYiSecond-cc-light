#!/usr/bin/env bash
# approve_change.sh - 提案状态机（pending -> approved/rejected/deferred -> applied）

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
PENDING_FILE="$ROOT_DIR/6-System/pending_approvals.md"
CHANGE_LOG="$ROOT_DIR/6-System/change_log.md"

ACTION="${1:-}"
PROPOSAL_ID="${2:-}"

usage() {
  cat <<USAGE
用法: $0 <action> [proposal_id]

命令:
  list                 列出提案及状态
  approve <id>         标记为 approved
  reject <id>          标记为 rejected
  defer <id>           标记为 deferred
  apply <id>           标记为 applied（已执行）
USAGE
  exit 1
}

[ -z "$ACTION" ] && usage

list_proposals() {
  python3 - "$PENDING_FILE" <<'PY'
from pathlib import Path
import re
import sys

path = Path(sys.argv[1])
if not path.exists():
    print("（无审批文件）")
    raise SystemExit(0)

text = path.read_text(encoding="utf-8", errors="ignore")
# 匹配 ### 提案 #NNN 格式
for m in re.finditer(r"^### 提案 #(.*)$", text, flags=re.M):
    pid = m.group(1).strip()
    block = text[m.start():]
    next_m = re.search(r"\n### 提案 #", block[1:])
    if next_m:
        block = block[:next_m.start()+1]
    status = "unknown"
    # 兼容两种格式：- 状态：xxx 和 - **状态**: xxx
    sm = re.search(r"^- (?:\*\*状态\*\*[:：]|状态[:：])\s*(.+)$", block, flags=re.M)
    if sm:
        status = sm.group(1).strip()
    print(f"- {pid}: {status}")
PY
}

set_status() {
  local target_status="$1"

  python3 - "$PENDING_FILE" "$PROPOSAL_ID" "$target_status" <<'PY'
from pathlib import Path
import re
import sys

path = Path(sys.argv[1])
pid = sys.argv[2]
status = sys.argv[3]

if not path.exists():
    print("审批文件不存在", file=sys.stderr)
    raise SystemExit(1)

text = path.read_text(encoding="utf-8", errors="ignore")
# 匹配 ### 提案 #NNN 格式
pattern = re.compile(rf"(^### 提案 #{re.escape(pid)}[^\n]*\n)(.*?)(?=^### 提案 #|\Z)", flags=re.M | re.S)
m = pattern.search(text)
if not m:
    print(f"未找到提案 #{pid}", file=sys.stderr)
    raise SystemExit(1)

head, body = m.group(1), m.group(2)

# 兼容两种状态字段格式并更新
# 格式1: - 状态：pending
# 格式2: - **状态**: ✅ 已批准
if re.search(r"^- \*\*状态\*\*", body, flags=re.M):
    body = re.sub(r"^(- \*\*状态\*\*[:：]\s*)(.+)$", rf"\g<1>{status}", body, flags=re.M)
elif re.search(r"^- 状态：", body, flags=re.M):
    body = re.sub(r"^(- 状态：)(.+)$", rf"\g<1>{status}", body, flags=re.M)
else:
    body = f"- 状态：{status}\n" + body

new_block = head + body
text = text[:m.start()] + new_block + text[m.end():]
path.write_text(text, encoding="utf-8")
print(f"提案 #{pid} -> {status}")
PY

  cat >> "$CHANGE_LOG" <<LOG

### [$(date '+%Y-%m-%d %H:%M:%S')] 审批动作 #$PROPOSAL_ID
- 类型：B/C 审批流
- 操作：$ACTION
- 状态：$target_status
- 执行方式：人工审批
LOG
}

case "$ACTION" in
  list)
    list_proposals
    ;;
  approve)
    [ -z "$PROPOSAL_ID" ] && usage
    set_status "approved"
    ;;
  reject)
    [ -z "$PROPOSAL_ID" ] && usage
    set_status "rejected"
    ;;
  defer)
    [ -z "$PROPOSAL_ID" ] && usage
    set_status "deferred"
    ;;
  apply)
    [ -z "$PROPOSAL_ID" ] && usage
    set_status "applied"
    ;;
  *)
    usage
    ;;
esac
