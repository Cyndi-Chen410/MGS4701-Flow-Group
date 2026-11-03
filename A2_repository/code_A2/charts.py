"""Small Pillow chart library (no matplotlib available in this environment)."""
from PIL import Image, ImageDraw, ImageFont
import math, random

FONT = '/System/Library/Fonts/Supplemental/Arial.ttf'
FONT_B = '/System/Library/Fonts/Supplemental/Arial Bold.ttf'

import os
# Cross-platform font lookup (fall back if the macOS path is absent)
if not os.path.exists(FONT) or not os.path.exists(FONT_B):
    candidates = [
        ('C:/Windows/Fonts/arial.ttf', 'C:/Windows/Fonts/arialbd.ttf'),
        ('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'),
        ('/System/Library/Fonts/Supplemental/Arial.ttf', '/System/Library/Fonts/Supplemental/Arial Bold.ttf'),
    ]
    for reg, bold in candidates:
        if os.path.exists(reg) and os.path.exists(bold):
            FONT, FONT_B = reg, bold
            break
INK = (33, 37, 41)
MUTED = (110, 117, 125)
GRID = (226, 230, 234)
PALETTE = [(31, 78, 121), (197, 90, 17), (46, 125, 50), (123, 31, 162), (0, 121, 140), (198, 40, 40)]

def _font(size, bold=False):
    return ImageFont.truetype(FONT_B if bold else FONT, size)

def _text(d, xy, s, size=26, fill=INK, bold=False, anchor='la'):
    d.text(xy, s, font=_font(size, bold), fill=fill, anchor=anchor)

def _canvas(w=1800, h=1050):
    im = Image.new('RGB', (w, h), 'white')
    return im, ImageDraw.Draw(im)

def _axes(d, L, R, T, B, ymax, ylabel, ticks=5, fmt='{:.0f}'):
    for i in range(ticks + 1):
        y = B - (B - T) * i / ticks
        d.line([(L, y), (R, y)], fill=GRID, width=2)
        _text(d, (L - 14, y), fmt.format(ymax * i / ticks), 24, MUTED, anchor='rm')
    _text(d, ((L + R) / 2, B + 95), '', 26)
    d.line([(L, T), (L, B)], fill=INK, width=3)
    d.line([(L, B), (R, B)], fill=INK, width=3)
    # y label rotated
    tmp = Image.new('RGBA', (500, 50), (0, 0, 0, 0))
    td = ImageDraw.Draw(tmp); td.text((0, 0), ylabel, font=_font(26), fill=MUTED)
    tmp = tmp.rotate(90, expand=True)
    # place
    return

def bar(path, labels, values, ylabel, title, figsize=(1800, 1050), color=PALETTE[0], ymax=None,
        value_fmt='{:.0f}', note=None, xtick_size=26):
    im, d = _canvas(*figsize); W, H = im.size
    L, R, T, B = 190, W - 70, 150, H - 230
    ymax = ymax or max(values) * 1.18
    _text(d, (L, 60), title, 38, INK, bold=True)
    if note: _text(d, (L, 108), note, 24, MUTED)
    # grid + ticks
    for i in range(6):
        y = B - (B - T) * i / 5
        d.line([(L, y), (R, y)], fill=GRID, width=2)
        _text(d, (L - 16, y), value_fmt.format(ymax * i / 5), 24, MUTED, anchor='rm')
    d.line([(L, T), (L, B)], fill=INK, width=3); d.line([(L, B), (R, B)], fill=INK, width=3)
    n = len(values); slot = (R - L) / n; bw = slot * 0.56
    for i, (lab, v) in enumerate(zip(labels, values)):
        x = L + slot * (i + 0.5)
        y = B - (B - T) * v / ymax
        d.rectangle([x - bw / 2, y, x + bw / 2, B], fill=color)
        _text(d, (x, y - 12), value_fmt.format(v), 26, INK, bold=True, anchor='mb')
        # wrap label
        words = lab.split(); lines = []; cur = ''
        for w_ in words:
            if len(cur + ' ' + w_) > 18 and cur: lines.append(cur); cur = w_
            else: cur = (cur + ' ' + w_).strip()
        lines.append(cur)
        for k, ln in enumerate(lines[:3]):
            _text(d, (x, B + 22 + k * 30), ln, xtick_size, INK, anchor='ma')
    # y label
    tmp = Image.new('RGBA', (600, 44), (255, 255, 255, 0)); td = ImageDraw.Draw(tmp)
    td.text((0, 0), ylabel, font=_font(26), fill=MUTED); tmp = tmp.rotate(90, expand=True)
    im.paste(tmp, (40, int((T + B) / 2 - tmp.size[1] / 2)), tmp)
    im.save(path, dpi=(200, 200))
    return path

def hbar(path, labels, values, xlabel, title, figsize=(1800, 1000), color=PALETTE[0], fmt='{:.0f}',
         xmax=None, note=None, label_w=430):
    im, d = _canvas(*figsize); W, H = im.size
    L, R, T, B = label_w, W - 110, 150, H - 130
    xmax = xmax or max(values) * 1.15
    _text(d, (60, 60), title, 38, INK, bold=True)
    if note: _text(d, (60, 108), note, 24, MUTED)
    for i in range(6):
        x = L + (R - L) * i / 5
        d.line([(x, T), (x, B)], fill=GRID, width=2)
        _text(d, (x, B + 16), fmt.format(xmax * i / 5), 24, MUTED, anchor='ma')
    n = len(values); slot = (B - T) / n; bh = slot * 0.6
    for i, (lab, v) in enumerate(zip(labels, values)):
        y = T + slot * (i + 0.5)
        d.rectangle([L, y - bh / 2, L + (R - L) * v / xmax, y + bh / 2], fill=color)
        _text(d, (L - 18, y), lab, 26, INK, anchor='rm')
        _text(d, (L + (R - L) * v / xmax + 12, y), fmt.format(v), 26, INK, bold=True, anchor='lm')
    d.line([(L, T), (L, B)], fill=INK, width=3); d.line([(L, B), (R, B)], fill=INK, width=3)
    _text(d, ((L + R) / 2, B + 70), xlabel, 26, MUTED, anchor='ma')
    im.save(path, dpi=(200, 200))
    return path

def stacked(path, cats, series, title, ylabel='Share of programmes (%)', figsize=(1800, 1050), note=None):
    im, d = _canvas(*figsize); W, H = im.size
    L, R, T, B = 190, W - 380, 150, H - 220
    _text(d, (L, 60), title, 38, INK, bold=True)
    if note: _text(d, (L, 108), note, 24, MUTED)
    n = len(cats); slot = (R - L) / n; bw = slot * 0.6
    for i in range(6):
        y = B - (B - T) * i / 5
        d.line([(L, y), (R, y)], fill=GRID, width=2)
        _text(d, (L - 16, y), f'{i*20}', 24, MUTED, anchor='rm')
    names = list(series.keys())
    for i, c in enumerate(cats):
        x = L + slot * (i + 0.5); y0 = B
        for j, nm in enumerate(names):
            v = series[nm][i]
            h = (B - T) * v / 100
            d.rectangle([x - bw / 2, y0 - h, x + bw / 2, y0], fill=PALETTE[j % len(PALETTE)])
            if v >= 6:
                _text(d, (x, y0 - h / 2), f'{v:.0f}', 22, 'white', bold=True, anchor='mm')
            y0 -= h
        _text(d, (x, B + 20), c, 26, INK, anchor='ma')
    d.line([(L, T), (L, B)], fill=INK, width=3); d.line([(L, B), (R, B)], fill=INK, width=3)
    for j, nm in enumerate(names):
        yy = T + 30 + j * 46
        d.rectangle([R + 40, yy - 12, R + 70, yy + 12], fill=PALETTE[j % len(PALETTE)])
        _text(d, (R + 82, yy), nm, 24, INK, anchor='lm')
    im.save(path, dpi=(200, 200))
    return path

def heatmap(path, rows, cols, matrix, title, figsize=(1800, 1000), vmax=None, note=None):
    im, d = _canvas(*figsize); W, H = im.size
    L, T = 420, 190
    cw = (W - L - 90) / len(cols); ch = (H - T - 120) / len(rows)
    vmax = vmax or max(max(r) for r in matrix) or 1
    _text(d, (60, 60), title, 38, INK, bold=True)
    if note: _text(d, (60, 108), note, 24, MUTED)
    for j, c in enumerate(cols):
        _text(d, (L + cw * (j + 0.5), T - 16), c, 24, INK, bold=True, anchor='mb')
    for i, r in enumerate(rows):
        _text(d, (L - 18, T + ch * (i + 0.5)), r, 26, INK, anchor='rm')
        for j in range(len(cols)):
            v = matrix[i][j]
            a = 0.10 + 0.85 * (v / vmax)
            col = (int(31 + (255 - 31) * (1 - a)), int(78 + (255 - 78) * (1 - a)), int(121 + (255 - 121) * (1 - a)))
            x0, y0 = L + cw * j, T + ch * i
            d.rectangle([x0 + 2, y0 + 2, x0 + cw - 2, y0 + ch - 2], fill=col)
            _text(d, (x0 + cw / 2, y0 + ch / 2), f'{v:.0f}', 26, 'white' if a > .55 else INK, bold=True, anchor='mm')
    im.save(path, dpi=(200, 200))
    return path

def stripplot(path, groups, title, ylabel, figsize=(1800, 1000), note=None):
    """groups: list of (label, [values])"""
    im, d = _canvas(*figsize); W, H = im.size
    L, R, T, B = 190, W - 90, 150, H - 210
    allv = [v for _, vs in groups for v in vs] or [0]
    ymax = max(allv) * 1.15
    _text(d, (L, 60), title, 38, INK, bold=True)
    if note: _text(d, (L, 108), note, 24, MUTED)
    for i in range(6):
        y = B - (B - T) * i / 5
        d.line([(L, y), (R, y)], fill=GRID, width=2)
        _text(d, (L - 16, y), f'{ymax*i/5:.0f}', 24, MUTED, anchor='rm')
    d.line([(L, T), (L, B)], fill=INK, width=3); d.line([(L, B), (R, B)], fill=INK, width=3)
    n = len(groups); slot = (R - L) / n
    random.seed(7)
    for i, (lab, vs) in enumerate(groups):
        cx = L + slot * (i + 0.5)
        if not vs: continue
        sv = sorted(vs)
        def q(p):
            k = (len(sv) - 1) * p; f = math.floor(k); c = math.ceil(k)
            return sv[f] + (sv[c] - sv[f]) * (k - f)
        q1, med, q3 = q(.25), q(.5), q(.75)
        lo, hi = min(vs), max(vs)
        bw = slot * 0.22
        d.line([(cx, B - (B - T) * lo / ymax), (cx, B - (B - T) * hi / ymax)], fill=MUTED, width=3)
        for v in (lo, hi):
            yy = B - (B - T) * v / ymax
            d.line([(cx - bw / 2, yy), (cx + bw / 2, yy)], fill=MUTED, width=3)
        d.rectangle([cx - bw / 2, B - (B - T) * q3 / ymax, cx + bw / 2, B - (B - T) * q1 / ymax], outline=INK, width=3, fill=(234, 240, 246))
        yy = B - (B - T) * med / ymax
        d.line([(cx - bw / 2, yy), (cx + bw / 2, yy)], fill=PALETTE[1], width=5)
        for v in vs:
            jx = cx + random.uniform(-bw * 1.5, bw * 1.5)
            yy = B - (B - T) * v / ymax
            r = 6
            d.ellipse([jx - r, yy - r, jx + r, yy + r], fill=(31, 78, 121))
        _text(d, (cx, B + 24), lab, 26, INK, anchor='ma')
        _text(d, (cx, B + 62), f'n={len(vs)}', 22, MUTED, anchor='ma')
    tmp = Image.new('RGBA', (600, 44), (255, 255, 255, 0)); td = ImageDraw.Draw(tmp)
    td.text((0, 0), ylabel, font=_font(26), fill=MUTED); tmp = tmp.rotate(90, expand=True)
    im.paste(tmp, (40, int((T + B) / 2 - tmp.size[1] / 2)), tmp)
    im.save(path, dpi=(200, 200))
    return path

def bar_ci(path, labels, values, lo, hi, ylabel, title, figsize=(1800, 1050), color=PALETTE[0],
           ymax=100, fmt='{:.0f}', note=None):
    im, d = _canvas(*figsize); W, H = im.size
    L, R, T, B = 190, W - 70, 160, H - 250
    _text(d, (L, 55), title, 37, INK, bold=True)
    if note: _text(d, (L, 105), note, 22, MUTED)
    for i in range(6):
        y = B - (B - T) * i / 5
        d.line([(L, y), (R, y)], fill=GRID, width=2)
        _text(d, (L - 16, y), fmt.format(ymax * i / 5), 24, MUTED, anchor='rm')
    d.line([(L, T), (L, B)], fill=INK, width=3); d.line([(L, B), (R, B)], fill=INK, width=3)
    n = len(values); slot = (R - L) / n; bw = slot * 0.5
    for i, lab in enumerate(labels):
        x = L + slot * (i + 0.5); v = values[i]
        y = B - (B - T) * v / ymax
        d.rectangle([x - bw / 2, y, x + bw / 2, B], fill=color)
        y1 = B - (B - T) * (v + hi[i]) / ymax; y2 = B - (B - T) * max(v - lo[i], 0) / ymax
        d.line([(x, y1), (x, y2)], fill=INK, width=3)
        for yy in (y1, y2): d.line([(x - 12, yy), (x + 12, yy)], fill=INK, width=3)
        _text(d, (x, y1 - 10), fmt.format(v), 26, INK, bold=True, anchor='mb')
        for k, ln in enumerate(lab.split('\n')):
            _text(d, (x, B + 20 + k * 30), ln, 25, INK, anchor='ma')
    tmp = Image.new('RGBA', (700, 44), (255, 255, 255, 0)); td = ImageDraw.Draw(tmp)
    td.text((0, 0), ylabel, font=_font(25), fill=MUTED); tmp = tmp.rotate(90, expand=True)
    im.paste(tmp, (38, int((T + B) / 2 - tmp.size[1] / 2)), tmp)
    im.save(path, dpi=(200, 200))
    return path
