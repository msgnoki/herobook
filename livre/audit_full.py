#!/usr/bin/env python3
"""Run manuscript audits required before publishing.

Epic 9 starts with the tag linter. Later editorial audits can be added here
without changing the handover validation command.
"""

from __future__ import annotations

import lint_tags


def main() -> int:
    return lint_tags.main()


if __name__ == "__main__":
    raise SystemExit(main())
