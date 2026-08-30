#!/usr/bin/env python3
"""Render data/contributions.json as a self-contained animated SVG."""

import datetime as dt
import html
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IN_PATH = os.path.join(ROOT, "data", "contributions.json")
OUT_PATH = os.environ.get("HEATMAP_OUTPUT", os.path.join(ROOT, "contrib-heatmap.svg"))
STATIC = bool(os.environ.get("STATIC"))
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
CELL, GAP, STEP = 12, 3, 15
PAD, LABEL_W, LABEL_H, TITLE_H = 22, 30, 20, 30


def level(count):
    if count == 0:
        return 0
    if count <= 3:
        return 1
    if count <= 8:
        return 2
    if count <= 15:
        return 3
    if count <= 25:
        return 4
    return 5


def grid_for(days):
    first = dt.date.fromisoformat(days[0]["date"])
    column = [None] * ((first.weekday() + 1) % 7)
    grid = []
    for item in days:
        weekday = (dt.date.fromisoformat(item["date"]).weekday() + 1) % 7
        while len(column) < weekday:
            column.append(None)
        column.append(item)
        if len(column) == 7:
            grid.append(column)
            column = []
    if column:
        grid.append(column + [None] * (7 - len(column)))
    return grid


def render(data):
    grid = grid_for(data["days"])
    cols = len(grid)
    art_w, art_h = cols * STEP, 7 * STEP
    width = PAD + LABEL_W + art_w + PAD
    height = TITLE_H + LABEL_H + art_h + 100 + PAD
    grid_x, grid_y = PAD + LABEL_W, TITLE_H + LABEL_H
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
        ('<style>.c{opacity:1}</style>' if STATIC else '<style>@keyframes cell{0%{opacity:0;transform:translateY(-6px)}100%{opacity:1;transform:translateY(0)}}.c{opacity:0;animation:cell .42s cubic-bezier(.2,.8,.2,1) both}</style>'),
        '<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0d1420"/><stop offset="1" stop-color="#0a0e14"/></linearGradient></defs>',
        f'<rect width="{width}" height="{height}" rx="12" fill="url(#bg)"/><rect x=".5" y=".5" width="{width-1}" height="{height-1}" rx="12" fill="none" stroke="#1f6feb" stroke-opacity=".55"/>',
        f'<line x1="0" y1="{TITLE_H}" x2="{width}" y2="{TITLE_H}" stroke="#1f6feb" stroke-opacity=".35"/>',
    ]
    for index, color in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
        parts.append(f'<circle cx="{PAD + index*16}" cy="15" r="5" fill="{color}"/>')
    parts.append(f'<text x="{width/2:.1f}" y="19" fill="#7d8590" font-size="12" text-anchor="middle">dias@github: ~/contributions --graph</text>')

    seen = set()
    for col, week in enumerate(grid):
        for item in week:
            if not item:
                continue
            date = dt.date.fromisoformat(item["date"])
            key = (date.year, date.month)
            if key not in seen and date.day <= 7:
                seen.add(key)
                parts.append(f'<text x="{grid_x + col*STEP}" y="44" fill="#7d8590" font-size="10">{date.strftime("%b")}</text>')
            break
    for row, label in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        parts.append(f'<text x="{PAD}" y="{grid_y + row*STEP + 9.5}" fill="#7d8590" font-size="9">{label}</text>')

    for col, week in enumerate(grid):
        for row, item in enumerate(week):
            if not item:
                continue
            x, y = grid_x + col*STEP, grid_y + row*STEP
            count = item["count"]
            delay = col * .018 + row * .045
            title = html.escape(f'{item["date"]}: {count} contribution{"s" if count != 1 else ""}')
            parts.append(f'<rect class="c" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" fill="{PALETTE[level(count)]}" style="animation-delay:{delay:.3f}s"><title>{title}</title></rect>')

    legend_y = grid_y + art_h + 7
    legend_x = width - PAD - 130
    parts.append(f'<text x="{legend_x}" y="{legend_y+9}" fill="#7d8590" font-size="10" text-anchor="end">Less</text>')
    x = legend_x + 8
    for color in PALETTE:
        parts.append(f'<rect x="{x}" y="{legend_y}" width="11" height="11" rx="2" fill="{color}"/>')
        x += 12
    parts.append(f'<text x="{x+4}" y="{legend_y+9}" fill="#7d8590" font-size="10">More</text>')

    sep = legend_y + 30
    parts.append(f'<line x1="0" y1="{sep}" x2="{width}" y2="{sep}" stroke="#1f6feb" stroke-opacity=".25"/>')
    total = data["total_contributions"]
    current = data["current_streak"]["length"]
    longest = data["longest_streak"]["length"]
    best = data["best_day"]
    rng = data["range"]
    parts.append(f'<text x="{PAD}" y="{sep+26}" font-size="13"><tspan fill="#39d353" font-weight="700">{total:,}</tspan><tspan fill="#7d8590"> contributions in the last year</tspan></text>')
    parts.append(f'<text x="{width-PAD}" y="{sep+26}" font-size="12" fill="#7d8590" text-anchor="end">{rng["start"]} &#8594; {rng["end"]}</text>')
    parts.append(f'<text x="{PAD}" y="{sep+51}" font-size="13" fill="#7d8590">current streak <tspan fill="#22d3ee" font-weight="700">{current} days</tspan><tspan>   &#183;   longest </tspan><tspan fill="#22d3ee" font-weight="700">{longest} days</tspan></text>')
    parts.append(f'<text x="{width-PAD}" y="{sep+51}" font-size="12" fill="#7d8590" text-anchor="end">best day <tspan fill="#f2cc60" font-weight="700">{best["count"]}</tspan> on {best["date"]}</text>')
    parts.append('</svg>')
    return ''.join(parts)


if __name__ == "__main__":
    with open(IN_PATH, encoding="utf-8") as handle:
        svg = render(json.load(handle))
    with open(OUT_PATH, "w", encoding="utf-8") as handle:
        handle.write(svg)
    print(f"wrote {OUT_PATH} ({len(svg)} bytes)")
