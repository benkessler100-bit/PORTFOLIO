#!/usr/bin/env python3
"""
Generate a WebP twin for every still in assets/v3/img.

The page serves these through <picture>, so the JPEG/PNG stays on disk as the
fallback source and nothing breaks on a browser that cannot decode WebP. Run it
after build-img.sh, or any time you drop new stills in.

    python3 tools/build-webp.py            # convert anything missing or stale
    python3 tools/build-webp.py --force    # re-encode everything

Why this matters here beyond page speed: Amplify bills egress at roughly
$0.15/GB, and this page ships ~50 stills. Halving them halves that line.
"""

import argparse
import os
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow is required:  python3 -m pip install --user Pillow")

ROOT = Path(__file__).resolve().parent.parent
IMGDIR = ROOT / "assets" / "v3" / "img"

# Photographs tolerate q=82 with no visible loss at the sizes this page displays.
# Logos are flat-ink PNGs with hard edges, where lossy encoding produces visible
# ringing along the mask — they go lossless, and still come out smaller.
QUALITY_PHOTO = 82
QUALITY_ALPHA = 88


def convert(src: Path, force: bool) -> tuple[int, int] | None:
    dst = src.with_suffix(".webp")
    if dst.exists() and not force and dst.stat().st_mtime >= src.stat().st_mtime:
        return None

    im = Image.open(src)
    has_alpha = im.mode in ("RGBA", "LA", "P") and "transparency" in im.info or im.mode in ("RGBA", "LA")

    if src.parent.name == "logos":
        im.save(dst, "WEBP", lossless=True, method=6)
    elif has_alpha:
        im.save(dst, "WEBP", quality=QUALITY_ALPHA, method=6)
    else:
        im.convert("RGB").save(dst, "WEBP", quality=QUALITY_PHOTO, method=6)

    return src.stat().st_size, dst.stat().st_size


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="re-encode even if up to date")
    args = ap.parse_args()

    if not IMGDIR.is_dir():
        sys.exit(f"not found: {IMGDIR}")

    sources = sorted(
        p for p in IMGDIR.rglob("*")
        if p.suffix.lower() in (".jpg", ".jpeg", ".png")
    )
    if not sources:
        sys.exit(f"no stills under {IMGDIR}")

    before = after = 0
    made = skipped = 0
    for src in sources:
        result = convert(src, args.force)
        if result is None:
            skipped += 1
            continue
        b, a = result
        before += b
        after += a
        made += 1
        print(f"  {src.relative_to(ROOT)}  {b // 1024}K → {a // 1024}K")

    if made:
        pct = 100 - (after * 100 // before)
        print(f"\n{made} converted, {skipped} already current")
        print(f"{before // 1024 // 1024}MB → {after // 1024 // 1024}MB  ({pct}% smaller)")
    else:
        print(f"nothing to do — {skipped} already current")


if __name__ == "__main__":
    main()
