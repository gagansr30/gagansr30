"""
make_ascii_svg.py

Converts source-prepped.png (see prep_photo.py) into a self-typing,
monochrome ASCII-art SVG: avi-ascii.svg.

The image is downsampled to a character grid, and each pixel's brightness
picks a glyph from a density ramp (sparse for bright areas, dense for
dark). Each row is wrapped in a horizontal clip that wipes left-to-right,
staggered top to bottom, so the whole portrait prints once and freezes --
no looping.
"""

from PIL import Image

SRC_PATH = "source-prepped.png"
OUT_PATH = "avi-ascii.svg"

COLS = 100
ROWS = 53
FONT_SIZE = 6
CHAR_W = FONT_SIZE * 0.6
CHAR_H = FONT_SIZE * 1.05
FILL = "#c9d1d9"
BG = "#0d1117"

# bright (sparse) -> dark (dense); leading space clears background to nothing.
RAMP = " .`:-=+*cs#%@"


def image_to_grid(path):
    img = Image.open(path).convert("L").resize((COLS, ROWS))
    pixels = list(img.getdata())
    return [pixels[r * COLS:(r + 1) * COLS] for r in range(ROWS)]


def brightness_to_char(value):
    idx = int(round((255 - value) / 255 * (len(RAMP) - 1)))
    return RAMP[max(0, min(idx, len(RAMP) - 1))]


def main():
    grid = image_to_grid(SRC_PATH)
    width = COLS * CHAR_W
    height = ROWS * CHAR_H

    rows_svg = []
    for r, row in enumerate(grid):
        chars = "".join(brightness_to_char(v) for v in row)
        y = (r + 1) * CHAR_H
        delay = r * 0.045
        clip_id = f"wipe{r}"
        rows_svg.append(
            f'<clipPath id="{clip_id}">'
            f'<rect x="0" y="{y - CHAR_H:.2f}" width="0" height="{CHAR_H:.2f}">'
            f'<animate attributeName="width" from="0" to="{width:.2f}" '
            f'begin="{delay:.3f}s" dur="0.22s" fill="freeze" '
            f'calcMode="spline" keySplines="0.3 0 0.2 1"/>'
            f'</rect></clipPath>'
            f'<text x="0" y="{y:.2f}" clip-path="url(#{clip_id})" '
            f'font-family="Consolas, monospace" font-size="{FONT_SIZE}" '
            f'fill="{FILL}" xml:space="preserve">{chars}</text>'
        )

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" '
        f'height="{height:.0f}" viewBox="0 0 {width:.0f} {height:.0f}">'
        f'<rect width="100%" height="100%" fill="{BG}"/>'
        f'{"".join(rows_svg)}'
        f'</svg>'
    )

    with open(OUT_PATH, "w") as f:
        f.write(svg)

    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
