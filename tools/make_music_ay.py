"""The race tune for the AY sound chip (Grant, 15 Nov 2026: "go ahead on ay-version"): src/music_ay.asm
from a driving tune in tools/make_ditties.py. The beeper could not carry a tune under the game
("no suggestion of music, just background beeping"); the AY plays by itself once its registers
are set, so the interrupt only has to set them - about 250 T a frame.
Usage: python3 tools/make_music_ay.py [ditty key, default ditty13 = Kettle's On, driving]
  mu_tune: a byte a step (MU_STEP frames): the note's place in mu_ptab (2 x its number), 254 a
           rest, 255 the end (it starts again)
  mu_ptab: 2 bytes a pitch: the AY's tone period (fine, coarse)
The bass (channel B) is a pedal on the tune's key note, low then an octave up, a step each; the
hat (channel C, noise) ticks on the off-beat. LOW: semitones the melody is under the music box."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_ditties as md
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
key = sys.argv[1] if len(sys.argv) > 1 else 'ditty13'
d = next(x for x in md.DITTIES + md.RACERS if x['key'] == key)
AY_HZ = 1773400                                   # the 128K's AY clock
LOW = int(os.environ.get('LOW', 24))             # two octaves: 495-1,108 Hz, a singing register (12 was shrill on paper: 990-2,217 Hz)
BASS = int(os.environ.get('BASS', 47))            # MIDI B2: the pedal (Kettle's On is in B)
period = lambda midi: round(AY_HZ / 16 / md.freq_of(midi))
STEP = d.get('step'); assert STEP
steps = [midi for t, midi, length in md.notes_of(d)]
kinds = []
for m in steps:
    if m is not None and m not in kinds: kinds.append(m)
with open(os.path.join(ROOT, 'src', 'music_ay.asm'), 'w') as f:
    f.write('; made by tools/make_music_ay.py from tools/make_ditties.py: "%s", %d steps of %d TV frames, for the AY chip\n' % (d['name'], len(steps), STEP))
    f.write('MU_STEP equ %d\nAY_BASS_LO equ %d                ; the bass pedal\'s tone periods: MIDI %d, and an octave up\nAY_BASS_HI equ %d\n' % (STEP, period(BASS), BASS, period(BASS + 12)))
    f.write('; a byte a step: the note\'s place in mu_ptab, 254 a rest, 255 the end\nmu_tune_src:\n')
    for q in range(0, len(steps), 12):
        f.write('        db ' + ','.join('254' if m is None else '%d' % (kinds.index(m) * 2) for m in steps[q:q + 12]) + '\n')
    f.write('        db 255\n; a word a pitch: the AY tone period\nmu_ptab_src:\n')
    for k in kinds:
        f.write('        dw %d    ; note %d, %.0f Hz\n' % (period(k - LOW), k - LOW, AY_HZ / 16 / period(k - LOW)))
JN = int(os.environ.get('JINGLE', 24))            # the start jingle: the tune's first steps on the ordinary speaker
with open(os.path.join(ROOT, 'src', 'jingle.asm'), 'w') as f:    # (the ROM's BEEPER at 0x03B5: DE = cycles, HL = 437,500 / Hz - 30)
    f.write('; made by tools/make_music_ay.py: the first %d steps of "%s" for the ROM\'s beeper routine - the start jingle\n' % (JN, d['name']))
    f.write('; (Grant, 15 Nov 2026: "At the start of the game before the lights - play the kettle\'s on jingle"). A step is\n; a note of 0.10 s and a HALT. jb_tab: a pitch\'s cycles (DE) and its period (HL); jb_tune: a pitch\'s place in it, 255 ends\njb_tab:\n')
    for k in kinds:
        hz = md.freq_of(k - LOW); f.write('        dw %d,%d    ; %.0f Hz\n' % (round(hz * 0.10), round(437500 / hz - 30.125), hz))
    f.write('jb_tune:\n        db ' + ','.join('%d' % (kinds.index(m) * 4) for m in steps[:JN]) + ',255\n')
print('music_ay.asm: %s, %d steps, %d pitches, %d bytes' % (d['name'], len(steps), len(kinds), len(steps) + 1 + 2 * len(kinds)))
