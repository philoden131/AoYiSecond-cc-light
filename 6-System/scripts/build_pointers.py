#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build lightweight knowledge pointers from markdown files."""

from __future__ import annotations

import hashlib
import json
import re
import datetime
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[2]
TARGET_DIRS = [
    ROOT / "0-Inbox",
    ROOT / "1-Projects",
    ROOT / "2-Areas",
    ROOT / "3-Resources",
    ROOT / "4-Archives",
    ROOT / "5-Identity",
]
OUTPUT_FILE = ROOT / "6-System" / "indexes" / "knowledge_pointers.jsonl"
PARA_WEIGHTS = {
    "project": 1.0,
    "area": 0.95,
    "resource": 0.9,
    "identity": 0.85,
    "archive": 0.65,
    "inbox": 0.4,
}
STATUS_WEIGHTS = {
    "verified": 1.0,
    "active": 0.9,
    "draft": 0.7,
    "stale": 0.5,
}


TAG_VOCAB_FILE = ROOT / "6-System" / "indexes" / "tag_vocabulary.md"
KB_HEALTH_FILE = ROOT / "6-System" / "indexes" / "kb_health.json"
OVERVIEW_FILE = ROOT / "6-System" / "indexes" / "para_overview.json"
COLD_TAG_THRESHOLD = 1
TEMPLATE_DESC_RE = re.compile(r"^与「.*」相关的方法、案例与实践沉淀。?$")
SYSTEM_TYPES = {"context", "note"}  # 系统内部用，不算非标
STALE_ACTIVE_DAYS = 180
WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]")
L3_REQUIRED_FIELDS = {"para", "type", "status"}


def parse_frontmatter(text: str) -> Tuple[Dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text

    parts = text.split("\n---\n", 1)
    if len(parts) != 2:
        return {}, text

    raw_meta, body = parts
    meta: Dict[str, str] = {}
    for line in raw_meta.splitlines()[1:]:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip()
    return meta, body


def parse_tags(value: str) -> List[str]:
    v = value.strip()
    if not v:
        return []
    if v.startswith("[") and v.endswith("]"):
        core = v[1:-1]
        return [x.strip().strip('"\'') for x in core.split(",") if x.strip()]
    return [v]


def infer_para(rel_path: str) -> str:
    if rel_path.startswith("0-Inbox/"):
        return "inbox"
    if rel_path.startswith("1-Projects/"):
        return "project"
    if rel_path.startswith("2-Areas/"):
        return "area"
    if rel_path.startswith("3-Resources/"):
        return "resource"
    if rel_path.startswith("4-Archives/"):
        return "archive"
    if rel_path.startswith("5-Identity/"):
        return "identity"
    return "unknown"


def infer_domain(rel_path: str, meta: Dict[str, str]) -> str:
    if "domain" in meta and meta["domain"]:
        return meta["domain"]
    parts = rel_path.split("/")
    if len(parts) >= 2 and parts[0] == "3-Resources":
        return parts[1]
    return "general"


def extract_summary(meta: Dict[str, str], body: str) -> str:
    if meta.get("summary"):
        return meta["summary"][:120]
    for line in body.splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith("#"):
            continue
        if s.startswith("---"):
            continue
        return re.sub(r"\s+", " ", s)[:120]
    return ""


def normalize_value(v: str) -> str:
    return v.strip().strip('"\'')


def _days_since(date_str: str) -> int:
    d = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    return (datetime.datetime.now(datetime.timezone.utc).date() - d).days


def compute_freshness(reviewed_at: str, updated: str) -> Tuple[str, int]:
    if not reviewed_at:
        # 未复核文档也不应一刀切 stale：先按 updated 估算新鲜度，并限制最高到 aging。
        try:
            delta = _days_since(updated)
        except Exception:
            return "stale", 99999
        if delta <= 90:
            return "aging", delta
        return "stale", delta
    try:
        delta = _days_since(reviewed_at)
    except Exception:
        return "stale", 99999
    if delta <= 30:
        return "fresh", delta
    if delta <= 90:
        return "aging", delta
    return "stale", delta


def build_pointer(md_file: Path):
    rel_path = md_file.relative_to(ROOT).as_posix()
    raw = md_file.read_text(encoding="utf-8", errors="ignore")
    meta, body = parse_frontmatter(raw)

    title = normalize_value(meta.get("title", "")) or md_file.stem
    para = normalize_value(meta.get("para", "")) or infer_para(rel_path)
    domain = normalize_value(infer_domain(rel_path, meta))
    typ = normalize_value(meta.get("type", "")) or "note"
    status = normalize_value(meta.get("status", "")) or "active"
    updated = normalize_value(meta.get("updated", ""))
    if not updated:
        updated = datetime.datetime.fromtimestamp(md_file.stat().st_mtime, tz=datetime.timezone.utc).strftime("%Y-%m-%d")
    reviewed_at = normalize_value(meta.get("reviewed_at", ""))
    freshness, review_age_days = compute_freshness(reviewed_at, updated)

    summary = extract_summary(meta, body)
    tags = parse_tags(meta.get("tags", ""))

    confidence = 0.5
    if "confidence" in meta:
        try:
            confidence = float(meta["confidence"])
        except Exception:
            confidence = 0.5

    hid = hashlib.sha1(rel_path.encode("utf-8")).hexdigest()[:12]
    para_score = PARA_WEIGHTS.get(para, 0.5)
    status_score = STATUS_WEIGHTS.get(status, 0.7)
    rank = round(para_score * 0.55 + status_score * 0.2 + confidence * 0.25, 3)

    updated_sort = 0
    try:
        updated_sort = int(datetime.datetime.strptime(updated, "%Y-%m-%d").replace(tzinfo=datetime.timezone.utc).timestamp())
    except Exception:
        updated_sort = int(md_file.stat().st_mtime)

    return {
        "id": hid,
        "title": title,
        "path": rel_path,
        "para": para,
        "domain": domain,
        "type": typ,
        "status": status,
        "tags": tags,
        "summary": summary,
        "updated": updated,
        "reviewed_at": reviewed_at,
        "freshness": freshness,
        "review_age_days": review_age_days,
        "confidence": confidence,
        "rank": rank,
        "_updated_sort": updated_sort,
    }


def main() -> None:
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    pointers = []

    for base in TARGET_DIRS:
        if not base.exists():
            continue
        for md in base.rglob("*.md"):
            if md.name == "CLAUDE.md":
                continue
            rel_path = md.relative_to(ROOT).as_posix()
            if rel_path.startswith("6-System/"):
                continue
            pointers.append(build_pointer(md))

    pointers.sort(
        key=lambda x: (
            float(x.get("rank", 0.0)),
            int(x.get("_updated_sort", 0)),
            float(x.get("confidence", 0.0)),
        ),
        reverse=True,
    )

    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        for p in pointers:
            p.pop("_updated_sort", None)
            f.write(json.dumps(p, ensure_ascii=False) + "\n")

    print(f"pointers_built={len(pointers)}")
    print(f"output={OUTPUT_FILE.relative_to(ROOT)}")

    # Update tag vocabulary
    _update_tag_vocabulary(pointers)

    # Generate kb health report (replaces old tag_health_report)
    _kb_health_report(pointers)


def _update_tag_vocabulary(pointers: List[dict]) -> None:
    """Scan all tags from pointers and update tag_vocabulary.md counts."""
    # Collect tag -> {domains, count}
    tag_stats: Dict[str, Dict] = {}
    for p in pointers:
        for tag in p.get("tags", []):
            tag = tag.strip()
            if not tag:
                continue
            if tag not in tag_stats:
                tag_stats[tag] = {"domains": set(), "count": 0}
            tag_stats[tag]["domains"].add(p.get("domain", ""))
            tag_stats[tag]["count"] += 1

    if not tag_stats:
        return

    # Read existing vocabulary to preserve descriptions
    existing_desc: Dict[str, str] = {}
    if TAG_VOCAB_FILE.exists():
        for line in TAG_VOCAB_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("|") and not line.startswith("| 标签") and not line.startswith("|---"):
                parts = [c.strip() for c in line.split("|")]
                # parts: ['', tag, desc, domains, count, '']
                if len(parts) >= 5 and parts[1] and parts[1] != "标签":
                    existing_desc[parts[1]] = parts[2]

    # Build new table rows
    rows = []
    for tag in sorted(tag_stats.keys()):
        stats = tag_stats[tag]
        desc = existing_desc.get(tag, "")
        domains = ", ".join(sorted(stats["domains"] - {""}))
        rows.append(f"| {tag} | {desc} | {domains} | {stats['count']} |")

    # Read full file, replace 主题标签 table
    if TAG_VOCAB_FILE.exists():
        content = TAG_VOCAB_FILE.read_text(encoding="utf-8")
    else:
        content = "# 标签词汇表\n\n## 结构标签\n\n## 主题标签\n"

    # Find and replace the 主题标签 table
    header = "| 标签 | 含义 | 涉及领域 | 文件数 |"
    sep = "|------|------|----------|--------|"
    table = header + "\n" + sep + "\n" + "\n".join(rows) if rows else header + "\n" + sep

    # Replace everything from "## 主题标签" to the next section or end
    pattern = r"(## 主题标签\n\n)[\s\S]*?(?=\n---|\Z)"
    replacement = f"## 主题标签\n\n{table}\n"
    new_content = re.sub(pattern, replacement, content)

    TAG_VOCAB_FILE.write_text(new_content, encoding="utf-8")
    print(f"tag_vocabulary_updated={len(tag_stats)} tags")


def _parse_valid_types() -> set:
    """Parse valid structure tag names from tag_vocabulary.md."""
    valid = set()
    if not TAG_VOCAB_FILE.exists():
        return valid
    in_struct = False
    for line in TAG_VOCAB_FILE.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("## 结构标签"):
            in_struct = True
            continue
        if in_struct and line.strip().startswith("## "):
            break
        if in_struct and line.startswith("|") and not line.startswith("| 标签") and not line.startswith("|---"):
            parts = [c.strip() for c in line.split("|")]
            if len(parts) >= 3 and parts[1]:
                valid.add(parts[1])
    return valid


def _detect_similar_tags(tags: List[str]) -> List[List[str]]:
    """Detect tag pairs where one is a substring of the other (length diff <= 3)."""
    pairs = []
    for i, t1 in enumerate(tags):
        if len(t1) <= 1:
            continue
        for t2 in tags[i + 1:]:
            if len(t2) <= 1:
                continue
            if (t1 in t2 or t2 in t1) and abs(len(t1) - len(t2)) <= 3:
                pairs.append([t1, t2])
    return pairs


# ---------------------------------------------------------------------------
#  Tag health (originally _tag_health_report, now part of kb_health_report)
# ---------------------------------------------------------------------------

def _collect_tag_health(pointers: List[dict]) -> dict:
    """Collect tag health data. Returns the 'tags' section of kb_health."""
    valid_types = _parse_valid_types()

    tag_stats: Dict[str, Dict] = {}
    for p in pointers:
        for tag in p.get("tags", []):
            tag = tag.strip()
            if not tag:
                continue
            if tag not in tag_stats:
                tag_stats[tag] = {"count": 0, "files": []}
            tag_stats[tag]["count"] += 1
            if len(tag_stats[tag]["files"]) < 3:
                tag_stats[tag]["files"].append(p["path"])

    existing_desc: Dict[str, str] = {}
    if TAG_VOCAB_FILE.exists():
        for line in TAG_VOCAB_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("|") and not line.startswith("| 标签") and not line.startswith("|---"):
                parts = [c.strip() for c in line.split("|")]
                if len(parts) >= 5 and parts[1] and parts[1] != "标签":
                    existing_desc[parts[1]] = parts[2]

    cold_tags = [
        {"tag": tag, "count": s["count"], "files": s["files"]}
        for tag, s in sorted(tag_stats.items())
        if s["count"] <= COLD_TAG_THRESHOLD
    ]
    empty_desc = [tag for tag in sorted(tag_stats) if not existing_desc.get(tag, "").strip()]
    template_desc = [
        tag for tag in sorted(tag_stats)
        if existing_desc.get(tag) and TEMPLATE_DESC_RE.match(existing_desc[tag])
    ]
    invalid_types = []
    for p in pointers:
        t = p.get("type", "")
        if t and t not in valid_types and t not in SYSTEM_TYPES:
            invalid_types.append({"file": p["path"], "type": t})
    similar_pairs = _detect_similar_tags(sorted(tag_stats.keys()))

    return {
        "total": len(tag_stats),
        "cold_tags": cold_tags,
        "cold_tag_count": len(cold_tags),
        "empty_desc": empty_desc,
        "empty_desc_count": len(empty_desc),
        "template_desc": template_desc,
        "template_desc_count": len(template_desc),
        "invalid_types": invalid_types,
        "invalid_type_count": len(invalid_types),
        "similar_pairs": similar_pairs,
        "similar_pair_count": len(similar_pairs),
    }


# ---------------------------------------------------------------------------
#  Structure health (L2/L3)
# ---------------------------------------------------------------------------

def _has_md_content(d: Path) -> int:
    """Count user-authored .md files in directory (excluding CLAUDE.md), non-recursive."""
    return sum(
        1 for f in d.iterdir()
        if f.is_file() and f.suffix == ".md" and f.name != "CLAUDE.md"
    )


def _parse_l2_members(l2_path: Path) -> List[str]:
    """Extract member file/dir names mentioned in an L2 CLAUDE.md.

    Uses a loose heuristic: lines containing `.md` or backtick-wrapped names
    in list items or table rows.
    """
    if not l2_path.exists():
        return []
    text = l2_path.read_text(encoding="utf-8", errors="ignore")
    members: List[str] = []
    # Match patterns like `filename.md`, **filename.md**, or bare filename.md in list/table
    # Use broad character class to support CJK, full-width symbols (【】：), etc.
    for m in re.finditer(r"`([^`]+\.md)`|(?:^[-*]|\|)\s*\*?\*?([^\s|*][^:\n]*?\.md)", text, re.MULTILINE):
        name = m.group(1) or m.group(2)
        if name:
            members.append(name.strip().strip("`"))
    return members


def _scan_l2_health() -> dict:
    """Scan for L2 missing and L2 stale issues."""
    l2_missing = []
    l2_stale = []

    for base in TARGET_DIRS:
        if not base.exists():
            continue
        # Check base directory itself
        dirs_to_check = [base]
        # Also check one level of subdirectories
        for sub in sorted(base.iterdir()):
            if sub.is_dir() and not sub.name.startswith((".", "_")):
                dirs_to_check.append(sub)

        for d in dirs_to_check:
            md_count = _has_md_content(d)
            l2 = d / "CLAUDE.md"
            rel = d.relative_to(ROOT).as_posix()

            if md_count > 0 and (not l2.exists() or l2.stat().st_size == 0):
                l2_missing.append({"dir": rel, "md_count": md_count})
            elif md_count > 0 and l2.exists() and l2.stat().st_size > 0:
                # Check staleness: listed members vs actual files
                listed = _parse_l2_members(l2)
                actual_files = [
                    f.name for f in d.iterdir()
                    if f.is_file() and f.suffix == ".md" and f.name != "CLAUDE.md"
                ]
                extra = sorted(set(actual_files) - set(listed))
                ghost = sorted(set(listed) - set(actual_files))
                if extra or ghost:
                    l2_stale.append({
                        "dir": rel,
                        "listed": len(listed),
                        "actual": len(actual_files),
                        "extra_files": extra[:10],
                        "ghost_files": ghost[:10],
                    })

    return {
        "l2_missing": l2_missing,
        "l2_missing_count": len(l2_missing),
        "l2_stale": l2_stale,
        "l2_stale_count": len(l2_stale),
    }


def _scan_l3_health(pointers: List[dict]) -> dict:
    """Scan for L3 frontmatter issues."""
    l3_issues = []

    for p in pointers:
        issues = []
        path = p["path"]
        md_file = ROOT / path

        # Re-read frontmatter to check raw fields
        try:
            raw = md_file.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        meta, _ = parse_frontmatter(raw)

        # Check required fields
        for field in L3_REQUIRED_FIELDS:
            if not meta.get(field, "").strip():
                issues.append(f"missing_{field}")

        # Check para mismatch
        meta_para = normalize_value(meta.get("para", ""))
        if meta_para:
            inferred = infer_para(path)
            if meta_para != inferred and inferred != "unknown":
                issues.append("para_mismatch")

        if issues:
            l3_issues.append({"file": path, "issues": issues})

    return {
        "l3_issues": l3_issues,
        "l3_issue_count": len(l3_issues),
    }


# ---------------------------------------------------------------------------
#  Knowledge smells
# ---------------------------------------------------------------------------

def _scan_smell_health(pointers: List[dict]) -> dict:
    """Scan for knowledge smells: stale active, orphans, broken links, inbox, hollow dirs."""

    # 1. Stale active files (status=active but updated > STALE_ACTIVE_DAYS ago)
    stale_active = []
    for p in pointers:
        if p.get("status") != "active":
            continue
        updated = p.get("updated", "")
        if not updated:
            continue
        try:
            days = _days_since(updated)
        except Exception:
            continue
        if days > STALE_ACTIVE_DAYS:
            stale_active.append({
                "file": p["path"],
                "updated": updated,
                "days": days,
            })

    # 2. Orphan candidates (no tags AND no wikilinks in body)
    orphan_candidates = []
    for p in pointers:
        if p.get("tags"):
            continue
        md_file = ROOT / p["path"]
        try:
            raw = md_file.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        _, body = parse_frontmatter(raw)
        if not WIKILINK_RE.search(body):
            orphan_candidates.append({
                "file": p["path"],
                "reason": "no_tags_no_links",
            })

    # 3. Broken wikilinks
    broken_links = []
    all_stems = set()
    for p in pointers:
        stem = Path(p["path"]).stem
        all_stems.add(stem)
    # Also collect all md file stems (including CLAUDE.md etc.)
    for base in TARGET_DIRS:
        if not base.exists():
            continue
        for md in base.rglob("*.md"):
            all_stems.add(md.stem)

    for p in pointers:
        md_file = ROOT / p["path"]
        try:
            raw = md_file.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        _, body = parse_frontmatter(raw)
        for m in WIKILINK_RE.finditer(body):
            target = m.group(1).strip()
            # Remove heading anchors
            if "#" in target:
                target = target.split("#")[0].strip()
            if not target:
                continue
            # Check if target stem exists
            target_stem = Path(target).stem if "/" in target else target
            if target_stem not in all_stems:
                broken_links.append({
                    "file": p["path"],
                    "target": m.group(1).strip(),
                })

    # 4. Inbox count
    inbox_dir = ROOT / "0-Inbox"
    inbox_count = 0
    if inbox_dir.exists():
        inbox_count = sum(
            1 for f in inbox_dir.iterdir()
            if f.is_file() and f.suffix == ".md" and f.name != "CLAUDE.md"
        )

    # 5. Hollow dirs (has L2 CLAUDE.md but no member files)
    hollow_dirs = []
    for base in TARGET_DIRS:
        if not base.exists():
            continue
        for d in sorted(base.iterdir()):
            if not d.is_dir() or d.name.startswith((".", "_")):
                continue
            l2 = d / "CLAUDE.md"
            if l2.exists() and _has_md_content(d) == 0:
                # Check if there are subdirectories with content
                has_sub_content = any(
                    _has_md_content(sub) > 0
                    for sub in d.iterdir() if sub.is_dir()
                )
                if not has_sub_content:
                    hollow_dirs.append(d.relative_to(ROOT).as_posix())

    return {
        "stale_active": stale_active,
        "stale_active_count": len(stale_active),
        "orphan_candidates": orphan_candidates,
        "orphan_candidate_count": len(orphan_candidates),
        "broken_links": broken_links,
        "broken_link_count": len(broken_links),
        "inbox_count": inbox_count,
        "hollow_dirs": hollow_dirs,
        "hollow_dir_count": len(hollow_dirs),
    }


# ---------------------------------------------------------------------------
#  Index freshness
# ---------------------------------------------------------------------------

def _file_age_days(path: Path) -> int | None:
    """Return days since file was last modified, or None if missing."""
    if not path.exists():
        return None
    mtime = datetime.datetime.fromtimestamp(path.stat().st_mtime, tz=datetime.timezone.utc)
    return (datetime.datetime.now(datetime.timezone.utc) - mtime).days


def _scan_index_freshness() -> dict:
    """Check how old the index files are."""
    pointers_age = _file_age_days(OUTPUT_FILE)
    overview_age = _file_age_days(OVERVIEW_FILE)

    return {
        "pointers_age_days": pointers_age if pointers_age is not None else -1,
        "overview_age_days": overview_age if overview_age is not None else -1,
        "any_stale": (pointers_age is not None and pointers_age > 7) or
                     (overview_age is not None and overview_age > 7) or
                     pointers_age is None or overview_age is None,
    }


# ---------------------------------------------------------------------------
#  Combined kb_health_report
# ---------------------------------------------------------------------------

def _kb_health_report(pointers: List[dict]) -> None:
    """Generate comprehensive kb_health.json (replaces old tag_health.json)."""
    tags = _collect_tag_health(pointers)
    structure = _scan_l2_health()
    structure.update(_scan_l3_health(pointers))
    smells = _scan_smell_health(pointers)
    indexes = _scan_index_freshness()

    # Severity classification
    critical = structure["l2_missing_count"] + smells["broken_link_count"]
    warning = (
        structure["l2_stale_count"]
        + structure["l3_issue_count"]
        + smells["stale_active_count"]
        + (1 if smells["inbox_count"] > 5 else 0)
    )
    info = (
        tags["cold_tag_count"]
        + tags["empty_desc_count"]
        + tags["template_desc_count"]
        + tags["similar_pair_count"]
        + smells["orphan_candidate_count"]
        + (1 if indexes["any_stale"] else 0)
    )

    report = {
        "generated_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "tags": tags,
        "structure": structure,
        "smells": smells,
        "indexes": indexes,
        "summary": {
            "total_issues": critical + warning + info,
            "critical": critical,
            "warning": warning,
            "info": info,
        },
    }

    KB_HEALTH_FILE.parent.mkdir(parents=True, exist_ok=True)
    KB_HEALTH_FILE.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    tag_issues = tags["cold_tag_count"] + tags["empty_desc_count"] + tags["template_desc_count"] + tags["invalid_type_count"]
    print(f"kb_health: {critical} critical, {warning} warning, {info} info")
    print(f"  tags: {tag_issues} issues ({tags['cold_tag_count']} cold, {tags['empty_desc_count']} empty_desc, {tags['template_desc_count']} template_desc, {tags['invalid_type_count']} invalid_type)")
    print(f"  structure: {structure['l2_missing_count']} L2 missing, {structure['l2_stale_count']} L2 stale, {structure['l3_issue_count']} L3 issues")
    print(f"  smells: {smells['stale_active_count']} stale_active, {smells['orphan_candidate_count']} orphans, {smells['broken_link_count']} broken_links, {smells['inbox_count']} inbox")


if __name__ == "__main__":
    main()
