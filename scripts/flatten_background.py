"""Flatten the composited background SVG into a single optimized WebP.

The original background.svg references four 2501x2501 WebP images (~2.1 MB)
that are only ever displayed a few hundred pixels wide. This script bakes the
exact compositing the SVG performs into one small image:

- Left square  = photo bg-04 masked by the luminance of bg-02
- Right square = photo bg-03 masked by the luminance of bg-01
- The whole thing is drawn at 40% opacity over the cream page background.
"""

from PIL import Image

SRC = "site/assets/bg-images"
OUT = "site/assets/background.webp"
HALF = 800  # per-square size; final image is (2*HALF) x HALF
GLOBAL_OPACITY = 0.4
PAGE_BG = (251, 251, 243)  # #fbfbf3


def masked_square(photo_name, mask_name):
    photo = Image.open(f"{SRC}/{photo_name}.webp").convert("RGB").resize(
        (HALF, HALF), Image.LANCZOS
    )
    mask = Image.open(f"{SRC}/{mask_name}.webp").convert("L").resize(
        (HALF, HALF), Image.LANCZOS
    )
    square = photo.convert("RGBA")
    square.putalpha(mask)
    return square


def main():
    right = masked_square("bg-03", "bg-01")
    left = masked_square("bg-04", "bg-02")

    canvas = Image.new("RGBA", (2 * HALF, HALF), (0, 0, 0, 0))
    canvas.alpha_composite(left, (0, 0))
    canvas.alpha_composite(right, (HALF, 0))

    # Apply the SVG's global 40% opacity.
    alpha = canvas.getchannel("A").point(lambda a: int(a * GLOBAL_OPACITY))
    canvas.putalpha(alpha)

    # Bake onto the cream page background so the export can be fully opaque.
    background = Image.new("RGB", canvas.size, PAGE_BG)
    background.paste(canvas, (0, 0), canvas)

    background.save(OUT, "WEBP", quality=82, method=6)
    print(f"Wrote {OUT} at {background.size}")


if __name__ == "__main__":
    main()
