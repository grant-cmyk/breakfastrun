"""The 'latent fault' of 16 Nov 2026, shown to be the TEST's own race (docs/design/OPTIMISATION-PLAN.md, 5).
drive_test.py's ramming check wrote the cars' places (put) wherever the emulator happened to stop. If that
is inside the game's own move of that car (physics has read the place and not yet written it back) the game
writes the OLD place over the test's: the computer car is back at its parked spot, 66 px down (SY+58 against
SY-8). This probe stops at many moments, writes the place and looks one TV frame later; it names the code
the emulator was in each time the write was lost.   python3 tests/put_race_probe.py   (TRIALS=n)"""
import sys, os, re, bisect
from zx._spectrum import Spectrum
import zx._spectrum as zs
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
TAP = os.environ.get('ZTAP', os.path.join(ROOT, 'build', 'racer.tap'))
SYMF = os.environ.get('ZSYM', os.path.join(ROOT, 'build', 'racer.sym'))
SYM = {}
for line in open(SYMF):
    p = line.split()
    if len(p) >= 3 and p[1] == 'EQU': SYM[p[0].lower()] = int(p[2].rstrip('H'), 16)
LAB = sorted((v, k) for k, v in SYM.items() if 0x5F00 <= v < 0xD100)
def where(pc):
    i = bisect.bisect_right(LAB, (pc, '~')) - 1
    return '%s+%d' % (LAB[i][1], pc - LAB[i][0])
CS = SYM['c_size']; CARS = SYM['cars']
src = open(os.path.join(ROOT, 'src', 'world.asm')).read()
SY = int(re.search(r'TRACK_SY\s+equ\s+(\d+)', src).group(1))
def press(sp, k, down): sp.devices.notify(zs.KeyStroke(zs.KEYS[k].ID, pressed=down))
def put(sp, n, x, y, ang=None):
    b = CARS + n * CS
    sp.write(b + 1, bytes([x & 255, x >> 8])); sp.write(b + 4, bytes([y & 255, y >> 8])); sp.write(b + 6, bytes(4))
    if ang is not None: sp.write(b + 10, bytes([ang]))
TRIALS = int(os.environ.get('TRIALS', '400'))
with Spectrum(headless=True) as sp:
    sp.load_tape(TAP); t = 0
    while sp.read8(0x5800 + 8 * 32 + 10) != 0x7A and t < 60: sp.run(duration=0.1, fast_forward=True); t += 0.1
    sp.run(duration=0.5, fast_forward=True); sp.write(SYM['jin_on'], bytes([0xFF]))
    press(sp, '1', True); sp.run(duration=0.2, fast_forward=True); press(sp, '1', False)
    sp.run(duration=3.5, fast_forward=True)
    press(sp, 'Q', True); t = 0
    while sp.read8(SYM['race_on']) == 0 and t < 6: sp.run(duration=0.02, fast_forward=True); t += 0.02
    press(sp, 'Q', False); sp.run(duration=1.0, fast_forward=True)
    # 1. the proof: stop INSIDE physics's move of car 1 (ph_yp+10: A holds the old y, not yet stored), write, look
    hit = {'on': True}
    def bp():
        if hit['on'] and sp.pc == SYM['ph_yp'] + 10 and sp.ix == CARS + CS:
            hit['on'] = False; raise zs.EmulatorException('in the move')
    sp.on_breakpoint = bp
    for i in range(1, 5): put(sp, i, 4 + 40 * i, SY + 58)
    sp.run(duration=0.2, fast_forward=True)
    sp.set_breakpoint(SYM['ph_yp'] + 10)
    try:
        for _ in range(50): sp.run(duration=0.02, fast_forward=True)
    except zs.EmulatorException: pass
    print('stopped at %s, IX = car 1: %s' % (where(sp.pc), sp.ix == CARS + CS))
    put(sp, 1, 230, SY - 8, 16)
    sp.run(duration=0.02, fast_forward=True)
    y = sp.read16(CARS + CS + 4); x = sp.read16(CARS + CS + 1)
    print('written (230, %d); one TV frame later the car is at (%d, %d): y is %d px off - %s' % (SY - 8, x, y, y - (SY - 8),
          "THE WRITE WAS LOST (the test's race, not the game)" if abs(y - (SY - 8)) > 20 else 'kept'))
    # 2. how often a blind write lands there
    lost = {}; stops = {}
    for k in range(TRIALS):
        for i in range(1, 5): put(sp, i, 4 + 40 * i, SY + 58)        # parked apart, as the test does
        sp.run(duration=0.0201 + 0.00137 * (k % 29), fast_forward=True)   # stop somewhere else each time
        pc = sp.pc
        put(sp, 0, 200, SY - 8, 16); put(sp, 1, 230, SY - 8, 16)
        sp.write(CARS + CS + 16, bytes([60, 2]))
        sp.run(duration=0.02, fast_forward=True)
        y = sp.read16(CARS + CS + 4)
        stops[where(pc).split('+')[0]] = stops.get(where(pc).split('+')[0], 0) + 1
        if abs(y - (SY - 8)) > 20:
            lost.setdefault(where(pc), []).append(y - (SY - 8))
    n = sum(len(v) for v in lost.values())
    print('%d of %d writes of the car\'s place were lost (the car back near its old place):' % (n, TRIALS))
    for w, v in sorted(lost.items()): print('  stopped in %-22s x %d  (y off by %s)' % (w, len(v), sorted(set(v))))
    print('where the emulator stopped, most often:', sorted(stops.items(), key=lambda kv: -kv[1])[:8])
