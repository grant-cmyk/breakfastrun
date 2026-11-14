; made by tools/make_music.py from tools/make_ditties.py: "Kettle's On, driving" (driving: a steady pulse under the tune, 167 beats a minute), 96 steps of 6 TV frames
MU_STEP equ 6
MU_GATE equ 5
; a byte a step: the note's place in mu_ptab, 254 a rest, 255 the end
; (kept with the title's tables at TD, not in the program: racer.asm gives mu_tune and mu_ptab)
mu_tune_src:
        db 0,3,6,9,0,6,12,0,6
        db 3,0,0,15,3,18,6,6,3
        db 15,6,6,6,6,6,0,3,6
        db 9,0,21,9,0,12,6,0,0
        db 18,12,6,3,15,3,0,0,0
        db 0,0,0,12,18,12,9,18,12
        db 6,0,3,6,0,0,18,18,18
        db 12,18,18,3,0,0,0,0,0
        db 0,3,6,9,0,6,12,9,12
        db 6,0,3,15,18,3,15,6,3
        db 0,0,0,0,0,0
        db 255
; 3 bytes a pitch: the cycles in a burst (one a frame), n, m
mu_ptab_src:
        db 2,109,109    ; note 95
        db 2,86,86    ; note 99
        db 3,72,72    ; note 102
        db 4,54,53    ; note 107
        db 3,64,64    ; note 104
        db 2,97,97    ; note 97
        db 3,81,81    ; note 100
        db 4,48,47    ; note 109
