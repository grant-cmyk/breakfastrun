; =====================================================================
; THE TITLE SCREEN'S TABLES (see title.asm) that do not fit beside its code:
; loaded in the start-up area and copied once to TD (0x5B4C), where they stay.
; Use them as TD + name_src - td_src.
; =====================================================================
td_src:
k_chars_src:                        ; the keyboard's 40 keys, as k_scan numbers them (0: not offered)
        db 0,"ZXCV","ASDFG","QWERT","12345","09876","POIUY",0,"LKJH"," ",0,"MNB"
k_names_src:
        db "LEFT",0,"RIGHT",0,"ACCELERATE",0,"BRAKE",0,"NOS",0
; your car's lap of the title screen's edge (Grant, 15 Nov 2026: "have my car racing around the
; outside of the title screen"): its middle's start x + 8, y + 18, the way it goes (64 = right),
; then parts: steps, turn a step; 0 ends it (and it starts again). 2 pixels a step, 25 steps a
; second; a turn of 4 for 16 steps is a quarter circle of 20 pixels. Its middle keeps 12 pixels
; from the screen's edge: the middle of the 3-cell border of checks.
a_runs_src:
        db 40,30,64,  96,0, 16,4, 64,0, 16,4, 96,0, 16,4, 64,0, 16,4, 0
        defs 0x5C78 - TD - ($ - td_src)   ; (up to FRAMES ...
        defs 3                  ; ... which the copy sets to 0, once, at start-up)
key_ch_src: db "OPQA "              ; 1UP's keys: left, right, accelerate, brake, NOS
k_patch_src:                        ; ... and where read_keys reads each one
        dw k_left+1, k_right+1, k_go+1, k_brake+1, k_nos+1
k_sp_src:   db "SP",0
k_script_src:
        db 0x41,9,T_KEY,"K",0
        db 0x41,12,T_TABLE,"KEYS",0
        db 0x84,9,1,14,T_P1
        db 4,14,"1UP",0
        db 0x85,9,11,14,T_CARD
        db 17,7,"PRESS THE KEY FOR",0
        db 0xFF
t_norec_src: db "-:--.-",0
td_end:
