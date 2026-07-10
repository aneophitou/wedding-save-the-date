"""Extract embedded raster images from background.svg and compress to WebP."""
from __future__ import annotations

import base64
import io
import re
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "Save The Date Assets" / "background.svg"
OUTPUT_SVG = ROOT / "site" / "assets" / "background.svg"
OUTPUT_DIR = ROOT / "site" / "assets" / "bg-images"

PATTERN = re.compile(
    r'xlink:href="data:image/(png|jpeg|jpg);base64,([^"]+)"'
)


def main() -> None:
    svg = INPUT.read_text(encoding="utf-8")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    total_before = 0
    total_after = 0
    index = 0

    def replace_match(match: re.Match[str]) -> str:
        nonlocal index, total_before, total_after
        index += 1
        raw = base64.b64decode(match.group(2))
        total_before += len(raw)

        image = Image.open(io.BytesIO(raw))
        if image.mode not in ("RGB", "RGBA"):
            image = image.convert("RGBA")

        file_name = f"bg-{index:02d}.webp"
        out_path = OUTPUT_DIR / file_name
        image.save(out_path, format="WEBP", quality=82, method=6)
        total_after += out_path.stat().st_size

        return f'xlink:href="/assets/bg-images/{file_name}"'

    optimized_svg = PATTERN.sub(replace_match, svg)
    OUTPUT_SVG.write_text(optimized_svg, encoding="utf-8")

    svg_size = OUTPUT_SVG.stat().st_size
    print(f"Extracted {index} embedded images")
    print(f"Raster before: {total_before / 1024 / 1024:.2f} MB")
    print(f"Raster after:  {total_after / 1024 / 1024:.2f} MB")
    print(f"SVG file size: {svg_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
