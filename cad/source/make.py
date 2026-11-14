#!/usr/bin/env python3
"""Build every part, check the assembly, and export STEP + STL files."""
import itertools
import json
import math
import os
import struct
import sys

import gmsh
import numpy as np

import rig
from rig import occ

import shutil

OUT = 'out'
shutil.rmtree(OUT, ignore_errors=True)
for d in ('stl', 'step', 'assembly'):
    os.makedirs(f'{OUT}/{d}', exist_ok=True)

gmsh.initialize()
gmsh.option.setNumber('General.Terminal', 0)
gmsh.option.setNumber('General.Verbosity', 1)
report = dict(parts={}, checks=[])


def check(label, ok, detail=''):
    report['checks'].append([label, bool(ok), detail])
    print('PASS' if ok else 'FAIL', label, '|', detail)


def cleanup():
    """Drop construction points, lines and faces that are not part of a solid."""
    occ.synchronize()
    vols = gmsh.model.getEntities(3)
    surf = gmsh.model.getBoundary(vols, combined=False, oriented=False, recursive=False)
    curv = gmsh.model.getBoundary(surf, combined=False, oriented=False, recursive=False) if surf else []
    pts = gmsh.model.getBoundary(curv, combined=False, oriented=False, recursive=False) if curv else []
    keep = set(vols) | set(surf) | set(curv) | set(pts)
    extra = [e for d in (2, 1, 0) for e in gmsh.model.getEntities(d) if e not in keep]
    if extra:
        occ.remove(extra)
        occ.synchronize()


def set_mesh(per_turn, size_max):
    gmsh.option.setNumber('Mesh.MeshSizeFromCurvature', per_turn)
    gmsh.option.setNumber('Mesh.MeshSizeMax', size_max)
    gmsh.option.setNumber('Mesh.MeshSizeMin', 0.15)
    gmsh.option.setNumber('Mesh.Algorithm', 6)


def volume_mesh(tag, lut, coords):
    tris = []
    for _, s in gmsh.model.getBoundary([(3, tag)], combined=False, oriented=False, recursive=False):
        types, _, nodes = gmsh.model.mesh.getElements(2, s)
        for t, n in zip(types, nodes):
            assert t == 2, t
            tris.append(np.asarray(n, dtype=np.int64).reshape(-1, 3))
    f = lut[np.vstack(tris)]
    used = np.unique(f)
    remap = np.full(len(coords), -1, dtype=np.int64)
    remap[used] = np.arange(len(used))
    return coords[used].copy(), remap[f]


def all_nodes():
    tags, xyz, _ = gmsh.model.mesh.getNodes()
    tags = np.asarray(tags, dtype=np.int64)
    lut = np.full(tags.max() + 1, -1, dtype=np.int64)
    lut[tags] = np.arange(len(tags))
    return lut, np.asarray(xyz).reshape(-1, 3)


def orient(v, f):
    """Make the triangle winding consistent and outward. Returns faces and a dict of mesh facts."""
    f = f.copy()
    edges = {}
    for i, (a, b, c) in enumerate(f):
        for p, q in ((a, b), (b, c), (c, a)):
            edges.setdefault((min(p, q), max(p, q)), []).append(i)
    bad = sum(1 for e in edges.values() if len(e) != 2)
    nbr = [[] for _ in range(len(f))]
    for e in edges.values():
        if len(e) == 2:
            nbr[e[0]].append(e[1])
            nbr[e[1]].append(e[0])
    seen = np.zeros(len(f), dtype=bool)
    shells = 0
    for seed in range(len(f)):
        if seen[seed]:
            continue
        shells += 1
        seen[seed] = True
        stack = [seed]
        while stack:
            i = stack.pop()
            di = {(f[i][k], f[i][(k + 1) % 3]) for k in range(3)}
            for j in nbr[i]:
                if seen[j]:
                    continue
                dj = {(f[j][k], f[j][(k + 1) % 3]) for k in range(3)}
                if di & dj:                      # same direction on the shared edge: flip j
                    f[j] = f[j][::-1]
                seen[j] = True
                stack.append(j)
    p0, p1, p2 = v[f[:, 0]], v[f[:, 1]], v[f[:, 2]]
    vol = float(np.einsum('ij,ij->i', p0, np.cross(p1, p2)).sum() / 6)
    if vol < 0:
        f = f[:, ::-1].copy()
        vol = -vol
    return f, dict(triangles=int(len(f)), open_or_nonmanifold_edges=int(bad), shells=shells, mesh_volume=vol)


def write_stl(path, v, f):
    p0, p1, p2 = v[f[:, 0]], v[f[:, 1]], v[f[:, 2]]
    n = np.cross(p1 - p0, p2 - p0)
    ln = np.linalg.norm(n, axis=1)
    n = n / np.where(ln > 0, ln, 1)[:, None]
    rec = np.zeros(len(f), dtype=[('n', '<f4', 3), ('a', '<f4', 3), ('b', '<f4', 3), ('c', '<f4', 3), ('attr', '<u2')])
    rec['n'], rec['a'], rec['b'], rec['c'] = n, p0, p1, p2
    with open(path, 'wb') as fh:
        fh.write(os.path.basename(path).encode()[:79].ljust(80, b' '))
        fh.write(struct.pack('<I', len(f)))
        fh.write(rec.tobytes())


def overhang(v, f):
    """Downward faces steeper than 45 degrees that are not on the bed, grouped into connected patches."""
    p0, p1, p2 = v[f[:, 0]], v[f[:, 1]], v[f[:, 2]]
    n = np.cross(p1 - p0, p2 - p0)
    area = np.linalg.norm(n, axis=1) / 2
    nz = n[:, 2] / np.maximum(2 * area, 1e-12)
    zmin = np.minimum(np.minimum(p0[:, 2], p1[:, 2]), p2[:, 2])
    sel = np.nonzero((nz < -0.7072) & (zmin > 0.05) & (area > 1e-9))[0]
    if not len(sel):
        return []
    idx = {int(i): k for k, i in enumerate(sel)}
    parent = list(range(len(sel)))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    edges = {}
    for i in sel:
        a, b, c = f[i]
        for p, q in ((a, b), (b, c), (c, a)):
            edges.setdefault((min(p, q), max(p, q)), []).append(idx[int(i)])
    for e in edges.values():
        for k in e[1:]:
            parent[find(k)] = find(e[0])
    groups = {}
    for k, i in enumerate(sel):
        groups.setdefault(find(k), []).append(i)
    out = []
    for g in groups.values():
        g = np.array(g)
        pts = np.vstack([p0[g], p1[g], p2[g]])
        ext = pts.max(0) - pts.min(0)
        out.append(dict(area=float(area[g].sum()), size=[round(float(e), 1) for e in ext], z=round(float(pts[:, 2].min()), 1), flat=bool((nz[g] < -0.999).all())))
    return sorted(out, key=lambda d: -d['area'])


# ---------------------------------------------------------------- 1. assembly: build, interference, STEP
gmsh.model.add('assembly')
tags = {}
for name in list(rig.PRINTED) + list(rig.COPIES) + list(rig.BOUGHT):
    if name in rig.ASM_ONLY:
        continue
    dt = rig.build(name)
    assert len(dt) == 1 and dt[0][0] == 3, (name, dt)
    tags[name] = dt[0][1]
occ.synchronize()
vol = {n: occ.getMass(3, t) for n, t in tags.items()}
bbx = {n: occ.getBoundingBox(3, t) for n, t in tags.items()}


def overlap(a, b):
    out = occ.intersect(occ.copy([(3, a)]), occ.copy([(3, b)]))[0]
    v = sum(occ.getMass(3, t) for d, t in out if d == 3)
    if out:
        occ.remove(out, recursive=True)
    return v


def boxes_touch(a, b, pad=0.01):
    return all(a[i] - pad < b[i + 3] and b[i] - pad < a[i + 3] for i in range(3))


worst = []
for a, b in itertools.combinations(tags, 2):
    if boxes_touch(bbx[a], bbx[b]):
        v = overlap(tags[a], tags[b])
        if v > 0.05:
            worst.append((round(v, 2), a, b))
check('no two parts occupy the same space (mirror at the middle tilt)', not worst, f'{len(worst)} overlaps {sorted(worst, reverse=True)[:6]}')

# the mirror at its other positions against everything near it
near = [n for n in ('stage', 'petri_dish', 'upright_left', 'upright_right', 'dipper_arm_wedge', 'speaker') if n in tags]
for label, phi in [('low', rig.phi_of(rig.TILTS['low'])), ('high', rig.phi_of(rig.TILTS['high'])), ('flipped up', 90.0), ('tipped forward', 50.0)]:
    extra = {}
    for nm, fn in (('hinge_bar', rig.hinge_bar), ('mirror_tile', rig.glass)):
        extra[nm] = rig.xform(fn(), rig.r_mirror(phi), rig.MIR_T)[0][1]
    hits = [(round(overlap(t, tags[o]), 2), nm, o) for nm, t in extra.items() for o in near]
    hits = [h for h in hits if h[0] > 0.05]
    check(f'mirror {label} ({phi:.1f} deg) clears the stage, dish, uprights and dipper', not hits, str(hits[:4]))
    occ.remove([(3, t) for t in extra.values()], recursive=True)

# ---------------------------------------------------------------- 1b. does every part actually mount?
def shifted(a, b, d):
    """Overlap of part a, moved by d, with part b."""
    ca = occ.copy([(3, tags[a])])
    occ.translate(ca, *d)
    out = occ.intersect(ca, occ.copy([(3, tags[b])]))[0]
    v = sum(occ.getMass(3, t) for dd, t in out if dd == 3)
    if out:
        occ.remove(out, recursive=True)
    return v


def free(label, a, others, shifts):
    """Part a can move by each shift without touching the others: proves a clearance."""
    hits = [(b, tuple(round(x, 2) for x in d), round(shifted(a, b, d), 2)) for b in others for d in shifts]
    hits = [h for h in hits if h[2] > 0.02]
    check(label, not hits, str(hits[:3]) if hits else f'{len(shifts)} moves tried')


def held(label, a, moves):
    """Each move of part a runs into the named part: proves something locates it."""
    res = [(b, tuple(round(x, 2) for x in d), round(shifted(a, b, d), 2)) for b, d in moves]
    loose = [r for r in res if r[2] <= 0.02]
    check(label, not loose, 'not stopped: ' + str(loose[:3]) if loose else f'{len(moves)} directions blocked')


def screws(label, pins, bite=()):
    """Each pin is a screw shank that must pass through its parts untouched. Each bite is a thread that must cut into its part."""
    bad, weak = [], []
    for p, d, r, names in pins:
        t = occ.addCylinder(*p, *d, r)
        bad += [(n, round(v, 3)) for n in names for v in [overlap(t, tags[n])] if v > 0.02]
        occ.remove([(3, t)])
    for p, d, r, n in bite:
        t = occ.addCylinder(*p, *d, r)
        v = overlap(t, tags[n])
        if v < 1.0:
            weak.append((n, round(v, 3)))
        occ.remove([(3, t)])
    check(label, not bad and not weak, f'blocked {bad[:3]} no thread {weak[:3]}' if bad or weak else f'{len(pins)} shanks clear' + (f', {len(bite)} threads bite' if bite else ''))


R5, R5MIN, R3, R3MIN = 2.5, 2.07, 1.5, 1.23           # screw outer radius and thread root radius
side = {-1: 'left', 1: 'right'}
zt = rig.ZR + rig.FL_T
screws('stage to uprights: four M5 screws pass through the ears into the outer slots',
       [((-rig.EXT / 2, s * (rig.EAR_Y + rig.FL_T + 0.5), z), (0, -s * 10.5, 0), R5, ['stage', f'upright_{side[s]}']) for s in (-1, 1) for z in (rig.ZS + 12, rig.ZS + 36)])
screws('base bracket to rails: four M5 screws reach the top slots',
       [((x, s * rig.RAIL_Y, zt + 0.5), (0, 0, -10.5), R5, ['base_bracket', f'rail_{side[s]}']) for s in (-1, 1) for x in (-45, -130)])
screws('base bracket to uprights: four M5 screws reach the rear slots',
       [((-rig.EXT - rig.FL_T - 0.5, s * rig.RAIL_Y, z), (10.5, 0, 0), R5, ['base_bracket', f'upright_{side[s]}']) for s in (-1, 1) for z in (50, 95)])
screws('LED sled to rails: four M5 screws reach the top slots',
       [((x, s * rig.RAIL_Y, zt + 0.5), (0, 0, -10.5), R5, ['led_sled', f'rail_{side[s]}']) for s in (-1, 1) for x in (rig.XE - 22, rig.XE + 34)])
feet = [('outrigger_foot', 1, rig.FOOT_X[1]), ('outrigger_foot_2', 1, rig.FOOT_X[0]), ('outrigger_foot_3', -1, rig.FOOT_X[1]), ('outrigger_foot_4', -1, rig.FOOT_X[0])]
screws('outrigger feet to rails: four M5 screws reach the outer side slots',
       [((x, s * (rig.RAIL_Y + rig.EXT / 2 + rig.FL_T + 0.5), rig.EXT / 2), (0, -s * 10.5, 0), R5, [n, f'rail_{side[s]}']) for n, s, x in feet])
screws('mirror lock screw: clear through the left post, thread bites in the bar',
       [((rig.XH, -(rig.POST_Y + 6.5), rig.ZH), (0, 6.6, 0), R5, ['stage']), ((rig.XH, -(rig.BAR_HW + 0.3), rig.ZH), (0, 8.0, 0), R5MIN, ['hinge_bar'])],
       bite=[((rig.XH, -(rig.BAR_HW + 0.3), rig.ZH), (0, 8.0, 0), R5, 'hinge_bar')])
screws('mirror pivot screw: thread bites in the right post, bar turns freely on it',
       [((rig.XH, rig.POST_Y - 0.1, rig.ZH), (0, 6.6, 0), R5MIN, ['stage']), ((rig.XH, rig.BAR_HW + 0.3, rig.ZH), (0, -8.0, 0), R5, ['hinge_bar'])],
       bite=[((rig.XH, rig.POST_Y - 0.1, rig.ZH), (0, 6.6, 0), R5, 'stage')])
xy = [(x, y) for x in rig.RAIL_HOLES_X for y in (-46.5, 46.5)]
screws('card rails to stage: four M3 screws pass the rails, threads bite in the stage',
       [((x, y, rig.ZB - 5), (0, 0, 5.0), R3, ['card_rails']) for x, y in xy] + [((x, y, rig.ZB), (0, 0, 5.5), R3MIN, ['stage']) for x, y in xy],
       bite=[((x, y, rig.ZB), (0, 0, 5.5), R3, 'stage') for x, y in xy])
sx, sz = rig.led_local(0.0, rig.HFACE - rig.HS_H + 5.0)
screws('heatsink set screws: M3 threads bite in both sled cheeks', [((sx, -26, sz), (0, 52, 0), R3MIN, ['led_sled'])], bite=[((sx, -26, sz), (0, 52, 0), R3, 'led_sled')])

lx = (math.cos(math.radians(rig.LEAN)), 0.0, math.sin(math.radians(rig.LEAN)))      # up the heatsink slope
neg = lambda v, k=1.0: tuple(-k * c for c in v)
pos = lambda v, k=1.0: tuple(k * c for c in v)
t_mid, n_mid = rig.frame(rig.PHI_MID)                                              # up the mirror, and out of its reflecting face
free('stage ears clear the uprights by 0.25 mm a side', 'stage', ['upright_left', 'upright_right'], [(0, 0.25, 0), (0, -0.25, 0)])
free('hinge bar has 0.3 mm of end float between the posts', 'hinge_bar', ['stage'], [(0, 0.3, 0), (0, -0.3, 0)])
free('mirror tile has 0.4 mm of side room in its channel', 'mirror_tile', ['hinge_bar', 'stage'], [(0, 0.4, 0), (0, -0.4, 0)])
free('heatsink has 0.25 mm of side room in the sled', 'heatsink', ['led_sled'], [(0, 0.25, 0), (0, -0.25, 0)])
free('window card slides freely', 'window_card_40x56', ['card_rails', 'stage'], [(0, 0.4, 0), (0, -0.4, 0), (0, 0, 0.25), (0, 0, -0.25)])
free('a 100 mm dish has 1 mm of play between the stops', 'petri_dish', ['stage'], [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0)])
free('snoot clears a star board 2 mm oversize', 'led_star', ['snoot'], [pos(lx), neg(lx), (0, 1, 0), (0, -1, 0)])
free('dipper arm is a loose fit in the foot', 'dipper_arm_wedge', ['dipper_foot'], [(0.15, 0, 0), (-0.15, 0, 0), (0, 0.15, 0), (0, -0.15, 0)])

held('four stops locate the dish', 'petri_dish', [('stage', d) for d in ((2.5, 0, 0), (-2.5, 0, 0), (0, 2.5, 0), (0, -2.5, 0))])
held('sled cradle holds the heatsink downhill, sideways and from below', 'heatsink',
     [('led_sled', neg(lx)), ('led_sled', (0, 1.0, 0)), ('led_sled', (0, -1.0, 0)), ('led_sled', neg(tuple(rig.AX), 0.5))])
held('rails, rear bar and stage hold the window card', 'window_card_40x56',
     [('card_rails', (-1.5, 0, 0)), ('card_rails', (0, 1.0, 0)), ('card_rails', (0, -1.0, 0)), ('card_rails', (0, 0, -1.0)), ('stage', (0, 0, 1.0))])
held('channel holds the mirror tile sideways, downward and front to back', 'mirror_tile',
     [('hinge_bar', (0, 1.0, 0)), ('hinge_bar', (0, -1.0, 0)), ('hinge_bar', neg(tuple(t_mid))), ('hinge_bar', pos(tuple(n_mid), 2.0)), ('hinge_bar', neg(tuple(n_mid)))])
held('posts hold the hinge bar end to end', 'hinge_bar', [('stage', (0, 1.0, 0)), ('stage', (0, -1.0, 0))])
held('ears and flange locate the stage on the uprights', 'stage',
     [('upright_left', (-0.5, 0, 0)), ('upright_right', (-0.5, 0, 0)), ('upright_right', (0, -1.0, 0)), ('upright_left', (0, 1.0, 0))])
held('base bracket wall backs the left upright', 'upright_left', [('base_bracket', (-0.5, 0, 0))])
held('base bracket wall backs the right upright', 'upright_right', [('base_bracket', (-0.5, 0, 0))])
held('foot socket holds the dipper arm', 'dipper_arm_wedge', [('dipper_foot', d) for d in ((1.0, 0, 0), (-1.0, 0, 0), (0, 1.0, 0), (0, -1.0, 0), (0, 0, -1.0))])
held('tapered seat carries and centres the speaker', 'speaker', [('stage', (0, 0, -1.5)), ('stage', (2.0, 0, 0)), ('stage', (0, -2.0, 0))])
cleanup()
gmsh.write(f'{OUT}/assembly/caustic_rig_assembly.step')
report['assembly_solids'] = len(gmsh.model.getEntities(3))

# coarse mesh of the assembly for the 3D viewer
set_mesh(28, 40)
gmsh.model.mesh.generate(2)
lut, xyz = all_nodes()
viewer = {}
for n, t in tags.items():
    v, f = volume_mesh(t, lut, xyz)
    f, _ = orient(v, f)
    viewer[n] = (v, f)
np.savez_compressed(f'{OUT}/assembly/viewer_mesh.npz', **{f'{n}__v': v.astype(np.float32) for n, (v, f) in viewer.items()}, **{f'{n}__f': f.astype(np.uint32) for n, (v, f) in viewer.items()})

# ---------------------------------------------------------------- 2. optics, with the as-drawn positions
U_LO, U_HI, Y_MAX = rig.U0 + 4.4 + 3, rig.U0 + rig.TILE - rig.BEVEL, rig.TILE / 2 - rig.BEVEL
optics = {}
for cname, (a, b) in rig.CARDS.items():
    for tname, e in rig.TILTS.items():
        phi = rig.phi_of(e)
        res = [rig.trace(c, phi) for c in rig.corners(a, b)]
        us, ys = [r[1] for r in res], [abs(r[0][1]) for r in res]
        m = min(min(us) - U_LO, U_HI - max(us), Y_MAX - max(ys))
        optics[f'{cname}/{tname}'] = dict(u=[min(us), max(us)], y=max(ys), margin=m)
        if True:
            check(f'beam lands on the flat of the mirror, card {cname}, tilt {tname}', m >= 4, f'u {min(us):.0f}..{max(us):.0f} of {U_LO:.0f}..{U_HI:.0f}, half width {max(ys):.0f} of {Y_MAX:.0f}, margin {m:.1f}')
report['optics'] = optics
big = rig.CARDS['40x56']
hole = max(math.hypot(c[0] - rig.XD, c[1]) for z in (rig.ZB, rig.ZS + rig.LIP) for c in rig.corners(*big, z))
check('largest window clears the beam hole', rig.HOLE_R - hole >= 1.5, f'{rig.HOLE_R - hole:.1f} mm')
lit = rig.corners(*big, rig.ZW)
lit_r, lit_y = max(math.hypot(c[0] - rig.XD, c[1]) for c in lit), max(abs(c[1]) for c in lit)
check('lit water stays inside a 95 mm dish (inner radius 45)', 45 - lit_r >= 2, f'{45 - lit_r:.1f} mm')
check('dipper tip is outside the lit water', rig.TIP_Y - 3 - lit_y >= 2, f'{rig.TIP_Y - 3 - lit_y:.1f} mm')
ang = max(math.degrees(math.acos(np.dot((c - rig.E) / np.linalg.norm(c - rig.E), rig.AX))) for c in rig.corners(*big))
snoot = math.degrees(math.atan(rig.SNOOT_R / rig.SNOOT_TOP))
check('snoot passes the largest window', snoot - ang >= 1.0, f'snoot {snoot:.1f} deg, window corner {ang:.1f} deg')
report['numbers'] = dict(XE=rig.XE, ZE=rig.ZE, ZS=rig.ZS, ZW=rig.ZW, ZK=rig.ZK, led_to_water=float((rig.ZW - rig.ZE) / math.cos(math.radians(rig.LEAN))),
                         phi={k: rig.phi_of(v) for k, v in rig.TILTS.items()}, sled_x=[rig.XE - 30, rig.XE + 42])

# ---------------------------------------------------------------- 3. each printed part, in print orientation
set_mesh(56, 12)
for name, spec in rig.PRINTED.items():
    gmsh.model.add(name)
    dt = spec[0](*rig.PRINT_ARGS.get(name, spec[1]))
    assert len(dt) == 1 and dt[0][0] == 3, (name, dt)
    rig.xform(dt, spec[4])
    cleanup()
    tag = gmsh.model.getEntities(3)[0][1]
    cad_vol = occ.getMass(3, tag)
    gmsh.model.mesh.generate(2)
    lut, xyz = all_nodes()
    v, f = volume_mesh(tag, lut, xyz)
    f, facts = orient(v, f)
    lo, hi = v.min(0), v.max(0)                   # sit the part on the bed, centred, using the exact mesh extents
    shift = np.array([-(lo[0] + hi[0]) / 2, -(lo[1] + hi[1]) / 2, -lo[2]])
    v = v + shift
    occ.translate([(3, tag)], *shift)
    occ.synchronize()
    gmsh.write(f'{OUT}/step/{name}.step')
    write_stl(f'{OUT}/stl/{name}.stl', v, f)
    size = [round(float(s), 1) for s in (v.max(0) - v.min(0))]
    oh = overhang(v, f)
    facts.update(cad_volume=cad_vol, size=size, overhangs=oh[:6], overhang_area=sum(o['area'] for o in oh))
    report['parts'][name] = facts
    ok = facts['open_or_nonmanifold_edges'] == 0 and facts['shells'] == 1 and abs(facts['mesh_volume'] - cad_vol) / cad_vol < 0.01
    check(f'{name}: watertight single shell, volume matches the solid', ok,
          f"{facts['triangles']} triangles, {size[0]} x {size[1]} x {size[2]} mm, {cad_vol / 1000:.1f} cm3, mesh/solid {facts['mesh_volume'] / cad_vol:.4f}")
    check(f'{name}: fits the 256 mm bed', max(size[0], size[1]) <= 240 and size[2] <= 240, '')
    gmsh.model.remove()

# ---------------------------------------------------------------- 4. STEP round trip
for name in rig.PRINTED:
    gmsh.model.add('rt')
    dt = occ.importShapes(f'{OUT}/step/{name}.step')
    occ.synchronize()
    vols = [t for d, t in dt if d == 3]
    v = sum(occ.getMass(3, t) for t in vols)
    ref = report['parts'][name]['cad_volume']
    check(f'{name}: STEP reads back as one solid with the same volume', len(vols) == 1 and abs(v - ref) / ref < 1e-6, f'{len(vols)} solid, {v / 1000:.2f} cm3')
    gmsh.model.remove()

json.dump(report, open(f'{OUT}/report.json', 'w'), indent=1, default=float)
bad = [c for c in report['checks'] if not c[1]]
print(f"\n{len(report['checks'])} checks, {len(bad)} failed")
gmsh.finalize()
sys.exit(1 if bad else 0)
