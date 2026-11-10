"""Record what the game sends to the speaker (port 254) on the real ROM - the start
lights, accelerating, coasting, a skid, NOS fired and picked up, a crash - and write it
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
    marks = []
    def mark(name): marks.append((len(frames) / 50, name))
    mark('the lights: Q, red, red, red, green (beeps)'); go_green(sp)
    for i in CPUS: put(sp, i, 4 + 40 * i, SY + 58)       # the computer cars out of the way
    put(sp, 0, 190, SY - 8, 16)
    mark('accelerating (engine)'); hold(sp, ['Q'], 1.5)
    mark('coasting - no keys (quiet)'); sp.run(duration=1.0, fast_forward=True)
    put(sp, 0, 190, SY - 8, 16); mark('accelerating again'); press(sp, 'Q', True); sp.run(duration=1.0, fast_forward=True)
    mark('turning at speed (skid hiss + engine)'); press(sp, 'P', True); sp.run(duration=0.6, fast_forward=True); press(sp, 'P', False)
    press(sp, 'Q', False); mark('coasting'); sp.run(duration=0.8, fast_forward=True)
    put(sp, 0, 190, SY - 8, 16)
    mark('NOS fired (rush)'); press(sp, 'SPACE', True); sp.run(duration=0.1, fast_forward=True); press(sp, 'SPACE', False)
    sp.run(duration=1.0, fast_forward=True)
    mark('NOS picked up (chirp)'); put(sp, 0, SYM['nos_a_x'] - 8, SYM['nos_a_y'] - 8, 16); sp.run(duration=0.8, fast_forward=True)
    put(sp, 0, 190, SY - 8, 16); put(sp, 2, 230, SY - 8, 16)
    mark('driving into a car (crash)'); hold(sp, ['Q'], 1.2)
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
print('frames', len(frames), 'seconds', len(a) / RATE)
for k, (t0, name) in enumerate(marks):                 # speaker flips a second in each part
    t1 = marks[k + 1][0] if k + 1 < len(marks) else len(frames) / 50
    n = sum(int(((w & 0xff) == 0xfe).sum()) for w in frames[int(t0 * 50):int(t1 * 50)])
    print('%5.1f s  %-45s %5d flips a second' % (t0, name, n / max(t1 - t0, 0.02)))
