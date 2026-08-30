#!/usr/bin/env python3
"""Generate the animated neofetch-style profile card."""

import html
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT = os.environ.get("INFO_CARD_OUTPUT", os.path.join(ROOT, "info-card.svg"))
STATIC = bool(os.environ.get("STATIC"))
WIDTH, HEIGHT, PAD, TITLE_H = 560, 430, 24, 30
ROWS = [
    ("Role", "Full-stack developer"),
    ("Base", "Astana, Kazakhstan"),
    ("Stack", "Django · Next.js · React Native"),
    ("Cloud", "AWS · Azure · Docker · CI/CD"),
    ("Studio", "Dala Digital · 65+ launches"),
    ("Proof", "4+ years · 25+ clients"),
    ("Scale", "Aleem · 600k users"),
    ("Accel", "Alchemist · San Francisco"),
    ("Status", "Open to remote worldwide"),
]
COLORS = ["#22d3ee", "#a371f7", "#39d353", "#58a6ff", "#f2cc60", "#ff7b72", "#39d353", "#a371f7", "#22d3ee"]
parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
    ('<style>.line{opacity:1}</style>' if STATIC else '<style>@keyframes line{0%{opacity:0;transform:translateX(-10px)}100%{opacity:1;transform:translateX(0)}}.line{opacity:0;animation:line .34s cubic-bezier(.2,.8,.2,1) both}</style>'),
    '<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#111722"/><stop offset="1" stop-color="#0d1117"/></linearGradient></defs>',
    f'<rect width="{WIDTH}" height="{HEIGHT}" rx="12" fill="url(#bg)"/><rect x=".5" y=".5" width="{WIDTH-1}" height="{HEIGHT-1}" rx="12" fill="none" stroke="#30363d"/>',
    f'<line x1="0" y1="{TITLE_H}" x2="{WIDTH}" y2="{TITLE_H}" stroke="#30363d"/>',
]
for index, color in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
    parts.append(f'<circle cx="{PAD + index*16}" cy="15" r="5" fill="{color}"/>')
parts.append(f'<text x="{WIDTH/2}" y="19" fill="#7d8590" font-size="12" text-anchor="middle">dias@github: ~$ neofetch</text>')
parts.append('<g class="line" style="animation-delay:.12s"><text x="24" y="70" fill="#e6edf3" font-size="22" font-weight="700">Dias Oralbekov</text><text x="24" y="94" fill="#7d8590" font-size="12">──────────────────────────────────────────────</text></g>')
for index, ((key, value), color) in enumerate(zip(ROWS, COLORS)):
    y = 128 + index*31
    delay = .25 + index*.12
    parts.append(f'<g class="line" style="animation-delay:{delay:.2f}s"><text xml:space="preserve" x="24" y="{y}" fill="{color}" font-size="14" font-weight="700">{html.escape(key.ljust(7))}</text><text x="105" y="{y}" fill="#c9d1d9" font-size="14">{html.escape(value)}</text></g>')
parts.append('<g class="line" style="animation-delay:1.45s"><text x="24" y="410" fill="#7d8590" font-size="12">● ● ●</text><text x="92" y="410" fill="#39d353" font-size="12">ready</text><rect x="137" y="399" width="8" height="14" fill="#c9d1d9"><animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.5;.51;1" dur="1s" repeatCount="indefinite"/></rect></g></svg>')
svg = "".join(parts)
with open(OUTPUT, "w", encoding="utf-8") as handle:
    handle.write(svg)
print(f"wrote {OUTPUT} ({len(svg)} bytes)")
