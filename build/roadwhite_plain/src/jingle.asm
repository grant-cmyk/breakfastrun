; made by tools/make_music_ay.py (JKEYS=ditty3:43,ditty12:47): the jingles, for jin_start / jin_flag (plateco.asm)
; Two voices on the one speaker: the tune, and under it a bass on the key note - low, high, low, high, four steps to
; a beat - with a kick on each beat and a tick of noise half way. Kept in the table block at TD (racer.asm: jc_a, jc_b).
        if 1 - JIN_PART
; the start: "Spilt Milk", 56 steps, 5.6 s
jc_a_src:                       ; what jin_go copies to jc: the tune, the periods, a step's turns, a beat's, the bass low and high
        dw TD + jb_tune_a - td_src, TD + jb_per_a - td_src, 3846, 3269
        db 196, 98
jb_per_a:                       ; each pitch's period
        db 39    ; 493 Hz (wanted 494)
        db 37    ; 520 Hz (wanted 523)
        db 35    ; 549 Hz (wanted 554)
        db 33    ; 583 Hz (wanted 587)
        db 29    ; 663 Hz (wanted 659)
        db 28    ; 687 Hz (wanted 698)
        db 26    ; 740 Hz (wanted 740)
        db 25    ; 769 Hz (wanted 784)
        db 22    ; 874 Hz (wanted 880)
jb_tune_a:                      ; a pitch a step; 254 a rest; 255 ends
        db 0,1,3,3,254,254,3,3,254,254,254,254,7,7,254,254,6,5,4,4,254,254,1,1,254,254,254,254,254,254,254,254,0,1,3,3,254,254,3,3,254,254,8,8,7,7,254,254,4,4,254,254,2,2,254,254,255
        endif
        if JIN_PART
; the chequered flag: "Second Helpings", 36 steps, 5.8 s
jc_b_src:                       ; what jin_go copies to jc: the tune, the periods, a step's turns, a beat's, the bass low and high
        dw TD + jb_tune_b - td_src, TD + jb_per_b - td_src, 6154, 5577
        db 156, 78
jb_per_b:                       ; each pitch's period
        db 39    ; 493 Hz (wanted 494)
        db 35    ; 549 Hz (wanted 554)
        db 31    ; 620 Hz (wanted 622)
        db 29    ; 663 Hz (wanted 659)
        db 26    ; 740 Hz (wanted 740)
        db 23    ; 836 Hz (wanted 831)
        db 22    ; 874 Hz (wanted 880)
        db 19    ; 1012 Hz (wanted 988)
jb_tune_b:                      ; a pitch a step; 254 a rest; 255 ends
        db 3,5,254,5,7,5,3,3,2,4,254,4,7,4,2,2,1,3,254,3,5,3,1,1,0,2,4,7,6,4,2,2,3,5,254,5,255
        endif
