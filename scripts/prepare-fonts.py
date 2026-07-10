#!/usr/bin/env python3
"""Convert licensed OTF/TTF wedding fonts to self-hosted woff2 files.

Place source files in site/assets/fonts/source/ using these names:
  - Simple-Serenity-Script.otf
  - Parfumerie-Script.otf
  - Kulachat-Serif-Regular.otf

Then run:
  python scripts/prepare-fonts.py
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "site" / "assets" / "fonts" / "source"
OUT_DIR = ROOT / "site" / "assets" / "fonts"

MAPPINGS = {
    "Simple-Serenity-Script.otf": "simple-serenity-script.woff2",
    "Parfumerie-Script.otf": "parfumerie-script.woff2",
    "Kulachat-Serif-Regular.otf": "kulachat-serif-regular.woff2",
}


def convert(src: Path, dest: Path) -> None:
    try:
        from fontTools.ttLib import TTFont
        from fontTools.woff2 import compress
    except ImportError:
        print("Install fonttools: pip install fonttools brotli", file=sys.stderr)
        sys.exit(1)

    tmp = dest.with_suffix(".tmp.ttf")
    font = TTFont(src)
    font.flavor = None
    font.save(tmp)
    compress(tmp, dest)
    tmp.unlink(missing_ok=True)
    print(f"Wrote {dest.relative_to(ROOT)}")


def main() -> None:
    if not SOURCE_DIR.is_dir():
        SOURCE_DIR.mkdir(parents=True)
        print(f"Created {SOURCE_DIR.relative_to(ROOT)}")
        print("Add licensed OTF files there, then re-run this script.")
        return

    converted = 0
    for source_name, out_name in MAPPINGS.items():
        src = SOURCE_DIR / source_name
        if not src.exists():
            # Also accept .ttf extension
            alt = src.with_suffix(".ttf")
            if alt.exists():
                src = alt
            else:
                print(f"Skip (missing): {source_name}")
                continue
        convert(src, OUT_DIR / out_name)
        converted += 1

    if converted == 0:
        print("No source fonts found. Expected files:")
        for name in MAPPINGS:
            print(f"  - {SOURCE_DIR / name}")
        sys.exit(1)

    print(f"Converted {converted} font(s).")


if __name__ == "__main__":
    main()
