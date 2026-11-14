; (from strip.asm: here to fill the gap before sq4's page)
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

; INV_DRAW: each slot whose item changed: its icon (or empty)
inv_draw:
        ld hl,INV
        ld de,INV_SH
        ld c,32                 ; slot 0 at x 32 (columns 4-5), then 48, 64
id_1:
        ld a,(de)
        cp (hl)
        jr z,id_next
        ld a,(hl)
        ld (de),a
        push hl
        push de
        push bc
        ld b,170                ; the icon's rows: 170.. (centred in 169-182)
        ld e,a                  ; E = the item
        ld hl,NOS_ICON
id_row:
        push bc
        push hl
        push de
        call scr_addr           ; HL = the slot's left byte (C = its x)
        ex de,hl
        pop bc                  ; C = the item
        pop hl
        ld a,(de)               ; keep the frame: bit 7 left, bit 0 right
        and 0x80
        bit 0,c
        jr z,id_e1
        or (hl)
id_e1:
        ld (de),a
        inc hl
        inc e
        ld a,(de)
        and 0x01
        bit 0,c
        jr z,id_e2
        or (hl)
id_e2:
        ld (de),a
        inc hl
        ld e,c
        pop bc
        inc b
        ld a,b
        cp 170+NOS_ROWS
        jr nz,id_row
        pop bc
        pop de
        pop hl
id_next:
        inc hl
        inc de
        ld a,c
        add a,16
        ld c,a
        cp 32+48
        jr nz,id_1
        ret

; the race box's lines (from strip.asm)
rb_line:
        ld c,3*8
        call scr_addr
        ld (hl),0x3F
        ld b,16
rbl_1:
        inc l
        ld (hl),0xFF
        djnz rbl_1
        inc l
        ld (hl),0xFC
        ret

; (from hud.asm: the message bar's place, lap and time - here to fill the gap)
bar_tick:
        ld a,(you_done)         ; FINISHED nTH stays
        or a
        ret nz
        ld hl,(race_time)       ; the clock: another second?
        ld de,(bar_next)
        or a
        sbc hl,de
        jr c,bt_1
        ld hl,50
        add hl,de
        ld (bar_next),hl
        ld hl,bar_time+3        ; m:ss, a digit at a time
        ld c,22                 ; (C = its column, if only it changes)
        inc (hl)
        ld a,(hl)
        cp '9'+1
        jr c,bt_dig
        ld (hl),'0'
        dec hl
        inc (hl)
        ld a,(hl)
        cp '6'
        jr c,bt_all
        ld (hl),'0'
        dec hl
        dec hl
        inc (hl)
bt_all:
        xor a                   ; more than one digit: the whole time, below
        ld (bar_shown+6),a
        jr bt_1
bt_dig:
        ld a,(msg_timer)        ; one digit: straight on (if the bar is free
        ld b,a                  ; and the time is up to date)
        ld a,(bar_shown+6)
        dec a
        or b
        jr nz,bt_1
        ld b,MSG_ROW
        jp print_at
bt_1:
        ld a,(msg_timer)        ; a message has the bar
        or a
        ret nz
        ld hl,bar_shown         ; one thing a picture: your place (bright white
        ld a,(position)         ; on red, your colour) ...
        cp (hl)
        jr z,bt_lap
        ld (hl),a
        call place_txt
        ld c,1
        ld e,3
        ld a,0x57
        jp msg_at
bt_lap:
        inc hl                  ; ... the lap (black on bright yellow; behind
        ld a,(cars+C_LAPS)      ; the line at the start: 1) ...
        or a
        jr nz,bt_2
        inc a
bt_2:
        add a,'0'
        cp (hl)
        jr z,bt_txt
        ld (hl),a
        ld hl,bar_lap
        ld (hl),a
        ld c,13
        ld e,3
        ld a,0x70
        jp msg_at
bt_txt:
        ld hl,bar_shown+6       ; ... then LAP, and the whole time
        ld a,(hl)
        or a
        ret nz
        inc (hl)
        ld hl,txt_blap
        ld bc,MSG_ROW*256+9
        call print_at
        ld hl,bar_time
        ld bc,MSG_ROW*256+19
        jp print_at

; (from hud.asm: your car's set-up row and its tables - here to fill the gap)
su_gtab:                        ; the grip at each level: gripping, with Q, sliding, both
        db G_GRIP, G_Q, G_SLIDE, G_QSLIDE       ; 1 (0.085 px a frame of sideways speed)
        db 25, 16, 16, 10                        ; 2
        db 29, 18, 18, 12                        ; 3
        db 32, 20, 20, 13                        ; 4
        db 35, 22, 22, 14                        ; 5
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
