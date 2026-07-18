"""
prep_photo.py

One-time photo prep for the ASCII portrait pipeline (make_ascii_svg.py).

A flatly-lit face converts to a dark, unreadable blob, so this script:
  1. Removes the background with rembg so the subject is isolated.
  2. Boosts local contrast with OpenCV's CLAHE (contrast-limited adaptive
     histogram equalization), which gives a flat face real highlights
     and shadows.
  3. Composites onto pure white so the background maps to the blank end
     of the ASCII ramp (white -> spaces) used by make_ascii_svg.py.

Run once per photo:
    python scripts/prep_photo.py source-photo.jpg
"""

import io
import sys

import cv2
import numpy as np
from PIL import Image
from rembg import remove

OUT_PATH = "source-prepped.png"


def prep(src_path, out_path=OUT_PATH):
    with open(src_path, "rb") as f:
        input_bytes = f.read()

    cutout_bytes = remove(input_bytes)
    cutout = Image.open(io.BytesIO(cutout_bytes)).convert("RGBA")

    white_bg = Image.new("RGBA", cutout.size, (255, 255, 255, 255))
    composited = Image.alpha_composite(white_bg, cutout).convert("L")

    gray = np.array(composited)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    Image.fromarray(enhanced).save(out_path)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/prep_photo.py <source-photo.jpg>")
        sys.exit(1)
    prep(sys.argv[1])
