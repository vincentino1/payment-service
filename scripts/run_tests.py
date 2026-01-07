from __future__ import annotations

import sys

import pytest


def main() -> int:
    # Run pytest programmatically so CI can rely on exit code even if stdout capture is flaky.
    return pytest.main(["-q"])


if __name__ == "__main__":
    raise SystemExit(main())

