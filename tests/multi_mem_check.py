"""The tape with several tracks: after T at the title picks track n, is memory what that track's OWN build has?
Loads build/racer_2tracks.tap, presses T, reads the memory; loads the track's own padded build (build/multi/pad_t<n>.tap,
the same program at the same addresses), reads its memory at its title; compares every byte outside the screen, the
back buffer's window, the stack and the packed tracks themselves. Bytes that differ between two looks at the same
build are variables and are not counted.     Usage: python3 tests/multi_mem_check.py [tape name]"""
import os, sys, json
from zx._spectrum import Spectrum
import zx._spectrum as zs
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); M = os.path.join(ROOT, 'build', 'multi')
NAME = sys.argv[1] if len(sys.argv) > 1 else 'racer_2tracks'
info = json.load(open(os.path.join(M, 'multi.json')))
SYM = {}
for line in open(os.path.join(ROOT, 'build', NAME + '.sym')):
    p = line.split()
    if len(p) >= 3 and p[1] == 'EQU': SYM[p[0].lower()] = int(p[2].rstrip('H'), 16)
def press(sp, k, down): sp.devices.notify(zs.KeyStroke(zs.KEYS[k].ID, pressed=down))
def looks(tap, tsel):
    out = []
    with Spectrum(headless=True) as sp:
        sp.load_tape(tap); n = 0
        while sp.read8(0x5800 + 8 * 32 + 10) != 0x7A and n < 600: sp.run(duration=0.1, fast_forward=True); n += 1
        sp.run(duration=1.0, fast_forward=True)
        for _ in range(tsel):
            press(sp, 'T', True); sp.run(duration=0.3, fast_forward=True); press(sp, 'T', False); sp.run(duration=0.5, fast_forward=True)
        for w in (0.5, 2.3):
            sp.run(duration=w, fast_forward=True); out.append(bytes(sp.read(0, 65536)))
        text = ''.join(chr(c) if 32 <= c < 127 else '?' for c in [next((32 + k for k in range(96) if bytes(sp.read(0x3D00 + 8 * k, 8)) == bytes(sp.read8(0x4000 | ((14 & 0x18) << 8) | ((14 & 7) << 5) | col | (r << 8)) for r in range(8))), 63) for col in range(6, 26)])
    return out, text
AREAS = [(0x5B00, 0x5E00), (0x5F00, SYM['lp_src']), (SYM['topmem'], SYM['code_end'])] + [(0xD0A0 + 256 * k, 0xD0FA + 256 * k) for k in range(8)] + [(0xE800, SYM['hp']), (SYM['himem'], 0xFFF4)]
fails = 0
for i, t in enumerate(info['tracks']):
    (a1, a2), text = looks(os.path.join(ROOT, 'build', NAME + '.tap'), i if i else len(info['tracks']))    # (the first track: all the way round and back to it)
    (b1, b2), _ = looks(os.path.join(M, 'pad_t%d.tap' % t), 0)
    var = lambda x: a1[x] != a2[x] or b1[x] != b2[x]
    diff = [x for lo, hi in AREAS for x in range(lo, hi) if a1[x] != b1[x] and not var(x)]
    nvar = sum(1 for lo, hi in AREAS for x in range(lo, hi) if var(x))
    # known, harmless: the hook's own CALL (HP's stand-in in the single build), the track number, the title's message line
    known = [x for x in diff if SYM['mapdat'] + 3 * 17 <= x < SYM['mapdat'] + 90]      # (the mini-map's strip past a shorter map's last line: start-up leftovers)
    scratch = [x for x in diff if 0xD2C0 <= x < 0xD2FA or x == SYM['pa_last']]                                # (cloth_pat, PNUM and print_at's own byte: the track's name was printed)
    diff = [x for x in diff if x not in known and x not in scratch]
    import bisect
    lab = sorted((v, k) for k, v in SYM.items() if 0x5B00 <= v <= 0xFFFF)
    near = lambda a: '%s+%d' % (lab[bisect.bisect_right(lab, (a, '~')) - 1][1], a - lab[bisect.bisect_right(lab, (a, '~')) - 1][0])
    ok = not diff
    fails += not ok
    print('%s track %d chosen with T (%d presses; the title says %r): %d bytes compared with its own build, %d differ%s (%d variables and %d leftover bytes of the mini-map strip not counted)'
          % ('PASS' if ok else 'FAIL', t, i if i else len(info['tracks']), text.strip(), sum(hi - lo for lo, hi in AREAS), len(diff), '' if ok else ' at ' + ' '.join('%04X(%s)' % (x, near(x)) for x in diff[:16]), nvar, len(known)))
print('RESULT: %s' % ('PASS' if not fails else '%d FAIL' % fails))
