"""THE RACE-TRACK TRIAL'S FIXED BOXES (17 Nov 2026): the mini-map, the place plate and the mug are sent to the screen only
when they have changed (src/racetrack.asm, rt_hud). This checks that what the SCREEN shows is still right at every
picture: a drive in the pack from before the lights, stopped each time a picture has just gone up (copy_done), and the
screen's squares for each box compared, to the pixel and the colour, with what the game holds for it at that moment -
the map with its dots (MAPDAT), the plate as composed (pl_bmp: place, lap, lap time), the mug (dmg_bmp).
Usage: python3 tests/rt_fixed_test.py [tape name] [build folder]     FRAMES=3000 (how long is driven)"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rt_lib import Game, ROOT
name = sys.argv[1] if len(sys.argv) > 1 else 'racer_racetrack_noline'
folder = sys.argv[2] if len(sys.argv) > 2 else name.replace('racer_', '')
FRAMES = int(os.environ.get('FRAMES', '3000'))
g = Game(name, os.path.join(ROOT, 'build', folder, 'src')); S = g.sym
BUF = S['buf']
def where(baddr):
    """a back-buffer address -> (screen line 0-191, screen byte column): the buffer is laid out like the screen, one byte right"""
    o = baddr - BUF
    return (o >> 11) * 64 + ((o >> 5) & 7) * 8 + ((o >> 8) & 7), (o & 31) - 1
def box(scr, y0, x0, lines, wide):
    out = []
    for y in range(y0, y0 + lines):
        a = ((y >> 6) << 11) | ((y & 7) << 8) | (((y >> 3) & 7) << 5)
        out.append(bytes(scr[a + x0:a + x0 + wide]))
    return out
def attrs(scr, y0, x0, rows, wide): return [bytes(scr[6144 + (y0 // 8 + r) * 32 + x0:][:wide]) for r in range(rows)]
MAP_H = S['map_h']; my, mx = where(S['map_buf']); py, px = where(S['pl_b']); dy, dx = where(S['dmg_b'])
PL_W, PL_H, DMG_ROWS = S['pl_w'], S['pl_h'], S['dmg_rows']
bad = {}; seen = {'map': 0, 'plate': 0, 'mug': 0}; changes = {'map': 0, 'plate': 0, 'mug': 0}; last = {}
def check():
    scr = g.mem(0x4000, 6912)
    md = g.mem(S['mapdat'], MAP_H * 3)
    y0 = my & ~7                                                          # the map's 3 x 3 squares, from the top of its first row of squares
    want = [bytes(3)] * (my - y0) + [md[i * 3:i * 3 + 3] for i in range(MAP_H)]
    want += [bytes(3)] * (24 - len(want))
    got = {'map': (box(scr, y0, mx, 24, 3), attrs(scr, y0, mx, 3, 3))}
    exp = {'map': (want, [b'\x07' * 3] * 3)}
    dm = g.mem(S['dmg_bmp'], DMG_ROWS * 3)
    got['mug'] = (box(scr, dy, dx, DMG_ROWS, 3), attrs(scr, dy, dx, 2, 3))
    exp['mug'] = ([dm[i * 3:i * 3 + 3] for i in range(DMG_ROWS)], [b'\x03' * 3] * 2)
    if g.mem(S['lt_on'], 1)[0] == 0:                                      # (the start lights hang where the plate is)
        pb = g.mem(S['pl_bmp'], PL_W * PL_H)
        y0 = py & ~7
        want = [bytes(PL_W)] * (py - y0) + [pb[i * PL_W:(i + 1) * PL_W] for i in range(PL_H)]
        want += [bytes(PL_W)] * (24 - len(want))
        got['plate'] = (box(scr, y0, px, 24, PL_W), attrs(scr, y0, px, 3, PL_W))
        exp['plate'] = (want, [b'\x07' * PL_W] * 3)
    for k in got:
        seen[k] += 1
        if got[k] != exp[k]: bad.setdefault(k, []).append(g.w16(S['renders']))
        if last.get(k) != exp[k]: changes[k] += 1; last[k] = exp[k]
g.to_grid(); g.key('Q', True); g.wp = g.mem(S['cars'], 14)[13]
for f in range(FRAMES):
    if g.mem(S['race_on'], 1)[0]: g.steer()
    g.rpc('run', until_pc=S['copy_done'], max_frames=1)
    if g.rpc('regs')['pc'] == S['copy_done']:
        check(); g.rpc('step', n=1)
g.close() if hasattr(g, 'close') else None
ok = True
for k in ('map', 'plate', 'mug'):
    good = k not in bad and seen[k] > 100 and changes[k] > 3
    ok &= good
    print('%s  the %s on the screen is what the game holds for it at every picture: %d pictures looked at, it changed %d times%s' % (
        'PASS' if good else 'FAIL', k, seen[k], changes[k], '' if k not in bad else '; WRONG in %d, first at picture %d' % (len(bad[k]), bad[k][0])))
print('%d passed, %d failed' % (sum(1 for k in seen if k not in bad), len(bad)) if ok or bad else 'too few pictures or changes to judge')
sys.exit(0 if ok else 1)
