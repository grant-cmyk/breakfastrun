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
; outside of the title screen"): its middle's start x, y + 18, the way it goes (64 = right),
; then parts: steps, turn a step; 0 ends it (and it starts again). 2 pixels a step, 25 steps a
; second; a turn of 4 for 16 steps is a quarter circle of 20 pixels. Its middle keeps 12 pixels
; from the screen's edge: the middle of the 3-cell border of checks.
a_runs_src:
        db 32,30,64,  96,0, 16,4, 64,0, 16,4, 96,0, 16,4, 64,0, 16,4, 0
; POD_ANIM: the podium's faces move (Grant, 15 Nov 2026). Called each TV frame while the podium is up
; (main_wait), it ends in hud_over. Every 32 frames a step (pa_step, plate_slow.asm): the everyday face,
; the eyes, the everyday face, then happy for the winner and sad for second and third. Each face is drawn
; afresh as every day and the step's rows laid over it (faces_mood). The title's row of faces does the
; same with happy (t_anim, plate_slow.asm). It runs here in the table block (in the room before FRAMES
; that the title's old tables left): its own calls go through the equs in racer.asm.
pod_anim_src:
        call pa_step
        jr z,pa_out
        ld d,1                  ; D = the mood's frame: 1 happy (the winner), then 2 sad
        ld hl,order
        ld bc,0x070C
        call pa_one
        ld bc,0x0808
        call pa_one
        ld bc,0x0910
        call pa_one
pa_out:
        jp hud_over
pa_one_src:                     ; the car at (HL)'s face in cells B, C for step E
        ld a,(hl)
        inc hl
        push hl
        call pa_car
        pop hl
        inc e                   ; (the next face a step on: Grant, 16 Nov 2026, "have the animations happening at
                                ; different cycles, they look too synchronised")
        ld d,2
        ret
pa_car_src:                     ; car A's face in cells B, C for step E (mood frame D); E and D kept
        push de
        push bc
        push af
        call pd_face
        pop af
        pop bc
        pop de
        bit 0,e
        ret z                   ; (steps 0 and 2: as every day)
        if OPT_CHOOSE
        call who_a              ; CHOOSE: the driver in this car today
        endif
        ld l,a
        add a,a
        add a,l                 ; the car's three lists: eyes, happy, sad
        bit 1,e
        jr z,po_0
        add a,d
po_0:
        push de
        call pa_face
        pop de
        ret
pa_face_src:                    ; list A of faces_mood laid over the face in cells B, C
        if OPT_CHOOSE
        ld hl,(HP_MOOD)         ; (CHOOSE: seven drivers' lists, above the copy routine)
        else
        ld hl,faces_mood
        endif
pf_s0:
        or a
        jr z,pf_a
pf_s1:
        ld e,(hl)
        inc hl
        inc e
        jr z,pf_s2
        inc hl
        inc hl
        jr pf_s1
pf_s2:
        dec a
        jr pf_s0
pf_a:
        ld a,(hl)               ; a row (0-15), or 0xFF: the end
        inc hl
        cp 16
        ret nc
        push hl
        push bc
        cp 8
        jr c,pf_a1
        inc b
pf_a1:
        and 7
        ld e,a
        call cell_addr
        ld a,h
        add a,e
        ld h,a
        ex de,hl
        pop bc
        pop hl
        ld a,(hl)
        ld (de),a
        inc hl
        inc e
        ld a,(hl)
        ld (de),a
        inc hl
        jr pf_a
t_name_src:                     ; the title: the driver's name under the face, in the small letters, centred
        ld a,(t_tmp+1)          ; on it (Grant, 15 Nov 2026: "have each persons name underneath"). It runs
        inc a                   ; in the table block, at t_name: nothing in it is tied to where it is.
        add a,a
        add a,a
        add a,a
        ld c,a
        ld b,146
        ld a,(t_tmp)
        jp pd_name
JIN_PART defl 1
        include "jingle.asm"    ; the flag jingle's notes
; (the keys' two small tables sit here, before FRAMES, since 15 Nov 2026: the block's end needed their 15 bytes)
key_ch_src: db "OPQA "              ; 1UP's keys: left, right, accelerate, brake, NOS
k_patch_src:                        ; ... and where read_keys reads each one
        dw k_left+1, k_right+1, k_go+1, k_brake+1, k_nos+1
        defs 0x5C78 - TD - ($ - td_src)   ; (up to FRAMES ...
        defs 3                  ; ... which the copy sets to 0, once, at start-up)
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
