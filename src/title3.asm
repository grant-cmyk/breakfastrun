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
; the cast: the five cars in the game today. Each: name (two lines), two lines
; about them - what the game's own notes say of how each drives (tools/make_faces.py,
; consts.asm, cars_init)
t_cast_src:
        db "YOU",0,0,"THE RED CAR.",0,"PLAYER ONE",0
        db "CYAN",0,0,"THE RACER.",0,"FULL THROTTLE",0
        db "GREEN",0,0,"A SLOW TRUCK.",0,"FEW MISTAKES",0
        db "PINK",0,0,"THE TANK.",0,"MOST MISTAKES",0
        db "SLIM",0,"JANE",0,"THE FASTEST.",0,"RARELY WRONG",0
; the runs: start x + 32 - 8, start y + 32 - 14 (the car's middle on the cloth,
; 112 x 96), the way it goes (0 up, 64 right), then parts: steps, turn a step;
; 0 ends it. 2 pixels a step, 25 steps a second; a turn of 3 is a circle of
; 27 pixels, 4 of 20, 5 of 16.
a_runs_src:
        db 8,95,64,   36,0, 86,-3, 34,0, 0,0,0          ; YOU: a circle, anticlockwise
        db 8,66,64,   36,0, 64,4, 64,-4, 34,0, 0        ; CYAN: a figure of eight
        db 152,95,192, 36,0, 86,3, 34,0, 0,0,0          ; GREEN: a circle, clockwise
        db 152,66,192, 36,0, 64,4, 64,-4, 34,0, 0       ; PINK: an eight from the right
        db 8,82,64,   36,0, 103,-5, 34,0, 0,0,0         ; SLIM JANE: two tight rings
        defs 0x5C78 - TD - ($ - td_src)   ; (up to FRAMES ...
        defs 3                  ; ... which the copy sets to 0, once, at start-up)
key_ch_src: db "OPQA "              ; 1UP's keys: left, right, accelerate, brake, NOS
k_patch_src:                        ; ... and where read_keys reads each one
        dw k_left+1, k_right+1, key_go+1, k_brake+1, k_nos+1
k_sp_src:   db "SP",0
t_script_src:
        db 0x80,17,1,14,T_HEAD
        db 0,19,"LAP RECORD",0
        db 0x82,1,2,10,0x72     ; the logo's colours: RUN red, the egg white
        db 0x82,11,2,4,0x77
        db 0x84,1,14,16,0x31    ; the stage: the frame's cells blue on the table ...
        db 0x85,2,12,14,0x29    ; ... the cloth blue on cyan
        db 0x85,18,12,13,T_CARD ; the card
        db 0x85,18,1,13,T_HEAD
        db 5,18,"DRIVER   OF 5",0
        db 0x53,1,T_KEY,"1",0
        db 0x53,3,T_P1,"1UP",0
        db 21,1,"1 PLAYER",0
        db 0x53,11,T_KEY,"2",0
        db 0x53,13,T_HEAD,"2UP",0
        db 21,11,"2 PLAYERS",0
        db 0x53,21,T_KEY,"K",0
        db 0x53,23,T_CARD,"KEYS",0
        db 21,23,"REDEFINE",0
        db 0x97,5,1,21,0xB0     ; (flashing)
        db 23,5
t_press_src: db "PRESS 1 OR 2 TO START",0
        db 0xFF
k_script_src:
        db 0x41,9,T_KEY,"K",0
        db 0x41,12,T_TABLE,"KEYS",0
        db 0x84,9,1,14,T_P1
        db 4,14,"1UP",0
        db 0x85,9,11,14,T_CARD
        db 17,7,"PRESS THE KEY FOR",0
        db 0xFF
t_soon_src: db "   2UP COMING SOON   ",0
t_norec_src: db "-:--.-",0
td_end:
