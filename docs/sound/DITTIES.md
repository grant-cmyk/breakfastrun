# Breakfast Run - background ditties to choose from

Classification: Internal. 14 November 2026.

Grant asked for "a little ditty sound playing in the background", with car
noises kept to events. Here are four original tunes, each played three ways.
Everything in this folder is made by `tools/make_ditties.py` (run it again to
remake the lot); the WAVs are an exact simulation of the Spectrum's one-bit
speaker, not the real machine, and nobody has listened to them yet - the
numbers below are measured from the files.

## How to listen

Start with `demo_in_game.wav` (the recommended tune with a crash, pick-up
chirps, a NOS rush and skid ticks over it), then compare the `_plink` files
of the four tunes. Each file is the tune twice round, 26-31 seconds.

## The three ways of playing a note

| Style | File ending | What it is | Honest description |
|---|---|---|---|
| Pips | `_pips.wav` | One tiny burst (about a thousandth of a second) when the note starts | Dry, sparse "tick with a pitch". Cheapest. Sound is present only 1-3% of the time |
| Plink | `_plink.wav` | The pip, then two fainter repeats on the next two frames | The note rings and fades a little, like a music box. Still mostly silence (2-5% of the time) |
| Buzz | `_buzz.wav` | A burst on every frame for the first half of the note | A held, buzzy note with a 50 Hz rattle in it. Closest to the old engine drone; dearest |

## The four ditties

**1. Toast Rack March** (`ditty1_*`) - a jaunty little march, 125 beats a
minute, 8 bars, loops every 15 s. A clear tune with a pause at the end of most
lines. Suits plink. Light tick-tock percussion.

**2. Marmalade Swing** (`ditty2_*`) - bouncy, lazy long-short swing, 143 beats
a minute, 8 bars, loops every 13 s. Suits plink. The busiest of the four.

**3. Spilt Milk** (`ditty3_*`) - cheeky and stop-start, like tiptoeing: little
two-note scurries, then gaps. 150 beats a minute, 8 bars, loops every 13 s.
Suits pips or plink. Leaves the most room for event sounds.

**4. Sunny Side Up** (`ditty4_*`) - a calm morning music-box waltz, 100 beats a
minute, 8 bars, loops every 14 s. No percussion. Suits plink. The gentlest and
the cheapest, but the least racy.

## What each costs the game

The budget is 1,000-1,500 T-states a TV frame on average (a frame is 69,888)
and no single burst over about 4,000. All twelve fit. Figures include 120 T a
frame for the note counter, which is an estimate because the player is not
written yet.

| Ditty | Style | Average T a frame | Share of a frame | Longest burst (T) | Note table (bytes) |
|---|---|---|---|---|---|
| 1 Toast Rack March | pips | 310 | 0.4% | 3,863 | 97 |
| | plink | 556 | 0.8% | 3,863 | 97 |
| | buzz | 1,084 | 1.6% | 3,835 | 97 |
| 2 Marmalade Swing | pips | 340 | 0.5% | 3,863 | 99 |
| | plink | 637 | 0.9% | 3,863 | 99 |
| | buzz | 1,005 | 1.4% | 3,835 | 99 |
| 3 Spilt Milk | pips | 304 | 0.4% | 3,979 | 119 |
| | plink | 542 | 0.8% | 3,979 | 119 |
| | buzz | 746 | 1.1% | 3,835 | 119 |
| 4 Sunny Side Up | pips | 214 | 0.3% | 3,712 | 47 |
| | plink | 344 | 0.5% | 3,712 | 47 |
| | buzz | 706 | 1.0% | 3,684 | 47 |

The note table is 2 bytes a note or rest, plus an end marker. The percussion
pattern is one more byte or two. The player routine itself is not counted.

## Recommendation

**Toast Rack March, played as plink** (`ditty1_plink.wav`, and in the mix in
`demo_in_game.wav`).

- It is the most tune-like of the four and fits the jaunty morning mood.
- Plink costs about half the low end of the budget (556 T a frame, under 1% of
  the machine's time), so the game should not slow.
- It is silent about 95% of the time, so crashes, pick-ups and skid ticks come
  through without a fight.
- Runner-up: **Spilt Milk as plink**, if the march is too busy once the events
  are in - it has the most gaps.
- Buzz is not recommended: it costs twice as much and its rattle is the kind
  of constant noise the old engine sound was.

## Limits, in plain words

- **Only high notes are possible.** The speaker has to be flipped by hand, and
  a low note takes too long. Every tune sits in a music-box range (about 2,000
  to 4,400 Hz). There is no bass.
- **Notes cannot be held.** A pip is about a thousandth of a second. The tune
  is sparkly ticks, not singing notes.
- **The pitch is blurry.** In a burst that short the ear gets only two to four
  cycles of the note. The rise and fall of the tune should come through; exact
  notes will not, and the lowest notes are the vaguest. Each pip also carries
  a small "tick" of its own.
- **Tuning is close, not perfect**: up to a quarter of a semitone out on the
  highest notes.
- **One speaker.** While an event sound plays, the tune drops out for those
  frames and carries on in step afterwards.
- **A real TV speaker will sound different** from these files (duller, more
  click). The proper test is the game itself in an emulator.

## What was checked (by measurement, not by ear)

- Every file: not silent, not clipped, peak at 30%, right length.
- Every frame that should make a sound does, and no others (0 missing, 0
  stray, in all 13 files) - so the rhythm and tempo are as written.
- The pitch of every note's first burst, measured from the file: within 1.4%
  of the true note, with the right number of cycles. That 1.4% is the
  player's own rounding; the files match the player to 0.2%.
- The in-game demo uses the game's present chirp timing, whose first burst is
  5,538 T - over the 4,000 limit already, nothing to do with the music.
