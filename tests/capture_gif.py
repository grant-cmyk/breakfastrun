"""Record build/stage2_drive.gif: the real-ROM run, one picture per TV frame,
driving along the bottom straight and round the first bend."""
import os, numpy as np
from PIL import Image
from zx._spectrum import Spectrum
import zx._spectrum as zs
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
frames = []
def grab(sp):
    sp.render_screen()
    px = np.array(sp.get_frame_pixels(), dtype=np.uint8).reshape(-1, 352, 4)[:, :, [2, 1, 0]]
    frames.append(Image.fromarray(px[24:-24, 32:-32]).resize((576, 464), Image.NEAREST))
def press(sp, k, down):
    sp.devices.notify(zs.KeyStroke(zs.KEYS[k].ID, pressed=down))
with Spectrum(headless=True) as sp:
    sp.load_tape(os.path.join(ROOT, 'build', 'racer.tap'))
    sp.run(duration=45, fast_forward=True)
    press(sp, 'Q', True)
    plan = [(70, None), (14, 'O'), (40, None), (12, 'O'), (40, None)]
    for n, steer in plan:
        if steer: press(sp, steer, True)
        for _ in range(n):
            sp.run(duration=0.02, fast_forward=True)
            grab(sp)
        if steer: press(sp, steer, False)
out = os.path.join(ROOT, 'build', 'stage2_drive.gif')
frames[0].save(out, save_all=True, append_images=frames[1:], duration=20, loop=0)
frames[60].save(os.path.join(ROOT, 'build', 'stage2_frame.png'))
print(len(frames), 'frames ->', out)
