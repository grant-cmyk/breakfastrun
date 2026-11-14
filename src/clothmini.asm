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
        ld b,2
        jp print_at
bt_1:
        ld a,(msg_timer)        ; a message has the bar
        or a
        ret nz
        ld a,(position)         ; your place: "1ST".."5TH"
        dec a
        add a,a
        add a,a
        ld e,a
        ld d,0
        ld hl,txt_places
        add hl,de
        ld de,bar_shown
        ld c,1
        ld a,0x57               ; (bright white on red)
        call bar_3
        ld a,(cars+C_LAPS)      ; the lap (behind the line at the start: 1)
        or a
        jr nz,bt_2
        inc a
bt_2:
        add a,'0'
        ld hl,bar_lap
        ld (hl),a
        ld c,12
        ld a,0x70               ; (black on bright yellow)
        call bar_3
        ld a,(de)               ; the small text: LAP, and the whole time
        or a
        ret nz
        inc a
        ld (de),a
        ld hl,txt_blap
        ld b,2
        ld c,9
        call print_at
        ld hl,bar_time
        ld b,2
        ld c,19
        jp print_at
; bar_3: 3 big letters at HL against those shown at DE, from column C in
; colour A: the first that differs is drawn, and that is all for this picture
bar_3:
        ld (pb_attr),a
        ld b,3
b3_1:
        ld a,(de)
        cp (hl)
        jr nz,b3_draw
        inc hl
        inc de
        inc c
        inc c
        djnz b3_1
        ret
b3_draw:
        ld a,(hl)
        ld (de),a
        ld (txt_digit),a
        pop hl                  ; (not back to bar_tick)
        ld hl,txt_digit
        ld b,1
        ld a,(pb_attr)
        jp print_big

; (from hud.asm: your car's set-up row and its tables - here to fill the gap)
; SU_DRAW: the set-up row: "1G#####  2S#####  3A#####" from column 0
su_draw:
        ld hl,su_lv
        ld c,0                  ; C = the part's first column: 0, 8, 16
su_d1:
        push hl
        push bc
        ld a,c                  ; its key - only while it can be pressed
        rrca
        rrca
        rrca
        ld e,a
        add a,'1'
        ld b,a
        ld a,(race_on)
        or a
        jr z,su_d2
        ld b,' '
su_d2:
        ld hl,su_txt
        ld (hl),b
        ld d,0                  ; its letter
        ld hl,su_names
        add hl,de
        ld a,(hl)
        ld hl,su_txt+1
        ld (hl),a
        dec hl
        ld b,23
        call print_at
        pop bc
        pop hl
        push hl
        push bc
        ld d,(hl)               ; D = filled pips to go, E = pips to go
        ld e,5
        inc c
su_d3:
        inc c
        push de
        push bc
        ld a,d
        or a
        ld de,su_pip
        jr nz,su_d4
        ld de,su_pip+8
su_d4:
        ld b,23
        call tr_glyph
        pop bc
        pop de
        ld a,d
        or a
        jr z,su_d5
        dec d
su_d5:
        dec e
        jr nz,su_d3
        pop bc
        pop hl
        inc hl
        ld a,c
        add a,8
        ld c,a
        cp 24
        jr nz,su_d1
        ret
su_pip:   db 0,0x7E,0x7E,0x7E,0x7E,0x7E,0x7E,0   ; a level you have
          db 0,0x7E,0x42,0x42,0x42,0x42,0x7E,0   ; ... and one you have not
su_gtab:                        ; the grip at each level: gripping, with Q, sliding, both
        db G_GRIP, G_Q, G_SLIDE, G_QSLIDE       ; 1 (0.085 px a frame of sideways speed)
        db 25, 16, 16, 10                        ; 2
        db 29, 18, 18, 12                        ; 3
        db 32, 20, 20, 13                        ; 4
        db 35, 22, 22, 14                        ; 5
su_lv:    db 1,1,1              ; your levels: GRIP, SPEED, ACCEL
su_pts:   db 2                  ; points still to spend
su_up:    db 0                  ; 1: no set-up key was down last picture
su_txt:   db "1G",0
su_names: db "GSA"
