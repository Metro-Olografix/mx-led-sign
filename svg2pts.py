#!/usr/bin/env python3
"""Converte il path del logo MX in una lista di punti (mm) per OpenSCAD."""
import re, sys, math

def parse(d):
    toks = re.findall(r'[A-Za-z]|-?\d*\.?\d+(?:e-?\d+)?', d)
    i = 0; cmd = None; cur = (0.0, 0.0); start = cur; pts = []
    def num():
        nonlocal i
        v = float(toks[i]); i += 1; return v
    while i < len(toks):
        if re.match(r'[A-Za-z]', toks[i]):
            cmd = toks[i]; i += 1
            if cmd in 'zZ':
                cur = start; continue
        rel = cmd.islower(); c = cmd.lower()
        if c == 'm':
            x, y = num(), num()
            cur = (cur[0]+x, cur[1]+y) if rel else (x, y)
            start = cur; pts.append(cur); cmd = 'l' if rel else 'L'
        elif c == 'l':
            x, y = num(), num()
            cur = (cur[0]+x, cur[1]+y) if rel else (x, y); pts.append(cur)
        elif c == 'h':
            x = num(); cur = (cur[0]+x if rel else x, cur[1]); pts.append(cur)
        elif c == 'v':
            y = num(); cur = (cur[0], cur[1]+y if rel else y); pts.append(cur)
        elif c == 'c':
            v = [num() for _ in range(6)]
            if rel:
                v = [v[k] + cur[k % 2] for k in range(6)]
            p0 = cur; p1 = (v[0], v[1]); p2 = (v[2], v[3]); p3 = (v[4], v[5])
            L = math.dist(p0, p1) + math.dist(p1, p2) + math.dist(p2, p3)
            n = max(2, int(L / 0.4))
            for k in range(1, n+1):
                t = k / n; u = 1 - t
                pts.append((u**3*p0[0] + 3*u*u*t*p1[0] + 3*u*t*t*p2[0] + t**3*p3[0],
                            u**3*p0[1] + 3*u*u*t*p1[1] + 3*u*t*t*p2[1] + t**3*p3[1]))
            cur = p3
        else:
            raise ValueError(cmd)
    return pts

svg = open(sys.argv[1]).read()
d = re.search(r'<path[^>]*?\sd="([^"]+)"', svg, re.S).group(1)
pts = parse(d)
# rimuovi duplicati consecutivi e il punto di chiusura
clean = []
for p in pts:
    if not clean or math.dist(p, clean[-1]) > 0.05:
        clean.append(p)
if math.dist(clean[0], clean[-1]) < 0.05:
    clean.pop()
xs = [p[0] for p in clean]; ys = [p[1] for p in clean]
x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
# origine in basso a sinistra, asse Y verso l'alto
out = [(round(x - x0, 3), round(y1 - y, 3)) for x, y in clean]
per = sum(math.dist(out[k], out[(k+1) % len(out)]) for k in range(len(out)))
area = sum(out[k][0]*out[(k+1)%len(out)][1] - out[(k+1)%len(out)][0]*out[k][1] for k in range(len(out)))/2
with open(sys.argv[2], 'w') as f:
    f.write('// Generato da svg2pts.py a partire da MX_black.svg (unita: mm, scala 1:1 col file)\n')
    f.write(f'LOGO_W = {x1-x0:.3f};\nLOGO_H = {y1-y0:.3f};\nLOGO_PERIMETER = {per:.2f};\n')
    f.write('LOGO_PTS = [' + ','.join(f'[{x},{y}]' for x, y in out) + '];\n')
print(f'punti={len(out)} bbox={x1-x0:.2f} x {y1-y0:.2f} perimetro={per:.1f} area={area:.0f}')
