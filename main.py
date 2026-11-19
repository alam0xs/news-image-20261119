"""Write the finished poster to /output/entry.png.

The poster image is stored as base64 text in the three companion
modules (img_part1, img_part2, img_part3) next to this file. This
program only joins and decodes that data, so it needs nothing but
the Python standard library: no image library, no network, no clock.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import base64
import os

from img_part1 import DATA as _PART1
from img_part2 import DATA as _PART2
from img_part3 import DATA as _PART3


def main() -> int:
    try:
        png = base64.b64decode(_PART1 + _PART2 + _PART3, validate=True)
    except Exception as exc:
        print(f"error: cannot decode poster data: {exc}", file=sys.stderr)
        return 1

    if len(sys.argv) > 1:
        target = Path(sys.argv[1])
    else:
        out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
        target = out_dir / "entry.png"

    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(png)
    except OSError as exc:
        print(f"error: cannot write {target}: {exc}", file=sys.stderr)
        return 1

    print(f"wrote {target} ({len(png)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
