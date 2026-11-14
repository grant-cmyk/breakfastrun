"""The background ditty as the game plays it: src/music.asm from a tune in tools/make_ditties.py.
Usage: python3 tools/make_music.py [ditty key, default ditty3 = Spilt Milk]

The interrupt (racer.asm, isr_q) steps the tune; the main loop sounds the note once a picture
(mu_burst), the way Manic Miner does: a burst of the note milliseconds long and low in pitch,
for as long as the note lasts. A cycle is: flip, wait 17 + 16 n T, flip, wait 30 + 16 m T.
  mu_tune: 3 bytes an event - the event's place in mu_ptab, the TV frames until the next event,
           the frames it sounds for; 255 ends the tune (it starts again)
  mu_ptab: 4 bytes a pitch - the cycles in a whole burst (BURST_T), n, m, and what a cycle
           costs in units of 279 T (the burst is cut to the picture's spare time)
LOW: the tune is played this many semitones under the music-box register of make_ditties."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_ditties as md
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
key = sys.argv[1] if len(sys.argv) > 1 else 'ditty3'
d = next(x for x in md.DITTIES + md.RACERS if x['key'] == key)
BURST_T = int(os.environ.get('BURST_T', 14000))   # a whole burst: 4 ms ("half-miner"; Manic Miner's is 28,000)
LOW = int(os.environ.get('LOW', 17))
def pitch(midi):
    hp = md.CPU_HZ / (2.0 * md.freq_of(midi - LOW)); s = max(2, round((2 * hp - 47) / 16)); P = 47 + 16 * s
    n = (s + 1) // 2; assert n < 256
    return [max(2, round(BURST_T / P)), n, s - n, -(-(P + 60) // 279)], md.CPU_HZ / P / 2 ** (-LOW / 12)
loop = md.loop_frames(d)
ev = {t: ('n', midi) for t, midi, length in md.notes_of(d) if midi is not None}
gate = {t: max(1, length - 2) for t, midi, length in md.notes_of(d) if midi is not None}
for t, ch in md.drums_of(d).items():
    pass                                           # (no drums: a burst a picture cannot place them)
times = sorted(ev); assert times[0] == 0, 'the tune must start with a note or a drum'
kinds = []                                       # the pitch table's rows, in order of first use
for t in times:
    if ev[t] not in kinds: kinds.append(ev[t])
assert len(kinds) * 4 < 255
rows = {}; worst = 0
for k in kinds:
    if k[0] == 'n':
        rows[k], f = pitch(k[1]); worst = max(worst, abs(f / md.freq_of(k[1]) - 1))
    else:
        rows[k] = [1, 30 if k[1] == 'o' else 6, 1]
with open(os.path.join(ROOT, 'src', 'music.asm'), 'w') as f:
    f.write('; made by tools/make_music.py from tools/make_ditties.py: "%s" (%s), %d TV frames a loop\n' % (d['name'], d['mood'], loop))
    f.write('mu_tune:\n')
    for i, t in enumerate(times):
        wait = (times[i + 1] if i + 1 < len(times) else loop) - t
        assert 1 <= wait <= 255
        f.write('        db %d,%d,%d\n' % (kinds.index(ev[t]) * 4, wait, min(gate[t], wait)))
    f.write('        db 255\nmu_ptab:\n')
    for k in kinds:
        f.write('        db %s    ; %s\n' % (','.join('%d' % v for v in rows[k]), 'note %d' % k[1] if k[0] == 'n' else 'drum ' + k[1]))
print('music.asm: %s, %d events, %d pitches, %d bytes; worst pitch error %.1f%%' % (d['name'], len(times), len(kinds), len(times) * 3 + 1 + len(kinds) * 3, worst * 100))
