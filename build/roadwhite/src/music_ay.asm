; made by tools/make_music_ay.py from tools/make_ditties.py: "Kettle's On, driving", 96 steps of 6 TV frames, for the AY chip
MU_STEP equ 6
AY_BASS_LO equ 898                ; the bass pedal's tone periods: MIDI 47, and an octave up
AY_BASS_HI equ 449
; a byte a step: the note's place in mu_ptab, 254 a rest, 255 the end
mu_tune_src:
        db 0,2,4,6,0,4,8,0,4,2,0,0
        db 10,2,12,4,4,2,10,4,4,4,4,4
        db 0,2,4,6,0,14,6,0,8,4,0,0
        db 12,8,4,2,10,2,0,0,0,0,0,0
        db 8,12,8,6,12,8,4,0,2,4,0,0
        db 12,12,12,8,12,12,2,0,0,0,0,0
        db 0,2,4,6,0,4,8,6,8,4,0,2
        db 10,12,2,10,4,2,0,0,0,0,0,0
        db 255
; a word a pitch: the AY tone period
mu_ptab_src:
        dw 224    ; note 71, 495 Hz
        dw 178    ; note 75, 623 Hz
        dw 150    ; note 78, 739 Hz
        dw 112    ; note 83, 990 Hz
        dw 133    ; note 80, 833 Hz
        dw 200    ; note 73, 554 Hz
        dw 168    ; note 76, 660 Hz
        dw 100    ; note 85, 1108 Hz
