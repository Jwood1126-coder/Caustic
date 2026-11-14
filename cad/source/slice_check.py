#!/usr/bin/env python3
"""Independent checks on the STL files: PrusaSlicer and ADMesh re-read each mesh, then PrusaSlicer slices it
with automatic supports switched on. Writes out/slice_report.json. Needs prusa-slicer and admesh on the PATH."""
import concurrent.futures
import glob
import json
import os
import re
import subprocess

OPTS = ('--layer-height 0.2 --first-layer-height 0.2 --nozzle-diameter 0.4 --filament-diameter 1.75 --filament-density 1.27 --temperature 240 '
        '--first-layer-temperature 240 --bed-temperature 70 --first-layer-bed-temperature 70 --perimeters 3 --top-solid-layers 5 --bottom-solid-layers 4 '
        '--fill-density 15% --fill-pattern gyroid --bed-shape 0x0,256x0,256x256,0x256 --center 128,128 --use-relative-e-distances --gcode-comments '
        '--support-material --support-material-auto --dont-support-bridges').split()
os.makedirs('slice', exist_ok=True)


def one(stl):
    n = os.path.basename(stl)[:-4]
    gcode = f'slice/{n}.gcode'
    subprocess.run(['prusa-slicer', '--export-gcode', *OPTS, '--output', gcode, stl], capture_output=True, check=True)
    info = subprocess.run(['prusa-slicer', '--info', stl], capture_output=True).stdout.decode(errors='ignore')
    adm = subprocess.run(['admesh', stl], capture_output=True).stdout.decode(errors='ignore')
    t = open(gcode, errors='ignore').read()
    get = lambda k: (re.search(k + r'\s*=\s*(.+)', t) or [None, '?'])[1].strip()
    support, cur = 0.0, None
    for line in t.splitlines():
        if line.startswith(';TYPE:'):
            cur = line[6:]
        elif cur and cur.startswith('Support') and line.startswith('G1'):
            m = re.search(r' E(-?[\d.]+)', line)
            if m and float(m[1]) > 0:
                support += float(m[1])
    return n, dict(grams=float(get(r'; total filament used \[g\]')), time=get(r'; estimated printing time \(normal mode\)'), support_mm=round(support, 1),
                   manifold=re.search(r'manifold = (\w+)', info)[1], parts=int(re.search(r'number_of_parts =\s*(\d+)', info)[1]),
                   disconnected=int(re.search(r'Total disconnected facets\s*:\s*(\d+)', adm)[1]), normals_fixed=int(re.search(r'Normals fixed\s*:\s*(\d+)', adm)[1]),
                   reversed=int(re.search(r'Facets reversed\s*:\s*(\d+)', adm)[1]))


with concurrent.futures.ThreadPoolExecutor(4) as ex:
    rows = dict(ex.map(one, sorted(glob.glob('out/stl/*.stl'))))
json.dump(rows, open('out/slice_report.json', 'w'), indent=1)
bad = {n: r for n, r in rows.items() if r['support_mm'] > 0 or r['manifold'] != 'yes' or r['parts'] != 1 or r['disconnected'] or r['normals_fixed'] or r['reversed']}
print(len(rows), 'parts sliced. Problems:', bad or 'none.', 'Total', round(sum(r['grams'] for r in rows.values())), 'g')
raise SystemExit(1 if bad else 0)
