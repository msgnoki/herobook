#!/usr/bin/env python3
"""Audit graph reachability for Les_Jardins_de_Verre-Lune.md.

Checks that:
  - every section §1..§350 is reachable from §1 by following raw choice
    links (gates are ignored — we only assert structural connectivity);
  - the 7 endings (333, 336, 339, 342, 345, 348, 350) are reachable;
  - sections that are not endings have at least one outgoing choice
    (no accidental dead-ends).

Run via `python3 livre/audit_full.py` (this module is invoked from there).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import sys
from collections import deque


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "Les_Jardins_de_Verre-Lune.md"
ENDINGS = {333, 336, 339, 342, 345, 348, 350}


@dataclass(frozen=True)
class Issue:
    line: int
    message: str


# Each section heading: `### N` or `### N — title …` with optional inline tags.
SECTION_RE = re.compile(r"^###\s+(\d+)(?:\s+—\s+[^\n{]+)?(?:\s+\{[^\n]*)?\s*$", re.MULTILINE)
LEGACY_TARGET_RE = re.compile(r"va au \*\*(\d+)\*\*", re.IGNORECASE)
ARROW_TARGET_RE = re.compile(r"^\s*-\s*(?:→|->)\s*(\d+)\s*::", re.MULTILINE)


def parse_sections(text: str) -> dict[int, str]:
    """Return {section_num: body} for every `### N` heading in the manuscript."""
    matches = list(SECTION_RE.finditer(text))
    annexes = re.search(r"^##\s+Annexes de contrôle\s*$", text, re.MULTILINE)
    end_pos = annexes.start() if annexes else len(text)

    sections: dict[int, str] = {}
    for idx, m in enumerate(matches):
        num = int(m.group(1))
        body_start = m.end()
        body_end = matches[idx + 1].start() if idx + 1 < len(matches) else end_pos
        sections[num] = text[body_start:body_end]
    return sections


def extract_targets(body: str) -> set[int]:
    """Pull every numeric link out of a section body (legacy + arrow forms)."""
    targets: set[int] = set()
    for m in LEGACY_TARGET_RE.finditer(body):
        targets.add(int(m.group(1)))
    for m in ARROW_TARGET_RE.finditer(body):
        targets.add(int(m.group(1)))
    return targets


def main() -> int:
    text = SRC.read_text(encoding="utf-8")
    sections = parse_sections(text)
    issues: list[Issue] = []

    if len(sections) != 350:
        issues.append(Issue(0, f"{len(sections)} sections détectées, 350 attendues"))

    graph: dict[int, set[int]] = {}
    for num, body in sections.items():
        graph[num] = extract_targets(body)

    # BFS from §1
    reachable: set[int] = set()
    queue: deque[int] = deque([1])
    while queue:
        node = queue.popleft()
        if node in reachable:
            continue
        reachable.add(node)
        for target in graph.get(node, set()):
            if target not in reachable:
                queue.append(target)

    # Endings must all be reachable
    missing_endings = ENDINGS - reachable
    for ending in sorted(missing_endings):
        issues.append(Issue(0, f"fin §{ending} non atteignable depuis §1"))

    # Every section should be reachable from §1
    orphans = set(sections.keys()) - reachable
    for orphan in sorted(orphans):
        issues.append(Issue(0, f"section §{orphan} orpheline (jamais atteinte depuis §1)"))

    # Non-ending sections should have at least one outgoing link
    for num in sorted(sections.keys()):
        if num in ENDINGS:
            continue
        if not graph[num]:
            issues.append(Issue(0, f"section §{num} sans choix sortant (et n'est pas une fin)"))

    if issues:
        for issue in issues:
            print(f"audit_reachability: {issue.message}", file=sys.stderr)
        print(
            f"audit_reachability: {len(issues)} problème(s) — "
            f"{len(reachable)}/{len(sections)} sections atteignables",
            file=sys.stderr,
        )
        return 1

    print(
        f"audit_reachability: OK ({len(reachable)} sections atteignables, "
        f"{len(ENDINGS)} fins atteignables)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
