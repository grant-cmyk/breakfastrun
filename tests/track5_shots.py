"""Pictures of track 5's BRIDGE, for looking at (not a test): docs/design/tracks/built/
    track5_ramp_up.png      your car on the ramp up
    track5_deck.png         your car on the deck, a computer car on it too, one half out of the tunnel
    track5_under.png        your car on the lower road wholly under the deck (not to be seen)
    track5_half_under.png   ... and half out of the tunnel mouth
    track5_ramp_down.png    your car on the ramp down
    track5_cross.gif        your car driven over the deck while a computer car passes under it
Run:  python3 tests/track5_shots.py   (after TRACK=5 bash build.sh). The grid, the lap, the mini-map and the
cars' lines come from  TRACK=5 python3 tests/track_shots.py."""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'track5_test.py')).read()
src = src[:src.index('# ---- LEVELS')]
exec(src.replace("os.path.dirname(os.path.abspath(__file__))", repr(HERE)))
DEST = os.path.join(ROOT_, 'docs', 'design', 'tracks', 'built'); os.makedirs(DEST, exist_ok=True)
OUT = DEST                                              # (shot() saves there)
def frame(sp):
    sp.render_screen()
    px = np.array(sp.get_frame_pixels(), dtype=np.uint8).reshape(-1, 352, 4)[:, :, [2, 1, 0]]
    return Image.fromarray(px).crop((40, 40, 312, 248))
sp = fresh(); sp.run(duration=6.0, fast_forward=True)   # (the crew chief's first words are over)
place(sp, 0, XC - 8, BR['Y0'] + 14, 32, 1); sp.run(duration=2.0, fast_forward=True); shot(sp, 'track5_ramp_up.png')
place(sp, 0, XC - 8, BR['Y3'] - 30, 32, 1); sp.run(duration=2.0, fast_forward=True); shot(sp, 'track5_ramp_down.png')
place(sp, 0, XC - 16, YC - 30, 32, 1); place(sp, 1, XC + 4, YC + 6, 32, 1); place(sp, 2, BR['H0'] - 9, YC - 12, 48, 0); place(sp, 3, XC, YC - 8, 48, 0)
sp.run(duration=2.0, fast_forward=True); shot(sp, 'track5_deck.png')
park_cpus(sp); [setl(sp, n, 0) for n in CPUS]
place(sp, 0, XC - 8, YC - 8, 48, 0); sp.run(duration=2.0, fast_forward=True); shot(sp, 'track5_under.png')
place(sp, 0, BR['H0'] - 8, YC - 8, 48, 0); sp.run(duration=2.0, fast_forward=True); shot(sp, 'track5_half_under.png')
# the view of Grant's own picture (16 Nov 2026: the left-hand tunnel mouth), from the game, 4x, beside his picture
place(sp, 0, 120, 326, 48, 0); sp.run(duration=3.0, fast_forward=True); at_copy_done(sp)
print('fix view: camera at', g(sp, 'camx'), g(sp, 'camy'), '(his picture: 32, 258)')
bits = screen_bits(sp)[WY:WY + WH, 8:8 + WW]
game = Image.fromarray(np.where(bits[..., None].astype(bool), np.array((0, 0, 215), dtype=np.uint8), np.array((0, 215, 215), dtype=np.uint8))).resize((WW * 4, WH * 4), Image.NEAREST)
his = os.path.join(ROOT_, 'docs', 'design', 'tracks', 'grant_bridge_picture.png')
sheet = Image.new('RGB', (WW * 8 + 72, WH * 4 + 90), (215, 215, 0)); sheet.paste(game, (24, 50))
from PIL import ImageDraw, ImageFont
dr = ImageDraw.Draw(sheet); f_ = ImageFont.load_default(size=22)
dr.text((24, 14), 'FROM THE GAME (track 5 tape, 4x; your car is the one in the middle)', fill=(0, 0, 0), font=f_)
if os.path.exists(his):
    sheet.paste(Image.open(his).convert('RGB').resize((WW * 4, WH * 4), Image.NEAREST), (48 + WW * 4, 50)); dr.text((48 + WW * 4, 14), 'GRANT\'S PICTURE', fill=(0, 0, 0), font=f_)
dr.text((24, WH * 4 + 58), 'The same view: the left-hand tunnel mouth. Classification: Internal.', fill=(0, 0, 0), font=ImageFont.load_default(size=16))
sheet.save(os.path.join(DEST, 'track5_fix_view.png'))
# the whole bridge, from two pictures of the game (the window is 152 lines, the bridge 192): your car on the deck near each end
whole = Image.new('RGB', (WW * 4, 244 * 4), (0, 215, 215))
for yy in (BR['Y0'] + 8, YC - 10, BR['Y3'] - 28):
    place(sp, 0, XC - 8, yy, 32, 1); sp.run(duration=3.0, fast_forward=True); at_copy_done(sp)
    b_ = screen_bits(sp)[WY:WY + WH, 8:8 + WW]; cy_ = g(sp, 'camy'); b_ = b_[20:WH - 44] if yy < YC else b_[20:WH - 44]
    im_ = Image.fromarray(np.where(b_[..., None].astype(bool), np.array((0, 0, 215), dtype=np.uint8), np.array((0, 215, 215), dtype=np.uint8))).resize((WW * 4, b_.shape[0] * 4), Image.NEAREST)
    whole.paste(im_, (0, (cy_ + 20 - (BR['Y0'] - 40)) * 4))
whole.save(os.path.join(DEST, 'track5_whole_bridge.png'))
# the GIF: you from above the ramp up, flat out down the screen; FRANK and JANE along the lower road, under you
place(sp, 0, XC - 8, BR['Y0'] - 50, 32, 0)
for n, x in ((1, XC + 150), (4, XC + 215)):
    place(sp, n, x, YC - 8 + (6 if n == 1 else -10), 48, 0)
    sp.write(CARS + n * CS + 13, bytes([min(range(NWP), key=lambda k: math.dist(WPS[k], (XC - 60, YC)))])); sp.write(CARS + n * CS + C_PACE, bytes([15]))
frames = []; press(sp, 'Q', True); t = 0.0; seen = []
while t < 4.6:
    sp.run(duration=0.08, fast_forward=True); t += 0.08
    c = car(sp, 0); e = (heading(c['x'] + 8, c['y'] + 8, XC, c['y'] + 80) - c['ang'] + 32) % 64 - 32
    press(sp, 'P', e > 1); press(sp, 'O', e < -1)
    frames.append(frame(sp)); seen.append((round(t, 2), c['x'], c['y'], lvl(sp, 0), [(car(sp, n)['x'], lvl(sp, n)) for n in (1, 4)]))
for k in 'QOP': press(sp, k, False)
frames[0].save(os.path.join(DEST, 'track5_cross.gif'), save_all=True, append_images=frames[1:], duration=80, loop=0)
for s in seen[::6]: print(s)
print('bumps', g(sp, 'bumps'))
sp.__exit__(None, None, None)
print('saved in', DEST)
