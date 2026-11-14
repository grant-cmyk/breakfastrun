; made by tools/make_music.py from tools/make_ditties.py: "Kettle's On, driving" (driving: a steady pulse under the tune, 167 beats a minute), 96 steps of 6 TV frames
MU_STEP equ 6
MU_GATE equ 5
; a byte a step: the note's place in mu_ptab, 254 a rest, 255 the end
; (kept with the title's tables at TD, not in the program: racer.asm gives mu_tune and mu_ptab)
mu_tune_src:
        db 0,4,8,12,0,8,16,0,8
        db 4,0,0,20,4,24,8,8,4
        db 20,8,8,8,8,8,0,4,8
        db 12,0,28,12,0,16,8,0,0
        db 24,16,8,4,20,4,0,0,0
        db 0,0,0,16,24,16,12,24,16
        db 8,0,4,8,0,0,24,24,24
        db 16,24,24,4,0,0,0,0,0
        db 0,4,8,12,0,8,16,12,16
        db 8,0,4,20,24,4,20,8,4
        db 0,0,0,0,0,0
        db 255
; 4 bytes a pitch: the cycles in a whole burst, n, m, what a cycle costs (units of 279 T)
mu_ptab_src:
        db 3,147,146,18    ; note 95
        db 4,116,116,14    ; note 99
        db 4,97,97,12    ; note 102
        db 6,73,72,9    ; note 107
        db 5,87,86,11    ; note 104
        db 3,130,130,16    ; note 97
        db 4,110,109,13    ; note 100
        db 7,65,64,8    ; note 109
