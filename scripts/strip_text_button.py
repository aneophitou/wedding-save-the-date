"""Remove the decorative ADD TO CALENDAR text from text.svg."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "site" / "assets" / "text.svg"
TARGET = ROOT / "site" / "assets" / "text-no-button.svg"

svg = SOURCE.read_text(encoding="utf-8")

# Remove only the decorative "Add to Calendar" button art. Keep clipPath
# 8539229197 — it clips the uppercase "SAVE THE DATE" label.
svg = re.sub(r"<clipPath id=\"ce581e5eeb\">.*?</clipPath>", "", svg, flags=re.S)
svg = re.sub(r"<g clip-path=\"url\(#ce581e5eeb\)\">.*?</g></g>", "", svg, flags=re.S)

TARGET.write_text(svg, encoding="utf-8")
print(f"Wrote {TARGET.name}")
