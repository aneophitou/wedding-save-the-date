#!/usr/bin/env python3
"""Convert licensed OTF/TTF wedding fonts to self-hosted woff2 files.

Place source files in site/assets/fonts/source/ using these names:
  - Simple Serenity Script.ttf
  - Simple Serenity Serif.ttf
  - Sloop-ScriptThree.ttf
  - parfumerie-script-old-style.otf

Noto Serif Display date numerals are generated separately as a woff2
subset (noto-serif-display-regular.woff2) from site/fonts/.

Then run:
  python scripts/prepare-fonts.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "site" / "assets" / "fonts" / "source"
OUT_DIR = ROOT / "site" / "assets" / "fonts"

MAPPINGS = {
    "Simple Serenity Script.ttf": "simple-serenity-script.woff2",
    "Simple Serenity Serif.ttf": "simple-serenity-serif.woff2",
    "Sloop-ScriptThree.ttf": "sloop-script-three.woff2",
    "parfumerie-script-old-style.otf": "parfumerie-script.woff2",
}


def resolve_source(source_name: str) -> Path | None:
    base = SOURCE_DIR / source_name
    if base.exists():
        return base
    stem = Path(source_name).stem
    for ext in (".otf", ".ttf", ".OTF", ".TTF"):
        candidate = SOURCE_DIR / f"{stem}{ext}"
        if candidate.exists():
            return candidate
    return None


def convert(src: Path, dest: Path) -> None:
    try:
        from fontTools.ttLib import TTFont
        from fontTools.ttLib.woff2 import compress
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
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    if not SOURCE_DIR.is_dir():
        SOURCE_DIR.mkdir(parents=True)
        print(f"Created {SOURCE_DIR.relative_to(ROOT)}")
        print("Add licensed OTF files there, then re-run this script.")
        return

    converted = 0
    for source_name, out_name in MAPPINGS.items():
        src = resolve_source(source_name)
        if src is None:
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
