"""Remove the decorative ADD TO CALENDAR text from text.svg."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "site" / "assets" / "text.svg"
TARGET = ROOT / "site" / "assets" / "text-no-button.svg"

svg = SOURCE.read_text(encoding="utf-8")

svg = re.sub(r"<clipPath id=\"ce581e5eeb\">.*?</clipPath>", "", svg, flags=re.S)
svg = re.sub(r"<clipPath id=\"8539229197\">.*?</clipPath>", "", svg, flags=re.S)
svg = re.sub(r"<g clip-path=\"url\(#ce581e5eeb\)\">.*?</g></g>", "", svg, flags=re.S)

TARGET.write_text(svg, encoding="utf-8")
print(f"Wrote {TARGET.name}")
