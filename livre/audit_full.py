#!/usr/bin/env python3
"""Run manuscript audits required before publishing.

Each audit returns 0 on success, non-zero on issues. We run them all and
return the OR of their results so failures aren't silently masked.
"""

from __future__ import annotations

import lint_tags
import audit_reachability


def main() -> int:
    rc = 0
    rc |= lint_tags.main()
    rc |= audit_reachability.main()
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
