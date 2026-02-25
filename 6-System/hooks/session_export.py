#!/usr/bin/env python3
"""Session export hook: save full conversation (user + AI) as MD to session_logs/."""

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
    return dt.strftime("%H:%M")


def _extract_text(content) -> str:
    """Extract visible text from message content (str or list of blocks)."""
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = []
        for block in content:
            if not isinstance(block, dict):
                continue
            btype = block.get("type", "")
            # Only include text blocks; skip thinking/tool_use/tool_result
            if btype == "text":
                text = block.get("text", "").strip()
                if text:
                    parts.append(text)
        return "\n\n".join(parts)
    return ""


def _parse_transcript(transcript_path: str) -> list[dict]:
    """Return list of conversation turns: {type, text, timestamp}."""
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
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except Exception:
            continue

        msg_type = obj.get("type", "")
        if msg_type not in ("user", "assistant"):
            continue

        msg = obj.get("message", {})
        content = msg.get("content", "")
        text = _extract_text(content)
        if not text:
            continue

        # Skip user messages that are pure tool-result payloads
        if isinstance(content, list) and all(
            isinstance(b, dict) and b.get("type") == "tool_result"
            for b in content
            if isinstance(b, dict)
        ):
            continue

        ts = _parse_timestamp(obj.get("timestamp", ""))
        turns.append({"type": msg_type, "text": text, "ts": ts})

    return turns


def _derive_output_path(turns: list[dict], transcript_path: str) -> Path:
    """Build output file path from first-message time + session ID snippet."""
    SESSION_LOGS_DIR.mkdir(parents=True, exist_ok=True)

    # Session ID from transcript filename (first 8 chars of UUID)
    session_snippet = Path(transcript_path).stem[:8] if transcript_path else "unknown"

    first_ts = turns[0]["ts"] if turns else None
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

    first_ts = turns[0]["ts"]
    last_ts = turns[-1]["ts"]
    date_str = first_ts.strftime("%Y-%m-%d") if first_ts else datetime.now().strftime("%Y-%m-%d")
    start_t = _fmt_hhmm(first_ts)
    end_t = _fmt_hhmm(last_ts)

    lines = [
        f"# 会话记录 {date_str}",
        "",
        f"**时间段**：{start_t} — {end_t}" if end_t else f"**时间**：{start_t}",
        f"**消息数**：{len(turns)} 条（{sum(1 for t in turns if t['type']=='user')} 用户 / "
        f"{sum(1 for t in turns if t['type']=='assistant')} AI）",
        "",
        "---",
        "",
    ]

    for turn in turns:
        time_tag = f"**{_fmt_hhmm(turn['ts'])}** " if turn["ts"] else ""
        speaker = "**奥一**" if turn["type"] == "user" else "**CC**"
        lines.append(f"{time_tag}{speaker}")
        lines.append("")
        lines.append(turn["text"])
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
