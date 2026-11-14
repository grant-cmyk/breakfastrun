"""More ways to play a ditty's notes (Grant, 14 Nov 2026: "probably kettle's on for sound, but I
don't like the buzz sound or plink or pip"). Renders one tune in five further styles with the
exact speaker model of tools/make_ditties.py, and prints what each costs.
Usage: python3 tools/make_ditty_styles.py [ditty key, default ditty5]   -> docs/sound/<key>_<style>.wav

  marimba  an octave LOWER: two fat pulses a period apart as the note starts, two thin ones on
           the next frame - a woody "tock" with a pitch
  flute    the note's own pitch as THIN pulses (quiet, soft-edged), three a frame, held for
           three quarters of the note
  shimmer  the note and the octave above it on alternate frames, for half the note - the old
           Spectrum trick that sounds like two notes at once
  echo     a pip, then the same note fainter 4 frames later and fainter again 8 frames later
  hum      an octave lower, two thin pulses on every frame for half the note - soft and low

The way Manic Miner does it (measured in zxdev from Grant's snapshot, 14 Nov 2026: its in-game
tune is a burst 7-8 ms long - 28,000 T-states, 40% of a TV frame - about 11 times a second, at
640-1,200 Hz, for as long as the note lasts). The same here, a twelfth lower than the styles above:
  miner      8 ms of the note once a picture (every 3rd frame), for the whole note
  minerhalf  4 ms once a picture
  held       2.7 ms on EVERY frame (the same time a picture as miner, spread evenly)
  heldlight  1.5 ms (two cycles at least) on every frame
These cost real time: 28,000 / 14,000 / 28,000 / about 17,000 T a picture."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_ditties as md
key = sys.argv[1] if len(sys.argv) > 1 else 'ditty5'
d = next(x for x in md.DITTIES if x['key'] == key)
STYLES = ['marimba', 'flute', 'shimmer', 'echo', 'hum', 'miner', 'minerhalf', 'held', 'heldlight']
LOW = 17                                         # the Manic Miner styles play this many semitones lower (660-1,480 Hz)
B, S = md.LOOP_BASE_T, md.LOOP_STEP_T
q = lambda t: B + S * max(1, int(round((t - B) / S)))            # a wait the player's loop can make
def pulses(period, width, n):
    """n pulses, each `width` wide, one `period` apart"""
    w = q(width); b = [w, period - w] * n; b[-1] = md.LAST_T; return b
old = md.note_bursts
def note_bursts(style, midi, length):
    hp = md.half_period(midi); P = 2 * hp
    if style == 'marimba':
        plan = {0: pulses(2 * P, P / 2, 2), 1: pulses(2 * P, P / 8, 2)}
    elif style == 'flute':
        plan = {f: pulses(P, hp / 4, 3) for f in range(min(12, max(2, length * 3 // 4)))}
    elif style == 'shimmer':
        up = q(hp / 2)
        plan = {f: ([hp] * 4 if f % 2 == 0 else [up] * 6) for f in range(min(8, max(2, length // 2)))}
    elif style == 'echo':
        full = md.even_cycles(md.PIP_T, hp)
        plan = {0: [hp] * full, 4: md.thin_pulses(hp, full // 2, 2), 8: md.thin_pulses(hp, full // 2, 4)}
    elif style == 'hum':
        plan = {f: pulses(2 * P, P / 4, 2) for f in range(min(6, max(2, length // 2)))}
    elif style in ('miner', 'minerhalf', 'held', 'heldlight'):
        lhp = q(md.CPU_HZ / (2.0 * md.freq_of(midi - LOW)))
        t, step = {'miner': (28000, 3), 'minerhalf': (14000, 3), 'held': (9300, 1), 'heldlight': (5200, 1)}[style]
        n = max(4, int(t // lhp)); n -= n & 1
        plan = {f: [lhp] * n for f in range(0, max(1, length - 2), step)}
    else:
        return old(style, midi, length)
    return {f: b for f, b in plan.items() if f < length}
md.note_bursts = note_bursts
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'docs', 'sound')
n = md.loop_frames(d) * md.LOOPS
for st in STYLES:
    frames, starts = md.music_frames(d, st)
    avg, worst = md.cost_of(frames, n)
    md.render(frames, n, os.path.join(out, '%s_%s.wav' % (d['key'], st)))
    print('%s %-8s %5.0f T a frame on average, longest burst %5d T%s' % (d['key'], st, avg, worst, '' if worst <= 4200 and avg <= 1500 else '  (over the interrupt budget)'))
