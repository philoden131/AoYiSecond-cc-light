#!/usr/bin/env python3
"""Lightweight stop hook: daily memory breadcrumb."""

import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DAILY_DIR = ROOT / "6-System" / "memory" / "daily"


def _extract_user_messages(transcript_path: str) -> list[str]:
    """Extract first line of each user message from transcript."""
    if not transcript_path:
        return []
    path = Path(transcript_path)
    if not path.exists():
        return []
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception:
        return []

    messages = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except Exception:
            continue
        if obj.get("type") != "user":
            continue
        msg = obj.get("message", {})
        content = msg.get("content", "")
        if isinstance(content, list):
            texts = [
                c.get("text", "")
                for c in content
                if isinstance(c, dict) and c.get("type") == "text"
            ]
            content = " ".join(texts)
        if isinstance(content, str) and content.strip():
            first_line = content.strip().split("\n")[0][:120]
            messages.append(first_line)
    return messages


def _write_daily(messages: list[str]):
    """Write user messages as daily breadcrumb."""
    if not messages:
        return
    now = datetime.now()
    month_dir = DAILY_DIR / now.strftime("%Y%m")
    month_dir.mkdir(parents=True, exist_ok=True)

    daily_file = month_dir / f"{now.strftime('%Y%m%d')}.md"
    time_str = now.strftime("%H:%M")

    # Cap total output at ~500 chars
    output_lines = []
    total = 0
    for msg in messages:
        if total + len(msg) > 500:
            break
        output_lines.append(f"- {time_str} {msg}")
        total += len(msg)

    if output_lines:
        with open(daily_file, "a", encoding="utf-8") as f:
            f.write("\n".join(output_lines) + "\n")


def main():
    try:
        payload = json.loads(sys.stdin.read())
    except Exception:
        payload = {}

    transcript_path = payload.get("transcript_path", "")
    messages = _extract_user_messages(transcript_path)
    _write_daily(messages)


if __name__ == "__main__":
    main()
