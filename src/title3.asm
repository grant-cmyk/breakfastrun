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
        db 8,95,64,   36,0, 86,-3, 40,0, 0,0,0          ; YOU: a circle, anticlockwise
        db 8,66,64,   36,0, 64,4, 64,-4, 40,0, 0        ; CYAN: a figure of eight
        db 152,95,192, 36,0, 86,3, 40,0, 0,0,0          ; GREEN: a circle, clockwise
        db 152,66,192, 36,0, 64,4, 64,-4, 40,0, 0       ; PINK: an eight from the right
        db 8,82,64,   36,0, 103,-5, 40,0, 0,0,0         ; SLIM JANE: two tight rings
td_end:
