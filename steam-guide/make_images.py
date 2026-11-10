"""Images for the Steam guide: one gallery of map previews per section (chapter / mode) and a category legend.

Run from anywhere:  python steam-guide/make_images.py
Reads data/levels.csv and maps/*.html (marker data), writes steam-guide/images/gallery_*.png and legend.png.
"""
import collections
import csv
import json
import os
import re

import numpy as np
from PIL import Image, ImageDraw, ImageFont

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAPS = os.path.join(SITE, 'maps')
OUT = os.path.join(SITE, 'steam-guide', 'images')
BG = (21, 19, 15)
PANEL = (31, 27, 21)
TEXT = (232, 226, 214)
SUB = (185, 173, 151)
FONT = 'C:/Windows/Fonts/segoeui.ttf'
FONTB = 'C:/Windows/Fonts/segoeuib.ttf'


def font(size, bold=False):
    return ImageFont.truetype(FONTB if bold else FONT, size)


def hexrgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def page(level):
    h = open(os.path.join(MAPS, level + '.html'), encoding='utf-8').read()
    data = json.loads(re.search(r'const DATA = (.*);\n', h).group(1))
    cats = {c['id']: c for c in json.loads(re.search(r'const CATS = (.*);\n', h).group(1))}
    return data, cats


_icons = {}


def badge(icon, ring, d):
    """Round marker like the map page: dark disc, icon, coloured ring. d = diameter in px."""
    key = (icon, ring, d)
    if key in _icons:
        return _icons[key]
    s = d * 4  # supersample
    im = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    dr.ellipse((0, 0, s - 1, s - 1), fill=(17, 17, 17, 255))
    if icon and os.path.exists(os.path.join(MAPS, icon)):
        ic = Image.open(os.path.join(MAPS, icon)).convert('RGBA')
        w, h = ic.size
        c = min(w, h)
        ic = ic.crop(((w - c) // 2, (h - c) // 2, (w + c) // 2, (h + c) // 2)).resize((s, s), Image.LANCZOS)
        mask = Image.new('L', (s, s), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, s - 1, s - 1), fill=255)
        im.paste(ic, (0, 0), Image.composite(ic.split()[3], Image.new('L', (s, s), 0), mask))
    w = max(s // 9, 4)
    dr.ellipse((w // 2, w // 2, s - 1 - w // 2, s - 1 - w // 2), outline=hexrgb(ring) + (255,), width=w)
    im = im.resize((d, d), Image.LANCZOS)
    _icons[key] = im
    return im


def blend_layers(data, S):
    """The page's default background: relief, with the minimap overlay-blended onto it (as the page's CSS
    mix-blend-mode: overlay) or, for territory regions, drawn translucent over it."""
    dark = (42, 36, 27, 255)
    ld = lambda u: Image.open(os.path.join(MAPS, u)).convert('RGBA').resize((S, S), Image.LANCZOS)
    base = Image.new('RGBA', (S, S), dark)
    if data.get('terrain'):
        base.alpha_composite(ld(data['terrain']))
    if data.get('bg'):
        if data.get('regions') or not data.get('terrain'):
            base.alpha_composite(ld(data['bg']))
        else:
            top = Image.new('RGBA', (S, S), dark)
            top.alpha_composite(ld(data['bg']))
            b = np.asarray(base, float)[..., :3] / 255
            a = np.asarray(top, float)[..., :3] / 255
            ov = np.where(b < .5, 2 * a * b, 1 - 2 * (1 - a) * (1 - b))
            base = Image.fromarray((ov * 255).round().astype(np.uint8), 'RGB').convert('RGBA')
    return base


def tile(level, size):
    """Map preview: background (minimap or terrain relief, else grid) and markers, framed like the page."""
    data, cats = page(level)
    S = 1024
    ms = data['markers']
    if data.get('bg'):
        x0, y0, x1, y1 = 0, 0, S, S
    else:  # page fits the marker bounds (+8%) when there is no minimap
        xs, ys = [m['x'] for m in ms], [-m['y'] for m in ms]
        cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
        half = max(max(xs) - min(xs), max(ys) - min(ys)) / 2 * 1.16 + 20
        x0, y0, x1, y1 = cx - half, cy - half, cx + half, cy + half
    canvas = blend_layers(data, S)
    if not data.get('bg'):
        g = ImageDraw.Draw(canvas)
        for i in range(0, S + 1, 64):
            g.line([(i, 0), (i, S)], fill=(58, 50, 38, 255))
            g.line([(0, i), (S, i)], fill=(58, 50, 38, 255))
    # crop the frame (may extend past the 1024 square) onto a dark board
    k = size / (x1 - x0)
    board = Image.new('RGBA', (size, size), (42, 36, 27, 255))
    view = canvas.resize((max(1, round(S * k)), max(1, round(S * k))), Image.LANCZOS)
    board.paste(view, (round(-x0 * k), round(-y0 * k)), view)
    d = max(12, round(size / 17))
    for m in sorted(ms, key=lambda m: m['cat'] != 'wildlife'):  # wildlife underneath
        dd = round(d * 0.8) if m['cat'] == 'wildlife' else d
        b = badge(m.get('icon'), m.get('ring') or cats[m['cat']]['color'], dd)
        px, py = round((m['x'] - x0) * k - dd / 2), round((-m['y'] - y0) * k - dd / 2)
        board.paste(b, (px, py), b)
    return board


def gallery(rows, title, path, cols=4, size=290, gap=16):
    n = len(rows)
    cols = min(cols, n)
    nrows = (n + cols - 1) // cols
    label_h, head_h = 54, 64
    W = cols * size + (cols + 1) * gap
    H = head_h + nrows * (size + label_h + gap) + gap
    im = Image.new('RGB', (W, H), BG)
    dr = ImageDraw.Draw(im)
    dr.text((gap, 14), title, font=font(30, True), fill=TEXT)
    for i, r in enumerate(rows):
        x = gap + (i % cols) * (size + gap)
        y = head_h + (i // cols) * (size + label_h + gap)
        dr.rectangle((x - 1, y - 1, x + size, y + size + label_h), fill=PANEL)
        im.paste(tile(r['level'], size).convert('RGB'), (x, y))
        name = r['map_name']
        f = font(20, True)
        while dr.textlength(name, font=f) > size - 12 and f.size > 13:
            f = font(f.size - 1, True)
        dr.text((x + 8, y + size + 4), name, font=f, fill=TEXT)
        kind = r['subtitle'].split(' · ')[-1] if ' · ' in r['subtitle'] else r['subtitle']
        kind = kind.split(' (')[0]
        dr.text((x + 8, y + size + 28), kind, font=font(15), fill=SUB)
    im.save(path, optimize=True)
    if os.path.getsize(path) > 1_000_000:  # keep each guide image under 1 MB: fall back to a 256-colour palette
        im.quantize(256, method=Image.Quantize.FASTOCTREE).save(path, optimize=True)
    return im.size


def legend(rows, path):
    """Category legend: a typical icon for each category with its label and total count across all maps."""
    _, cats = page(rows[0]['level'])
    icons = collections.defaultdict(collections.Counter)
    rings = {}
    for r in rows:
        data, _ = page(r['level'])
        for m in data['markers']:
            if m.get('icon'):
                icons[m['cat']][m['icon']] += 1
                if m['cat'] == 'nest' and m.get('ring'):
                    rings[m['icon']] = m['ring']
    totals = {c: sum(int(r.get(cats[c]['label']) or 0) for r in rows) for c in cats}
    items = list(cats.values())
    cols, cw, rh, gap = 2, 600, 64, 20
    nr = (len(items) + cols - 1) // cols
    W, H = cols * cw + gap, 70 + nr * rh + gap
    im = Image.new('RGB', (W, H), BG)
    dr = ImageDraw.Draw(im)
    dr.text((gap, 14), 'Marker categories', font=font(30, True), fill=TEXT)
    for i, c in enumerate(items):
        x, y = gap + (i // nr) * cw, 70 + (i % nr) * rh
        icon = icons[c['id']].most_common(1)[0][0] if icons[c['id']] else None
        b = badge(icon, rings.get(icon, c['color']) if c['id'] == 'nest' else c['color'], 48)
        im.paste(b, (x, y), b)
        dr.text((x + 64, y + 2), c['label'], font=font(22, True), fill=TEXT)
        dr.text((x + 64, y + 30), f"{totals[c['id']]:,} on all maps", font=font(16), fill=SUB)
    im.save(path, optimize=True)
    return im.size


def main():
    rows = list(csv.DictReader(open(os.path.join(SITE, 'data', 'levels.csv'), encoding='utf-8-sig')))
    groups = collections.OrderedDict()
    for r in rows:
        groups.setdefault(r['group'], []).append(r)
    os.makedirs(OUT, exist_ok=True)
    for g, rs in groups.items():
        slug = re.sub(r'[^a-z0-9]+', '-', g.lower()).strip('-')
        p = os.path.join(OUT, f'gallery_{slug}.png')
        print(os.path.basename(p), gallery(rs, g, p), f'{os.path.getsize(p) // 1024} KB')
    p = os.path.join(OUT, 'legend.png')
    print('legend.png', legend(rows, p), f'{os.path.getsize(p) // 1024} KB')


if __name__ == '__main__':
    main()
