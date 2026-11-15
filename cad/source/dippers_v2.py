#!/usr/bin/env python3
"""Dipper arms, revision 3: twelve T-family tips that tolerate the water level, a snug riser, tips 12.7 mm lower.

Run from cad/source:  python dippers_v2.py
Writes ../stl/dippers_v2/*.stl, ../step/dippers_v2/*.step, ../stl/dippers_v2/all_12_plate.stl and a profile preview.

Changes from the rev 2 arms:
* Riser and arm are 3.3 mm square instead of 3.0, so they fit the existing 3.4 mm foot socket with 0.05 mm a side.
* Every tip reaches 12.7 mm (half an inch) lower than the rev 2 tips. The riser length is unchanged, so an arm
  pushed fully into the foot sits exactly where the old one did.
* All tips are flat profiles, so they print flat with no supports.
"""
import math
import os

import gmsh
import numpy as np

import rig
from rig import occ, box, prism, fuse, ZA, ZW, ZCAP, SPK

T = 3.3                                  # arm and riser thickness (x) and riser width (y)
EXTRA = 10.0                             # same trimmable riser allowance as the rev 2 print files
DROP = 12.7                              # tips reach this much lower than rev 2
ZT = ZW - 2.0 - DROP                     # rev 2 T-bar bottom, lowered: the reference level for every tip
Y0, Y1 = 36.0, 50.0                      # tip bar span; inner edge stays where the rev 2 T had it
YC = (Y0 + Y1) / 2
X0, X1 = SPK[0] - T / 2, SPK[0] + T / 2
STEM = 2.4                               # stem width


def ext(poly):
    """poly is (y, z) points; extruded through the arm thickness."""
    return prism(poly, 'x', X0, X1)


def bar(bottom, top_z=ZT + 3.0):
    """A T bar whose underside follows bottom: list of (y, z) from Y0 to Y1."""
    return ext([(Y1, top_z), (Y0, top_z)] + bottom)


def wave(n_pts, amp, periods, phase=0.0):
    return [(Y0 + (Y1 - Y0) * i / n_pts, ZT + amp * math.sin(2 * math.pi * periods * i / n_pts + phase)) for i in range(n_pts + 1)]


def teeth(n, h):
    w = (Y1 - Y0) / n
    pts = []
    for i in range(n):
        pts += [(Y0 + i * w, ZT + h), (Y0 + (i + 0.5) * w, ZT)]
    return pts + [(Y1, ZT + h)]


TIPS = {
    # name: (description, builder)
    't_flat':   ('The rev 2 T, wider and 12.7 mm lower. Baseline.', lambda: bar([(Y0, ZT), (Y1, ZT)])),
    't_slant':  ('Bar tilted 5 mm end to end. The wetted length grows smoothly with the water level.', lambda: bar([(Y0, ZT), (Y1, ZT + 5)], ZT + 8)),
    't_vee':    ('V underside, point in the middle. Starts as one dot and spreads as the level rises.', lambda: bar([(Y0, ZT + 4), (YC, ZT), (Y1, ZT + 4)], ZT + 7)),
    't_arch':   ('Ends lower than the middle. Two dots that merge into a line as the level rises.', lambda: bar([(Y0, ZT), (YC, ZT + 4), (Y1, ZT)], ZT + 7)),
    't_wave':   ('Wavy underside, 2 mm deep, two waves. Always several crests touching.', lambda: bar(wave(40, 2.0, 2), ZT + 5)),
    't_wave3':  ('Wavy underside, 3 mm deep, three waves. More level tolerance, finer ripples.', lambda: bar(wave(60, 3.0, 3), ZT + 6)),
    't_saw':    ('Five sharp teeth, 3 mm tall. Five point sources that interfere.', lambda: bar(teeth(5, 3.0), ZT + 6)),
    't_saw8':   ('Eight fine teeth, 2 mm tall. Busier, finer pattern.', lambda: bar(teeth(8, 2.0), ZT + 5)),
    't_steps':  ('Three 2 mm steps. Pick the step by the water level.', lambda: bar([(Y0, ZT), (Y0 + 4.67, ZT), (Y0 + 4.67, ZT + 2), (Y0 + 9.33, ZT + 2), (Y0 + 9.33, ZT + 4), (Y1, ZT + 4)], ZT + 7)),
    't_round':  ('Half-round underside, radius 7 mm. The smoothest response to level changes.',
                 lambda: bar([(YC + 7 * math.cos(math.pi + math.pi * i / 24), ZT + 7 + 7 * math.sin(math.pi + math.pi * i / 24)) for i in range(25)], ZT + 9)),
    't_double': ('Two stacked bars 4 mm apart. Works at two water levels.',
                 lambda: fuse(bar([(Y0, ZT), (Y1, ZT)], ZT + 2.0), ext([(Y1, ZT + 4), (Y1, ZT + 6), (Y0, ZT + 6), (Y0, ZT + 4)]),
                              ext([(YC - 1.2, ZT + 1), (YC + 1.2, ZT + 1), (YC + 1.2, ZT + 5), (YC - 1.2, ZT + 5)]))),
    't_comb':   ('Four tines, 1.5 mm wide, each 1.5 mm shorter than the last. One or more always touches.',
                 lambda: fuse(ext([(Y1, ZT + 9), (Y0, ZT + 9), (Y0, ZT + 6), (Y1, ZT + 6)]),
                              *[ext([(Y0 + 1 + i * 4, ZT + 6), (Y0 + 1 + i * 4, ZT + i * 1.5), (Y0 + 2.5 + i * 4, ZT + i * 1.5), (Y0 + 2.5 + i * 4, ZT + 6)]) for i in range(4)])),
}


def arm(name):
    """Riser into the foot, horizontal arm over the dish rim, stem down to the tip. Assembly coordinates."""
    ys = SPK[1]
    riser = box(X0, X1, ys - T / 2, ys + T / 2, ZCAP + 2.0 - EXTRA, ZA + 3)
    beam = box(X0, X1, YC - STEM / 2, ys + T / 2, ZA, ZA + 3)
    tip = TIPS[name][1]()
    occ.synchronize()
    top = max(gmsh.model.getBoundingBox(*e)[5] for e in tip)   # stem joins the top of the tip
    stem = box(X0, X1, YC - STEM / 2, YC + STEM / 2, top - 1.0, ZA + 0.1)
    return fuse(riser, beam, stem, tip)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    stl_dir = os.path.join(here, '..', 'stl', 'dippers_v2')
    step_dir = os.path.join(here, '..', 'step', 'dippers_v2')
    os.makedirs(stl_dir, exist_ok=True)
    os.makedirs(step_dir, exist_ok=True)
    gmsh.initialize()
    gmsh.option.setNumber('General.Terminal', 0)
    gmsh.option.setNumber('Mesh.MeshSizeFromCurvature', 24)
    gmsh.option.setNumber('Mesh.MeshSizeMax', 1.0)
    gmsh.option.setNumber('Mesh.Binary', 1)              # binary STL, about 5x smaller
    report = []
    for i, name in enumerate(TIPS):
        gmsh.model.add(name)
        dt = arm(name)
        occ.removeAllDuplicates()
        occ.synchronize()
        vols = gmsh.model.getEntities(3)
        assert len(vols) == 1, (name, vols)
        rig.xform(vols, rig.R_FLAT_X)                       # thickness becomes print height
        occ.synchronize()
        lo = gmsh.model.getBoundingBox(3, vols[0][1])
        occ.translate(vols, -(lo[0] + lo[3]) / 2, -(lo[1] + lo[4]) / 2, -lo[2])
        occ.synchronize()
        b = gmsh.model.getBoundingBox(3, vols[0][1])
        vol = occ.getMass(3, vols[0][1])
        gmsh.write(os.path.join(step_dir, f'dipper_arm_{name}.step'))
        gmsh.model.mesh.generate(2)
        gmsh.write(os.path.join(stl_dir, f'dipper_arm_{name}.stl'))
        report.append((name, b[3] - b[0], b[4] - b[1], b[5] - b[2], vol))
        gmsh.model.remove()

    # one plate with all twelve, 4 x 3 grid
    gmsh.model.add('plate')
    for i, name in enumerate(TIPS):
        gmsh.merge(os.path.join(step_dir, f'dipper_arm_{name}.step'))
        v = gmsh.model.getEntities(3)[-1:]
        occ.synchronize()
        occ.translate(v, (i % 4) * 50.0 - 75.0, (i // 4) * 50.0 - 50.0, 0)
    occ.synchronize()
    gmsh.model.mesh.generate(2)
    gmsh.write(os.path.join(stl_dir, 'all_12_plate.stl'))
    gmsh.finalize()

    for r in report:
        print(f'{r[0]:10s} {r[1]:5.1f} x {r[2]:5.1f} x {r[3]:4.1f} mm  {r[4] / 1000:.2f} cm3')


if __name__ == '__main__':
    main()
