"""Entry point for the news-image-20261119 poster.

Draws the Thursday 19 November 2026 world-news poster deterministically
and writes it to /output/entry.png, or to the path given as argv[1].
"""

import sys
from pathlib import Path

from build_image import build


def main() -> int:
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/output/entry.png")
    try:
        out = build(str(target))
    except Exception as exc:  # any draw failure is reported, not hidden
        print(f"error: could not draw poster: {exc}", file=sys.stderr)
        return 1
    print(f"wrote {out} ({out.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
