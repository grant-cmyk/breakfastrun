; (from strip.asm: here to fill the gap before sq4's page)
        if OPT_PIT              ; (the pit talk's: left out with it)
line_x:                         ; MSG_P at a line: MSG_X = its centred start
        ld hl,(MSG_P)
        ld b,0
lx_1:
        ld a,(hl)
        or a
        jr z,lx_2
        cp '|'
        jr z,lx_2
        inc b
        inc hl
        jr lx_1
lx_2:
        ld a,b                  ; x = BOX_X + (BOX_W - (4n - 1)) / 2
        add a,a
        add a,a
        dec a
        neg
        add a,BOX_W
        srl a
        add a,BOX_X
        ld (MSG_X),a
        ret

        endif
; THE TITLE'S RUN (Grant, 15 Nov 2026: speed lines, "the line through the middle", "two colours -
; top and bottom": S4 of docs/design/run_split_options.png). Three drawn letters, 6 x 8, each
; pixel 3 across and 2 down, leaning a pixel a row, from x 114 at lines 40-55; lines 47 and 48 -
; either side of the join of the two character rows - left out: that is the cut, and each row
; has an ink of its own (the title's list: yellow above, red below). Then the speed lines.
; (Here, where the message bar's code was: the gap before sq4's page.)
t_run:
        ld hl,t_runl
        ld d,114                ; D = the letter's x
trn_let:
        ld e,0                  ; E = its row, 0..7
trn_row:
        ld a,(hl)
        inc hl
        push hl
        ld h,a                  ; H = the row's 6 pixels, from the top bit
        ld a,d
        add a,7
        sub e
        ld c,a                  ; x: the lean
        ld a,e
        add a,a
        add a,40
        ld b,a                  ; y: two lines a row
        ld l,6
trn_bit:
        sla h
        jr nc,trn_adv
        ld a,e                  ; (row 4's first line is 48, row 3's second 47: the cut)
        cp 4
        call nz,trn_3
        ld a,e
        cp 3
        jr z,trn_adv
        inc b
        call trn_3
        dec b
trn_adv:
        inc c
        inc c
        inc c
        dec l
        jr nz,trn_bit
        pop hl
        inc e
        bit 3,e
        jr z,trn_row
        ld a,d
        add a,21
        ld d,a
        cp 114+63
        jr nz,trn_let
        ld e,6                  ; the speed lines: 6 lines of 3 bytes from column 11 (HL = t_rlin)
trn_ln:
        ld b,(hl)
        inc hl
        ld c,88
        push de
        push hl
        call scr_addr
        ex de,hl
        pop hl
        ldi
        ldi
        ldi
        pop de
        dec e
        jr nz,trn_ln
        ret
trn_3:                           ; 3 pixels from (C, B)
        push hl
        push bc
        call trn_p
        inc c
        call trn_p
        inc c
        call trn_p
        pop bc
        pop hl
        ret
trn_p:                           ; the pixel at (C, B)
        call scr_addr
        ld a,c
        and 7
        ld a,0x80
        jr z,trn_p2
        push bc
        ld b,a                  ; (B = 0x80: the count comes from C again)
        ld a,c
        and 7
        ld c,a
        ld a,b
trn_p1:
        rrca
        dec c
        jr nz,trn_p1
        pop bc
trn_p2:
        or (hl)
        ld (hl),a
        ret
t_runl:
        db %11111000,%11001100,%11001100,%11111000,%11011000,%11001100,%11001100,%11001100   ; R
        db %11001100,%11001100,%11001100,%11001100,%11001100,%11001100,%11001100,%01111000   ; U
        db %11001100,%11101100,%11111100,%11111100,%11011100,%11001100,%11001100,%11001100   ; N
t_rlin:                         ; the speed lines: a line, its 3 bytes (x 88-111)
        db 42,0xFF,0xFF,0xF8, 43,0xFF,0xFF,0xF8, 46,0x03,0xFF,0xFE
        db 49,0x03,0xFF,0xFE, 52,0xFF,0xFF,0xF8, 53,0xFF,0xFF,0xF8

; YOUR LAP TIMES (Grant, 15 Nov 2026: "at the end of the race in the HUD, can you show the laptimes
; for your racer - so all laps"). yl_note keeps each as you finish it; yl_show, at the race's
; end, lists them under YOUR RACE (rows 19-21): the lap, its time.
yl_note:                        ; HL = a lap's time, IX = whose (kept: HL)
        ld a,(ix+C_KIND)
        or a
        ret nz
        ld a,(ix+C_LAPS)
        sub 2
        cp LAPS
        ret nc
        add a,a
        add a,you_laps AND 255
        ld e,a
        ld a,0
        adc a,you_laps/256
        ld d,a
        ex de,hl
        ld (hl),e
        inc hl
        ld (hl),d
        ex de,hl
        push hl                 ; a lap done: a high beep, a quarter of a second (Grant, 15 Nov 2026:
        if OPT_SND2             ; "As you go past a lap, make a sound")
        ld hl,3*256+16          ; (SND2: its own chime, 16 frames - racer.asm fx_bonk)
        else
        ld hl,14*256+14
        endif
        ld (snd_fxt),hl
        pop hl
        jr yl_show              ; and shown at once
yl_show:                        ; (called as each lap is done: HL and IX kept for lap_timed)
        push hl
        push ix
        call yl_all
        pop ix
        pop hl
        ret
yl_all:
        xor a
yl_1:
        ld (yl_n),a
        add a,a
        ld e,a
        ld d,0
        ld hl,you_laps
        add hl,de
        ld a,(hl)
        inc hl
        ld h,(hl)
        ld l,a
        or h
        ret z                   ; (a lap not done: you did not finish)
        call time_fmt
        call yl_y
        ld c,29
        ld hl,time_txt+2
        call st_text
        call yl_y               ; LAP, the lap, its time (Grant, 15 Nov 2026: "is there space to have lap written there")
        ld a,b
        ld (MSG_Y),a
        ld a,209
        ld (MSG_X),a
        ld hl,pd_t5
        call sm_text
        ld a,(yl_n)             ; (its number straight after LAP, in the same letters)
        add a,'1'
        call glyph
        ld a,(yl_n)
        inc a
        cp LAPS
        jr nz,yl_1
        ret
yl_y:                           ; B = lap yl_n's line: 153, 161, 169 (rows 19-21)
        ld a,(yl_n)
        add a,a
        add a,a
        add a,a
        add a,153
        ld b,a
        ret
yl_n:   db 0

; the podium's words and figures (plate_slow.asm has its code: the room under 0x8000 is full)
pd_t1:  db "CHEQUERED FLAG",0
pd_t2:  db "WINNER",0
pd_t3:  db "FASTEST LAP",0
pd_t4:  db "PRESS ANY KEY",0
pd_t5:  db "LAP ",0
pd_d1:  db "1",0
pd_d2:  db "2",0
pd_d3:  db "3",0
        if 1-OPT_CHOOSE         ; (CHOOSE: seven names, in choose.asm)
pd_names:                       ; by car: you, cyan, green, pink, white (Grant, 15 Nov 2026: "each player needs a name")
        db "YOU",0,"FRANK",0,"SPIKE",0,"BRUNO",0,"JANE",0
        endif
sm_dig:                         ; the small figures 0-9 and the colon, as the letters: 15 bits, top row first
        db 0xF6,0xDE   ; 0
        db 0x59,0x2E   ; 1
        db 0xE7,0xCE   ; 2
        db 0xE7,0x9E   ; 3
        db 0xB7,0x92   ; 4
        db 0xF3,0x9E   ; 5
        db 0xF3,0xDE   ; 6
        db 0xE5,0x24   ; 7
        db 0xF7,0xDE   ; 8
        db 0xF7,0x9E   ; 9
        db 0x08,0x20   ; :

pd_t6:  db "FINISHED ",0
pd_t7:  db "YOUR RACE",0
; (from hud.asm: your car's set-up row and its tables - here to fill the gap)
        if OPT_SIMPLE = 0       ; (SIMPLE: not used - the memory hunt, 24 Nov 2026)
su_gtab:                        ; the grip at each level: gripping, with Q, sliding, both
        db G_GRIP, G_Q, G_SLIDE, G_QSLIDE       ; 1 (0.085 px a frame of sideways speed)
        if OPT_CARDS            ; (CARDS: each level of grip you buy is one more point on your card's grip rating - cards.asm)
        db CD_L2_G, CD_L2_Q, CD_L2_S, CD_L2_B
        db CD_L3_G, CD_L3_Q, CD_L3_S, CD_L3_B
        db CD_L4_G, CD_L4_Q, CD_L4_S, CD_L4_B
        db CD_L5_G, CD_L5_Q, CD_L5_S, CD_L5_B
        else
        if OPT_CHOOSE
        db 18, 9, 9, 6                           ; 2 (CHOOSE: the GRIP extra - about an eighth more)
        else
        db 20, 11, 11, 7                         ; 2
        endif
        db 25, 14, 14, 9                         ; 3
        db 30, 18, 18, 11                        ; 4
        db 36, 22, 22, 14                        ; 5
        endif                   ; (CARDS)
        endif                   ; (SIMPLE)
su_lv:    db 1,1,1              ; your levels: GRIP, SPEED, ACCEL
su_pts:   db 2                  ; points still to spend
su_up:    db 0                  ; 1: no set-up key was down last picture
; (from grip.asm)
yg_gtab: db G_GRIP, G_Q, G_SLIDE, G_QSLIDE   ; (your set-up's grip: su_apply writes it)
yg_pushv: dw G_PUSH             ; ... its push
yg_topv:  dw G_TOP              ; ... its top speed
yg_topn:  dw G_TOP              ; this frame's top speed (twice it with NOS)
; (hudtext_flag.asm's two texts were here: nothing showed them any more - 29 bytes, 15 Nov 2026)
; JB_KEY: the jingle's step A kept, and A KEY SKIPS THE JINGLE (Grant, 16 Nov 2026: "key should skip a jingle").
; Looked for once a step. The keys that count are the number rows and the two bottom rows (1-0, SPACE, ENTER,
; SYMBOL SHIFT, CAPS SHIFT, Z X C V, B N M, H J K L): NOT the rows of Q, A and P, so the accelerator, brake or
; steering held over the finish line does not cut the flag's jingle short. Called from jb_1 (plateco.asm) in
; place of its 3-byte LD (jb_n+1),A, and kept out of the jingle player on purpose: on 16 Nov 2026 a build with
; 23 bytes more in the player - even 23 unused bytes - failed drive_test's ramming check (the computer car put
; in front of you jumped 66 pixels down in one frame). Something later in the program depends on where it
; sits; not found yet.
jb_key:
        ld (jb_n+1),a
        ld a,0x26               ; (the address lines low for those five rows)
        in a,(254)
        or 0xE0
        inc a
        ret z                   ; none of them down
        pop af                  ; (the call's return: we leave by jb_end instead)
        jp jb_end
; CF_BLINK: the crew chief blinks (Grant, 15 Nov 2026: "His eyes will just become one dot for a brief
; period and then two pixels each again"). His face is kept on the screen under the window (screen_once);
; its eyes are 2 pixels high, in rows 5 and 6. For 2 pictures in every 32 the upper pixel of each is
; taken away. Then fl_draw, which copies the face into the window while he is talking.
CF_EYES equ 0x5000 + 6*32 + 5*256 + 16  ; the face's row 5: screen line 181, columns 16-17
cf_blink:
        ld a,(renders)
        and 31
        cp 2
        ld de,0x4E74            ; (the row's two bytes, eyes open: .XXX.X.. .X..XXX.)
        jr nc,cb_1
        ld de,0x0E70            ; (... and shut)
cb_1:
        ld (CF_EYES),de
        jp cf_wave              ; (plate_slow.asm; it ends in fl_draw)
