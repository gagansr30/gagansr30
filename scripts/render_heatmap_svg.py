"""
render_heatmap_svg.py

Reads data/contributions.json (written by fetch_contributions.py) and renders
contrib-heatmap.svg: a 53-week x 7-day calendar of rounded, colored boxes with
a one-time diagonal slide-down reveal (CSS keyframes), a Less->More legend,
and a stats footer.
"""
import html
import json
import os
from datetime import datetime

IN_PATH = os.path.join("data", "contributions.json")
OUT_PATH = "contrib-heatmap.svg"

ROWS = 7
COLS = 53
CELL = 12
GAP = 3
LEFT_PAD = 30
TOP_PAD = 24
RIGHT_PAD = 10
BOTTOM_PAD = 54

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
DAY_LABELS = {1: "Mon", 3: "Wed", 5: "Fri"}


def esc(s):
    return html.escape(s, quote=True)


def month_label(date_str):
    y, m, _ = date_str.split("-")
    return MONTH_NAMES[int(m) - 1]


def render(payload):
    grid = payload["grid"]
    stats = payload["stats"]

    grid_w = COLS * (CELL + GAP) - GAP
    grid_h = ROWS * (CELL + GAP) - GAP
    width = LEFT_PAD + grid_w + RIGHT_PAD
    height = TOP_PAD + grid_h + BOTTOM_PAD

    rects = []
    for c in range(COLS):
        for r in range(ROWS):
            day = grid[c][r]
            if not day:
                continue
            x = LEFT_PAD + c * (CELL + GAP)
            y = TOP_PAD + r * (CELL + GAP)
            level = day.get("level", 0) or 0
            fill = PALETTE[level] if 0 <= level < len(PALETTE) else PALETTE[0]
            delay = (c + r) * 14
            count = day.get("count", 0)
            noun = "contribution" if count == 1 else "contributions"
            rects.append(
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" ry="2" '
                f'fill="{fill}" class="cell" style="animation-delay:{delay}ms">'
                f'<title>{count} {noun} on {esc(day.get("date",""))}</title></rect>'
            )

    month_labels = []
    prev_month = None
    for c in range(COLS):
        day = grid[c][0]
        if not day or not day.get("date"):
            continue
        m = day["date"][:7]
        if m != prev_month:
            x = LEFT_PAD + c * (CELL + GAP)
            month_labels.append(f'<text x="{x}" y="{TOP_PAD-8}" class="mlabel">{month_label(day["date"])}</text>')
            prev_month = m

    day_labels = []
    for row, label in DAY_LABELS.items():
        y = TOP_PAD + row * (CELL + GAP) + CELL - 2
        day_labels.append(f'<text x="{LEFT_PAD-6}" y="{y}" text-anchor="end" class="dlabel">{label}</text>')

    legend_y = TOP_PAD + grid_h + 22
    legend_boxes = []
    for i, col in enumerate(PALETTE):
        x = LEFT_PAD + grid_w - 118 + i * 16
        legend_boxes.append(f'<rect x="{x}" y="{legend_y}" width="11" height="11" rx="2" fill="{col}"/>')

    best = stats.get("best_day") or {}
    best_date = best.get("date", "")
    best_str = best_date
    try:
        best_str = datetime.strptime(best_date, "%Y-%m-%d").strftime("%B %d, %Y")
    except Exception:
        pass

    total = stats.get("total", 0)
    footer = (
        f'{total} contribution{"s" if total != 1 else ""} in the last year  \u2022  '
        f'current streak {stats.get("current_streak", 0)}  \u2022  '
        f'longest streak {stats.get("longest_streak", 0)}  \u2022  '
        f'best day {best.get("count", 0)} on {best_str}'
    )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" font-family="Consolas, 'Courier New', monospace">
  <style>
    .mlabel {{ fill: #8b949e; font-size: 11px; }}
    .dlabel {{ fill: #8b949e; font-size: 10px; }}
    .legend-label {{ fill: #8b949e; font-size: 10px; }}
    .footer {{ fill: #c9d1d9; font-size: 12px; }}
    .cell {{
      opacity: 0;
      transform-box: fill-box;
      transform-origin: center;
      animation: reveal 0.5s ease-out forwards;
    }}
    @keyframes reveal {{
      0%   {{ opacity: 0; transform: translate(-6px, -10px); }}
      100% {{ opacity: 1; transform: translate(0, 0); }}
    }}
  </style>
  <rect x="0" y="0" width="{width}" height="{height}" fill="#0d1117"/>
  {"".join(month_labels)}
  {"".join(day_labels)}
  {"".join(rects)}
  <text x="{LEFT_PAD+grid_w-158}" y="{legend_y+10}" class="legend-label">Less</text>
  {"".join(legend_boxes)}
  <text x="{LEFT_PAD+grid_w+4}" y="{legend_y+10}" class="legend-label">More</text>
  <text x="{LEFT_PAD}" y="{height-14}" class="footer">{esc(footer)}</text>
</svg>'''
    return svg


def main():
    with open(IN_PATH, "r", encoding="utf-8") as f:
        payload = json.load(f)

    svg = render(payload)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg)

    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
