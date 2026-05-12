# Repository Guidelines

## Project Structure & Module Organization

This repository contains a French interactive gamebook and its generated XHTML version.

- `livre/Les_Jardins_de_Verre-Lune.md` is the canonical manuscript source.
- `livre/build_xhtml.py` converts the manuscript into playable static XHTML.
- `livre/xhtml/` contains generated output (`index.htm`, `sect*.htm`, `game.js`, `main.css`, data pages).
- `xhtml/lw/26tfobm/` is a reference XHTML/assets tree from the original source material; treat it as imported reference content unless a task specifically targets it.
- Root `EDB_*.md` files are editorial/design documents.

Prefer editing the Markdown source and generator over hand-editing generated `livre/xhtml/` files.

## Build, Test, and Development Commands

- `python3 livre/build_xhtml.py` regenerates the static site in `livre/xhtml/`.
- `python3 -m http.server 8000 -d livre/xhtml` serves the generated book locally at `http://localhost:8000/`.
- `python3 -m py_compile livre/build_xhtml.py` checks the generator for syntax errors without rebuilding content.

There is no package manager or external dependency setup in this checkout; the generator uses Python standard-library modules.

## Coding Style & Naming Conventions

Use Python 3 with 4-space indentation. Keep constants such as `SRC`, `OUT`, `SKILLS`, and `OBJECT_INFO` in uppercase near the top of `build_xhtml.py`. Use `pathlib.Path` for filesystem paths and UTF-8 for manuscript and XHTML text.

For manuscript edits, preserve the existing Markdown style: numbered sections as headings, bold section references such as `**42**`, and French game terms exactly as used in the source. Generated section files follow `sect<number>.htm`.

## Manuscript ↔ Generator Contract for Choices

The manuscript keeps the classic gamebook syntax (`- Si tu …, va au **N**.`) for two reasons: it stays human-readable and it lets the generator extract structure deterministically.

At render time, `md_section_to_html` in `livre/build_xhtml.py` does three things on each `- …` line under a `Choix :` block:

1. **Extracts the target.** `re.search(r'va au \*\*(\d+)\*\*', …)` runs on the raw line and feeds `data-target="N"` on the `<li>`. Do not rename the marker or move the regex elsewhere; it is the only thing tying a choice to its destination.
2. **Extracts requirements.** `detect_choice_requirements` parses bold tokens (`**Graine lumineuse**`, `**Orientation**`, `**CONFIANCE DES LUCIOLES**`) qualified by neighbouring prose (`possèdes`, `portes`, `compétence`, `mot-clé`) and emits `data-requires-skill|object|keyword` on the `<li>`. The JS in `game.js` reads those attributes to lock/unlock choices.
3. **Rewrites the visible text** via `rewrite_choice_display` so the player sees an action, not a conditional with a number. The pipeline is:
   - strip every `va au **N**` (the number lives in `data-target` already, so it never appears in the body);
   - turn `Si tu (possèdes|portes|as) …, tu (peux|veux) X` into `X.` (handles multi-comma conditions and `et que tu veux` joins);
   - strip leading `Si tu `, `Si `, or `Pour ` from non-gated choices and capitalize the remainder.
   The function falls back to "keep the text as-is, just without the number" rather than risk garbling unusual phrasings.

After the text rewrite, requirement badges are appended to the `<li>`: `⚑ skill`, `◆ object`, `✦ keyword`, styled by `.req` / `.req-skill` / `.req-object` / `.req-keyword` in the CSS block at the top of `build_xhtml.py`.

When you touch this pipeline, keep two invariants:
- target extraction always runs on the **raw** manuscript line, never on the rewritten display string;
- `data-requires-*` attributes match exactly what is in `SKILLS`, `OBJECT_INFO`, and the keyword set — the player-state checks in `game.js` use string equality.

If you change manuscript phrasing in a way the rewriter can't handle cleanly (e.g. observational `Si tu remarques …`), edit the source line directly; do not add a new branch to `rewrite_choice_display` just to cover one section.

## Testing Guidelines

No automated test suite is present. For generator changes, run `python3 -m py_compile livre/build_xhtml.py`, then `python3 livre/build_xhtml.py`. Smoke-test `livre/xhtml/index.htm`, `setup.htm`, a few `sect*.htm` pages, and gated choices that depend on skills, objects, or keywords.

When changing parsing rules, verify at least one positive and one negative example in the generated XHTML. For the choice rewriter specifically, spot-check the four canonical cases in the generated `sect*.htm`:

- a plain narrative choice (e.g. `sect1.htm`) — text starts with an imperative verb, no `Si`, no `va au`;
- an object-gated choice (e.g. `sect36.htm`, `data-target="42"`) — `◆ Graine lumineuse` badge present;
- a keyword-gated choice with multi-clause condition (e.g. `sect100.htm`, `data-target="102"`) — `✦ RÊVE D'ANYA` badge present, no `Si tu portes` in body;
- a skill-gated choice (e.g. `sect30.htm`, `data-target="35"`) — `⚑ Orientation` badge present.

## Commit & Pull Request Guidelines

This checkout has no usable Git history, so no project-specific commit convention can be inferred. Use short imperative commits, for example `Update keyword gate detection`.

Pull requests should describe the manuscript or generator change, list validation commands run, and include screenshots or browser notes for visible XHTML changes. Link related issues or editorial tasks when available.

## Agent-Specific Instructions

Do not overwrite generated or imported reference trees unless the task requires it. Keep changes scoped, and call out when generated files need to be refreshed after source edits.
