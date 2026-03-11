#!/usr/bin/env python3
"""Lightweight stop hook: save clean per-session conversation breadcrumbs."""

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DAILY_DIR = ROOT / "6-System" / "working-memory" / "daily"


def _strip_tool_renders(text: str) -> str:
    """Remove Claude Code terminal tool-call rendering lines from text.
    Filters lines starting with ⏺ / ⎿ and their indented sub-lines.
    """
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


# Claude Code system markers that are not real user messages
_SYSTEM_MARKERS = frozenset([
    "[Request interrupted by user]",
    "[Request interrupted by user for tool use]",
    "Continue from where you left off.",
])


def _strip_system_artifacts(text: str) -> str:
    """Remove Claude Code background-task notices from captured text."""
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
    """Extract real user-typed text, skipping tool_result blocks,
    tool render artifacts, and Claude Code system markers."""
    if isinstance(content, str):
        text = content.strip()
        if text in _SYSTEM_MARKERS:
            return ""
        return _strip_system_artifacts(_strip_tool_renders(text))
    if isinstance(content, list):
        parts = []
        for b in content:
            if not isinstance(b, dict):
                continue
            if b.get("type") == "tool_result":
                continue
            if b.get("type") == "text":
                text = b.get("text", "").strip()
                if text in _SYSTEM_MARKERS:
                    continue
                text = _strip_system_artifacts(_strip_tool_renders(text))
                if text:
                    parts.append(text)
        return "\n".join(parts)
    return ""


def _extract_assistant_text_blocks(content) -> list[str]:
    """Extract all assistant text blocks in order, skipping thinking/tool_use."""
    parts: list[str] = []
    if isinstance(content, str):
        text = _strip_tool_renders(content)
        return [text] if text else []
    if isinstance(content, list):
        for block in content:
            if not isinstance(block, dict) or block.get("type") != "text":
                continue
            text = _strip_tool_renders(block.get("text", "").strip())
            if text:
                parts.append(text)
    return parts


def _extract_complete_turns(transcript_path: str) -> list[dict]:
    """Return complete user/assistant turns from transcript."""
    if not transcript_path:
        return []
    path = Path(transcript_path)
    if not path.exists():
        return []
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception:
        return []

    turns: list[dict] = []
    pending_user = ""
    pending_user_ts: datetime | None = None
    pending_ai_parts: list[str] = []
    pending_ai_ts: datetime | None = None

    for line in lines:
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
            if user_text:
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
        elif msg_type == "assistant":
            if not pending_user:
                continue
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


def _session_file(transcript_path: str) -> Path:
    """Resolve the per-session breadcrumb file: daily/YYYYMM/YYYYMMDD/{session}.md"""
    now = datetime.now()
    day_dir = DAILY_DIR / now.strftime("%Y%m") / now.strftime("%Y%m%d")
    day_dir.mkdir(parents=True, exist_ok=True)
    session_id = Path(transcript_path).stem[:8] if transcript_path else "unknown"
    return day_dir / f"{session_id}.md"


def _render_turns(turns: list[dict]) -> str:
    lines: list[str] = []
    for turn in turns:
        user_time = _fmt_hhmm(turn["user_ts"])
        assistant_time = _fmt_hhmm(turn["assistant_ts"]) or user_time
        lines.append(f"- {user_time} [你]" if user_time else "- [你]")
        lines.append(turn["user"])
        lines.append("")
        lines.append(f"- {assistant_time} [cc]" if assistant_time else "- [cc]")
        lines.append(turn["assistant"])
        lines.append("")
        lines.append("---")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _write_session_file(session_file: Path, turns: list[dict]):
    """Rewrite the current session breadcrumb file from transcript truth."""
    if not turns:
        return
    session_file.write_text(_render_turns(turns), encoding="utf-8")


def main():
    try:
        payload = json.loads(sys.stdin.read())
    except Exception:
        payload = {}

    transcript_path = payload.get("transcript_path", "")
    session_file = _session_file(transcript_path)

    turns = _extract_complete_turns(transcript_path)
    _write_session_file(session_file, turns)

    # Retry once to catch the tail of a turn whose last text lands slightly later.
    time.sleep(3)
    turns = _extract_complete_turns(transcript_path)
    _write_session_file(session_file, turns)


if __name__ == "__main__":
    main()
