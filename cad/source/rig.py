#!/usr/bin/env python3
"""Caustic bench rig, printable parts for a frame of four 400 mm 2020 extrusions.

Geometry is built with the OpenCASCADE kernel through gmsh. Assembly coordinates, millimetres:
x = throw direction (toward the wall), y = sideways, z = up from the desk.
Two base rails lie along x at y = +-50. Two uprights stand on them with their front faces at x = 0.
"""
import math

import gmsh
import numpy as np

occ = gmsh.model.occ
rad, sin, cos, tan = math.radians, math.sin, math.cos, math.tan

# ---------------------------------------------------------------- frame and optics
RAIL_Y, RAIL_X0, RAIL_X1, EXT = 50.0, -150.0, 250.0, 20.0
ZR = EXT                           # top of the base rails
UP_Z1 = ZR + 400.0
LEAN = 25.0                        # beam leans back toward the uprights
ZE = 57.0                          # LED emitter height
T_PL = 6.0                         # stage plate thickness
ZS = 188.0                         # stage top
ZB = ZS - T_PL                     # stage underside
CARD_T, SLOT_H = 1.8, 2.4
ZK = ZB - SLOT_H / 2               # window card mid-plane
XK = 87.0                          # window centre
XE = XK + (ZK - ZE) * tan(rad(LEAN))
E = np.array([XE, 0.0, ZE])
AX = np.array([-sin(rad(LEAN)), 0.0, cos(rad(LEAN))])
XD, HOLE_R = 83.0, 40.0            # dish centre and beam hole radius
PL_X1, PL_Y0, PL_Y1 = XD + 60.0, -91.0, 104.0      # stage plate outline (rear edge at x = 0)
LIP = 1.2
DISH_R, DISH_H, DISH_T, DEPTH = 50.0, 17.0, 2.5, 7.0
ZW = ZS + LIP + DISH_T + DEPTH     # water surface
PEG_R = 51.5                       # inner face of the dish stops
SPK = (XD, 77.0)                   # speaker centre
SPK_R = 18.7                       # speaker through-hole radius
TIP_Y = 40.0                       # dipper tip
XH, ZH = 22.0, ZS + 20.0           # mirror hinge axis
TILE_POCKET = 152.4 / 2 + 0.5      # half length of the glass channel: the tile plus 0.5 mm each side
BAR_HW = TILE_POCKET + 1.8         # hinge bar half length: the channel has closed ends
POST_Y = BAR_HW + 0.4              # inner face of the hinge posts
U0, TILE, GLASS_T, BEVEL = 9.6, 152.4, 3.0, 7.0
CF = -0.7                          # apparent reflecting plane, measured from the hinge axis
TILTS = {'low': 5.0, 'mid': 20.0, 'high': 35.0}
CARDS = {'24x34': (12.0, 17.0), '32x44': (16.0, 22.0), '40x56': (20.0, 28.0), 'slit_8x56': (4.0, 28.0)}
HFACE = -2.8                       # heatsink face in LED-local z (emitter at 0)
HS, HS_H = 40.0, 20.0
SNOOT_R, SNOOT_TOP = 11.0, 35.2
M5C, M5T, M3C, M3P = 5.6, 4.5, 3.4, 2.7      # clearance and self-thread hole diameters
M5P = 5.3                          # plain hole that turns on an M5 pivot screw
STOP_H = 7.0                       # height of the dish stops
FL_T = 5.0                         # flange thickness for M5 x 10 into a T-nut
EAR_Y = RAIL_Y + EXT / 2 + 0.3      # inner face of the stage's clamp ears, just outside the uprights


def phi_of(e):
    return 45.0 + (e + LEAN) / 2.0


def led_local(lx, lz):
    """LED-local (x along the heatsink face up the slope, z along the beam) to assembly (x, z)."""
    b = rad(LEAN)
    return XE + lx * cos(b) - lz * sin(b), ZE + lx * sin(b) + lz * cos(b)


# ---------------------------------------------------------------- kernel helpers
def box(x0, x1, y0, y1, z0, z1):
    return [(3, occ.addBox(min(x0, x1), min(y0, y1), min(z0, z1), abs(x1 - x0), abs(y1 - y0), abs(z1 - z0)))]


def cyl(p, d, r):
    return [(3, occ.addCylinder(p[0], p[1], p[2], d[0], d[1], d[2], r))]


def cone(p, d, r0, r1):
    return [(3, occ.addCone(p[0], p[1], p[2], d[0], d[1], d[2], r0, r1))]


def prism(poly, axis, a0, a1):
    """Extrude a polygon along an axis. axis 'y': poly is (x, z). axis 'x': poly is (y, z). axis 'z': poly is (x, y)."""
    if axis == 'y':
        pts = [occ.addPoint(p[0], a0, p[1]) for p in poly]
        d = (0, a1 - a0, 0)
    elif axis == 'x':
        pts = [occ.addPoint(a0, p[0], p[1]) for p in poly]
        d = (a1 - a0, 0, 0)
    else:
        pts = [occ.addPoint(p[0], p[1], a0) for p in poly]
        d = (0, 0, a1 - a0)
    n = len(pts)
    loop = occ.addCurveLoop([occ.addLine(pts[i], pts[(i + 1) % n]) for i in range(n)])
    out = occ.extrude([(2, occ.addPlaneSurface([loop]))], *d)
    return [e for e in out if e[0] == 3]


def tear(p, axis, length, r):
    """Sideways hole with a 45 degree peaked roof, so it prints without support. Roof points to +z."""
    k, top = r / math.sqrt(2), r * math.sqrt(2)
    if axis == 'x':
        return [cyl(p, (length, 0, 0), r), prism([(p[1] - k, p[2] + k), (p[1] + k, p[2] + k), (p[1], p[2] + top)], 'x', p[0], p[0] + length)]
    return [cyl(p, (0, length, 0), r), prism([(p[0] - k, p[2] + k), (p[0] + k, p[2] + k), (p[0], p[2] + top)], 'y', p[1], p[1] + length)]


def fuse(a, *others):
    tools = [t for o in others for t in o]
    return occ.fuse(a, tools)[0] if tools else a


def cut(a, *others):
    tools = [t for o in others for t in o]
    return occ.cut(a, tools)[0] if tools else a


def xform(dt, R, t=(0, 0, 0)):
    occ.affineTransform(dt, [R[0][0], R[0][1], R[0][2], t[0], R[1][0], R[1][1], R[1][2], t[1], R[2][0], R[2][1], R[2][2], t[2]])
    return dt


def rot_y(deg):
    a = rad(deg)
    return np.array([[cos(a), 0, sin(a)], [0, 1, 0], [-sin(a), 0, cos(a)]])


I3 = np.eye(3)
R_LED = rot_y(-LEAN)               # LED-local to assembly


def r_mirror(phi):                 # mirror-local (x up the mirror, z behind the glass) to assembly
    return rot_y(-phi)


# ---------------------------------------------------------------- printed parts
def stage():
    """Stage: plate, dish seat, speaker seat, hinge posts and the clamp flange, in one print."""
    s = box(0, PL_X1, PL_Y0, PL_Y1, ZB, ZS)
    add = []
    add += [cut(cyl((XD, 0, ZS), (0, 0, LIP), HOLE_R + 3.5), cyl((XD, 0, ZS - 1), (0, 0, LIP + 2), HOLE_R + 0.5))]        # spill lip
    for px, py, w, h in ((XD + PEG_R, 0, 3, 12), (XD - PEG_R - 3, 0, 3, 12)):
        add += [box(px, px + w, py - h / 2, py + h / 2, ZS, ZS + STOP_H)]                                                   # dish stops, +-x
    for py in (PEG_R, -PEG_R - 3):
        add += [box(XD - 6, XD + 6, py, py + 3, ZS, ZS + STOP_H)]                                                           # dish stops, +-y
    add += [box(PL_X1 - 2.5, PL_X1, PL_Y0, PL_Y1, ZS, ZS + 3), box(0, PL_X1, PL_Y0, PL_Y0 + 2.5, ZS, ZS + 3), box(0, PL_X1, PL_Y1 - 2.5, PL_Y1, ZS, ZS + 3),
            box(0, 2.5, PL_Y0, -EAR_Y, ZS, ZS + 3), box(0, 2.5, EAR_Y, PL_Y1, ZS, ZS + 3)]                                       # drip rim
    add += [box(0, FL_T, -EAR_Y - FL_T, EAR_Y + FL_T, ZS, ZS + 46)]                                                    # rear flange, bears on the upright fronts
    for sg in (-1, 1):
        add += [box(-EXT, 0, sg * EAR_Y, sg * (EAR_Y + FL_T), ZB, ZS + 46)]                                           # clamp ears on the outer sides of the uprights
    add += [cut(cyl((SPK[0], SPK[1], ZS), (0, 0, LIP), SPK_R + 4.8), cyl((SPK[0], SPK[1], ZS - 1), (0, 0, LIP + 2), SPK_R + 2.8))]   # dam: keeps a spill out of the speaker
    for y in (-37, 33):
        add += [prism([(FL_T, ZS), (23, ZS), (FL_T, ZS + 18)], 'y', y, y + 4)]                                         # flange gussets
    for y in (-POST_Y - 6, POST_Y):
        add += [prism([(XH - 14, ZS), (XH + 14, ZS), (XH + 7, ZS + 29), (XH - 7, ZS + 29)], 'y', y, y + 6)]            # hinge posts
    s = fuse(s, *add)
    holes = [cyl((XD, 0, ZB - 1), (0, 0, T_PL + LIP + 2), HOLE_R)]                                                     # beam hole
    holes += [cyl((SPK[0], SPK[1], ZB - 1), (0, 0, T_PL + 2), SPK_R), cone((SPK[0], SPK[1], ZS - 2), (0, 0, 2.2), SPK_R, SPK_R + 2.2)]
    for z in (ZS + 12, ZS + 36):
        holes += tear((-EXT / 2, -80, z), 'y', 160, M5C / 2)                                                           # ears to the uprights' outer slots
    holes += [box(SPK[0] - 6, SPK[0] + 6, SPK[1], SPK[1] + 20.5, ZB - 1, ZS + 1)]                                        # room for the speaker terminals and leads
    holes += tear((XH, -100, ZH), 'y', 100, M5C / 2)                                                                   # -y post: clearance for the lock screw
    holes += tear((XH, 0, ZH), 'y', 100, M5T / 2)                                                                      # +y post: thread for the pivot screw
    for x in RAIL_HOLES_X:
        for y in (-46.5, 46.5):
            holes += [cyl((x, y, ZB - 1), (0, 0, T_PL + 2), M3P / 2)]                                                  # card rail pilots, M3 cuts its own thread
    return cut(s, *holes)


RAIL_HOLES_X = (XD - 28.0, XD + 42.0)
CR_X0, CR_X1 = XD - 38.0, XD + 50.0


def card_rails():
    r = box(CR_X0, CR_X0 + 4, -50, 50, ZB - 4.4, ZB)
    add = []
    for s in (-1, 1):
        add += [box(CR_X0 + 4, CR_X1, s * 43, s * 50, ZB - 4.4, ZB), box(CR_X0 + 4, CR_X1, s * 38.5, s * 43, ZB - 4.4, ZB - SLOT_H)]
    r = fuse(r, *add)
    holes = [cyl((x, y, ZB - 6), (0, 0, 8), M3C / 2) for x in RAIL_HOLES_X for y in (-46.5, 46.5)]
    return cut(r, *holes)


def card(a, b):
    z0 = ZK - CARD_T / 2
    return cut(box(CR_X0 + 4.5, PL_X1 + 14, -42.5, 42.5, z0, z0 + CARD_T), box(XK - a, XK + a, -b, b, z0 - 1, z0 + CARD_T + 1),
               cyl((PL_X1 + 7, 0, z0 - 1), (0, 0, CARD_T + 2), 4.0))


def hinge_bar():
    """Mirror-local: x = distance up the mirror from the hinge axis, z = behind the glass."""
    prof = [(-8, 6), (46, 6), (46, 2.2), (U0, 2.2), (U0, -2.2), (14, -2.2), (14, -6), (-8, -6)]       # (u, -w)
    b = prism(prof, 'y', -TILE_POCKET, TILE_POCKET)
    b = fuse(b, *[box(-8, 14, s * TILE_POCKET, s * BAR_HW, -6, 6) for s in (-1, 1)])                 # closed ends locate the tile sideways
    holes = []
    # -y end: thread for the lock screw. +y end: plain hole that turns on the pivot screw. Roofs point up the mirror, which is up when printed.
    for s, r, depth in ((-1, M5T / 2, 14.0), (1, M5P / 2, 12.0)):
        y0, y1 = sorted((s * (BAR_HW + 1), s * (BAR_HW - depth)))
        k, top = r / math.sqrt(2), r * math.sqrt(2)
        holes += [cyl((0, y0, 0), (0, y1 - y0, 0), r), prism([(k, -k), (top, 0), (k, k)], 'y', y0, y1)]
    return cut(b, *holes)


def snoot():
    """LED-local: z along the beam, heatsink face at z = HFACE."""
    s = fuse(cyl((0, 0, HFACE), (0, 0, 2), 19.0), cyl((0, 0, HFACE), (0, 0, SNOOT_TOP - HFACE), SNOOT_R + 2.0))
    return cut(s, cyl((0, 0, HFACE - 1), (0, 0, SNOOT_TOP - HFACE + 2), SNOOT_R),
               cyl((0, 0, HFACE - 1), (0, 0, 2.2), SNOOT_R + 1.0), cone((0, 0, HFACE + 1.2), (0, 0, 1.73), SNOOT_R + 1.0, SNOOT_R),      # room for the star board, 60 degree roof
               prism([(-3.5, HFACE - 1), (3.5, HFACE - 1), (3.5, HFACE + 2.5), (0, HFACE + 6), (-3.5, HFACE + 2.5)], 'y', 6, 21))


def sled():
    zt = ZR + FL_T
    hb = HFACE - HS_H                                   # fin tips, LED-local z
    p1, p2 = led_local(-HS / 2, hb), led_local(HS / 2, hb)
    q1, q2 = led_local(-HS / 2, hb + 10), led_local(HS / 2, hb + 10)
    a, b = led_local(-HS / 2 - 3.3, hb + 8), led_local(-HS / 2 - 0.3, hb + 8)
    cx = b[0] + (b[1] - zt) * tan(rad(LEAN))            # where the stop face meets the plate
    s = box(XE - 30, XE + 42, -60, 60, ZR, zt)
    add = []
    for sg in (-1, 1):
        y0, y1, y2 = sg * 14.0, sg * (HS / 2 + 0.3), sg * (HS / 2 + 4.3)
        add += [prism([(p1[0], zt), (p2[0], zt), p2, p1], 'y', min(y0, y1), max(y0, y1))]                     # ledge under the outer fins
        add += [prism([(q1[0], zt), (p2[0], zt), p2, q2, q1], 'y', min(y1, y2), max(y1, y2))]                 # cheek
        add += [prism([(a[0], zt), (cx, zt), b, a], 'y', min(y0, y2), max(y0, y2))]                           # lower stop
    add += [prism([(XE - 27, 34), (XE - 14, 40), (XE - 14, 28)], 'z', zt, zt + 0.6)]                            # raised arrow: this end faces the uprights
    s = fuse(s, *add)
    holes = [box(XE - 9, XE + 30, -13.5, 13.5, ZR - 1, zt + 1)]                                               # air window
    holes += [cyl((x, y, ZR - 1), (0, 0, FL_T + 2), M5C / 2) for x in (XE - 22, XE + 34) for y in (-RAIL_Y, RAIL_Y)]
    sx, sz = led_local(0.0, hb + 5.0)
    holes += tear((sx, -HS / 2 - 6, sz), 'y', HS + 12, M3P / 2)                                               # M3 set screws through the cheeks pinch the heatsink
    return cut(s, *holes)


def base_bracket():
    zt = ZR + FL_T
    s = box(-150, -20, -60, 60, ZR, zt)
    add = [box(-20 - FL_T, -20, -60, 60, ZR, 110)]
    for y in (-60, -43, 40, 57):
        add += [prism([(-25, zt), (-70, zt), (-25, 75)], 'y', y, y + 3)]
    s = fuse(s, *add)
    holes = [cyl((x, y, ZR - 1), (0, 0, FL_T + 2), M5C / 2) for x in (-45, -130) for y in (-RAIL_Y, RAIL_Y)]
    for z in (50, 95):
        for y in (-RAIL_Y, RAIL_Y):
            holes += tear((-26, y, z), 'x', FL_T + 2, M5C / 2)
    holes += [prism([(-17, zt), (17, zt), (17, zt + 8), (0, zt + 25), (-17, zt + 8)], 'x', -26, -19)]           # cable port between the uprights
    holes += [box(-88, -80, sg * 4, sg * 7, ZR - 1, zt + 1) for sg in (-1, 1)]                                  # slots for a cable tie
    return cut(s, *holes)


ZCAP = ZS - 1.0                    # assumed top of the speaker dust cap
ZA = ZS + 24.0                     # underside of the dipper arm


def dipper_foot():
    """Glued to the speaker dust cap. Local: z up, origin at the cap."""
    s = fuse(cyl((0, 0, 0), (0, 0, 1.5), 6.0), box(-3.25, 3.25, -3.25, 3.25, 1.5, 8.0))
    return cut(s, box(-1.7, 1.7, -1.7, 1.7, 2.0, 9.0))


def dipper_arm(kind, extra=0.0):
    """Flat arm, 3 mm thick in x. Assembly coordinates. extra lengthens the riser so it can be trimmed to suit the speaker."""
    x0, x1, ys = SPK[0] - 1.5, SPK[0] + 1.5, SPK[1]
    s = fuse(box(x0, x1, ys - 1.5, ys + 1.5, ZCAP + 2.0 - extra, ZA + 3), box(x0, x1, TIP_Y - 3, ys + 1.5, ZA, ZA + 3))
    if kind == 'wedge':
        tip = prism([(TIP_Y - 3, ZA), (TIP_Y + 3, ZA), (TIP_Y + 3, ZW + 6), (TIP_Y, ZW - 3.5), (TIP_Y - 3, ZW + 6)], 'x', x0, x1)
    elif kind == 'paddle':
        tip = fuse(box(x0, x1, TIP_Y - 1.5, TIP_Y + 1.5, ZW, ZA), box(x0, x1, TIP_Y - 4, TIP_Y + 4, ZW - 2, ZW + 1))
    else:
        tip = prism([(TIP_Y - 1.5, ZA), (TIP_Y + 1.5, ZA), (TIP_Y + 0.6, ZW - 3), (TIP_Y - 0.6, ZW - 3)], 'x', x0, x1)
    return fuse(s, tip)


def outrigger_foot():
    """Bolts to the outer side slot of a base rail and widens the stance. Local: rail face at y = 0, desk at z = 0."""
    s = fuse(box(-12, 12, 0, FL_T, 0, EXT), box(-12, 12, 0, 80, 0, 5.0))
    s = fuse(s, *[prism([(FL_T, 5.0), (25, 5.0), (FL_T, EXT)], 'x', x0, x0 + 4) for x0 in (-12, 8)])
    return cut(s, *tear((0, -1, EXT / 2), 'y', FL_T + 2, M5C / 2))


# ---------------------------------------------------------------- bought parts, as reference solids
def extrusion(axis, p, length):
    """2020 bar with four 6.2 x 6.1 mm slots. p = corner of the 20 x 20 section, axis 'x' or 'z'."""
    if axis == 'x':
        s = box(p[0], p[0] + length, p[1], p[1] + EXT, p[2], p[2] + EXT)
        c = (p[1] + EXT / 2, p[2] + EXT / 2)
        g = [box(p[0] - 1, p[0] + length + 1, c[0] - 3.1, c[0] + 3.1, p[2] + EXT - 6.1, p[2] + EXT + 1), box(p[0] - 1, p[0] + length + 1, c[0] - 3.1, c[0] + 3.1, p[2] - 1, p[2] + 6.1),
             box(p[0] - 1, p[0] + length + 1, p[1] - 1, p[1] + 6.1, c[1] - 3.1, c[1] + 3.1), box(p[0] - 1, p[0] + length + 1, p[1] + EXT - 6.1, p[1] + EXT + 1, c[1] - 3.1, c[1] + 3.1)]
    else:
        s = box(p[0], p[0] + EXT, p[1], p[1] + EXT, p[2], p[2] + length)
        c = (p[0] + EXT / 2, p[1] + EXT / 2)
        g = [box(p[0] + EXT - 6.1, p[0] + EXT + 1, c[1] - 3.1, c[1] + 3.1, p[2] - 1, p[2] + length + 1), box(p[0] - 1, p[0] + 6.1, c[1] - 3.1, c[1] + 3.1, p[2] - 1, p[2] + length + 1),
             box(c[0] - 3.1, c[0] + 3.1, p[1] - 1, p[1] + 6.1, p[2] - 1, p[2] + length + 1), box(c[0] - 3.1, c[0] + 3.1, p[1] + EXT - 6.1, p[1] + EXT + 1, p[2] - 1, p[2] + length + 1)]
    return cut(s, *g)


def heatsink():                    # LED-local
    s = box(-HS / 2, HS / 2, -HS / 2, HS / 2, HFACE - 4, HFACE)
    fins = [box(-HS / 2, HS / 2, -HS / 2 + i * (HS - 1.7) / 8, -HS / 2 + i * (HS - 1.7) / 8 + 1.7, HFACE - HS_H, HFACE - 4) for i in range(9)]
    return fuse(s, *fins)


def led_star():                    # LED-local
    return fuse(cyl((0, 0, HFACE), (0, 0, 1.6), 10.0), cyl((0, 0, HFACE + 1.6), (0, 0, 1.2), 1.75))


def glass():                       # mirror-local, 0.5 mm of tape behind it
    return box(U0, U0 + TILE, -TILE / 2, TILE / 2, 2.2 - 0.5 - GLASS_T, 2.2 - 0.5)


def dish():
    z0 = ZS + LIP
    return cut(cyl((XD, 0, z0), (0, 0, DISH_H), DISH_R), cyl((XD, 0, z0 + DISH_T), (0, 0, DISH_H), DISH_R - DISH_T))


def speaker():
    s = fuse(cone((SPK[0], SPK[1], ZS - 1.3), (0, 0, 1.3), SPK_R - 0.3, 20.0), cone((SPK[0], SPK[1], ZS - 12), (0, 0, 10.7), 13.0, SPK_R - 0.3),
             cyl((SPK[0], SPK[1], ZS - 20), (0, 0, 8), 13.0))
    return cut(s, cyl((SPK[0], SPK[1], ZCAP), (0, 0, 3), 16.0))


def breadboard():
    return box(-148, -93, -41, 41, ZR + FL_T, ZR + FL_T + 9.5)


# name: (builder, args, local-to-assembly rotation, translation, print rotation, group, colour)
R_X180 = np.array([[1, 0, 0], [0, -1, 0], [0, 0, -1]])
R_Z180 = np.array([[-1, 0, 0], [0, -1, 0], [0, 0, 1]])
FOOT_X = (-110.0, 215.0)           # where the outrigger feet sit along the rails
R_BAR_PRINT = np.array([[0, 0, -1], [0, 1, 0], [1, 0, 0]])       # mirror-local u becomes print z
R_FLAT_X = np.array([[0, 1, 0], [0, 0, 1], [1, 0, 0]])           # thickness in x becomes print z
PHI_MID = phi_of(TILTS['mid'])
MIR_T = (XH, 0, ZH)
PRINTED = {
    'stage': (stage, (), I3, (0, 0, 0), I3, 'Stage', '#5d7389'),
    'card_rails': (card_rails, (), I3, (0, 0, 0), I3, 'Stage', '#465a6e'),
    **{f'window_card_{k}': (card, v, I3, (0, 0, 0), I3, 'Stage', '#23272c') for k, v in CARDS.items()},
    'hinge_bar': (hinge_bar, (), r_mirror(PHI_MID), MIR_T, R_BAR_PRINT, 'Mirror', '#465a6e'),
    'led_sled': (sled, (), I3, (0, 0, 0), I3, 'Light', '#5d7389'),
    'snoot': (snoot, (), R_LED, (XE, 0, ZE), I3, 'Light', '#23272c'),
    'base_bracket': (base_bracket, (), I3, (0, 0, 0), I3, 'Frame', '#465a6e'),
    'dipper_foot': (dipper_foot, (), I3, (SPK[0], SPK[1], ZCAP), I3, 'Wave driver', '#e58a45'),
    **{f'dipper_arm_{k}': (dipper_arm, (k,), I3, (0, 0, 0), R_FLAT_X, 'Wave driver', '#e58a45') for k in ('wedge', 'paddle', 'pin')},
    'outrigger_foot': (outrigger_foot, (), I3, (FOOT_X[1], RAIL_Y + EXT / 2, 0), I3, 'Frame', '#465a6e'),
}
# further copies of printed parts in the assembly: name -> (printed part, rotation, translation)
COPIES = {'outrigger_foot_2': ('outrigger_foot', I3, (FOOT_X[0], RAIL_Y + EXT / 2, 0)),
          'outrigger_foot_3': ('outrigger_foot', R_Z180, (FOOT_X[1], -RAIL_Y - EXT / 2, 0)),
          'outrigger_foot_4': ('outrigger_foot', R_Z180, (FOOT_X[0], -RAIL_Y - EXT / 2, 0))}
QTY = {'outrigger_foot': 4}
BOUGHT = {
    'rail_left': (extrusion, ('x', (RAIL_X0, -RAIL_Y - EXT / 2, 0), 400.0), I3, (0, 0, 0), 'Frame', '#33373c'),
    'rail_right': (extrusion, ('x', (RAIL_X0, RAIL_Y - EXT / 2, 0), 400.0), I3, (0, 0, 0), 'Frame', '#33373c'),
    'upright_left': (extrusion, ('z', (-EXT, -RAIL_Y - EXT / 2, ZR), 400.0), I3, (0, 0, 0), 'Frame', '#33373c'),
    'upright_right': (extrusion, ('z', (-EXT, RAIL_Y - EXT / 2, ZR), 400.0), I3, (0, 0, 0), 'Frame', '#33373c'),
    'heatsink': (heatsink, (), R_LED, (XE, 0, ZE), 'Light', '#c4cad1'),
    'led_star': (led_star, (), R_LED, (XE, 0, ZE), 'Light', '#ffd34d'),
    'mirror_tile': (glass, (), r_mirror(PHI_MID), MIR_T, 'Mirror', '#e6eef5'),
    'petri_dish': (dish, (), I3, (0, 0, 0), 'Dish', '#d6f1ff'),
    'speaker': (speaker, (), I3, (0, 0, 0), 'Wave driver', '#1b1d21'),
    'breadboard': (breadboard, (), I3, (0, 0, 0), 'Electronics', '#e9e6dc'),
}
ASM_ONLY = {'window_card_24x34', 'window_card_32x44', 'window_card_slit_8x56', 'dipper_arm_paddle', 'dipper_arm_pin'}
PRINT_ARGS = {f'dipper_arm_{k}': (k, 10.0) for k in ('wedge', 'paddle', 'pin')}                 # printed with a longer riser   # alternates, left out of the assembly


def build(name, in_assembly=True):
    if name in COPIES:
        base, R, t = COPIES[name]
        return xform(PRINTED[base][0](*PRINTED[base][1]), R, t)
    spec = PRINTED.get(name) or BOUGHT[name]
    dt = spec[0](*spec[1])
    if in_assembly:
        xform(dt, spec[2], spec[3])
    return dt


# ---------------------------------------------------------------- optics
def frame(phi):
    p = rad(phi)
    return np.array([cos(p), 0, sin(p)]), np.array([sin(p), 0, -cos(p)])


def trace(pk, phi):
    t, n = frame(phi)
    h = np.array([XH, 0, ZH])
    d = (pk - E) / np.linalg.norm(pk - E)
    hit = pk + ((np.dot(h - pk, n) + CF) / np.dot(d, n)) * d
    return hit, float(np.dot(hit - h, t)), d - 2 * np.dot(d, n) * n


def corners(a, b, z=None):
    z = ZK if z is None else z
    s = (z - ZE) / (ZK - ZE)
    return [E + s * (np.array([XK + sx * a, sy * b, ZK]) - E) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
