#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build PARA overview for startup context injection."""

from __future__ import annotations

import datetime
import json
from pathlib import Path
from typing import Dict, List


ROOT = Path(__file__).resolve().parents[2]
POINTER_FILE = ROOT / "6-System" / "indexes" / "knowledge_pointers.jsonl"
OUTPUT_FILE = ROOT / "6-System" / "indexes" / "para_overview.json"

PARA_DIRS = {
    "inbox": ROOT / "0-Inbox",
    "project": ROOT / "1-Projects",
    "area": ROOT / "2-Areas",
    "resource": ROOT / "3-Resources",
    "archive": ROOT / "4-Archives",
    "identity": ROOT / "5-Identity",
}


def count_markdown(base: Path) -> int:
    if not base.exists():
        return 0
    return sum(1 for p in base.rglob("*.md") if p.name != "CLAUDE.md")


def load_pointers(path: Path) -> List[Dict]:
    if not path.exists():
        return []
    out: List[Dict] = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except Exception:
            continue
    return out


def main() -> None:
    counts = {key: count_markdown(base) for key, base in PARA_DIRS.items()}
    total = sum(counts.values())

    pointers = load_pointers(POINTER_FILE)
    domain_counts: Dict[str, int] = {}
    for p in pointers:
        domain = str(p.get("domain", "")).strip() or "general"
        domain_counts[domain] = domain_counts.get(domain, 0) + 1

    top_domains = sorted(
        [{"domain": k, "count": v} for k, v in domain_counts.items()],
        key=lambda x: x["count"],
        reverse=True,
    )[:6]

    def sort_key(x: Dict) -> tuple:
        return (
            float(x.get("rank", 0.0)),
            str(x.get("updated", "")),
            float(x.get("confidence", 0.0)),
        )

    hot_notes = [x for x in pointers if x.get("para") != "inbox"]
    hot_notes.sort(key=sort_key, reverse=True)
    hot_notes = [
        {
            "title": x.get("title", "untitled"),
            "path": x.get("path", ""),
            "para": x.get("para", "unknown"),
            "domain": x.get("domain", "general"),
            "summary": x.get("summary", ""),
            "rank": x.get("rank", 0.0),
        }
        for x in hot_notes[:6]
    ]

    payload = {
        "generated_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "counts": counts,
        "total_markdown": total,
        "top_domains": top_domains,
        "hot_notes": hot_notes,
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"para_overview_built=1")
    print(f"output={OUTPUT_FILE.relative_to(ROOT)}")
    print(f"total_markdown={total}")


if __name__ == "__main__":
    main()
