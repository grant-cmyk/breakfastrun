"""MOCK-UP ONLY (no game change): the fixes Grant asked for after driving the bridge tape, 16 Nov 2026 -
"the diagonals jutting out must be masked, and the area on the inside track needs more boundary circles.
Also - the outside of the bridge are not solid - just alternating blue blocks."
Drawn from the real track 5 world (tools/make_world.py, TRACK=5), at the game's pixels, blue ink on cyan, 4x.
  docs/design/tracks/bridge_fix_mock.png       the view of his screenshot and the whole bridge: as built, and the options
  docs/design/tracks/bridge_fix_overview.png   the whole track with the cereal O's that would be added, ringed
Prints the O counts and the estimated cost of each option (tiles, bytes, T-states a picture).
Run: python3 tools/make_bridge_fix_mock.py"""
import os, sys, math, runpy, tempfile, contextlib, io
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
DEST = os.path.join(HERE, '..', 'docs', 'design', 'tracks')
def world(track):
    os.environ['TRACK'] = str(track); os.environ['WORLD_OUT'] = tempfile.mkdtemp()
    with contextlib.redirect_stdout(io.StringIO()):
        return runpy.run_path(os.path.join(HERE, 'make_world.py'))
w1 = world(1); w = world(5)
PW, PH, ROAD, B, td = w['PW'], w['PH'], w['ROAD'], w['BRIDGE'], w['_td']
ink0 = np.array(w['img'], dtype=bool); cloth = w['cloth_on']; O_RING = w['O_RING']
xc, yc = B['cross']; x0, x1 = xc - ROAD // 2, xc + ROAD // 2
(u0, u1), (d0, d1), (r0, r1) = B['ramp_up'], B['deck'], B['ramp_down']
gw, gi, tw, ti, cells, mb = td.plan_parts(B, 'P4D1')

# ---------------------------------------------------------------- 3. more cereal O's
def edges(wd):
    """points along both edges of the road, where the O's stand (make_world.place_os): (x, y)"""
    pts = wd['PATH'] + [wd['PATH'][0]]; seq = []
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        n = max(1, int(math.hypot(xb - xa, yb - ya)))
        for i in range(n): seq.append((xa + (xb - xa) * i / n, ya + (yb - ya) * i / n))
    out = []
    for side in (-1, 1):
        for i in range(len(seq)):
            (xa, ya), (xb, yb) = seq[i - 2], seq[(i + 2) % len(seq)]
            d = math.hypot(xb - xa, yb - ya) or 1
            nx, ny = -(yb - ya) / d, (xb - xa) / d
            out.append((seq[i][0] + side * nx * (ROAD / 2 + 3), seq[i][1] + side * ny * (ROAD / 2 + 3)))
    return out, np.array(seq)
def nearest(p, os_): return min(math.hypot(p[0] - ox - 4, p[1] - oy - 4) for ox, oy in os_)
e1, _ = edges(w1); g1 = sorted(nearest(p, w1['OS']) for p in e1)
T1 = g1[int(len(g1) * 0.98)]                           # track 1's edges: 98 in 100 points are within this of an O's middle
e5, seq5 = edges(w)
def allowed(ox, oy):
    """may an O's tile stand here?  not on either road, not on the bridge, its walls, its wings or the tunnel mouths"""
    cx, cy = ox + 4, oy + 4
    if np.hypot(seq5[:, 0] - cx, seq5[:, 1] - cy).min() < ROAD / 2 - 1: return False          # on a road (as near as the O's now are)
    if x0 - 24 <= cx < x1 + 24 and u0 - 8 <= cy < r1 + 8: return False                            # the bridge, kerbs, ramp walls (+ a tile)
    if CONC[max(oy - 6, 0):oy + 14, max(ox - 6, 0):ox + 14].any(): return False                  # within 6 px of a wing, a ramp wall or a mouth
    return True
CONC = np.zeros((PH, PW), dtype=bool)
for (x, y) in gw | tw: CONC[y, x] = True
OS0 = list(w['OS']); OS = list(OS0); added = []
while True:
    cand = sorted(((nearest(p, OS), p) for p in e5), reverse=True)
    for d, p in cand:
        if d <= T1: cand = None; break
        q = (int(round((p[0] - 4) / 8)) * 8, int(round((p[1] - 4) / 8)) * 8)
        if allowed(*q) and all(math.hypot(q[0] - a, q[1] - b) >= 18 for a, b in OS): OS.append(q); added.append(q); break
    else: break
    if cand is None: break
g5a = sorted(nearest(p, OS0) for p in e5); g5b = sorted(nearest(p, OS) for p in e5)
free = [p for p in e5 if allowed(int(round((p[0] - 4) / 8)) * 8, int(round((p[1] - 4) / 8)) * 8)]
print('cereal O\'s: track 1 %d; track 5 as built %d, with the added ones %d (+%d)' % (len(w1['OS']), len(OS0), len(OS), len(added)))
print('widest gap where an O may stand: as built %.0f px, after %.0f px (track 1: %.0f px)' % (max(nearest(p, OS0) for p in free), max(nearest(p, OS) for p in free), g1[-1]))
assert all(allowed(*q) for q in added)

# ---------------------------------------------------------------- 1, 2. the bridge's pictures
def bridge(kerb, concrete, deck, os_):
    """(ink, wipe): the track's ink with the kerb drawn one way, and where the cloth's dots are wiped off"""
    ink = ink0.copy(); wipe = np.array(w['imask'], dtype=bool).copy()
    for ox, oy in os_:
        for j, r in enumerate(O_RING):
            for i, c in enumerate(r):
                if c == '#': ink[oy + j, ox + i] = True
    if concrete:
        for (x, y) in gw | tw: wipe[y, x] = True
    if deck: wipe[u0:r1, x0:x1] = True
    for xa in (x0 - 8, x1):
        k = ink[u0:r1, xa:xa + 8]
        if kerb == 'built': continue
        k[:] = False; wipe[u0:r1, xa:xa + 8] = True
        if kerb == 'K1': k[:] = True
        if kerb == 'K2':
            k[:, 0] = k[:, 7] = True; k[0] = k[-1] = True
            for j in range(0, r1 - u0, 16): k[j:j + 8] = True
        if kerb == 'K3':
            k[:] = True; k[1:-1, 3:5] = False
    return ink, wipe
def cost(ink, wipe):
    """the bridge's rows (30-53) as the game would hold them: tiles to draw, different pictures, masked tiles, masks, bytes, T a picture"""
    ent = 0; pics = set(); masks = set(); nm = 0; T = 0
    for ty in range(u0 // 8, r1 // 8):
        for tx in range((x0 - 56) // 8, (x1 + 56) // 8):
            sl = (slice(ty * 8, ty * 8 + 8), slice(tx * 8, tx * 8 + 8))
            t = np.packbits(ink[sl], axis=1).tobytes(); m = np.packbits(wipe[sl], axis=1).tobytes() if (wipe[sl] & cloth[sl] & ~ink[sl]).any() else bytes(8)    # (a mask only where it would hide a dot)
            if not any(t) and not any(m): continue
            ent += 1; pics.add((t, m))
            if any(m): masks.add(m); nm += 1; T += 1100
            else: T += 120 + 88 * sum(1 for b in t if b)
    return dict(entries=ent, pictures=len(pics), masked=nm, masks=len(masks), bytes=2 * ent + 8 * len(pics) + 9 * len(masks), T=int(T * 19 / 24))
OPTS = [('built', False, False, OS0), ('built', True, False, OS0), ('K1', True, False, OS), ('K2', True, False, OS), ('K3', True, False, OS), ('K2', True, True, OS)]
NAMES = ['as built', '1 concrete masked (kerb as built)', '1 + K1 solid bar', '1 + K2 blocks in a blue outline', '1 + K3 bar with a cyan stripe', '1 + K2 + the DECK wiped too']
C = [cost(*bridge(*o)) for o in OPTS]
PIC_T = 3500000 / 11.7                                 # a picture now, in T-states (11.7 pictures a second at the crossing)
print('ESTIMATES (not built): a plain tile 120 T + 88 T a line with ink; a masked tile 1,100 T; 19 of the bridge\'s 24 rows in view')
for n, c in zip(NAMES, C):
    dT = c['T'] - C[0]['T']
    print('  %-34s %3d tiles to draw, %2d pictures, %3d masked (%d masks): %4d bytes (%+4d), %6d T a picture (%+6d: about %.1f pictures a second)'
          % (n, c['entries'], c['pictures'], c['masked'], c['masks'], c['bytes'], c['bytes'] - C[0]['bytes'], c['T'], dT, 3500000 / (PIC_T + dT)))

# ---------------------------------------------------------------- the sheets
CYAN, BLUE, YEL, RED, BLACK = (0, 215, 215), (0, 0, 215), (215, 215, 0), (215, 0, 0), (0, 0, 0)
def font(n): return ImageFont.load_default(size=n)
def render(ink, wipe, box, s=4, ring=()):
    xa, ya, xb, yb = box
    bit = ink[ya:yb, xa:xb] | (cloth[ya:yb, xa:xb] & ~wipe[ya:yb, xa:xb])
    a = np.where(bit[..., None], np.array(BLUE, dtype=np.uint8), np.array(CYAN, dtype=np.uint8))
    im = Image.fromarray(a).resize(((xb - xa) * s, (yb - ya) * s), Image.NEAREST)
    d = ImageDraw.Draw(im)
    for ox, oy in ring: d.ellipse([(ox - xa - 3) * s, (oy - ya - 3) * s, (ox - xa + 11) * s, (oy - ya + 11) * s], outline=RED, width=3)
    return im
VIEW = (32, 258, 224, 410)                             # the window of Grant's screenshot: the left-hand tunnel mouth (192 x 152)
WHOLE = (96, 226, 280, 446)                            # the whole bridge, wings and all
pad = 24; S = 4
vw, vh = (VIEW[2] - VIEW[0]) * S, (VIEW[3] - VIEW[1]) * S; ww, wh = (WHOLE[2] - WHOLE[0]) * S, (WHOLE[3] - WHOLE[1]) * S
sheet = Image.new('RGB', (pad + 4 * (ww + pad), 70 + vh + 110 + wh + 150), YEL); d = ImageDraw.Draw(sheet)
d.text((pad, 14), 'TRACK 5 BRIDGE - fixes after Grant\'s drive (MOCK-UP, 4x, the game\'s pixels and colours; nothing here is in the game yet)', fill=BLACK, font=font(30))
rowA = [(0, 'BEFORE - as built (the view of your screenshot)', ['kerb: separate blocks, the cloth between them', 'wing and ramp wall: outlines, the cloth\'s dots inside', 'few cereal O\'s by the mouth'], False),
        (3, 'AFTER - concrete masked, kerb K2, O\'s added', ['the wing and wall are clean inside: solid concrete', 'the kerb is one wall with an edge down each side', 'added O\'s ringed in red here (the ring is not in the game)'], True),
        (5, 'AFTER, and the DECK wiped clean as well', ['the road on the bridge with no cloth dots either', 'costly: about %d more masked tiles in view' % (C[5]['masked'] - C[3]['masked']), '(see the estimates below)'], False)]
for i, (k, title, lines, rings) in enumerate(rowA):
    x = pad + i * (vw + pad); y = 60
    ink, wipe = bridge(*OPTS[k]); sheet.paste(render(ink, wipe, VIEW, ring=added if rings else ()), (x, y)); d.rectangle([x - 1, y - 1, x + vw, y + vh], outline=BLUE, width=2)
    d.text((x, y + vh + 6), title, fill=BLACK, font=font(24))
    for j, l in enumerate(lines): d.text((x, y + vh + 36 + 20 * j), l, fill=BLACK, font=font(17))
est = pad + 3 * (vw + pad)
d.text((est, 60), 'ESTIMATED COST (not built)', fill=BLACK, font=font(24))
for j, (n, c) in enumerate(zip(NAMES, C)):
    dT = c['T'] - C[0]['T']
    d.text((est, 100 + 62 * j), n, fill=BLACK, font=font(19))
    d.text((est, 124 + 62 * j), '  %d tiles drawn, %d masked; %+d bytes; %+d T a picture: %.1f pictures/s' % (c['entries'], c['masked'], c['bytes'] - C[0]['bytes'], dT, 3500000 / (PIC_T + dT)), fill=BLACK, font=font(16))
d.text((est, 100 + 62 * 6 + 10), 'Now: 11.7 pictures/s at the crossing,\n246 program bytes free.\nCereal O\'s: %d as built, %d with the\nadded ones (+%d), about 4 bytes each.' % (len(OS0), len(OS), len(added)), fill=BLACK, font=font(19))
rowB = [(0, 'BEFORE - as built', ['']), (2, 'K1  SOLID BAR', ['8 px of solid blue, ramp foot to ramp foot', 'the cheapest: plain tiles, nothing to wipe']),
        (3, 'K2  BLOCKS IN A BLUE OUTLINE', ['blue and cyan blocks, a blue line down both sides', 'the cyan blocks are clean paper']), (4, 'K3  BAR WITH A CYAN STRIPE', ['solid, a 2 px cyan line down its middle', ''])]
for i, (k, title, lines) in enumerate(rowB):
    x = pad + i * (ww + pad); y = 60 + vh + 110
    ink, wipe = bridge(*OPTS[k]); sheet.paste(render(ink, wipe, WHOLE), (x, y)); d.rectangle([x - 1, y - 1, x + ww, y + wh], outline=BLUE, width=2)
    d.text((x, y + wh + 6), title, fill=BLACK, font=font(24))
    for j, l in enumerate(lines): d.text((x, y + wh + 36 + 20 * j), l, fill=BLACK, font=font(17))
d.text((pad, sheet.size[1] - 56), 'The whole bridge. K1, K2 and K3 are shown with the concrete masked (wings and ramp walls clean inside) and the added O\'s. All cyan and blue only: no white cells.\n'
       'A mock-up drawn by tools/make_bridge_fix_mock.py from the real track 5 map. Classification: Internal.', fill=BLACK, font=font(17))
sheet.save(os.path.join(DEST, 'bridge_fix_mock.png'))
ink, wipe = bridge('K2', True, False, OS)
ov = render(ink, wipe, (0, 0, PW, PH), s=2, ring=added)
full = Image.new('RGB', (ov.size[0] + 2 * pad, ov.size[1] + 110), YEL); full.paste(ov, (pad, 60)); d = ImageDraw.Draw(full)
d.text((pad, 14), 'TRACK 5 - cereal O\'s: %d as built, %d with the %d added (ringed in red). MOCK-UP, 2x.' % (len(OS0), len(OS), len(added)), fill=BLACK, font=font(24))
d.text((pad, 66 + ov.size[1]), 'Added where a road edge had a gap wider than track 1 has, but never on a road, the bridge, a wing or a tunnel mouth.\nMade by tools/make_bridge_fix_mock.py. Classification: Internal.', fill=BLACK, font=font(15))
full.save(os.path.join(DEST, 'bridge_fix_overview.png'))
print('added at', added)
