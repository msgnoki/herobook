"""Shared parser for manuscript mechanics tags.

The migration format is intentionally small and Markdown-friendly:

    {grants-object: Graine lumineuse}
    {requires-keywords: [AMITIÉ DE NILO, FAON SAUVÉ]}
    {branch: 345, requires-keyword: PROMESSE TRANSFORMÉE}

This module does not know the book's object/skill vocabulary. It only parses
syntax, normalizes tag keys, and strips tags from text rendered to readers.
"""

from __future__ import annotations

from dataclasses import dataclass
import re


TAG_BLOCK_RE = re.compile(r"\{([^{}\n]+)\}")
TAG_KEY_RE = re.compile(r"^\s*([A-Za-z0-9_+\-]+)\s*:\s*(.*)$")

TAG_ALIASES = {
    "grants-objects": "grants-object",
    "grants-keywords": "grants-keyword",
    "remove-keywords": "remove-keyword",
    "removes-keyword": "remove-keyword",
    "removes-keywords": "remove-keyword",
    "requires-skills": "requires-skill",
    "requires-objects": "requires-object",
    "requires-keywords": "requires-keyword",
}

VALID_TAG_KEYS = {
    "lieu",
    "ending",
    "branch",
    "grants-object",
    "grants-keyword",
    "remove-keyword",
    "state+",
    "state-",
    "requires-skill",
    "requires-object",
    "requires-keyword",
    "requires-alliances-min",
}


@dataclass(frozen=True)
class Tag:
    key: str
    raw_key: str
    raw_value: str
    values: tuple[str, ...]
    line: int
    column: int
    raw: str


@dataclass(frozen=True)
class TagParseError:
    message: str
    line: int
    column: int
    raw: str


def canonical_key(key: str) -> str:
    key = key.strip().lower().replace("_", "-")
    return TAG_ALIASES.get(key, key)


def split_top_level_commas(text: str) -> list[str]:
    parts: list[str] = []
    start = 0
    depth = 0
    quote: str | None = None

    for i, ch in enumerate(text):
        if quote:
            if ch == quote:
                quote = None
            continue
        if ch in ("'", '"'):
            quote = ch
            continue
        if ch == "[":
            depth += 1
            continue
        if ch == "]" and depth:
            depth -= 1
            continue
        if ch == "," and depth == 0:
            parts.append(text[start:i].strip())
            start = i + 1

    parts.append(text[start:].strip())
    return parts


def _strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1].strip()
    return value


def parse_values(raw_value: str) -> tuple[str, ...]:
    raw_value = raw_value.strip()
    if raw_value.startswith("[") and raw_value.endswith("]"):
        inner = raw_value[1:-1].strip()
        if not inner:
            return ()
        return tuple(
            _strip_quotes(part)
            for part in split_top_level_commas(inner)
            if _strip_quotes(part)
        )
    value = _strip_quotes(raw_value)
    return (value,) if value else ()


def parse_tag_content(
    content: str,
    *,
    line: int,
    column: int,
    raw: str,
) -> tuple[list[Tag], list[TagParseError]]:
    tags: list[Tag] = []
    errors: list[TagParseError] = []
    chunks = split_top_level_commas(content)
    current_key: str | None = None
    current_value_parts: list[str] = []

    def flush() -> None:
        nonlocal current_key, current_value_parts
        if current_key is None:
            return
        raw_value = ", ".join(part for part in current_value_parts if part).strip()
        tags.append(
            Tag(
                key=canonical_key(current_key),
                raw_key=current_key.strip(),
                raw_value=raw_value,
                values=parse_values(raw_value),
                line=line,
                column=column,
                raw=raw,
            )
        )
        current_key = None
        current_value_parts = []

    for chunk in chunks:
        if not chunk:
            continue
        match = TAG_KEY_RE.match(chunk)
        if match:
            flush()
            current_key = match.group(1)
            current_value_parts = [match.group(2)]
        elif current_key is not None:
            current_value_parts.append(chunk)
        else:
            errors.append(
                TagParseError(
                    message="fragment de balise sans clé",
                    line=line,
                    column=column,
                    raw=raw,
                )
            )
    flush()

    if not tags and not errors:
        errors.append(
            TagParseError(
                message="balise vide",
                line=line,
                column=column,
                raw=raw,
            )
        )
    return tags, errors


def parse_tag_blocks(
    text: str,
    *,
    start_line: int = 1,
) -> tuple[list[Tag], list[TagParseError]]:
    tags: list[Tag] = []
    errors: list[TagParseError] = []
    line_starts = [0]
    for match in re.finditer("\n", text):
        line_starts.append(match.end())

    def line_col(pos: int) -> tuple[int, int]:
        # Number of line starts <= pos. The text is small enough that a linear
        # scan is fine and keeps the parser dependency-free.
        idx = 0
        for i, start in enumerate(line_starts):
            if start > pos:
                break
            idx = i
        return start_line + idx, pos - line_starts[idx] + 1

    for match in TAG_BLOCK_RE.finditer(text):
        line, column = line_col(match.start())
        block_tags, block_errors = parse_tag_content(
            match.group(1),
            line=line,
            column=column,
            raw=match.group(0),
        )
        tags.extend(block_tags)
        errors.extend(block_errors)
    return tags, errors


def extract_tags(text: str, *, start_line: int = 1) -> list[Tag]:
    tags, _ = parse_tag_blocks(text, start_line=start_line)
    return tags


def tag_values(tags: list[Tag] | tuple[Tag, ...], key: str) -> list[str]:
    wanted = canonical_key(key)
    values: list[str] = []
    for tag in tags:
        if tag.key == wanted:
            values.extend(tag.values)
    return values


def has_tag(tags: list[Tag] | tuple[Tag, ...], key: str) -> bool:
    wanted = canonical_key(key)
    return any(tag.key == wanted for tag in tags)


def strip_tags(text: str) -> str:
    text = TAG_BLOCK_RE.sub("", text)
    text = re.sub(r"\s+([,.])", r"\1", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


def strip_render_tags(text: str) -> str:
    """Remove mechanics tags from prose while preserving Markdown line shape."""
    lines: list[str] = []
    for line in text.splitlines():
        if "{" not in line:
            lines.append(line)
            continue
        stripped = strip_tags(line)
        if line.strip().startswith("{") and not stripped:
            continue
        lines.append(stripped)
    return "\n".join(lines)
