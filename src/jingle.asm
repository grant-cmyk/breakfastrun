; made by tools/make_music_ay.py: the first 48 steps of "Kettle's On, driving" for the start jingle (jin_start, plateco.asm)
; Two voices on the one speaker: the tune, and under it a bass on the key note - low, high, low, high, four steps to
; a beat - with a kick on each beat and a tick of noise half way: 125 beats a minute.
JB_LEN  equ 4615                ; turns of the loop in a step ...
JB_KICK equ 577                 ; ... less these on a beat: the kick takes their time
JB_B_LO equ 156                 ; the bass: 123 Hz
JB_B_HI equ 78                  ; and 247 Hz
jb_per_src:                     ; each pitch's period (kept in the table block at TD: racer.asm gives jb_per, jb_tune)
        db 39    ; 493 Hz (wanted 494)
        db 31    ; 620 Hz (wanted 622)
        db 26    ; 740 Hz (wanted 740)
        db 19    ; 1012 Hz (wanted 988)
        db 23    ; 836 Hz (wanted 831)
        db 35    ; 549 Hz (wanted 554)
        db 29    ; 663 Hz (wanted 659)
        db 17    ; 1131 Hz (wanted 1109)
jb_tune_src:                    ; a pitch a step; 255 ends
        db 0,1,2,3,0,2,4,0,2,1,0,0,5,1,6,2,2,1,5,2,2,2,2,2,0,1,2,3,0,7,3,0,4,2,0,0,6,4,2,1,5,1,0,0,0,0,0,0,255
