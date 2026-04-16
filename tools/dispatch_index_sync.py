from __future__ import annotations

import sys

import requests

import workflow_dispatch


DEFAULT_LABEL = "Index sync"


def main(argv: list[str] | None = None, session: requests.Session | None = None) -> int:
    args = list(argv or sys.argv[1:])
    return workflow_dispatch.main(["--label", DEFAULT_LABEL, *args], session=session)


if __name__ == "__main__":
    raise SystemExit(main())
