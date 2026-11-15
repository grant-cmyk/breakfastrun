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

; (from hud.asm: your car's set-up row and its tables - here to fill the gap)
su_gtab:                        ; the grip at each level: gripping, with Q, sliding, both
        db G_GRIP, G_Q, G_SLIDE, G_QSLIDE       ; 1 (0.085 px a frame of sideways speed)
        db 20, 11, 11, 7                         ; 2
        db 25, 14, 14, 9                         ; 3
        db 30, 18, 18, 11                        ; 4
        db 36, 22, 22, 14                        ; 5
su_lv:    db 1,1,1              ; your levels: GRIP, SPEED, ACCEL
su_pts:   db 2                  ; points still to spend
su_up:    db 0                  ; 1: no set-up key was down last picture
; (from grip.asm)
yg_gtab: db G_GRIP, G_Q, G_SLIDE, G_QSLIDE   ; (your set-up's grip: su_apply writes it)
yg_pushv: dw G_PUSH             ; ... its push
yg_topv:  dw G_TOP              ; ... its top speed
yg_topn:  dw G_TOP              ; this frame's top speed (twice it with NOS)
        if OPT_TALL
        include "hudtext_flag.asm"
        endif
