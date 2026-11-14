#!/usr/bin/env python3
"""make_ditties.py - background music ("a little ditty") options for Breakfast Run.

Grant, on the sound of the game (November 2026):

    "the sound is not good - the sound being made sounds like skidding. It is
    just annoying. We will need to work on the sound. I like the idea of a
    little ditty sound playing in the background. We can primarily keep car
    noises to bangs and hits and accelerates and pickups - so primarily
    events. A small sound on a skid is useful"

    "please can you run another agent to make some suggested background
    music/ditty for the game"

This tool composes four ORIGINAL short looping ditties and renders each one
the way a 48K Spectrum would really play it, so Grant can judge by listening.

    python3 tools/make_ditties.py            # writes docs/sound/*.wav, prints
                                             # the costs, then checks the WAVs
    python3 tools/make_ditties.py --no-check # skip the self-check

THE MACHINE'S LIMITS (why the music sounds the way it does)
-----------------------------------------------------------
The 48K has no sound chip: one bit of port 254 moves the speaker in or out,
and a tone is the CPU flipping that bit at the note's rate for as long as the
note lasts. Breakfast Run spends nearly all of its time drawing, so the music
gets only crumbs, all inside the 50 Hz interrupt routine:

    about 1,000-1,500 T-states per TV frame on average (a frame is 69,888 T)
    no single burst longer than about 4,000 T (interrupts are off meanwhile)

So a note cannot be held. What fits is a short burst of flips at the start of
a frame. One flip-to-flip gap (a half-period) is 1,750,000 / frequency
T-states, so only HIGH notes fit: C7 (2,093 Hz) is 836 T a half-period, and
the four of them that make two whole cycles are already 3,344 T. Below about
B6 (1,976 Hz) there is room for one cycle only, and one cycle is a click, not
a note. The ditties therefore live in a music-box register, B6 to about D8
(2-4.7 kHz): every tune is moved ("transpose") so its lowest note is B6.

THE PLAYER THIS TOOL SIMULATES (T-state exact)
----------------------------------------------
Once a frame the interrupt routine steps a note timer (reckoned at SEQ_T
T-states a frame, an estimate - the routine is not written yet). When there is
something to play it runs this loop, D = flips, E = the note's period byte:

    pip:  xor 24            ;  7 T
          out (254),a       ; 11 T   the flip
          ld b,e            ;  4 T
          djnz $            ; 13 T a count, less 5 on the last
          dec d             ;  4 T
          jr nz,pip         ; 12 T
                            ; = 33 + 13 x E  T-states from flip to flip

so every pitch is rounded to the nearest 13 T (at worst about 1.7% off at the
top of the range - a quarter of a semitone; the tool prints the worst case).
The burst's cost is flips x half-period, and that is what the cost table adds
up. Flip times are computed in T-states at 3.5 MHz, the 0/1 speaker signal is
built from them at 4 x 44.1 kHz with exact edge positions, then band-limited
and thinned to a 44.1 kHz WAV. The only thing added to the 1-bit signal is a
plain model of the output: the AC coupling (a 40 Hz high-pass, which is why a
single flip is heard as a click) and a small speaker's dull top (a gentle 6 kHz
low-pass). Volume is set so the peak is 30% of full scale.

THREE WAYS TO PLAY A NOTE
-------------------------
  pips   one burst on the note's first frame, as many whole cycles as fit in
         PIP_T (about 1 ms): a short dry "tick with a pitch".
  plink  the pip, then two fainter repeats on the next two frames: the note
         rings and dies away like a music box or a plucked string. Costs two
         to three times the pips. This is the "better trick within the
         budget": a 1-bit speaker has no volume, but a THIN pulse is quieter
         than a fat one. So the repeats keep the note's period (which is what
         carries the pitch) and narrow the pulse: half width on the second
         frame, quarter width on the third. In the player it is the same loop
         with two delay bytes used in turn (pulse width, then the rest of the
         period). An earlier try, repeats of fewer and fewer flips, measured
         worse: one lone cycle has no pitch, it only adds rattle.
  buzz   about half a millisecond of the note (two cycles at least) on EVERY
         frame for the first half of the note, 8 frames at most - any longer
         and the average cost breaks the budget: a short held, buzzy note
         with a strong 50 Hz rattle in it.

Percussion is cheap: "o" is two flips 501 T apart (a soft thud, ~540 T), "x"
is two flips 111 T apart (a thin tick, ~150 T). On a frame where a note also
starts there is no room for the thud, so it shrinks to the tick. No noise is
used in the music: hiss is kept for the crash and the skid, so the tune never
sounds like them.

The in-game demo mixes event sounds over the favourite ditty. One speaker:
on a frame where an event is sounding, the music's burst is simply skipped
(the tune keeps its place and carries on underneath).

Only the standard library and numpy are needed.
"""

import math
import os
import random
import sys
import wave

import numpy as np

# --------------------------------------------------------------------------
# The machine
# --------------------------------------------------------------------------
CPU_HZ = 3_500_000          # T-states a second
FRAME_T = 69_888            # T-states in a TV frame (50.08 Hz)
SR = 44_100                 # the WAV's sample rate
OVERSAMPLE = 4              # the speaker signal is built at 4 x SR
PEAK = 0.30                 # the WAV's peak, of full scale

ISR_LEAD_T = 160            # from the interrupt to the first flip (estimate)
SEQ_T = 120                 # the note timer etc, every frame (estimate)
LOOP_BASE_T = 33            # the pip loop: 33 + 13 x E from flip to flip
LOOP_STEP_T = 13

PIP_T = 3_600               # a pip: as many whole cycles as fit in this
BUZZ_T = 1_700              # a buzz frame: as many cycles as fit (2 at least)
BUZZ_GATE = 8               # a buzz note sounds for at most this many frames
BURST_LIMIT_T = 4_000       # the brief's limit for one burst
LAST_T = 40                 # after a burst's last flip: just the way out
THUD_GAP_T = LOOP_BASE_T + LOOP_STEP_T * 36     # 501 T: the thud's width
TICK_GAP_T = LOOP_BASE_T + LOOP_STEP_T * 6      # 111 T: the thin tick's width

NOTE_NAMES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def midi_of(name):
    """'C6' -> 84, 'F#6' -> 90, 'Bb6' -> 94 (C4 = 60, A4 = 69 = 440 Hz)."""
    if isinstance(name, int):
        return name
    n = NOTE_NAMES[name[0].upper()]
    rest = name[1:]
    while rest and rest[0] in "#b":
        n += 1 if rest[0] == "#" else -1
        rest = rest[1:]
    return n + 12 * (int(rest) + 1)


def freq_of(midi):
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)


def period_byte(midi):
    """The byte E the player would store for this note."""
    ideal = CPU_HZ / (2.0 * freq_of(midi))
    return max(1, min(255, int(round((ideal - LOOP_BASE_T) / LOOP_STEP_T))))


def half_period(midi):
    """T-states from flip to flip, as the player's loop really makes it."""
    return LOOP_BASE_T + LOOP_STEP_T * period_byte(midi)


def played_freq(midi):
    return CPU_HZ / (2.0 * half_period(midi))


# --------------------------------------------------------------------------
# The four ditties. All ORIGINAL (composed for this game).
# A tune is a list of bars; a bar is "NOTE:frames NOTE:frames ...", "r" = rest.
# drums: one string per bar, cut into equal steps: o = thud, x = tick, . = none
# --------------------------------------------------------------------------
def march():
    q, e = 24, 12                       # crotchet, quaver (in TV frames)
    bars = [
        f"G6:{e} G6:{e} C7:{q} E7:{e} D7:{e} C7:{q}",
        f"A6:{e} C7:{e} A6:{q} G6:{q} r:{q}",
        f"G6:{e} G6:{e} C7:{q} E7:{e} F7:{e} G7:{q}",
        f"E7:{e} D7:{e} B6:{e} G6:{e} D7:{q} r:{q}",
        f"F7:{e} F7:{e} A7:{q} G7:{e} F7:{e} E7:{q}",
        f"D7:{e} E7:{e} F7:{e} D7:{e} B6:{q} r:{q}",
        f"G6:{e} C7:{e} E7:{e} G7:{e} F7:{e} D7:{e} B6:{e} G6:{e}",
        f"C7:{q} r:{e} G6:{e} C7:{q} r:{q}",
    ]
    return dict(key="ditty1", name="Toast Rack March", mood="jaunty little march",
                beat=24, beats_per_bar=4, transpose=4, bars=bars,
                drums=["o.x.o.x."] * 8)


def swing():
    q, L, S = 21, 14, 7                 # crotchet; swung long and short
    bars = [
        f"D7:{L} E7:{S} G7:{q} E7:{L} D7:{S} B6:{q}",
        f"A6:{L} B6:{S} D7:{L} B6:{S} G6:{q} r:{q}",
        f"D7:{L} E7:{S} G7:{q} A7:{L} G7:{S} E7:{q}",
        f"D7:{q} r:{L} Bb6:{S} B6:{q} r:{q}",
        f"C7:{L} E7:{S} G7:{L} E7:{S} C7:{L} E7:{S} G7:{q}",
        f"B6:{L} D7:{S} G7:{L} D7:{S} B6:{q} r:{q}",
        f"A6:{L} C7:{S} E7:{L} F#7:{S} G7:{L} E7:{S} D7:{L} B6:{S}",
        f"G6:{q} r:{L} D7:{S} G7:{q} r:{q}",
    ]
    return dict(key="ditty2", name="Marmalade Swing", mood="bouncy, lazy swing",
                beat=21, beats_per_bar=4, transpose=4, bars=bars,
                drums=["o..x..o..x.."] * 8)


def stopstart():
    q, e, s = 20, 10, 5
    bars = [
        f"E6:{s} F6:{s} G6:{e} r:{e} G6:{e} r:{q} C7:{e} r:{e}",
        f"B6:{s} Bb6:{s} A6:{e} r:{e} F6:{e} r:{q} r:{q}",
        f"E6:{s} F6:{s} G6:{e} r:{e} G6:{e} r:{e} D7:{e} C7:{e} r:{e}",
        f"A6:{e} r:{e} F#6:{e} r:{e} G6:{q} r:{q}",
        f"C7:{s} B6:{s} C7:{e} r:{e} E7:{e} r:{q} D7:{e} r:{e}",
        f"C7:{s} B6:{s} A6:{e} r:{e} G6:{e} r:{q} r:{q}",
        f"F6:{e} A6:{e} r:{e} G6:{e} B6:{e} r:{e} A6:{e} C7:{e}",
        f"r:{q} D7:{s} D7:{s} r:{e} C7:{q} r:{q}",
    ]
    return dict(key="ditty3", name="Spilt Milk", mood="cheeky, stop-start, tiptoe",
                beat=20, beats_per_bar=4, transpose=7, bars=bars,
                drums=["o.....x."] * 8)


def musicbox():
    q, e, h = 30, 15, 60
    bars = [
        f"E6:{q} G6:{q} C7:{q}",
        f"D7:{h} B6:{q}",
        f"C7:{q} A6:{q} F6:{q}",
        f"G6:{h} r:{q}",
        f"E6:{q} G6:{q} E7:{q}",
        f"D7:{e} C7:{e} B6:{q} G6:{q}",
        f"A6:{q} C7:{q} B6:{e} D7:{e}",
        f"C7:{h} r:{q}",
    ]
    return dict(key="ditty4", name="Sunny Side Up", mood="calm morning music box (a waltz)",
                beat=30, beats_per_bar=3, transpose=7, bars=bars, drums=None)


# ---- four more (Grant, 14 Nov 2026: "please try the spilt milk, but also come up with some new
#      ditty options") - nearer Spilt Milk's cheek and gaps, with two racier ones ----
def jig():
    e, q, d = 9, 18, 27                 # quaver, crotchet, dotted crotchet (6/8)
    bars = [
        f"G6:{e} B6:{e} D7:{e} G7:{q} D7:{e}",
        f"E7:{q} D7:{e} B6:{d}",
        f"A6:{e} B6:{e} C7:{e} D7:{q} B6:{e}",
        f"A6:{d} r:{d}",
        f"G6:{e} B6:{e} D7:{e} G7:{q} A7:{e}",
        f"G7:{q} E7:{e} D7:{d}",
        f"C7:{e} E7:{e} D7:{e} B6:{e} A6:{e} B6:{e}",
        f"G6:{d} r:{d}",
        f"E7:{q} E7:{e} G7:{q} E7:{e}",
        f"D7:{q} B6:{e} D7:{d}",
        f"C7:{q} C7:{e} E7:{q} C7:{e}",
        f"B6:{d} r:{d}",
        f"G6:{e} B6:{e} D7:{e} G7:{q} D7:{e}",
        f"E7:{e} G7:{e} E7:{e} D7:{q} B6:{e}",
        f"A6:{e} C7:{e} B6:{e} A6:{q} B6:{e}",
        f"G6:{d} r:{d}",
    ]
    return dict(key="ditty5", name="Kettle's On", mood="a skipping jig",
                beat=27, beats_per_bar=2, transpose=4, bars=bars,
                drums=["o..x.."] * 16)


def chase():
    e, s = 16, 8
    bars = [
        f"A6:{s} A6:{s} C7:{e} A6:{s} A6:{s} E7:{e}",
        f"D7:{s} D7:{s} C7:{e} B6:{e} r:{e}",
        f"A6:{s} A6:{s} C7:{e} A6:{s} A6:{s} E7:{e}",
        f"G7:{e} E7:{e} D7:{e} r:{e}",
        f"F6:{s} F6:{s} A6:{e} F6:{s} F6:{s} C7:{e}",
        f"G6:{s} G6:{s} B6:{e} G6:{s} G6:{s} D7:{e}",
        f"E7:{s} D7:{s} C7:{s} B6:{s} A6:{s} G#6:{s} A6:{s} B6:{s}",
        f"A6:{e} r:{e} E6:{e} r:{e}",
    ]
    return dict(key="ditty6", name="Crumbs!", mood="a galloping chase, minor key",
                beat=16, beats_per_bar=4, transpose=7, bars=bars,
                drums=["o.x.o.x."] * 8)


def toaster():
    e, q = 11, 22
    bars = [
        f"C7:{e} r:{e} C7:{e} G6:{e} r:{q} G7:{e} r:{e}",
        f"E7:{e} r:{e} E7:{e} C7:{e} r:{q} r:{q}",
        f"D7:{e} r:{e} D7:{e} A6:{e} r:{q} A7:{e} r:{e}",
        f"G7:{e} F7:{e} E7:{e} D7:{e} r:{q} r:{q}",
        f"C7:{e} r:{e} C7:{e} G6:{e} r:{q} G7:{e} r:{e}",
        f"F7:{e} r:{e} F7:{e} A6:{e} r:{q} r:{q}",
        f"G6:{e} B6:{e} D7:{e} F7:{e} r:{e} E7:{e} D7:{e} r:{e}",
        f"C7:{q} r:{q} G7:{e} C7:{e} r:{q}",
    ]
    return dict(key="ditty7", name="Pop-Up Toaster", mood="boingy leaps and pauses",
                beat=22, beats_per_bar=4, transpose=4, bars=bars,
                drums=["o...x..."] * 8)


def butterfingers():
    q, e, s = 20, 10, 5
    bars = [
        f"E7:{s} Eb7:{s} D7:{e} r:{e} B6:{e} r:{q} G6:{e} r:{e}",
        f"A6:{e} r:{e} A6:{s} Bb6:{s} B6:{e} r:{q} r:{q}",
        f"E7:{s} Eb7:{s} D7:{e} r:{e} B6:{e} r:{e} G6:{e} E6:{e} r:{e}",
        f"F#6:{e} r:{e} A6:{e} r:{e} G6:{q} r:{q}",
        f"C7:{e} E7:{e} r:{e} C7:{s} B6:{s} A6:{e} r:{e} r:{q}",
        f"B6:{e} D7:{e} r:{e} B6:{s} A6:{s} G6:{e} r:{e} r:{q}",
        f"E6:{e} G6:{e} B6:{e} E7:{e} r:{e} D7:{s} C7:{s} B6:{e} r:{e}",
        f"G6:{s} G6:{s} r:{e} E6:{q} r:{q} r:{q}",
    ]
    return dict(key="ditty8", name="Butter Fingers", mood="clumsy slips and stumbles (Spilt Milk's cousin)",
                beat=20, beats_per_bar=4, transpose=7, bars=bars,
                drums=["x.....o."] * 8)


DITTIES = [march(), swing(), stopstart(), musicbox(), jig(), chase(), toaster(), butterfingers()]

# ---- four racers (Grant, 14 Nov 2026: "something more upbeat for racing"), written for the
#      half-miner way of playing (tools/make_ditty_styles.py, tools/make_music.py): a burst a
#      picture, so no note is shorter than 6 TV frames. Not rendered as pips / plink / buzz. ----
def greenlight():
    e, q = 8, 16
    a = f"C7:{e} C7:{e} E7:{e} G7:{e} E7:{e} C7:{e} E7:{q}"
    bars = [a,
        f"D7:{e} D7:{e} F7:{e} A7:{e} F7:{e} D7:{e} F7:{q}",
        f"E7:{e} E7:{e} G7:{e} E7:{e} D7:{e} C7:{e} D7:{q}",
        f"G6:{e} B6:{e} D7:{e} G7:{e} G7:{q} r:{q}",
        a,
        f"F7:{e} F7:{e} A7:{e} F7:{e} E7:{e} D7:{e} E7:{q}",
        f"D7:{e} E7:{e} F7:{e} D7:{e} B6:{e} G6:{e} B6:{e} D7:{e}",
        f"C7:{q} G6:{e} G6:{e} C7:{q} r:{q}"]
    return dict(key="ditty9", name="Green Light", mood="driving, bright, 188 beats a minute",
                beat=16, beats_per_bar=4, transpose=4, bars=bars, drums=None)


def flatout():
    e, q = 7, 14
    a = f"E6:{e} G#6:{e} B6:{e} C#7:{e} D7:{e} C#7:{e} B6:{e} G#6:{e}"
    bars = [a, a,
        f"A6:{e} C#7:{e} E7:{e} F#7:{e} G7:{e} F#7:{e} E7:{e} C#7:{e}",
        a,
        f"B6:{e} D#7:{e} F#7:{e} G#7:{e} A6:{e} C#7:{e} E7:{e} F#7:{e}",
        a,
        f"E6:{e} G#6:{e} B6:{e} E7:{q} r:{e} B6:{q}",
        f"E7:{q} r:{q} E6:{q} r:{q}"]
    return dict(key="ditty10", name="Flat Out", mood="a rock and roll boogie riff, 214 beats a minute",
                beat=14, beats_per_bar=4, transpose=7, bars=bars, drums=None)


def chequered():
    L, S, q = 12, 6, 18
    a = f"G6:{L} G6:{S} B6:{q} D7:{L} D7:{S} G7:{q}"
    bars = [a,
        f"E7:{L} E7:{S} G7:{q} D7:{q} r:{q}",
        f"C7:{L} C7:{S} E7:{q} B6:{L} B6:{S} D7:{q}",
        f"A6:{L} B6:{S} C7:{q} D7:{q} r:{q}",
        a,
        f"A7:{L} G7:{S} E7:{q} G7:{q} r:{q}",
        f"C7:{L} E7:{S} G7:{q} B6:{L} D7:{S} G7:{q}",
        f"A6:{q} D7:{q} G6:{q} r:{q}"]
    return dict(key="ditty11", name="Chequered Flag", mood="a galloping fanfare, 167 beats a minute",
                beat=18, beats_per_bar=4, transpose=4, bars=bars, drums=None)


def helpings():
    e, q = 8, 16
    a = f"C7:{e} E7:{e} r:{e} E7:{e} G7:{e} E7:{e} C7:{q}"
    bars = [a,
        f"B6:{e} D7:{e} r:{e} D7:{e} G7:{e} D7:{e} B6:{q}",
        f"A6:{e} C7:{e} r:{e} C7:{e} E7:{e} C7:{e} A6:{q}",
        f"G6:{e} B6:{e} D7:{e} G7:{e} F7:{e} D7:{e} B6:{q}",
        a,
        f"F7:{e} A7:{e} r:{e} A7:{e} F7:{e} D7:{e} A6:{q}",
        f"G6:{e} A6:{e} B6:{e} C7:{e} D7:{e} E7:{e} F7:{e} G7:{e}",
        f"C7:{q} r:{e} G7:{e} C7:{q} r:{q}"]
    return dict(key="ditty12", name="Second Helpings", mood="bouncy, off the beat, 188 beats a minute",
                beat=16, beats_per_bar=4, transpose=4, bars=bars, drums=None)


def drive(d, key, name, step=6, unit=9, pedal=None):
    """A tune made DRIVING (Grant, 14 Nov 2026: "less ditty and more driving almost trance like -
    can you up its tempo or beat" - "Kettles on is still the best"): faster (each `unit` frames of
    the tune becomes `step`), and a steady pulse - every step sounds: the tune's note where one
    starts, and on every other step a pedal note (one a bar, from `pedal`), so the tune rides on
    an unbroken run of short notes. Every note is one step long: tools/make_music.py stores a
    byte a step."""
    bars = []
    for i, bar in enumerate(d["bars"]):
        ped = pedal[i % len(pedal)]; out = []
        for tok in bar.split():
            n, length = tok.split(":"); k = int(length) // unit; assert k * unit == int(length)
            out += [(ped if n == "r" else n)] + [ped] * (k - 1)
        bars.append(" ".join(f"{n}:{step}" for n in out))
    return dict(key=key, name=name, mood="driving: a steady pulse under the tune, %d beats a minute" % round(60 * 50.08 / (3 * step)),
                beat=3 * step, beats_per_bar=d["beats_per_bar"], transpose=d["transpose"], bars=bars, drums=None, step=step)


RACERS = [greenlight(), flatout(), chequered(), helpings(),
          drive(jig(), "ditty13", "Kettle's On, driving", pedal=["G6", "G6", "D7", "D7", "G6", "G6", "D7", "G6", "C7", "G6", "C7", "G6", "G6", "G6", "D7", "G6"]),
          drive(jig(), "ditty14", "Kettle's On, faster still", step=5, pedal=["G6", "G6", "D7", "D7", "G6", "G6", "D7", "G6", "C7", "G6", "C7", "G6", "G6", "G6", "D7", "G6"])]
STYLES = ["pips", "plink", "buzz"]
FAVOURITE = ("ditty1", "plink")         # the one used for the in-game demo
LOOPS = 2


def notes_of(ditty):
    """[(start frame, midi or None, length in frames)] for one loop."""
    out, t = [], 0
    bar_frames = ditty["beat"] * ditty["beats_per_bar"]
    for i, bar in enumerate(ditty["bars"]):
        start = t
        for tok in bar.split():
            name, length = tok.split(":")
            midi = None if name == "r" else midi_of(name) + ditty["transpose"]
            out.append((t, midi, int(length)))
            t += int(length)
        assert t - start == bar_frames, f"{ditty['name']} bar {i + 1}: {t - start} frames"
    return out


def drums_of(ditty):
    """{frame: 'o' or 'x'} for one loop."""
    out = {}
    if not ditty["drums"]:
        return out
    bar_frames = ditty["beat"] * ditty["beats_per_bar"]
    for b, pat in enumerate(ditty["drums"]):
        step = bar_frames // len(pat)
        assert step * len(pat) == bar_frames
        for i, ch in enumerate(pat):
            if ch != ".":
                out[b * bar_frames + i * step] = ch
    return out


def loop_frames(ditty):
    return ditty["beat"] * ditty["beats_per_bar"] * len(ditty["bars"])


# --------------------------------------------------------------------------
# From a ditty to bursts. A burst is the list of gaps (T-states) that follow
# each flip, so: flips = len(burst), cost = sum(burst).
# --------------------------------------------------------------------------
def even_cycles(budget, hp, most=16):
    """As many flips as fit, an even number (whole cycles), at least 2."""
    n = min(most, int(budget // hp))
    return max(2, n - (n & 1))


def thin_pulses(hp, cycles, narrow):
    """A burst of thin pulses one whole period apart: each pulse is hp/narrow
    wide (to the loop's 13 T), the rest of the period is silence."""
    width = LOOP_BASE_T + LOOP_STEP_T * max(1, int(round((hp / narrow - LOOP_BASE_T) / LOOP_STEP_T)))
    burst = [width, 2 * hp - width] * cycles
    burst[-1] = LAST_T                  # nothing to wait for after the last
    return burst


def note_bursts(style, midi, length):
    """{frame offset within the note: burst} for one note."""
    hp = half_period(midi)
    full = even_cycles(PIP_T, hp)
    if style == "pips":
        plan = {0: [hp] * full}
    elif style == "plink":
        plan = {0: [hp] * full,
                1: thin_pulses(hp, full // 2, 2),
                2: thin_pulses(hp, full // 2, 4)}
    elif style == "buzz":
        gate = min(BUZZ_GATE, max(2, length // 2))
        flips = max(4, even_cycles(BUZZ_T, hp))
        plan = {f: [hp] * flips for f in range(gate)}
    else:
        raise ValueError(style)
    return {f: b for f, b in plan.items() if f < length}


def music_frames(ditty, style, loops=LOOPS):
    """{frame: [burst, ...]} for the whole piece, and the note starts."""
    frames, starts = {}, []
    n_loop = loop_frames(ditty)
    notes, drums = notes_of(ditty), drums_of(ditty)
    for lp in range(loops):
        base = lp * n_loop
        for (t, midi, length) in notes:
            if midi is None:
                continue
            hp = half_period(midi)
            plan = note_bursts(style, midi, length)
            starts.append((base + t, midi, len(plan[0])))
            for f, burst in plan.items():
                frames.setdefault(base + t + f, []).append(burst)
        for t, ch in drums.items():
            lst = frames.setdefault(base + t, [])
            spent = sum(sum(b) for b in lst)
            room = BURST_LIMIT_T - SEQ_T - spent - LAST_T
            if ch == "o" and THUD_GAP_T <= room:
                lst.append([THUD_GAP_T, LAST_T])
            elif TICK_GAP_T <= room:
                lst.append([TICK_GAP_T, LAST_T])
    return frames, starts


def flips_of(frames):
    """All flip times, in T-states from the start, in order."""
    times = []
    for f in sorted(frames):
        t = f * FRAME_T + ISR_LEAD_T
        for burst in frames[f]:
            for gap in burst:
                times.append(t)
                t += gap
    return np.array(times, dtype=np.float64)


def cost_of(frames, n_frames):
    """(average T a frame, longest burst T) including the per-frame timer."""
    per = [sum(sum(b) for b in bl) for bl in frames.values()]
    avg = SEQ_T + sum(per) / n_frames
    worst = SEQ_T + (max(per) if per else 0)
    return avg, worst


# --------------------------------------------------------------------------
# The speaker: flip times -> 44.1 kHz samples
# --------------------------------------------------------------------------
def speaker(flip_times_t, total_t):
    """Exact 0/1 signal at OVERSAMPLE x SR (each sample = the mean level over
    that sample, so an edge between samples lands where it really is)."""
    rate = SR * OVERSAMPLE
    n = int(math.ceil(total_t * rate / CPU_HZ)) + 2
    x = flip_times_t * rate / CPU_HZ
    k = np.floor(x).astype(np.int64)
    frac = x - k
    sign = np.where(np.arange(len(x)) % 2 == 0, 1.0, -1.0)
    step = np.zeros(n + 2)
    np.add.at(step, k, sign * (1.0 - frac))
    np.add.at(step, k + 1, sign * frac)
    return np.cumsum(step)[:n]


def to_wav_samples(level):
    """The output stage (40 Hz AC coupling, a 6 kHz speaker roll-off), the
    band limit, the thinning to SR and the volume."""
    rate = SR * OVERSAMPLE
    n = len(level)
    spec = np.fft.rfft(level)
    f = np.fft.rfftfreq(n, 1.0 / rate)
    hp = (1j * f / 40.0) / (1.0 + 1j * f / 40.0)
    lp = 1.0 / (1.0 + 1j * f / 6000.0)
    taper = np.clip((21000.0 - f) / 3000.0, 0.0, 1.0)
    taper = 0.5 - 0.5 * np.cos(np.pi * taper)
    y = np.fft.irfft(spec * hp * lp * taper, n)[::OVERSAMPLE]
    peak = np.max(np.abs(y))
    return y * (PEAK / peak) if peak > 0 else y


def write_wav(path, samples):
    data = np.clip(np.round(samples * 32767.0), -32768, 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())


def read_wav(path):
    with wave.open(path, "rb") as w:
        assert w.getnchannels() == 1 and w.getsampwidth() == 2 and w.getframerate() == SR
        return np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype(np.float64) / 32767.0


def render(frames, n_frames, path):
    total_t = (n_frames + 12) * FRAME_T         # a short tail of silence
    write_wav(path, to_wav_samples(speaker(flips_of(frames), total_t)))


# --------------------------------------------------------------------------
# The in-game demo: event sounds over the favourite. They use the timing of
# the game's own isr_burst (src/racer.asm): 75 + 16 x L T-states a flip.
# --------------------------------------------------------------------------
def game_gap(count):
    return 75 + 16 * count


def event_frames(rng, n_frames):
    """{frame: burst} and a list of (frame, what) for the guide."""
    ev, log = {}, []

    def skid(at, ticks):                # a short tick every 4th frame
        log.append((at, "skid ticks"))
        for i in range(ticks):
            ev[at + 4 * i] = [game_gap(rng.randint(3, 10)) for _ in range(3)]

    def pickup(at):                     # the NOS chirp: rises over 12 frames
        log.append((at, "pick-up chirp"))
        for i in range(12):
            ev[at + i] = [game_gap(3 * (11 - i) + 20)] * 6

    def crash(at):                      # noise that thins out over 10 frames
        log.append((at, "crash"))
        for i in range(10):
            ev[at + i] = [rng.randint(90, 420) for _ in range(12 - i)]

    def rush(at):                       # NOS fired: a rushing noise
        log.append((at, "NOS rush"))
        for i in range(14):
            ev[at + i] = [game_gap(rng.randint(8, 39))] * 6

    def sec(s):
        return int(round(s * CPU_HZ / FRAME_T))

    skid(sec(3.3), 4)
    pickup(sec(6.4))
    rush(sec(8.6))
    crash(sec(11.9))
    skid(sec(15.0), 6)
    skid(sec(18.8), 3)
    pickup(sec(21.3))
    crash(sec(24.6))
    skid(sec(27.5), 4)
    return {f: b for f, b in ev.items() if f < n_frames}, log


def demo_frames(ditty, style):
    music, _ = music_frames(ditty, style)
    n = loop_frames(ditty) * LOOPS
    events, log = event_frames(random.Random(1982), n)
    mixed = dict(music)
    for f, burst in events.items():     # the event wins the frame outright
        mixed[f] = [burst]
    return mixed, events, log, n


# --------------------------------------------------------------------------
# The self-check: read the WAVs back and measure them
# --------------------------------------------------------------------------
def frame_sample(frame):
    return frame * FRAME_T * SR / CPU_HZ


def frame_energy(x, n_frames):
    e = np.zeros(n_frames)
    for f in range(n_frames):
        a, b = int(frame_sample(f)), int(frame_sample(f + 1))
        seg = x[a:b]
        e[f] = np.sqrt(np.mean(seg * seg)) if len(seg) else 0.0
    return e


def measure_pip(x, frame, hp, flips):
    """The pitch of the pip that starts on this frame, from the spacing of
    its edges in the WAV (16 x interpolated). Returns (Hz, edges found)."""
    up = 16
    t0 = (frame * FRAME_T + ISR_LEAD_T) * SR / CPU_HZ
    dur = flips * hp * SR / CPU_HZ
    a = int(t0) - 48
    b = int(t0 + dur) + 48
    if a < 0 or b > len(x):
        return None, 0
    seg = x[a:b]
    n = len(seg)
    spec = np.fft.rfft(seg)
    fine = np.fft.irfft(np.concatenate([spec, np.zeros((up - 1) * n // 2 + 1)]), n * up) * up
    lo = int((t0 - a - 2) * up)
    hi = int((t0 - a + dur - 0.3 * hp * SR / CPU_HZ) * up)
    w = fine[lo:hi]
    mid = (w.max() + w.min()) / 2.0
    s = w - mid
    idx = np.nonzero(np.signbit(s[:-1]) != np.signbit(s[1:]))[0]
    if len(idx) < 3:
        return None, len(idx)
    cross = idx + s[idx] / (s[idx] - s[idx + 1])
    gap = (cross[-1] - cross[0]) / (len(cross) - 1) / up        # samples a half-period
    return SR / (2.0 * gap), len(cross)


def describe(x):
    """Numbers that stand in for listening."""
    n = len(x)
    spec = np.abs(np.fft.rfft(x)) ** 2
    f = np.fft.rfftfreq(n, 1.0 / SR)
    total = spec.sum()
    centroid = (spec * f).sum() / total
    band = lambda lo, hi: spec[(f >= lo) & (f < hi)].sum() / total
    win = SR // 1000                                            # 1 ms
    env = np.sqrt(np.convolve(x * x, np.ones(win) / win, mode="same"))
    sounding = float(np.mean(env > 0.02 * PEAK))
    return dict(peak=float(np.max(np.abs(x))), rms=float(np.sqrt(np.mean(x * x))),
                dc=float(np.mean(x)), clipped=int(np.sum(np.abs(x) >= 0.999)),
                centroid=centroid, low=band(0, 400), mid=band(400, 5000),
                high=band(5000, SR / 2), sounding=sounding)


def check(out_dir, jobs):
    print("\nSELF-CHECK (the WAV files, read back from disk)")
    print("  file               secs  peak   rms   clip  sounding  <400Hz 0.4-5k  >5k  centroid")
    ok = True
    for (path, frames, n_frames, starts, style) in jobs:
        x = read_wav(path)
        d = describe(x)
        name = os.path.basename(path)
        print(f"  {name:18s} {len(x) / SR:5.1f} {d['peak']:5.2f} {d['rms']:6.3f} {d['clipped']:4d}"
              f"   {100 * d['sounding']:5.1f}%   {100 * d['low']:4.0f}%  {100 * d['mid']:4.0f}%"
              f" {100 * d['high']:4.0f}%  {d['centroid']:6.0f} Hz")
        if d["rms"] < 0.001 or d["clipped"] or not (0.28 <= d["peak"] <= 0.31) or abs(d["dc"]) > 0.002:
            ok = False
            print("     ** level problem **")
        # every frame that should sound does, every silent frame is silent
        e = frame_energy(x, n_frames)
        want = np.zeros(n_frames, dtype=bool)
        for f in frames:
            want[f] = True
        tail = np.zeros(n_frames, dtype=bool)                   # the click's 4 ms tail
        tail[1:] = want[:-1]
        loud = e > 0.1 * np.median(e[want])
        missing = int(np.sum(want & ~loud))
        stray = int(np.sum(loud & ~want & ~tail))
        line = f"     frames: {int(want.sum())} should sound, {missing} missing, {stray} stray"
        if missing or stray:
            ok = False
            line += "   ** timing problem **"
        # the pitch of each note's first burst (first loop is enough)
        if starts:
            errs, bad_edges, n_meas = [], 0, 0
            for (f, midi, flips) in starts:
                if len(frames[f]) and len(frames[f][0]) != flips:
                    continue
                hz, edges = measure_pip(x, f, half_period(midi), flips)
                if hz is None:
                    continue
                n_meas += 1
                if edges != flips:
                    bad_edges += 1
                errs.append(100.0 * (hz / freq_of(midi) - 1.0))
            if errs:
                errs = np.array(errs)
                line += (f"; pitch of {n_meas} notes vs true pitch: mean {errs.mean():+.2f}%,"
                         f" worst {np.abs(errs).max():.2f}%, wrong edge count {bad_edges}")
                if np.abs(errs).max() > 3.0 or bad_edges:
                    ok = False
                    line += "   ** pitch problem **"
        print(line)
    print("  RESULT:", "all checks passed" if ok else "PROBLEMS FOUND - see above")
    return ok


# --------------------------------------------------------------------------
def main():
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "sound")
    os.makedirs(out_dir, exist_ok=True)
    jobs = []

    print("BREAKFAST RUN - ditty costs (48K beeper, played from the 50 Hz interrupt)")
    print(f"budget: 1,000-1,500 T a frame on average, no burst over {BURST_LIMIT_T:,} T;"
          f" figures include {SEQ_T} T a frame for the note timer (an estimate)\n")
    print("  ditty                    style  avg T/frame  longest burst  % of frame  notes  table bytes")
    for d in DITTIES:
        notes = notes_of(d)
        n_loop = loop_frames(d)
        table = 2 * len(notes) + 1                              # 2 a note or rest + an end byte
        bpm = 60.0 * CPU_HZ / FRAME_T / d["beat"]
        for style in STYLES:
            frames, starts = music_frames(d, style)
            avg, worst = cost_of(frames, n_loop * LOOPS)
            flag = "" if worst <= BURST_LIMIT_T and avg <= 1500 else "  (over budget)"
            print(f"  {d['key']} {d['name']:17s} {style:6s} {avg:9.0f} {worst:13,d}"
                  f" {100 * avg / FRAME_T:10.1f}% {sum(1 for n in notes if n[1] is not None):6d} {table:8d}{flag}")
            path = os.path.join(out_dir, f"{d['key']}_{style}.wav")
            render(frames, n_loop * LOOPS, path)
            jobs.append((path, frames, n_loop * LOOPS, starts, style))
        lo = min(n[1] for n in notes if n[1] is not None)
        hi = max(n[1] for n in notes if n[1] is not None)
        tune = max(abs(1200 * math.log2(played_freq(m) / freq_of(m))) for m in range(lo, hi + 1))
        print(f"      {len(d['bars'])} bars, {d['beat']} frames a beat ({bpm:.0f} beats a minute),"
              f" one loop {n_loop * FRAME_T / CPU_HZ:.1f} s; notes {freq_of(lo):.0f}-{freq_of(hi):.0f} Hz;"
              f" worst tuning error {tune:.0f} cents; drum pattern "
              f"{'none' if not d['drums'] else d['drums'][0]}\n")

    d = next(x for x in DITTIES if x["key"] == FAVOURITE[0])
    mixed, events, log, n = demo_frames(d, FAVOURITE[1])
    path = os.path.join(out_dir, "demo_in_game.wav")
    render(mixed, n, path)
    jobs.append((path, mixed, n, None, "demo"))
    ev_worst = max(sum(b) for b in events.values())
    print(f"  demo_in_game.wav: {d['name']} ({FAVOURITE[1]}) with events; the events take"
          f" {len(events)} of {n} frames; longest event burst {ev_worst:,} T")
    for f, what in log:
        print(f"      {f * FRAME_T / CPU_HZ:5.1f} s  {what}")

    if "--no-check" not in sys.argv:
        if not check(out_dir, jobs):
            sys.exit(1)


if __name__ == "__main__":
    main()
