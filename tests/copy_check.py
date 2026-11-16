"""The screen copy against the back buffer, byte for byte, at copy_done, over N pictures of a race
(the window's 152 lines x 24 bytes: buffer line 8 + y, bytes 2-25 -> screen line 8 + y, columns 1-24).
Usage: ZTAP=tape ZSYM=sym python3 tests/copy_check.py     (PICS=n, default 40; TKEY: the title key)"""
import os, sys
from zx._spectrum import Spectrum
import zx._spectrum as zs
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
TAP = os.environ.get('ZTAP', os.path.join(ROOT, 'build', 'racer.tap'))
SYMF = os.environ.get('ZSYM', os.path.join(ROOT, 'build', 'racer.sym'))
SYM = {}
for line in open(SYMF):
    p = line.split()
    if len(p) >= 3 and p[1] == 'EQU': SYM[p[0].lower()] = int(p[2].rstrip('H'), 16)
def press(sp, k, down): sp.devices.notify(zs.KeyStroke(zs.KEYS[k].ID, pressed=down))
class R(Spectrum):
    armed = False
    def on_breakpoint(self):
        if self.armed and self.pc == SYM['copy_done']:
            self.armed = False; raise zs.EmulatorException('copy_done')
def addr(base, y, x): return base | ((y & 0xC0) << 5) | ((y & 7) << 8) | ((y & 0x38) << 2) | x
with R(headless=True) as sp:
    sp.load_tape(TAP); t = 0
    while sp.read8(0x5800 + 8 * 32 + 10) != 0x7A and t < 60: sp.run(duration=0.1, fast_forward=True); t += 0.1
    sp.run(duration=0.5, fast_forward=True); sp.write(SYM['jin_on'], bytes([0xFF]))
    k = os.environ.get('TKEY', '1')
    press(sp, k, True); sp.run(duration=0.2, fast_forward=True); press(sp, k, False)
    if 'ch_np' in SYM:                                  # (the tape with the choose screen: accelerate through its four steps)
        for _ in range(4): sp.run(duration=0.3, fast_forward=True); press(sp, 'Q', True); sp.run(duration=0.15, fast_forward=True); press(sp, 'Q', False)
    sp.run(duration=3.0, fast_forward=True)
    press(sp, 'Q', True); press(sp, 'P', True)
    bad = 0; rows = 0; where = set(); N = int(os.environ.get('PICS', '40'))
    sp.set_breakpoint(SYM['copy_done'])
    for n in range(N):
        sp.armed = True
        try:
            for _ in range(60): sp.run(duration=0.02, fast_forward=True)
        except zs.EmulatorException: pass
        for y in range(SYM['win_h']):
            b = bytes(sp.read(addr(0xC000, 8 + y, 2), 24)); s = bytes(sp.read(addr(0x4000, 8 + y, 1), 24)); rows += 1
            if b != s:
                bad += 1; where.update((y, i) for i in range(24) if b[i] != s[i])
        sp.run(duration=0.001, fast_forward=True)
    print('%s the screen copy matches the back buffer: %d lines compared over %d pictures, %d differ%s' % ('PASS' if bad == 0 else 'FAIL', rows, N, bad,
          '' if not bad else ' - lines %s, bytes %s' % (sorted({y for y, _ in where})[:20], sorted({i for _, i in where}))))
    sys.exit(1 if bad else 0)
