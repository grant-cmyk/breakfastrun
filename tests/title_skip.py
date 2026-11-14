"""The title screen comes up before the race (src/title.asm). leave(sp) waits for its flashing
PRESS 1 OR 2 TO START and presses 1 (1UP), so a tool written for the race screen starts there.
(The tests that exec drive_test.py's header get the same from its Racer.load_tape.)"""
import zx._spectrum as zs
def leave(sp, limit=60.0):
    t = 0.0
    while sp.read8(0x5800 + 23 * 32 + 5) != 0xB0 and t < limit: sp.run(duration=0.1, fast_forward=True); t += 0.1
    sp.run(duration=0.5, fast_forward=True)                         # (the rest of the title is drawn after its prompt)
    sp.devices.notify(zs.KeyStroke(zs.KEYS['1'].ID, pressed=True)); sp.run(duration=0.2, fast_forward=True)
    sp.devices.notify(zs.KeyStroke(zs.KEYS['1'].ID, pressed=False))
