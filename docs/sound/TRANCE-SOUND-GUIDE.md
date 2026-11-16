# Breakfast Run: the "trance" beeper sound - a guide for another project

Classification: Internal. Written 16 Nov 2026 for Grant, to hand to another Claude chat as a reference
for the sound he wants. It describes two jingles from Breakfast Run (a ZX Spectrum 48K game) and exactly
how they are made, so the same feel can be rebuilt on another game. The two recordings that go with it are
`spilt-milk.mp3` and `second-helpings.mp3` (recorded from the game's own sound routine in an emulator).

## What Grant means by "trance" here
Not a genre exercise: a bright, simple lead tune riding on a steady four-to-the-floor pulse, all on a
1-bit speaker. He liked these two and called a third in the same sound ("Order Up") "great". What they share:

1. **A lead tune in a singing register**, about 500 to 1,100 Hz (roughly B4 to C#6). An octave higher was shrill.
2. **A bass pedal on one note for the whole jingle** - the key note - alternating LOW, HIGH (an octave up),
   LOW, HIGH, one per step, four steps to a beat. This octave bounce is what makes it read as trance.
3. **A kick on every beat** (the first step of each four) and **a short tick of noise half way** (step 3).
4. **Short and looping in feel**: about 5.8 seconds, minor or modal harmony, notes snapped to a fixed step grid,
   rests left as real silence in the lead while the bass and kick carry on underneath.
5. **Plain square waves.** No vibrato, no slides, no volume envelope. The character comes from the pattern.

## How the two voices share one speaker
The player is one tight loop of fixed length (91 T-states a turn at 3.5 MHz, about 38.5 kHz). Each voice has
a countdown; when it reaches zero the voice flips its level and reloads its period. The speaker bit is the
two voices combined, so both pitches are heard at once (with the gritty mixing that gives the 1-bit sound).
- voice 1: the lead, period looked up from the tune table each step (silent on a rest);
- voice 2: the bass, low on steps 1 and 3 of a beat, an octave up on steps 2 and 4;
- on step 1 of each beat the kick replaces the first part of the step: six flips with a quickly growing gap
  (a falling pitch thump, about 15 ms);
- on step 3 a few milliseconds of random flips (the tick) before the notes carry on.
Interrupts are off while it plays, so the pitch is steady. Nothing else runs during the jingle.

On a machine with real sound channels, the same recipe is: square lead + square bass doing the octave bounce
on one note + kick on the beat + closed-hat tick on the off-beat, all quantised, no effects.

## The two tunes
Notes are as they SOUND (two octaves below how they were first written). One entry is one step.

### "Spilt Milk" - used for the chequered flag (written as the start jingle)
- Mood as written: cheeky, stop-start, tiptoe
- One step = 5 TV frames = 100 ms; four steps to a beat = 150 beats a minute; 56 steps, 5.6 s
- Bass pedal: G2 and G3 (MIDI 43 and 55), alternating every step
- Lead, one step per entry:

```
B4   C5   D5   D5   rest rest D5   D5   rest rest rest rest G5   G5   rest rest
F#5  F5   E5   E5   rest rest C5   C5   rest rest rest rest rest rest rest rest
B4   C5   D5   D5   rest rest D5   D5   rest rest A5   A5   G5   G5   rest rest
E5   E5   rest rest C#5  C#5  rest rest
```
- The same as MIDI numbers (None = rest): `[71, 72, 74, 74, None, None, 74, 74, None, None, None, None, 79, 79, None, None, 78, 77, 76, 76, None, None, 72, 72, None, None, None, None, None, None, None, None, 71, 72, 74, 74, None, None, 74, 74, None, None, 81, 81, 79, 79, None, None, 76, 76, None, None, 73, 73, None, None]`

### "Second Helpings" - used for the start (written as the flag jingle)
- Mood as written: bouncy, off the beat, 188 beats a minute
- One step = 8 TV frames = 160 ms; four steps to a beat = 94 beats a minute; 36 steps, 5.8 s
- Bass pedal: B2 and B3 (MIDI 47 and 59), alternating every step
- Lead, one step per entry:

```
E5   G#5  rest G#5  B5   G#5  E5   E5   D#5  F#5  rest F#5  B5   F#5  D#5  D#5 
C#5  E5   rest E5   G#5  E5   C#5  C#5  B4   D#5  F#5  B5   A5   F#5  D#5  D#5 
E5   G#5  rest G#5 
```
- The same as MIDI numbers (None = rest): `[76, 80, None, 80, 83, 80, 76, 76, 75, 78, None, 78, 83, 78, 75, 75, 73, 76, None, 76, 80, 76, 73, 73, 71, 75, 78, 83, 81, 78, 75, 75, 76, 80, None, 80]`

## What to copy, what to change
- Keep: the octave-bounce bass on one note, the kick on every beat, the off-beat tick, the 500-1,100 Hz lead, the hard grid.
- Change freely: the lead tune, the key, the tempo (Spilt Milk's kick lands 150 times a minute; Second Helpings' 94 times, under a tune written at 188, so its kick is on every other beat of the tune).
- A third tune in the same sound that Grant liked, "Order Up", is a call-and-answer: a short phrase, a gap,
  then the same shape answered higher up. Gaps in the lead are part of the appeal.

Source in the Breakfast Run repository (GitHub, grant-cmyk/breakfastrun, branch claude/breakfast-run-layout-ik0vpe):
the tunes in tools/make_ditties.py, the conversion in tools/make_music_ay.py, the player (jin_go) in src/plateco.asm.
