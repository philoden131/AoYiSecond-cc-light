#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Periodic memory consolidation with bounded growth and TELOS candidate proposals."""

from __future__ import annotations

import argparse
import re
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MEMORY_FILE = ROOT / "6-System" / "working-memory" / "OPERATING_RULES.md"
PENDING_FILE = ROOT / "6-System" / "pending_approvals.md"

RECENT_HEADER = "## 近期会话索引"
CORE_HEADERS = ["## 长期偏好", "## 长期目标", "## 关键约束"]


def _read(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _parse_sections(text: str) -> tuple[list[str], dict[str, list[str]], list[str]]:
    sections: dict[str, list[str]] = {}
    order: list[str] = []
    preamble: list[str] = []
    current = ""
    seen_section = False

    for line in text.splitlines():
        if line.startswith("## "):
            current = line.strip()
            seen_section = True
            order.append(current)
            sections.setdefault(current, [])
            continue

        if not seen_section:
            preamble.append(line)
        elif current:
            sections[current].append(line)

    return order, sections, preamble


def _normalize_recent_line(line: str) -> str:
    s = line.strip()
    s = re.sub(r"^-+\s*", "", s)
    s = re.sub(r"^\d{4}-\d{2}-\d{2}\s*:\s*", "", s)
    return re.sub(r"\s+", " ", s).strip()


def _consolidate_recent(lines: list[str], max_items: int = 12) -> tuple[list[str], list[str]]:
    bullets = [ln for ln in lines if ln.strip().startswith("- ")]
    seen: set[str] = set()
    dedup: list[str] = []
    normalized: list[str] = []

    # Keep latest-first semantics; de-duplicate by normalized summary text.
    for ln in reversed(bullets):
        key = _normalize_recent_line(ln)
        if not key or key in seen:
            continue
        seen.add(key)
        dedup.append(ln.strip())
        normalized.append(key)

    dedup = list(reversed(dedup))[-max_items:]
    normalized = list(reversed(normalized))[-max_items:]
    return dedup, normalized


def _bound_core_section(lines: list[str], max_items: int = 8) -> list[str]:
    bullets = [ln.strip() for ln in lines if ln.strip().startswith("- ")]
    if len(bullets) <= max_items:
        return lines
    keep = bullets[-max_items:]
    return [""] + keep + [""]


def _build_telos_candidates(normalized_recent: list[str]) -> list[str]:
    freq = Counter(normalized_recent)
    stable = [k for k, v in freq.items() if v >= 2 and len(k) >= 8]
    return stable[:3]


def _proposal_fingerprint(candidates: list[str]) -> str:
    joined = "-".join(candidates).lower()
    clean = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "-", joined).strip("-")
    return clean[:80] or "memory-consolidation"


def _next_proposal_id(text: str) -> int:
    nums = [int(m.group(1)) for m in re.finditer(r"提案\s*#(\d+)", text)]
    return (max(nums) + 1) if nums else 1


def _append_telos_proposal(candidates: list[str]) -> bool:
    if not candidates or not PENDING_FILE.exists():
        return False

    text = _read(PENDING_FILE)
    today = datetime.now().strftime("%Y-%m-%d")
    fingerprint = f"auto/{today}/{_proposal_fingerprint(candidates)}"
    if fingerprint in text:
        return False

    pid = _next_proposal_id(text)
    candidate_lines = "; ".join(candidates)
    block = "\n".join(
        [
            "",
            f"## 提案 #{pid:03d}",
            "- 状态：pending",
            "- 类型：B",
            "- 目标：将稳定模式候选提升到 TELOS（需人工确认）",
            f"- 日期：{today}",
            f"- 内容：根据近期会话重复模式，提炼出稳定候选：{candidate_lines}",
            f"- 依据：来源 6-System/working-memory/OPERATING_RULES.md 的「近期会话索引」重复项",
            "- 影响：5-Identity/TELOS.md（仅在审批通过后写入）",
            "- 风险：medium",
            "- 回滚：拒绝该提案，或审批后 revert 对应变更",
            f"- 指纹：{fingerprint}",
            "",
        ]
    )
    with PENDING_FILE.open("a", encoding="utf-8") as f:
        f.write(block)
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-recent", type=int, default=12)
    args = parser.parse_args()

    raw = _read(MEMORY_FILE)
    if not raw:
        print("memory_updated=0")
        print("reason=memory_missing")
        return 0

    order, sections, preamble = _parse_sections(raw)
    recent_lines = sections.get(RECENT_HEADER, [])
    consolidated, normalized_recent = _consolidate_recent(recent_lines, args.max_recent)

    new_sections = sections.copy()
    if consolidated:
        new_sections[RECENT_HEADER] = [""] + consolidated + [""]

    for header in CORE_HEADERS:
        if header in new_sections:
            new_sections[header] = _bound_core_section(new_sections.get(header, []))

    out_lines: list[str] = preamble[:]
    if out_lines and out_lines[-1].strip():
        out_lines.append("")

    used: set[str] = set()
    for header in order:
        used.add(header)
        out_lines.append(header)
        out_lines.extend(new_sections.get(header, []))

    for header in [*CORE_HEADERS, RECENT_HEADER]:
        if header not in used and header in new_sections:
            out_lines.append(header)
            out_lines.extend(new_sections[header])

    merged = "\n".join(out_lines).rstrip() + "\n"
    changed = merged != raw
    if changed:
        _write(MEMORY_FILE, merged)

    candidates = _build_telos_candidates(normalized_recent)
    proposal_created = _append_telos_proposal(candidates)

    print(f"memory_updated={1 if changed else 0}")
    print(f"recent_count={len(consolidated)}")
    print(f"telos_candidates={len(candidates)}")
    print(f"proposal_created={1 if proposal_created else 0}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
