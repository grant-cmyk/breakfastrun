; made by tools/make_music_ay.py: the first 24 steps of "Kettle's On, driving" for the ROM's beeper routine - the start jingle
; (Grant, 15 Nov 2026: "At the start of the game before the lights - play the kettle's on jingle"). A step is
; a note of 0.10 s and a HALT. jb_tab: a pitch's cycles (DE) and its period (HL); jb_tune: a pitch's place in it, 255 ends
jb_tab:
        dw 49,856    ; 494 Hz
        dw 62,673    ; 622 Hz
        dw 74,561    ; 740 Hz
        dw 99,413    ; 988 Hz
        dw 83,497    ; 831 Hz
        dw 55,759    ; 554 Hz
        dw 66,634    ; 659 Hz
        dw 111,364    ; 1109 Hz
jb_tune:
        db 0,4,8,12,0,8,16,0,8,4,0,0,20,4,24,8,8,4,20,8,8,8,8,8,255
