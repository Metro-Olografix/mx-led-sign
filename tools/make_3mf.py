#!/usr/bin/env python3
"""Progetto OrcaSlicer pronto da stampare con le due lastre frontali del logo MX.

Le due lastre stanno sullo stesso piatto (come in mx_lastre_diffusore.obj), cosi'
i cambi colore, che cadono alla stessa quota, si pagano una volta sola. Ogni lastra
e' un oggetto con due parti: la piastra nera e la parte bianca (diffusore + labbro).

Le impostazioni vengono da slicer/orca_project_settings.json (profilo
"MX logo lastre @Elegoo CC2 0.4", filamenti PLA, CC2 0.4). In piu' c'e' un
modificatore di altezza da Z_FAST alla cima che porta la parete esterna a
FAST_OUTER_WALL mm/s: sopra quella quota resta solo la parete bianca del
diffusore, che e' larga due linee (Orca le stampa entrambe come parete esterna)
ed e' nascosta nella gola. Sotto Z_FAST non cambia niente: fronte e bordo neri,
incastro della parete nella piastra (skirt_key, da 3 a 4 mm) e labbro bianco
(da 4 a 4,8 mm) restano a 0,2 mm e alla velocita' del profilo. Stima di Orca per
entrambe le lastre: 2 h 11 min senza modificatore, 1 h 49 min con.

Legge export/stl/, scrive export/3mf/mx_lastre.3mf. Uso: make 3mf
"""
import json, os, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STL = os.path.join(ROOT, 'export', 'stl')
SETTINGS = os.path.join(ROOT, 'slicer', 'orca_project_settings.json')
OUT = os.path.join(ROOT, 'export', '3mf', 'mx_lastre.3mf')

BLACK, WHITE = 4, 3        # slot dei filamenti come nel progetto salvato: 4 = nero, 3 = bianco
GAP = 4.0                  # distanza dal bordo del piatto e tra le lastre
Z_FAST = 5.0               # sopra questa quota c'e' solo la parete del diffusore
FAST_OUTER_WALL = 200      # mm/s, come le pareti interne del profilo

GROUPS = [('lastra_destra', 'mx_plate_right.stl', 'mx_plate_right_white.stl'),
          ('lastra_sinistra', 'mx_plate_left.stl', 'mx_plate_left_white.stl')]


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


def bbox(meshes):
    pts = [p for m in meshes for t in m for p in t]
    return [min(p[i] for p in pts) for i in range(3)], [max(p[i] for p in pts) for i in range(3)]


def mesh_xml(oid, tris, off):
    idx, verts, faces = {}, [], []
    for t in tris:
        face = []
        for p in t:
            q = tuple(round(p[i] + off[i], 4) for i in range(3))
            if q not in idx:
                idx[q] = len(verts); verts.append(q)
            face.append(idx[q])
        faces.append(face)
    s = [f'  <object id="{oid}" type="model">', '   <mesh>', '    <vertices>']
    s += [f'     <vertex x="{x}" y="{y}" z="{z}"/>' for x, y, z in verts]
    s += ['    </vertices>', '    <triangles>']
    s += [f'     <triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in faces]
    s += ['    </triangles>', '   </mesh>', '  </object>']
    return '\n'.join(s)


NS = ('xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" '
      'xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" '
      'xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" requiredextensions="p"')
HEAD = '<?xml version="1.0" encoding="UTF-8"?>\n'
REL = 'http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel'

data = {g: [read_stl(os.path.join(STL, b)), read_stl(os.path.join(STL, w))] for g, b, w in GROUPS}
lo_r, hi_r = bbox(data['lastra_destra'])
place = {'lastra_destra': (GAP, GAP), 'lastra_sinistra': (GAP, GAP + hi_r[1] - lo_r[1] + GAP)}

cfg = json.load(open(SETTINGS))
files, objects, items, rels, obj_cfg, instances, ranges = {}, [], [], [], [], [], []
nid = 1
for index, (name, _, _) in enumerate(GROUPS, start=1):
    lo, hi = bbox(data[name])
    off = (place[name][0] - lo[0], place[name][1] - lo[1], -lo[2])
    height = hi[2] - lo[2]
    black_id, white_id, top_id = nid, nid + 1, nid + 2
    nid += 3
    path = f'3D/Objects/{name}.model'
    files[path] = (HEAD + f'<model unit="millimeter" xml:lang="en-US" {NS}>\n'
                   ' <metadata name="BambuStudio:3mfVersion">1</metadata>\n <resources>\n'
                   + mesh_xml(black_id, data[name][0], off) + '\n'
                   + mesh_xml(white_id, data[name][1], off) + '\n </resources>\n <build/>\n</model>\n')
    rels.append(f' <Relationship Target="/{path}" Id="rel-{top_id}" Type="{REL}"/>')
    objects.append(f'  <object id="{top_id}" type="model">\n   <components>\n'
                   f'    <component p:path="/{path}" objectid="{black_id}" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>\n'
                   f'    <component p:path="/{path}" objectid="{white_id}" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>\n'
                   '   </components>\n  </object>')
    items.append(f'  <item objectid="{top_id}" transform="1 0 0 0 1 0 0 0 1 0 0 0" printable="1"/>')
    parts = ''.join(
        f'    <part id="{pid}" subtype="normal_part">\n'
        f'      <metadata key="name" value="{name}_{label}"/>\n'
        '      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>\n'
        f'      <metadata key="extruder" value="{ext}"/>\n    </part>\n'
        for pid, label, ext in ((black_id, 'nero', BLACK), (white_id, 'bianco', WHITE)))
    obj_cfg.append(f'  <object id="{top_id}">\n    <metadata key="name" value="{name}"/>\n'
                   f'    <metadata key="extruder" value="{BLACK}"/>\n{parts}  </object>')
    instances.append(f'    <model_instance>\n      <metadata key="object_id" value="{top_id}"/>\n'
                     '      <metadata key="instance_id" value="0"/>\n    </model_instance>')
    # Orca identifica gli oggetti dei range con la posizione nella lista (da 1), non con l'id del file;
    # ogni range deve avere anche extruder (0 = quello dell'oggetto) e layer_height
    ranges.append(f' <object id="{index}">\n  <range min_z="{Z_FAST}" max_z="{height:.3f}">\n'
                  '   <option opt_key="extruder">0</option>\n'
                  f'   <option opt_key="layer_height">{cfg["layer_height"]}</option>\n'
                  f'   <option opt_key="outer_wall_speed">{FAST_OUTER_WALL}</option>\n'
                  '  </range>\n </object>\n')

files['3D/3dmodel.model'] = (HEAD + f'<model unit="millimeter" xml:lang="en-US" {NS}>\n'
                             ' <metadata name="Application">BambuStudio-02.06.00.51</metadata>\n'
                             ' <metadata name="OrcaSlicer">2.4.2</metadata>\n'     # senza, Orca rifiuta il file
                             ' <metadata name="BambuStudio:3mfVersion">1</metadata>\n'
                             ' <metadata name="Title">Logo MX - lastre frontali</metadata>\n'
                             ' <resources>\n' + '\n'.join(objects) + '\n </resources>\n'
                             ' <build>\n' + '\n'.join(items) + '\n </build>\n</model>\n')
files['3D/_rels/3dmodel.model.rels'] = (HEAD + '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
                                        + '\n'.join(rels) + '\n</Relationships>\n')
files['_rels/.rels'] = (HEAD + '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
                        f' <Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="{REL}"/>\n</Relationships>\n')
files['[Content_Types].xml'] = (HEAD + '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">\n'
                                ' <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>\n'
                                ' <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>\n'
                                '</Types>\n')
files['Metadata/model_settings.config'] = (HEAD + '<config>\n' + '\n'.join(obj_cfg) + '\n  <plate>\n'
                                           '    <metadata key="plater_id" value="1"/>\n'
                                           + '\n'.join(instances) + '\n  </plate>\n</config>\n')
files['Metadata/project_settings.config'] = json.dumps(cfg, indent=4)
files['Metadata/layer_config_ranges.xml'] = '<?xml version="1.0" encoding="utf-8"?>\n<objects>\n' + ''.join(ranges) + '</objects>\n'

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as z:
    for k, v in files.items():
        # data fissa: rigenerando con gli stessi STL si ottiene lo stesso file
        z.writestr(zipfile.ZipInfo(k, date_time=(2026, 1, 1, 0, 0, 0)), v, zipfile.ZIP_DEFLATED)
print(f'{os.path.relpath(OUT, ROOT)}: 2 lastre, parete esterna a {FAST_OUTER_WALL} mm/s sopra {Z_FAST} mm')
