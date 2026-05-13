#!/usr/bin/env python3
"""Lint mechanics tags in Les_Jardins_de_Verre-Lune.md.

This is the first Epic 9 linter: it validates the tag syntax, known
vocabulary, and section targets while the manuscript is migrated.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
import re
import sys

from tag_spec import Tag, VALID_TAG_KEYS, parse_tag_blocks


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "Les_Jardins_de_Verre-Lune.md"
BUILD = ROOT / "build_xhtml.py"


@dataclass(frozen=True)
class Issue:
    line: int
    column: int
    message: str


def load_literal(name: str):
    tree = ast.parse(BUILD.read_text(encoding="utf-8"))
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
            continue
        return ast.literal_eval(node.value)
    raise RuntimeError(f"Constante {name} introuvable dans {BUILD}")


def line_number(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def parse_sections(text: str):
    pattern = re.compile(r"^###\s+(\d+)(?P<rest>[^\n]*)$", re.MULTILINE)
    matches = list(pattern.finditer(text))
    annexes_match = re.search(r"^##\s+Annexes de contrôle\s*$", text, re.MULTILINE)
    annexes_start = annexes_match.start() if annexes_match else len(text)

    sections = []
    for idx, match in enumerate(matches):
        num = int(match.group(1))
        body_start = match.end()
        body_end = matches[idx + 1].start() if idx + 1 < len(matches) else annexes_start
        sections.append(
            {
                "num": num,
                "heading_rest": match.group("rest") or "",
                "heading_line": line_number(text, match.start()),
                "body": text[body_start:body_end],
                "body_line": line_number(text, body_start),
            }
        )
    return sections


def validate_tag(
    tag: Tag,
    location: str,
    issues: list[Issue],
    *,
    skills: set[str],
    objects: set[str],
    states: set[str],
    section_numbers: set[int],
) -> None:
    if tag.key not in VALID_TAG_KEYS:
        issues.append(Issue(tag.line, tag.column, f"balise inconnue `{tag.raw_key}`"))
        return

    if not tag.values:
        issues.append(Issue(tag.line, tag.column, f"valeur vide pour `{tag.raw_key}`"))
        return

    if location == "choice" and tag.key in {"lieu", "ending", "branch", "requires-alliances-min"}:
        issues.append(Issue(tag.line, tag.column, f"`{tag.raw_key}` n'est pas une balise de choix"))

    if tag.key == "requires-skill":
        for value in tag.values:
            if value not in skills:
                issues.append(Issue(tag.line, tag.column, f"compétence inconnue `{value}`"))

    if tag.key in {"requires-object", "grants-object"}:
        for value in tag.values:
            if value not in objects:
                issues.append(Issue(tag.line, tag.column, f"objet inconnu `{value}`"))

    if tag.key in {"state+", "state-"}:
        for value in tag.values:
            if value not in states:
                issues.append(Issue(tag.line, tag.column, f"état inconnu `{value}`"))

    if tag.key == "branch":
        for value in tag.values:
            if not value.isdigit():
                issues.append(Issue(tag.line, tag.column, f"branche non numérique `{value}`"))
                continue
            target = int(value)
            if target not in section_numbers:
                issues.append(Issue(tag.line, tag.column, f"branche vers section absente `{target}`"))

    if tag.key == "requires-alliances-min":
        for value in tag.values:
            if not value.isdigit():
                issues.append(Issue(tag.line, tag.column, f"minimum d'alliances non numérique `{value}`"))


def lint_choice_target(line: str, line_no: int, issues: list[Issue], section_numbers: set[int]) -> None:
    target = None
    arrow = re.match(r"\s*-\s*(?:→|->)\s*(\d+)\s*::", line)
    if arrow:
        target = int(arrow.group(1))
    else:
        legacy = re.search(r"va au \*\*(\d+)\*\*", line, re.IGNORECASE)
        if legacy:
            target = int(legacy.group(1))

    if target is not None and target not in section_numbers:
        issues.append(Issue(line_no, 1, f"choix vers section absente `{target}`"))


def main() -> int:
    text = SRC.read_text(encoding="utf-8")
    sections = parse_sections(text)
    section_numbers = {section["num"] for section in sections}
    issues: list[Issue] = []
    tag_count = 0

    if len(sections) != 350:
        issues.append(Issue(1, 1, f"{len(sections)} sections détectées, 350 attendues"))

    skills = set(load_literal("SKILLS"))
    objects = set(load_literal("OBJECT_INFO").keys())
    states = set(load_literal("STATE_KEYWORDS"))

    for section in sections:
        heading_tags, heading_errors = parse_tag_blocks(
            section["heading_rest"],
            start_line=section["heading_line"],
        )
        for error in heading_errors:
            issues.append(Issue(error.line, error.column, error.message))
        for tag in heading_tags:
            tag_count += 1
            validate_tag(
                tag,
                "heading",
                issues,
                skills=skills,
                objects=objects,
                states=states,
                section_numbers=section_numbers,
            )

        in_choices = False
        for offset, line in enumerate(section["body"].splitlines(), start=section["body_line"]):
            stripped = line.strip()
            if stripped == "Choix :":
                in_choices = True
                continue
            if in_choices and stripped and not stripped.startswith("- "):
                in_choices = False

            location = "choice" if in_choices and stripped.startswith("- ") else "section"
            line_tags, line_errors = parse_tag_blocks(line, start_line=offset)
            for error in line_errors:
                issues.append(Issue(error.line, error.column, error.message))
            for tag in line_tags:
                tag_count += 1
                validate_tag(
                    tag,
                    location,
                    issues,
                    skills=skills,
                    objects=objects,
                    states=states,
                    section_numbers=section_numbers,
                )
            if location == "choice":
                lint_choice_target(line, offset, issues, section_numbers)

    if issues:
        for issue in sorted(issues, key=lambda item: (item.line, item.column, item.message)):
            print(f"{SRC}:{issue.line}:{issue.column}: {issue.message}", file=sys.stderr)
        print(f"lint_tags: {len(issues)} problème(s)", file=sys.stderr)
        return 1

    print(f"lint_tags: OK (0 problème, {tag_count} balise(s), {len(sections)} sections)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
