#!/usr/bin/env python3
"""Lightweight startup hook: status summary + health detection."""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PENDING_FILE = ROOT / "6-System" / "pending_approvals.md"
OVERVIEW_FILE = ROOT / "6-System" / "indexes" / "para_overview.json"
KB_HEALTH_FILE = ROOT / "6-System" / "indexes" / "kb_health.json"
MAINT_FILE = ROOT / "6-System" / "state" / "maintenance.json"
MAINT_REMIND_DAYS = 5


def _read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _count_pending(path: Path) -> int:
    if not path.exists():
        return 0
    try:
        text = path.read_text(encoding="utf-8")
        return len(re.findall(r"##\s*提案\s*#\d+", text))
    except Exception:
        return 0


def _kb_health_summary() -> tuple[str | None, list[str]]:
    """Read kb_health.json and return (severity_line, detail_lines)."""
    data = _read_json(KB_HEALTH_FILE)
    if not data:
        return None, []

    summary = data.get("summary", {})
    critical = summary.get("critical", 0)
    warning = summary.get("warning", 0)

    # Severity line
    severity_parts = []
    if critical > 0:
        severity_parts.append(f"{critical}严重")
    if warning > 0:
        severity_parts.append(f"{warning}警告")
    severity_line = f"健康: {', '.join(severity_parts)}" if severity_parts else None

    # Detail lines (expand critical items)
    details = []
    structure = data.get("structure", {})
    l2_missing = structure.get("l2_missing", [])
    if l2_missing:
        dirs = ", ".join(item["dir"] for item in l2_missing[:5])
        details.append(f"L2缺失: {dirs}")

    tags = data.get("tags", {})
    tag_segs = []
    cold = tags.get("cold_tag_count", 0)
    empty = tags.get("empty_desc_count", 0)
    template = tags.get("template_desc_count", 0)
    invalid = tags.get("invalid_type_count", 0)
    if cold > 0:
        tag_segs.append(f"{cold}冷门")
    if empty + template > 0:
        tag_segs.append(f"{empty + template}缺描述")
    if invalid > 0:
        tag_segs.append(f"{invalid}非标type")
    if tag_segs:
        details.append(f"标签: {', '.join(tag_segs)}")

    smells = data.get("smells", {})
    stale_active = smells.get("stale_active_count", 0)
    if stale_active > 0:
        details.append(f"{stale_active}篇僵化")

    broken = smells.get("broken_link_count", 0)
    if broken > 0:
        details.append(f"{broken}断裂引用")

    return severity_line, details


def _maint_reminder() -> str | None:
    """If last maintenance was > MAINT_REMIND_DAYS ago, suggest /maintain."""
    data = _read_json(MAINT_FILE)
    last_run = data.get("last_run", "")
    if not last_run:
        return "(建议: /maintain)"
    try:
        lr = datetime.fromisoformat(last_run.replace("Z", "+00:00"))
        delta = datetime.now(timezone.utc) - lr
        if delta.days >= MAINT_REMIND_DAYS:
            return f"(维护已{delta.days}天, 建议: /maintain)"
    except Exception:
        pass
    return None


def main():
    try:
        json.loads(sys.stdin.read())
    except Exception:
        pass

    # Gather status
    pending_count = _count_pending(PENDING_FILE)
    overview = _read_json(OVERVIEW_FILE)
    total_docs = overview.get("total_markdown", overview.get("total_documents", "?"))

    # Output summary
    parts = [f"[系统启动] 知识库 {total_docs} 篇"]

    if pending_count > 0:
        parts.append(f"| {pending_count} 个待审批提案")

    # Health info from kb_health.json
    severity_line, details = _kb_health_summary()
    if severity_line:
        parts.append(f"| {severity_line}")
    if details:
        parts.append(f"| {' | '.join(details)}")

    # Maintenance reminder
    maint_hint = _maint_reminder()
    if maint_hint:
        parts.append(maint_hint)

    print(" ".join(parts))


if __name__ == "__main__":
    main()
