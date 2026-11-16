"""Pictures of every step of the choose screen, from the real tape in the emulator: docs/design/choose/*.png (3x).
Usage: python3 tests/choose_shots.py      (needs build/racer_choose.tap: bash tools/build_choose.sh)"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault('ZTAP', os.path.join(HERE, '..', 'build', 'racer_choose.tap'))
os.environ.setdefault('ZSYM', os.path.join(HERE, '..', 'build', 'racer_choose.sym'))
src = open(os.path.join(HERE, 'drive_test.py')).read()
src = src[:src.index('with Racer(headless=True)')].replace("os.path.dirname(os.path.abspath(__file__))", repr(HERE))
exec(src)
D = os.path.join(ROOT, 'docs', 'design', 'choose'); os.makedirs(D, exist_ok=True)
def snap(sp, name):
    sp.render_screen()
    px = np.array(sp.get_frame_pixels(), dtype=np.uint8).reshape(-1, 352, 4)[:, :, [2, 1, 0]]
    h = px.shape[0]; x0 = (352 - 256) // 2 - 8; y0 = (h - 192) // 2 - 8           # the screen and 8 pixels of border
    im = Image.fromarray(px).crop((x0, y0, x0 + 272, y0 + 208))
    im.resize((272 * 3, 208 * 3), Image.NEAREST).save(os.path.join(D, name)); print(name)
def tap(sp, k, down=0.15, after=0.35):
    press(sp, k, True); sp.run(duration=down, fast_forward=True); press(sp, k, False); sp.run(duration=after, fast_forward=True)
def title(sp):
    Spectrum.load_tape(sp, TAP); t = 0.0
    while sp.read8(0x5800 + 8 * 32 + 10) != 0x7A and t < 60: sp.run(duration=0.1, fast_forward=True); t += 0.1
    sp.run(duration=0.6, fast_forward=True); sp.write(SYM['jin_on'], bytes([0xFF]))
with Racer(headless=True) as sp:                          # one player: every step, the new drivers and cars
    title(sp); snap(sp, '01_title.png')
    tap(sp, '1'); snap(sp, '02_track_1_tiffanys.png')
    tap(sp, 'P'); snap(sp, '03_track_2_breakfast_club.png')
    tap(sp, 'P'); snap(sp, '04_track_3_green_eggs.png')
    tap(sp, 'P'); tap(sp, 'Q'); snap(sp, '05_driver_max.png')
    for n, nm in enumerate(['frank', 'spike', 'bruno', 'jane', 'specs_new', 'dot_new']):
        tap(sp, 'P'); snap(sp, '%02d_driver_%s.png' % (6 + n, nm))
    tap(sp, 'O'); tap(sp, 'Q'); snap(sp, '12_car_racer.png')
    for n, nm in enumerate(['coupe', 'clown_car', 'tank', 'dragster', 'saloon_new', 'truck_new']):
        tap(sp, 'P'); snap(sp, '%02d_car_%s.png' % (13 + n, nm))
    tap(sp, 'Q'); snap(sp, '19_extra_acceleration.png')
    tap(sp, 'P'); snap(sp, '20_extra_grip.png')
    tap(sp, 'P'); snap(sp, '21_extra_speed.png')
    tap(sp, 'Q'); sp.run(duration=0.8, fast_forward=True); snap(sp, '22_race_specs_in_the_truck.png')
    go_green(sp); hold(sp, ['Q'], 1.0)
    sp.write(SYM['order'], bytes([0, 4, 1, 3, 2])); sp.write(SYM['race_over'], bytes([1])); sp.run(duration=2.0, fast_forward=True)
    snap(sp, '23_podium_specs_first.png')
with Racer(headless=True) as sp:                          # two players
    title(sp); tap(sp, '2'); tap(sp, 'Q'); tap(sp, 'Q'); tap(sp, 'Q'); tap(sp, 'Q')
    snap(sp, '24_player2_driver.png')
    for _ in range(5): tap(sp, '7')
    tap(sp, '9'); tap(sp, '7'); snap(sp, '25_player2_car.png')
    tap(sp, '9'); tap(sp, '7'); snap(sp, '26_player2_extra.png')
    tap(sp, '9'); sp.run(duration=0.8, fast_forward=True); snap(sp, '27_race_two_players_chosen.png')
