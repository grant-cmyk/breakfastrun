"""Record what the game sends to the speaker (port 254) on the real ROM - the
lights, a run off the start, the start straight flat out, a crash - and write it
to docs/design/engine_sound.wav, so the sound can be heard without loading the tape."""
import os, sys, wave, numpy as np
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tests')
src = open(os.path.join(HERE, 'drive_test.py')).read()
src = src[:src.index('with Racer(headless=True)')].replace("os.path.dirname(os.path.abspath(__file__))", repr(HERE))
exec(src)
from zx._device import EndOfFrame
frames = []; rec = [False]
with Racer(headless=True) as sp:
    orig = sp.devices.notify
    def notify(e, *a, **k):
        if rec[0] and isinstance(e, EndOfFrame): frames.append(np.array(e.port_writes))
        return orig(e, *a, **k)
    sp.devices.notify = notify
    sp.load_tape(TAP); t = 0
    while g(sp, 'renders') == 0 and t < 60: sp.run(duration=0.1, fast_forward=True); t += 0.1
    rec[0] = True
    hold(sp, ['Q'], 9.0)          # the lights, then away (as a player would)
    for i in CPUS: put(sp, i, 20 + 25 * i, 420)
    put(sp, 0, 175, 344, 16)      # the start straight, flat out
    hold(sp, ['Q'], 3.0)
    put(sp, 2, car(sp, 0)['x'] + 30, car(sp, 0)['y'])   # a car in the way: a crash
    hold(sp, ['Q'], 2.0)
RATE = 44100; FT = 69888; level = 0; out = []
for w in frames:
    w = w[(w & 0xff) == 0xfe]
    lv = ((w >> 20) & 1).astype(int); tk = (w >> 32).astype(int)
    n = RATE // 50; buf = np.empty(n); pos = 0
    for l, t in zip(lv, tk):
        s = min(n, int(t * n / FT)); buf[pos:s] = level; pos = s; level = l
    buf[pos:] = level; out.append(buf)
a = np.concatenate(out); a = a - np.convolve(a, np.ones(441) / 441, 'same')   # no DC, as a speaker
a = (a / max(1e-9, np.abs(a).max()) * 0.6 * 32767).astype(np.int16)
p = os.path.join(HERE, '..', 'docs', 'design', 'engine_sound.wav')
with wave.open(p, 'wb') as f:
    f.setnchannels(1); f.setsampwidth(2); f.setframerate(RATE); f.writeframes(a.tobytes())
print('frames', len(frames), 'seconds', len(a) / RATE, 'flips', int(sum(((w & 0xff) == 0xfe).sum() for w in frames)))
