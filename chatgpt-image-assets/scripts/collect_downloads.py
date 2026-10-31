"""Move browser downloads of ChatGPT images into a project folder.

Usage:
  python collect_downloads.py '<got json>' '<names json>' <dest folder> [downloads dir]

  got json    {"00c": 1668641, "01": 1531641, ...}  (window.__got from the download snippet)
  names json  {"00c": "UIKit", "01": "LoadingUI", ...}

Downloads appear first as <guid>.tmp and are renamed later, so files are
matched by exact byte size whatever their current name. Each match is moved to
<dest>/<tag>_<Name>.png after checking the PNG signature.
"""
import glob
import json
import os
import shutil
import struct
import sys
import time

PNG_SIG = b"\x89PNG\r\n\x1a\n"


def main():
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    got = json.loads(sys.argv[1])
    names = json.loads(sys.argv[2])
    dest = sys.argv[3]
    downloads = sys.argv[4] if len(sys.argv) > 4 else os.path.expanduser("~/Downloads")
    os.makedirs(dest, exist_ok=True)

    recent = [f for f in glob.glob(os.path.join(downloads, "*"))
              if os.path.isfile(f) and time.time() - os.path.getmtime(f) < 6 * 3600]

    for tag, size in sorted(got.items()):
        matches = [f for f in recent if os.path.exists(f) and os.path.getsize(f) == size]
        if not matches:
            print(f"{tag}: MISSING (no download of {size} bytes)")
            continue
        src = max(matches, key=os.path.getmtime)
        with open(src, "rb") as fh:
            head = fh.read(32)
        if head[:8] != PNG_SIG:
            print(f"{tag}: {os.path.basename(src)} is not a PNG, skipped")
            continue
        width, height = struct.unpack(">II", head[16:24])
        alpha = head[25] in (4, 6)
        out = os.path.join(dest, f"{tag}_{names.get(tag, tag)}.png")
        shutil.move(src, out)
        recent.remove(src)
        print(f"{tag}: {os.path.basename(src)} -> {os.path.basename(out)} {width}x{height} alpha={alpha}")


if __name__ == "__main__":
    main()
