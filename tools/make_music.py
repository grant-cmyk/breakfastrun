"""The background ditty as the game plays it: src/music.asm from a tune in tools/make_ditties.py.
Usage: python3 tools/make_music.py [ditty key, default ditty13 = Kettle's On, driving]

The interrupt (racer.asm, isr_q) steps the tune; the main loop sounds the note once a picture
(mu_burst), the way Manic Miner does: a burst of the note milliseconds long and low in pitch,
for as long as the note lasts. A cycle is: flip, wait 17 + 16 n T, flip, wait 30 + 16 m T.
  mu_tune: a byte a step (MU_STEP frames) - the note's place in mu_ptab, 254 a rest; 255 ends
           the tune (it starts again). Only the driving tunes: a note on every step.
  mu_ptab: 4 bytes a pitch - the cycles in a whole burst (BURST_T), n, m, and what a cycle
           costs in units of 279 T (the burst is cut to the picture's spare time)
LOW: the tune is played this many semitones under the music-box register of make_ditties."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_ditties as md
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
key = sys.argv[1] if len(sys.argv) > 1 else 'ditty13'
d = next(x for x in md.DITTIES + md.RACERS if x['key'] == key)
BURST_T = int(os.environ.get('BURST_T', 14000))   # a whole burst: 4 ms ("half-miner"; Manic Miner's is 28,000)
LOW = int(os.environ.get('LOW', 17))
def pitch(midi):
    hp = md.CPU_HZ / (2.0 * md.freq_of(midi - LOW)); s = max(2, round((2 * hp - 47) / 16)); P = 47 + 16 * s
    n = (s + 1) // 2; assert n < 256
    return [max(2, round(BURST_T / P)), n, s - n, -(-(P + 60) // 279)], md.CPU_HZ / P / 2 ** (-LOW / 12)
STEP = d.get('step')
assert STEP, 'the game plays the driving tunes (a note on every step): ditty13, ditty14'
steps = []
for t, midi, length in md.notes_of(d):
    assert length == STEP and t % STEP == 0
    steps.append(midi)
kinds = []
for m in steps:
    if m is not None and m not in kinds: kinds.append(m)
assert len(kinds) * 4 < 254
rows = {}; worst = 0
for k in kinds:
    rows[k], f = pitch(k); worst = max(worst, abs(f / md.freq_of(k) - 1))
GATE = max(1, STEP - 1)                          # a step sounds for all but its last frame: the pulse
with open(os.path.join(ROOT, 'src', 'music.asm'), 'w') as f:
    f.write('; made by tools/make_music.py from tools/make_ditties.py: "%s" (%s), %d steps of %d TV frames\n' % (d['name'], d['mood'], len(steps), STEP))
    f.write('MU_STEP equ %d\nMU_GATE equ %d\n; a byte a step: the note\'s place in mu_ptab, 254 a rest, 255 the end\nmu_tune:\n' % (STEP, GATE))
    for q in range(0, len(steps), 9):
        f.write('        db ' + ','.join('254' if m is None else '%d' % (kinds.index(m) * 4) for m in steps[q:q + 9]) + '\n')
    f.write('        db 255\n; 4 bytes a pitch: the cycles in a whole burst, n, m, what a cycle costs (units of 279 T)\nmu_ptab:\n')
    for k in kinds:
        f.write('        db %s    ; note %d\n' % (','.join('%d' % v for v in rows[k]), k))
times = steps
print('music.asm: %s, %d steps, %d pitches, %d bytes; worst pitch error %.1f%%' % (d['name'], len(times), len(kinds), len(times) + 1 + len(kinds) * 4, worst * 100))
