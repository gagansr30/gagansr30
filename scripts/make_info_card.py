"""
make_info_card.py

Hand-authored neofetch-style info card SVG: info-card.svg.

Draws a small terminal panel with a title bar and colored key/value rows
(Now, Prev, Stack, Highlights). Each row fades and slides in on a short
stagger (CSS keyframes + animation-delay) so the panel looks like it's
printing next to the ASCII portrait.

Set STATIC=1 in the environment to emit a frozen (non-animated) frame,
useful for local previews.
"""

import os

OUT_PATH = "info-card.svg"
STATIC = os.environ.get("STATIC") == "1"

WIDTH = 490
HEIGHT = 300
LABEL_COLOR = "#7ee787"
TEXT_COLOR = "#c9d1d9"
BG = "#0d1117"
BORDER = "#30363d"

ROWS = [
    ("Now", "MSc Advanced Computer Science (AI), University of Leeds"),
    ("Prev", "ML Engineer Intern (AI) - Vosyn Inc. | SWE Intern - GAO Tek Inc."),
    ("Stack", "Python, FastAPI, React/TS, RAG/LLMs, PyTorch, Vertex AI, Docker/K8s, AWS/Azure/GCP"),
    ("Highlights", "Shipped AI CV Tailoring Tool end-to-end (Claude API, Stripe billing, <20s ATS export)"),
]


def row_svg(i, label, value, y):
    delay_ms = 160 + i * 160
    cls = "" if STATIC else ' class="line"'
    style = "" if STATIC else f' style="animation-delay:{delay_ms}ms"'
    return (
        f'<text x="22" y="{y}"{cls}{style} font-size="13.5">'
        f'<tspan fill="{LABEL_COLOR}" font-weight="bold">{label}:</tspan> '
        f'<tspan fill="{TEXT_COLOR}">{value}</tspan>'
        f'</text>'
    )


def main():
    rows_svg = []
    y = 144
    for i, (label, value) in enumerate(ROWS):
        rows_svg.append(row_svg(i, label, value, y))
        y += 28

    style_block = "" if STATIC else (
        '\n  <style>\n'
        '    .line { opacity: 0; transform-box: fill-box; transform-origin: left center; animation: typein 0.5s ease-out forwards; }\n'
        '    @keyframes typein {\n'
        '      0%   { opacity: 0; transform: translateX(-10px); }\n'
        '      100% { opacity: 1; transform: translateX(0); }\n'
        '    }\n'
        '  </style>'
    )

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" '
        f'font-family="Consolas, \'Courier New\', monospace">{style_block}\n'
        f'  <rect x="0" y="0" width="{WIDTH}" height="{HEIGHT}" rx="10" fill="{BG}" stroke="{BORDER}"/>\n'
        f'  <rect x="0" y="0" width="{WIDTH}" height="34" rx="10" fill="#161b22"/>\n'
        f'  <circle cx="22" cy="17" r="6" fill="#ff5f56" class="titlebar-dot"/>\n'
        f'  <circle cx="42" cy="17" r="6" fill="#ffbd2e" class="titlebar-dot"/>\n'
        f'  <circle cx="62" cy="17" r="6" fill="#27c93f" class="titlebar-dot"/>\n'
        f'  <text x="{WIDTH/2}" y="21" text-anchor="middle" fill="#8b949e" font-size="12">neofetch</text>\n'
        f'  {"".join(rows_svg)}\n'
        f'</svg>\n'
    )

    with open(OUT_PATH, "w") as f:
        f.write(svg)

    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
