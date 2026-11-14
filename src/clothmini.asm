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
        ld a,(race_on)          ; the clock runs from green to your finish
        or a
        jr z,bt_1
        ld a,(you_done)
        or a
        jr nz,bt_1
        ld hl,(race_time)       ; another second?
        ld de,(bar_next)
        or a
        sbc hl,de
        jr c,bt_1
        ld hl,50
        add hl,de
        ld (bar_next),hl
        ld hl,bar_time+3        ; m:ss, a digit at a time
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
        ld a,(bar_shown+6)      ; one digit: straight on, if the time is up to date
        dec a
        jr nz,bt_1
        ld bc,23*256+9
        jp print_at
bt_1:
        ld a,(position)         ; ONE thing a picture. Your place, large: the first of
        call place_txt          ; its 3 letters that is not as shown
        ld de,bar_shown
        ld bc,0x0304
bt_p:
        ld a,(de)
        cp (hl)
        jr nz,bt_big
        inc hl
        inc de
        inc c
        inc c
        djnz bt_p
        ld a,(race_on)          ; the strip: PRESS Q before the start,
        or a
        ld a,1
        jr z,bt_s
        ld a,(you_done)         ; FINISHED! at the flag,
        or a
        ld a,3
        jr nz,bt_s
        ld a,(msg_timer)        ; FINAL LAP for its 3 s,
        or a
        ld a,2
        jr nz,bt_s
        ld a,(cars+C_LAPS)      ; else LAP n/3 (behind the line at the start: 1)
        or a
        jr nz,bt_2
        inc a
bt_2:
        add a,'0'
bt_s:
        ex de,hl                ; (HL = bar_shown + 3: the strip as shown)
        cp (hl)
        jr z,bt_txt
        ld (hl),a
        cp 4
        jr nc,bt_ln
        ld e,a                  ; text 1..3: txt_strip + (n - 1) * 10
        add a,a
        add a,a
        add a,e
        add a,a
        sub 10
        ld e,a
        ld d,0
        ld hl,txt_strip
        add hl,de
        jr bt_sp
bt_ln:
        ld hl,bar_lap
        ld (bar_lap+5),a
bt_sp:
        ld bc,22*256+1
        jp print_at
bt_txt:
        ld hl,bar_shown+6       ; then TIME and the whole time
        ld a,(hl)
        or a
        ret nz
        inc (hl)
        ld hl,txt_time
        ld bc,23*256+1
        call print_at
        ld hl,bar_time
        ld bc,23*256+6
        jp print_at
bt_big:
        ld a,(hl)               ; one big letter: row 20, column C, white on your red
        ld (de),a
        ld (txt_digit),a
        ld hl,txt_digit
        ld b,20
        ld a,0x57
        jp print_big

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
