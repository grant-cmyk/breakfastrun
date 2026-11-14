"""The background ditty as the game plays it: src/music.asm from a tune in tools/make_ditties.py.
Usage: python3 tools/make_music.py [ditty key, default ditty3 = Spilt Milk]

The player lives in the interrupt (racer.asm, isr_q) and may use only A, H and L. A burst is H
cycles of: flip, wait 20 + 16 n T, flip, wait 36 + 16 m T - so a whole period is 56 + 16 (n + m)
T-states. A note is played "buzz" (Grant's pick from the Sound Lab, 14 Nov 2026: "Spilt Milk,
buzz"): a short burst of the note on every TV frame for the first half of the note, 8 frames at
most. A drum is one cycle on one frame.
  mu_tune: 3 bytes an event - the event's place in mu_ptab, the TV frames until the next event,
           the frames it sounds for; 255 ends the tune (it starts again)
  mu_ptab: 3 bytes a pitch - cycles, n, m"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_ditties as md
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
key = sys.argv[1] if len(sys.argv) > 1 else 'ditty3'
d = next(x for x in md.DITTIES if x['key'] == key)
BURST_T = 1700                                   # a burst's length at most (make_ditties' BUZZ_T)
def pitch(midi):
    hp = md.CPU_HZ / (2.0 * md.freq_of(midi)); s = max(2, round((2 * hp - 56) / 16)); P = 56 + 16 * s
    n = (s + 1) // 2
    return [max(2, int(BURST_T // P)), n, s - n], md.CPU_HZ / P
loop = md.loop_frames(d)
ev = {t: ('n', midi) for t, midi, length in md.notes_of(d) if midi is not None}
gate = {t: min(md.BUZZ_GATE, max(2, length // 2)) for t, midi, length in md.notes_of(d) if midi is not None}
for t, ch in md.drums_of(d).items():
    if not any(t - k in ev and k < gate[t - k] for k in range(8)): ev[t] = ('d', ch); gate[t] = 1   # (a drum on a note's frames gives way to it)
times = sorted(ev); assert times[0] == 0, 'the tune must start with a note or a drum'
kinds = []                                       # the pitch table's rows, in order of first use
for t in times:
    if ev[t] not in kinds: kinds.append(ev[t])
assert len(kinds) * 3 < 255
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
        f.write('        db %d,%d,%d\n' % (kinds.index(ev[t]) * 3, wait, min(gate[t], wait)))
    f.write('        db 255\nmu_ptab:\n')
    for k in kinds:
        f.write('        db %s    ; %s\n' % (','.join('%d' % v for v in rows[k]), 'note %d' % k[1] if k[0] == 'n' else 'drum ' + k[1]))
print('music.asm: %s, %d events, %d pitches, %d bytes; worst pitch error %.1f%%' % (d['name'], len(times), len(kinds), len(times) * 3 + 1 + len(kinds) * 3, worst * 100))
