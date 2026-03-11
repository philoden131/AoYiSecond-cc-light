#!/usr/bin/env python3
"""Session export hook: save clean turn-based conversation markdown."""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SESSION_LOGS_DIR = ROOT / "6-System" / "session_logs"


def _parse_timestamp(ts_str: str) -> datetime | None:
    if not ts_str:
        return None
    try:
        ts = ts_str.rstrip("Z").split(".")[0]
        return datetime.fromisoformat(ts).replace(tzinfo=timezone.utc)
    except Exception:
        return None


def _fmt_hhmm(dt: datetime | None) -> str:
    if dt is None:
        return ""
    return dt.astimezone().strftime("%H:%M")


def _strip_tool_renders(text: str) -> str:
    clean = []
    in_tool_block = False
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped.startswith("⏺") or stripped.startswith("⎿"):
            in_tool_block = True
            continue
        if in_tool_block and (line.startswith(" ") or line.startswith("\t") or stripped == ""):
            if stripped == "":
                in_tool_block = False
            continue
        in_tool_block = False
        clean.append(line)
    return "\n".join(clean).strip()


_SYSTEM_MARKERS = frozenset([
    "[Request interrupted by user]",
    "[Request interrupted by user for tool use]",
    "Continue from where you left off.",
])


def _strip_system_artifacts(text: str) -> str:
    clean = []
    in_task_notification = False
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped == "<task-notification>":
            in_task_notification = True
            continue
        if in_task_notification:
            if stripped == "</task-notification>":
                in_task_notification = False
            continue
        if stripped.startswith("Read the output file to retrieve the result:"):
            continue
        clean.append(line)
    return "\n".join(clean).strip()


def _extract_user_text(content) -> str:
    """Extract real user text, skipping tool results and system markers."""
    if isinstance(content, str):
        text = content.strip()
        if text in _SYSTEM_MARKERS:
            return ""
        return _strip_system_artifacts(_strip_tool_renders(text))
    if isinstance(content, list):
        parts = []
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "tool_result":
                continue
            if block.get("type") != "text":
                continue
            text = block.get("text", "").strip()
            if text in _SYSTEM_MARKERS:
                continue
            text = _strip_system_artifacts(_strip_tool_renders(text))
            if text:
                parts.append(text)
        return "\n".join(parts)
    return ""


def _extract_assistant_text_blocks(content) -> list[str]:
    """Extract visible assistant text blocks in order."""
    parts: list[str] = []
    if isinstance(content, str):
        text = _strip_tool_renders(content.strip())
        return [text] if text else []
    if isinstance(content, list):
        for block in content:
            if not isinstance(block, dict) or block.get("type") != "text":
                continue
            text = _strip_tool_renders(block.get("text", "").strip())
            if text:
                parts.append(text)
    return parts


def _parse_transcript(transcript_path: str) -> list[dict]:
    """Return complete turns: {user, assistant, user_ts, assistant_ts}."""
    if not transcript_path:
        return []
    path = Path(transcript_path)
    if not path.exists():
        return []
    try:
        raw = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return []

    turns = []
    pending_user = ""
    pending_user_ts: datetime | None = None
    pending_ai_parts: list[str] = []
    pending_ai_ts: datetime | None = None

    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except Exception:
            continue

        msg_type = obj.get("type", "")
        content = obj.get("message", {}).get("content", "")
        ts = _parse_timestamp(obj.get("timestamp", ""))

        if msg_type == "user":
            user_text = _extract_user_text(content)
            if not user_text:
                continue
            if pending_user and pending_ai_parts:
                turns.append(
                    {
                        "user": pending_user,
                        "assistant": "\n\n".join(pending_ai_parts).strip(),
                        "user_ts": pending_user_ts,
                        "assistant_ts": pending_ai_ts,
                    }
                )
            pending_user = user_text
            pending_user_ts = ts
            pending_ai_parts = []
            pending_ai_ts = None
        elif msg_type == "assistant" and pending_user:
            for chunk in _extract_assistant_text_blocks(content):
                if pending_ai_parts and pending_ai_parts[-1] == chunk:
                    continue
                pending_ai_parts.append(chunk)
                pending_ai_ts = ts or pending_ai_ts

    if pending_user and pending_ai_parts:
        turns.append(
            {
                "user": pending_user,
                "assistant": "\n\n".join(pending_ai_parts).strip(),
                "user_ts": pending_user_ts,
                "assistant_ts": pending_ai_ts,
            }
        )

    return turns


def _derive_output_path(turns: list[dict], transcript_path: str) -> Path:
    """Build output file path from first-message time + session ID snippet."""
    SESSION_LOGS_DIR.mkdir(parents=True, exist_ok=True)

    # Session ID from transcript filename (first 8 chars of UUID)
    session_snippet = Path(transcript_path).stem[:8] if transcript_path else "unknown"

    first_ts = turns[0]["user_ts"] if turns else None
    if first_ts:
        date_str = first_ts.strftime("%Y%m%d")
        time_str = first_ts.strftime("%H%M")
    else:
        now = datetime.now()
        date_str = now.strftime("%Y%m%d")
        time_str = now.strftime("%H%M")

    return SESSION_LOGS_DIR / f"{date_str}-{time_str}-{session_snippet}.md"


def _render_md(turns: list[dict]) -> str:
    if not turns:
        return ""

    first_ts = turns[0]["user_ts"]
    last_ts = turns[-1]["assistant_ts"] or turns[-1]["user_ts"]
    date_str = first_ts.strftime("%Y-%m-%d") if first_ts else datetime.now().strftime("%Y-%m-%d")
    start_t = _fmt_hhmm(first_ts)
    end_t = _fmt_hhmm(last_ts)
    user_count = len(turns)
    assistant_count = len(turns)

    lines = [
        f"# 会话记录 {date_str}",
        "",
        f"**时间段**：{start_t} — {end_t}" if end_t else f"**时间**：{start_t}",
        f"**消息数**：{user_count + assistant_count} 条（{user_count} 用户 / {assistant_count} AI）",
        "",
        "---",
        "",
    ]

    for turn in turns:
        user_time = f"**{_fmt_hhmm(turn['user_ts'])}** " if turn["user_ts"] else ""
        assistant_time = f"**{_fmt_hhmm(turn['assistant_ts'])}** " if turn["assistant_ts"] else ""

        lines.append(f"{user_time}**奥一**")
        lines.append("")
        lines.append(turn["user"])
        lines.append("")
        lines.append("---")
        lines.append("")

        lines.append(f"{assistant_time}**CC**")
        lines.append("")
        lines.append(turn["assistant"])
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def main():
    try:
        payload = json.loads(sys.stdin.read())
    except Exception:
        payload = {}

    transcript_path = payload.get("transcript_path", "")
    turns = _parse_transcript(transcript_path)

    if not turns:
        return

    output_path = _derive_output_path(turns, transcript_path)
    md = _render_md(turns)
    output_path.write_text(md, encoding="utf-8")


if __name__ == "__main__":
    main()
