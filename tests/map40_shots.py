"""The 40-wide mini-map on each track, as the game shows it (Grant, 16 Nov 2026, of the widths mocked up: "C wide
please"): real screens of the four MAPW40=1 tapes a moment after the green light, 3 x, side by side - so that the
tall ones (track 3's is 44 lines of the window's 152) can be seen against the rest of the window. On the REAL
48K ROM (zx package), with tests/drive_test.py's helpers.
Run:  python3 tests/map40_shots.py     after  MAPW40=1 TILE1=1 FLIP=1 TOWER=1 TRACK=n bash build.sh  for n = 1 2 3 5
Writes docs/design/arrows/map40_tracks.png."""
import os, sys, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT_ = os.path.join(HERE, '..'); BLD = os.path.join(ROOT_, 'build')
NAMES = {'1': 'track 1', '2': 'track 2', '3': 'track 3 (the tall one)', '5': 'track 5 (the bridge)'}
if len(sys.argv) > 1:                                   # one track: its screen, to build/map40_tN.png
    T = sys.argv[1]; tape = 'racer_map40' + ('' if T == '1' else '_track' + T); TSRC = os.path.join(BLD, 'map40_t' + T, 'src')
    os.environ.update(ZTAP=os.path.join(BLD, tape + '.tap'), ZSYM=os.path.join(BLD, tape + '.sym'), ZMAP=os.path.join(TSRC, 'minimap.asm'))
    src = open(os.path.join(HERE, 'drive_test.py')).read()
    src = src[:src.index('with Racer(headless=True)')].replace("os.path.dirname(os.path.abspath(__file__))", repr(HERE))
    src = src.replace("os.path.join(ROOT, 'src',", "os.path.join(%r," % TSRC)
    exec(src)
    sp = Racer(headless=True); sp.__enter__(); sp.load_tape(TAP); t = 0
    while g(sp, 'renders') == 0 and t < 60: sp.run(duration=0.1, fast_forward=True); t += 0.1
    go_green(sp); sp.run(duration=1.2, fast_forward=True)
    for _ in range(8):                                  # (a picture with your dot shown: it blinks)
        at_copy_done(sp)
        if minimap_diff(sp)[1][0] is not None: break
    bits = screen_bits(sp).astype(bool); at = np.frombuffer(bytes(sp.read(0x5800, 768)), dtype=np.uint8).reshape(24, 32)
    PAL = np.array([(0, 0, 0), (0, 0, 215), (215, 0, 0), (215, 0, 215), (0, 215, 0), (0, 215, 215), (215, 215, 0), (215, 215, 215),
                    (0, 0, 0), (0, 0, 255), (255, 0, 0), (255, 0, 255), (0, 255, 0), (0, 255, 255), (255, 255, 0), (255, 255, 255)], dtype=np.uint8)
    a = np.kron(at, np.ones((8, 8), dtype=np.uint8)); br = (a >> 3) & 8
    rgb = np.where(bits[..., None], PAL[(a & 7) | br], PAL[((a >> 3) & 7) | br])
    Image.fromarray(rgb.astype(np.uint8)).save(os.path.join(BLD, 'map40_t%s.png' % T))
    print('%s|%d|%d' % (T, MM_H, MM_TOP)); sp.__exit__(None, None, None); sys.exit(0)
S = 3; fnt = ImageFont.load_default(); info = {}
procs = [subprocess.Popen([sys.executable, __file__, T], stdout=subprocess.PIPE, text=True) for T in NAMES]
for p in procs:
    T, h, top = p.communicate()[0].strip().splitlines()[-1].split('|'); info[T] = (int(h), int(top))
sheet = Image.new('RGB', (2 * (256 * S + 16) + 16, 2 * (192 * S + 40) + 8), (17, 18, 22)); d = ImageDraw.Draw(sheet)
for i, T in enumerate(NAMES):
    ox, oy = 16 + (i % 2) * (256 * S + 16), 8 + (i // 2) * (192 * S + 40)
    h, top = info[T]
    d.text((ox, oy + 8), '%s: the map 40 wide, %d lines - window lines %d to %d of 152' % (NAMES[T], h, top, top + h - 1), fill=(236, 235, 230), font=fnt)
    sheet.paste(Image.open(os.path.join(BLD, 'map40_t%s.png' % T)).resize((256 * S, 192 * S), Image.NEAREST), (ox, oy + 28))
out = os.path.join(ROOT_, 'docs', 'design', 'arrows', 'map40_tracks.png'); sheet.save(out); print('wrote', out)
