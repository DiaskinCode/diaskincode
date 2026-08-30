#!/usr/bin/env python3
"""Convert the profile photo into a monochrome, self-typing ASCII SVG."""

import html
import os
import sys
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "source-photo.jpg")
OUTPUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "dias-ascii.svg")
COLS, ROWS, CELL_W, CELL_H = 100, 53, 8, 15
RAMP = " .`:-=+*cs#%@"
PAD, TITLE_H, STATUS_H = 20, 30, 30
ART_W, ART_H = COLS * CELL_W, ROWS * CELL_H
WIDTH, HEIGHT = ART_W + PAD*2, TITLE_H + ART_H + STATUS_H + PAD
STATIC = bool(os.environ.get("STATIC"))


image = Image.open(SOURCE).convert("L")
image = ImageOps.autocontrast(image, cutoff=1)
image = image.filter(ImageFilter.GaussianBlur(radius=0.8))
image = ImageEnhance.Contrast(image).enhance(1.08)
# Fit the complete photo without distortion. Terminal characters are taller
# than they are wide, so the raw image-grid aspect ratio must account for the
# physical character-cell dimensions before centering on a white background.
source_ratio = image.width / image.height
grid_ratio = source_ratio * CELL_H / CELL_W
if grid_ratio >= COLS / ROWS:
    content_w = COLS
    content_h = max(1, round(COLS / grid_ratio))
else:
    content_h = ROWS
    content_w = max(1, round(ROWS * grid_ratio))
image = image.resize((content_w, content_h), Image.Resampling.LANCZOS)
canvas = Image.new("L", (COLS, ROWS), 255)
canvas.paste(image, ((COLS - content_w) // 2, (ROWS - content_h) // 2))
image = canvas
pixels = image.load()
rows = []
for y in range(ROWS):
    line = []
    for x in range(COLS):
        luminance = pixels[x, y] / 255
        if luminance > .92:
            line.append(" ")
        else:
            index = round((1 - luminance) * (len(RAMP) - 1))
            line.append(RAMP[max(0, min(index, len(RAMP)-1))])
    rows.append("".join(line))

parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
    '<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#111722"/><stop offset="1" stop-color="#0d1117"/></linearGradient></defs>',
    f'<rect width="{WIDTH}" height="{HEIGHT}" rx="12" fill="url(#bg)"/><rect x=".5" y=".5" width="{WIDTH-1}" height="{HEIGHT-1}" rx="12" fill="none" stroke="#30363d"/>',
    f'<line x1="0" y1="{TITLE_H}" x2="{WIDTH}" y2="{TITLE_H}" stroke="#30363d"/>',
]
for index, color in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
    parts.append(f'<circle cx="{PAD + index*16}" cy="15" r="5" fill="{color}"/>')
parts.append(f'<text x="{WIDTH/2}" y="19" fill="#7d8590" font-size="12" text-anchor="middle">dias@github: ~$ ./portrait.sh</text>')
art_top = TITLE_H + PAD * .35
for row, line in enumerate(rows):
    y = art_top + row*CELL_H + CELL_H*.74
    top = art_top + row*CELL_H
    delay = row * .11
    text = f'<text xml:space="preserve" x="{PAD}" y="{y:.1f}" fill="#c9d1d9" font-size="12.9" textLength="{ART_W}" lengthAdjust="spacing">{html.escape(line)}</text>'
    if STATIC:
        parts.append(text)
    else:
        parts.append(f'<clipPath id="r{row}"><rect x="{PAD}" y="{top:.1f}" height="{CELL_H}" width="0"><animate attributeName="width" from="0" to="{ART_W}" begin="{delay:.3f}s" dur=".11s" fill="freeze"/></rect></clipPath><g clip-path="url(#r{row})">{text}</g>')
        parts.append(f'<rect y="{top+1:.1f}" width="{CELL_W}" height="{CELL_H-2}" fill="#c9d1d9" opacity="0"><animate attributeName="x" from="{PAD}" to="{PAD+ART_W}" begin="{delay:.3f}s" dur=".11s" fill="freeze"/><set attributeName="opacity" to=".85" begin="{delay:.3f}s"/><set attributeName="opacity" to="0" begin="{delay+.11:.3f}s"/></rect>')
status_line = TITLE_H + ART_H + PAD*.35
status_y = status_line + 19
parts.append(f'<line x1="0" y1="{status_line:.1f}" x2="{WIDTH}" y2="{status_line:.1f}" stroke="#30363d"/>')
parts.append(f'<text x="{PAD}" y="{status_y:.1f}" fill="#7d8590" font-size="13">dias@github:~$ whoami <tspan fill="#c9d1d9">Dias Oralbekov</tspan></text>')
parts.append(f'<rect x="{PAD+292}" y="{status_y-12:.1f}" width="8" height="14" fill="#c9d1d9"><animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.5;.51;1" dur="1s" repeatCount="indefinite"/></rect></svg>')
svg = "".join(parts)
with open(OUTPUT, "w", encoding="utf-8") as handle:
    handle.write(svg)
print(f"wrote {OUTPUT} ({len(svg)} bytes)")
