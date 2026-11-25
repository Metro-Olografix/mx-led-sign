#!/usr/bin/env python3
"""Dima 1:1 (A3 orizzontale) per controllare a muro le viti del logo MX.

Disegna il contorno del logo largo 260 mm, le due viti esistenti (interasse
238 mm), la posizione della tacca per il cavo e una barra di 100 mm per
verificare che la stampa sia in scala. Genera export/dima/dima_viti.svg e .pdf.
Uso: make dima   (il PDF richiede Pillow)
"""
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'export', 'dima')

LOGO_W_MM = 260.0
SCREWS = [(10.75, 89.75), (248.75, 89.75)]
FEED_X = 100 * LOGO_W_MM / 300
PAGE_W, PAGE_H = 420.0, 297.0
OX, OY_TOP = (PAGE_W - LOGO_W_MM) / 2, 60.0     # angolo in alto a sinistra del logo

src = open(os.path.join(ROOT, 'cad', 'logo_pts.scad')).read()
W = float(re.search(r'LOGO_W = ([\d.]+)', src).group(1))
HL = float(re.search(r'LOGO_H = ([\d.]+)', src).group(1))
s = LOGO_W_MM / W
H = HL * s
pts = [(float(a)*s, float(b)*s) for a, b in re.findall(r'\[(-?[\d.]+),(-?[\d.]+)\]', src.split('LOGO_PTS')[1])]

def page(x, y):            # coordinate logo (mm, y in su) -> pagina (mm, y in giu')
    return OX + x, OY_TOP + (H - y)

TEXT = [
    "DIMA 1:1 - logo MX 260 mm - stampare su A3 al 100% (senza 'adatta alla pagina')",
    "Controlla che la barra qui sotto misuri esattamente 100 mm.",
    "Appoggia la dima al muro: i due mirini devono cadere sulle viti esistenti",
    "e la linea tratteggiata deve essere in bolla.",
]

def svg():
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{PAGE_W}mm" height="{PAGE_H}mm" '
         f'viewBox="0 0 {PAGE_W} {PAGE_H}">',
         '<rect width="100%" height="100%" fill="white"/>']
    d = 'M ' + ' L '.join(f'{page(x, y)[0]:.3f},{page(x, y)[1]:.3f}' for x, y in pts) + ' Z'
    o.append(f'<path d="{d}" fill="#e8e8e8" stroke="black" stroke-width="0.4"/>')
    (x1, y1), (x2, y2) = [page(*p) for p in SCREWS]
    o.append(f'<line x1="{x1-30}" y1="{y1}" x2="{x2+30}" y2="{y2}" stroke="red" stroke-width="0.3" stroke-dasharray="3,2"/>')
    for (px, py) in [(x1, y1), (x2, y2)]:
        o.append(f'<circle cx="{px}" cy="{py}" r="3.5" fill="none" stroke="red" stroke-width="0.3"/>')
        o.append(f'<circle cx="{px}" cy="{py}" r="1.5" fill="none" stroke="red" stroke-width="0.3"/>')
        o.append(f'<line x1="{px-8}" y1="{py}" x2="{px+8}" y2="{py}" stroke="red" stroke-width="0.2"/>')
        o.append(f'<line x1="{px}" y1="{py-8}" x2="{px}" y2="{py+8}" stroke="red" stroke-width="0.2"/>')
    o.append(f'<text x="{(x1+x2)/2}" y="{y1-3}" font-size="5" text-anchor="middle" fill="red" '
             f'font-family="sans-serif">interasse viti 238 mm</text>')
    fx, fy = page(FEED_X, H)
    o.append(f'<line x1="{fx}" y1="{fy-18}" x2="{fx}" y2="{fy-1}" stroke="blue" stroke-width="0.4"/>')
    o.append(f'<path d="M {fx-2},{fy-4} L {fx},{fy-1} L {fx+2},{fy-4}" fill="none" stroke="blue" stroke-width="0.4"/>')
    o.append(f'<text x="{fx+3}" y="{fy-12}" font-size="4.5" fill="blue" font-family="sans-serif">ingresso cavo LED</text>')
    bx, by = 20, PAGE_H - 25
    o.append(f'<rect x="{bx}" y="{by}" width="100" height="4" fill="black"/>')
    o.append(f'<text x="{bx}" y="{by+10}" font-size="4.5" font-family="sans-serif">100 mm</text>')
    for i, t in enumerate(TEXT):
        o.append(f'<text x="20" y="{14 + i*6.5}" font-size="4.5" font-family="sans-serif">{t}</text>')
    o.append('</svg>')
    open(os.path.join(OUT_DIR, 'dima_viti.svg'), 'w').write('\n'.join(o))

def pdf():
    from PIL import Image, ImageDraw, ImageFont
    dpi = 300; k = dpi / 25.4
    im = Image.new('RGB', (round(PAGE_W*k), round(PAGE_H*k)), 'white'); d = ImageDraw.Draw(im)
    P = lambda x, y: (x*k, y*k)
    poly = [P(*page(x, y)) for x, y in pts]
    d.polygon(poly, fill=(232, 232, 232), outline='black', width=5)
    (x1, y1), (x2, y2) = [page(*p) for p in SCREWS]
    x = x1 - 30
    while x < x2 + 30:                       # linea tratteggiata
        d.line([P(x, y1), P(min(x+3, x2+30), y1)], fill='red', width=4); x += 5
    for (px, py) in [(x1, y1), (x2, y2)]:
        for r in (3.5, 1.5):
            d.ellipse([P(px-r, py-r), P(px+r, py+r)], outline='red', width=4)
        d.line([P(px-8, py), P(px+8, py)], fill='red', width=2)
        d.line([P(px, py-8), P(px, py+8)], fill='red', width=2)
    try:
        f = ImageFont.truetype('/usr/share/fonts/google-noto/NotoSans-Regular.ttf', round(4.5*k*0.8))
    except OSError:
        f = ImageFont.load_default()
    d.text(P((x1+x2)/2 - 25, y1-9), 'interasse viti 238 mm', fill='red', font=f)
    fx, fy = page(FEED_X, H)
    d.line([P(fx, fy-18), P(fx, fy-1)], fill='blue', width=5)
    d.line([P(fx-2, fy-4), P(fx, fy-1), P(fx+2, fy-4)], fill='blue', width=5)
    d.text(P(fx+3, fy-16), 'ingresso cavo LED', fill='blue', font=f)
    bx, by = 20, PAGE_H - 25
    d.rectangle([P(bx, by), P(bx+100, by+4)], fill='black')
    d.text(P(bx, by+6), '100 mm', fill='black', font=f)
    for i, t in enumerate(TEXT):
        d.text(P(20, 10 + i*6.5), t, fill='black', font=f)
    im.save(os.path.join(OUT_DIR, 'dima_viti.pdf'), resolution=dpi)

svg()
try:
    pdf()
except ImportError:
    print('Pillow non disponibile: generato solo lo SVG')
print('ok: dima_viti.svg / dima_viti.pdf')
