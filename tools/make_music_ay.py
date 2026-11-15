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
JN = int(os.environ.get('JINGLE', 48))            # the start jingle: the tune's first steps on the ordinary speaker,
LOOP_T = 91                                       # by jin_start's two-voice engine (src/plateco.asm): 89 T a turn of its loop,
bper = lambda hz: round(3500000 / (LOOP_T * 2 * hz))   # a voice flips every `period` turns - so Hz = 3,500,000 / 91 / 2 / period
STEP_T = 0.12 * 3500000; KICK_T = 6 * 7 / 2 * 2500     # a step is 0.12 s; the kick's six flips take 52,500 T of it
with open(os.path.join(ROOT, 'src', 'jingle.asm'), 'w') as f:
    f.write('; made by tools/make_music_ay.py: the first %d steps of "%s" for the start jingle (jin_start, plateco.asm)\n' % (JN, d['name']))
    f.write('; Two voices on the one speaker: the tune, and under it a bass on the key note - low, high, low, high, four steps to\n; a beat - with a kick on each beat and a tick of noise half way: 125 beats a minute.\n')
    f.write('JB_LEN  equ %d                ; turns of the loop in a step ...\nJB_KICK equ %d                 ; ... less these on a beat: the kick takes their time\n' % (round(STEP_T / LOOP_T), round(KICK_T / LOOP_T)))
    f.write('JB_B_LO equ %d                 ; the bass: %.0f Hz\nJB_B_HI equ %d                  ; and %.0f Hz\n' % (bper(md.freq_of(BASS)), (3500000 / LOOP_T / 2) / bper(md.freq_of(BASS)), bper(md.freq_of(BASS + 12)), (3500000 / LOOP_T / 2) / bper(md.freq_of(BASS + 12))))
    f.write('jb_per_src:                     ; each pitch\'s period (kept in the table block at TD: racer.asm gives jb_per, jb_tune)\n')
    for k in kinds:
        hz = md.freq_of(k - LOW); f.write('        db %d    ; %.0f Hz (wanted %.0f)\n' % (bper(hz), (3500000 / LOOP_T / 2) / bper(hz), hz))
    f.write('jb_tune_src:                    ; a pitch a step; 255 ends\n        db ' + ','.join('%d' % kinds.index(m) for m in steps[:JN]) + ',255\n')
print('music_ay.asm: %s, %d steps, %d pitches, %d bytes' % (d['name'], len(steps), len(kinds), len(steps) + 1 + 2 * len(kinds)))
