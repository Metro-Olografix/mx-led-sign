#!/usr/bin/env python3
"""Unisce gli STL delle due lastre frontali del logo MX in un unico OBJ colorato.

Dispone su un piatto da 256 x 256: lastra destra e lastra sinistra (nero + parete
bianca del diffusore, stesse coordinate). I tappini si stampano a parte (export/stl/mx_cap.stl). Ogni parte e' un oggetto
separato con il suo materiale (file .mtl) e anche il colore sui vertici, cosi'
Orca puo' proporre l'abbinamento ai filamenti anche senza il .mtl.
Scrive anche un OBJ per ciascuna lastra (mx_lastra_destra.obj, mx_lastra_sinistra.obj).
Legge export/stl/, scrive in export/obj/. Uso: make obj
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STL = os.path.join(ROOT, 'export', 'stl')
OUT_DIR = os.path.join(ROOT, 'export', 'obj')
OUT = os.path.join(OUT_DIR, 'mx_lastre_diffusore.obj')
GAP = 4.0
COLORS = {'nero': (0.08, 0.08, 0.08), 'bianco': (0.95, 0.95, 0.95)}

def read_stl(path):
    tris, cur = [], []
    with open(path) as f:
        for line in f:
            t = line.split()
            if t and t[0] == 'vertex':
                cur.append(tuple(float(v) for v in t[1:4]))
                if len(cur) == 3:
                    tris.append(cur); cur = []
    return tris

def bbox(tris_list):
    pts = [p for tris in tris_list for tri in tris for p in tri]
    return [min(p[i] for p in pts) for i in range(3)], [max(p[i] for p in pts) for i in range(3)]

# gruppi da disporre: (nome, [(file, colore), ...]) - i file di un gruppo restano allineati tra loro
groups = [
    ('lastra_destra',   [('mx_plate_right.stl', 'nero'), ('mx_plate_right_white.stl', 'bianco')]),
    ('lastra_sinistra', [('mx_plate_left.stl', 'nero'),  ('mx_plate_left_white.stl', 'bianco')]),
]
data = {g: [(f, c, read_stl(os.path.join(STL, f))) for f, c in parts] for g, parts in groups}

# posizioni (angolo in basso a sinistra di ogni gruppo sul piatto)
def size(g):
    lo, hi = bbox([t for _, _, t in data[g]]); return hi[0] - lo[0], hi[1] - lo[1]
wR, hR = size('lastra_destra'); wL, hL = size('lastra_sinistra')
place = {
    'lastra_destra':   (GAP, GAP),
    'lastra_sinistra': (GAP, GAP + hR + GAP),
}

mtl = os.path.splitext(OUT)[0] + '.mtl'
with open(mtl, 'w') as m:
    for name, (r, g, b) in COLORS.items():
        m.write(f'newmtl {name}\nKd {r} {g} {b}\nKa 0 0 0\nd 1\n\n')

def write_obj(out, names, placement):
    lines = [f'# Logo MX (unita: mm)', f'mtllib {os.path.basename(mtl)}']
    vbase = 1
    maxx = maxy = 0
    for g in names:
        lo, hi = bbox([t for _, _, t in data[g]])
        ox, oy = placement[g][0] - lo[0], placement[g][1] - lo[1]
        for f, col, tris in data[g]:
            rgb = COLORS[col]
            idx, verts, faces = {}, [], []
            for tri in tris:
                face = []
                for p in tri:
                    q = (round(p[0] + ox, 4), round(p[1] + oy, 4), round(p[2] - lo[2], 4))
                    if q not in idx:
                        idx[q] = len(verts); verts.append(q)
                    face.append(idx[q] + vbase)
                faces.append(face)
            lines.append(f'o {g}_{col}')
            lines.append(f'usemtl {col}')
            lines += [f'v {x} {y} {z} {rgb[0]} {rgb[1]} {rgb[2]}' for x, y, z in verts]
            lines += [f'f {a} {b} {c}' for a, b, c in faces]
            vbase += len(verts)
            maxx = max(maxx, max(v[0] for v in verts)); maxy = max(maxy, max(v[1] for v in verts))
    open(out, 'w').write('\n'.join(lines) + '\n')
    print(f'{os.path.relpath(out, ROOT)}: ingombro sul piatto {maxx:.0f} x {maxy:.0f} mm (piatto 256 x 256)')

# tutte e due le lastre su un piatto, e un file per ciascuna lastra (stesso .mtl)
write_obj(OUT, [g for g, _ in groups], place)
for g, _ in groups:
    write_obj(os.path.join(OUT_DIR, f'mx_{g}.obj'), [g], {g: (GAP, GAP)})
