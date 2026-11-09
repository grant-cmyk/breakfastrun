"""Headless drive test on the REAL 48K ROM (zx package).
Loads build/racer.tap through the real loader, holds keys, screenshots,
and checks the car moved, turned, and goes slower on grass."""
import sys, os
import numpy as np
from PIL import Image
from zx._spectrum import Spectrum
import zx._spectrum as zs
HERE = os.path.dirname(os.path.abspath(__file__))
TAP = os.path.join(HERE, '..', 'build', 'racer.tap')
OUT = os.path.join(HERE, '..', 'build')
SYM = {}
for line in open(os.path.join(OUT, 'racer.sym')):
    p = line.split()
    if len(p) >= 3 and p[1] == 'EQU':
        SYM[p[0].lower()] = int(p[2].rstrip('H'), 16)

def hold(sp, keys, secs):
    for k in keys: sp.devices.notify(zs.KeyStroke(zs.KEYS[k].ID, pressed=True))
    sp.run(duration=secs, fast_forward=True)
    for k in keys: sp.devices.notify(zs.KeyStroke(zs.KEYS[k].ID, pressed=False))

def state(sp):
    r16 = lambda a: sp.read16(a)
    s = lambda v: v - 65536 if v > 32767 else v
    return dict(x=r16(SYM['xpos']) / 256, y=r16(SYM['ypos']) / 256,
                vx=s(r16(SYM['vx'])) / 256, vy=s(r16(SYM['vy'])) / 256,
                angle=sp.read8(SYM['angle']))

def shot(sp, name):
    sp.render_screen()
    px = np.array(sp.get_frame_pixels(), dtype=np.uint8)
    n = px.size // 4
    w = 352
    h = n // w
    img = px.reshape(h, w, 4)[:, :, [2, 1, 0]]
    Image.fromarray(img).resize((w * 2, h * 2), Image.NEAREST).save(os.path.join(OUT, name))

fails = 0
def check(ok, msg):
    global fails
    print(('PASS ' if ok else 'FAIL ') + msg)
    fails += not ok

with Spectrum(headless=True) as sp:
    sp.load_tape(TAP)
    sp.run(duration=40, fast_forward=True)
    s0 = state(sp); print('start', s0)
    check(s0['x'] == 100 and s0['y'] == 148 and s0['angle'] == 16, 'car starts on the bottom straight facing right')
    shot(sp, 'shot1_start.png')

    hold(sp, ['Q'], 1.0)
    s1 = state(sp); print('after 1s of Q', s1)
    check(s1['x'] > s0['x'] + 30 and abs(s1['y'] - s0['y']) < 2, 'Q accelerates the car to the right')
    check(1.4 < s1['vx'] <= 1.8, 'top speed on road about 1.75 px/frame (got %.2f)' % s1['vx'])

    hold(sp, ['Q', 'O'], 0.2)      # ~10 frames of left steer while accelerating
    s2 = state(sp); print('after Q+O', s2)
    check(0 < s2['angle'] < 16, 'O steers left (angle went down)')
    check(s2['vy'] < 0, 'car now heading up the screen')
    shot(sp, 'shot2_turning.png')

    hold(sp, ['Q'], 1.5)
    s3 = state(sp); print('driving on', s3)
    shot(sp, 'shot3_onward.png')

    # coast to a stop: friction must bring speed to exactly zero
    sp.run(duration=2.0, fast_forward=True)
    s4 = state(sp); print('coasted', s4)
    check(s4['vx'] == 0 and s4['vy'] == 0, 'car coasts to a complete stop')

    # grass test: teleport car onto grass (centre of the infield), accelerate
    sp.write(SYM['xpos'], bytes([0, 120, 0, 90]))   # xpos=120.0, ypos=90.0
    sp.write(SYM['angle'], bytes([16]))
    hold(sp, ['Q'], 0.5)
    s5 = state(sp); print('on grass', s5)
    check(0.6 < s5['vx'] < 0.8, 'grass top speed about 0.75 px/frame (got %.2f)' % s5['vx'])
    shot(sp, 'shot4_grass.png')

    # walls: drive into the left edge with reverse
    sp.write(SYM['xpos'], bytes([0, 4, 0, 150]))
    hold(sp, ['A'], 1.0)
    s6 = state(sp); print('reversed into left wall', s6)
    check(s6['x'] == 0 and s6['vx'] == 0, 'left screen edge stops the car')

    attrs = sp.read(0x5800, 768)
    check(attrs[0] == 0x20 and attrs[19 * 32 + 10] == 0x38, 'track colours in attribute memory')

print('RESULT:', 'PASS' if fails == 0 else '%d FAIL' % fails)
sys.exit(1 if fails else 0)
