; The place plate's code (see below), kept after the page-aligned tables: there is room here
; and none before them (racer.asm includes this after faces.asm).
; ---------------------------------------------------------------------
; THE PLACE PLATE (Grant, 14 Nov 2026: "positional information into the game area, its easier
; for the player to see" - a small solid plate with rounded corners INSIDE the window, top
; right, the table showing all round it; P and your place's figure ("P1 or P2 or P3 instead of
; 3rd or 1st"), L and the lap small beside them, your lap's time so far small under them; and a quick message on a second plate below it - FINAL
; LAP! for its 3 seconds: "3 is good build 3"). Into the buffer each picture, like the gauge.
; A plate is FILLED (pl_fill: its rows by how near the top or bottom they are - clear, two
; rounding rows, solid), then its letters are CUT OUT a byte-wide column at a time (pl_cut).
; Not while the start lights hang there.
; ---------------------------------------------------------------------
; SPEED (the same evening): the plate is COMPOSED once, into pl_bmp (6 bytes a row, 24 rows),
; when your place or lap changes (pl_static, in the slow memory under 0x8000 with the other
; parts that run rarely); each picture only the time's figures are done again there, and the
; whole of pl_bmp is copied into the buffer. It was 12,000 T a picture built from nothing.
PL_B    equ BUF + 2*32 + 17     ; the place plate: buffer row 16 (window line 8), bytes 17-22, 24 rows
PL_M    equ BUF + 5*32 + 0x100 + 17     ; the message's: buffer row 41, bytes 17-22, 13 rows
pl_draw:
        ld a,(lt_on)
        or a
        ret nz
        inc a
        ld (pl_lin),a           ; (the letters go into pl_bmp: its rows are 6 bytes apart)
        ld a,(position)         ; your place (1 before the race) and lap (1 behind the line)
        or a
        jr nz,pd_1
        inc a
pd_1:
        ld b,a
        ld a,(cars+C_LAPS)
        or a
        jr nz,pd_2
        inc a
pd_2:
        ld c,a
        ld hl,(pl_key)          ; changed? the plate afresh
        or a
        sbc hl,bc
        call nz,pl_static
        ld hl,pl_bmp+15*6+1     ; your lap's time so far, small: m:ss.t - its 5 rows solid again,
        ld b,5
pd_3:
        ld (hl),0xFF
        inc hl
        ld (hl),0xFF
        inc hl
        ld (hl),0xFF
        inc hl
        inc hl
        inc hl
        inc hl
        djnz pd_3
        ld hl,(race_time)       ; then the figures cut out
        ld de,(cars+C_LST)
        or a
        sbc hl,de
        call time_fmt
        ld a,(time_txt)
        call pd_d
        ld c,10                 ; m and :
        ld hl,pl_bmp+15*6+1
        call pl_pair
        ld a,(time_txt+3)
        call pd_d
        ld c,a
        ld a,(time_txt+2)
        call pd_d               ; s s
        ld hl,pl_bmp+15*6+2
        call pl_pair
        ld a,(time_txt+5)
        call pd_d
        ld c,a
        ld a,11                 ; . and t
        ld hl,pl_bmp+15*6+3
        call pl_pair
        ld hl,pl_bmp            ; and the plate into the buffer
        ld de,PL_B
        ld b,24
pd_4:
        ld c,255                ; (so the 6 LDIs leave B, the row count, alone)
        ldi
        ldi
        ldi
        ldi
        ldi
        ldi
        ld a,e                  ; DE: back to the row's first byte, and a line down (the buffer
        sub 6                   ; is laid out like the screen)
        ld e,a
        inc d
        ld a,d
        and 7
        jr nz,pd_5
        ld a,e
        add a,32
        ld e,a
        ld a,d
        sub 8
        ld d,a
pd_5:
        djnz pd_4
        ld a,(msg_timer)        ; FINAL LAP! on a second plate while its 3 seconds run
        or a
        ret z
        jp pl_message
pl_pair:                        ; two small figures cut out of the column at HL: number A in bits 7-5,
        push hl                 ; number C beside it in bits 3-1
        call pd_g
        ld a,c
        ld b,d
        ld c,e                  ; BC -> the left one
        call pd_g               ; DE -> the right one
        pop hl
        ld a,5
pp_1:
        push af
        ld a,(de)               ; the right one, moved over to bits 3-1
        rrca
        rrca
        rrca
        rrca
        ld (pp_2+1),a
        ld a,(bc)
pp_2:   or 0
        xor (hl)
        ld (hl),a
        inc bc
        inc de
        call pl_down
        pop af
        dec a
        jr nz,pp_1
        ret
pd_d:                           ; a character of the time -> its figure (a space is a 0)
        sub '0'
        ret nc
        xor a
        ret
pd_g:                           ; DE -> small figure A (pl_g + 5 A)
        ld e,a
        add a,a
        add a,a
        add a,e
        add a,pl_g AND 255
        ld e,a
        ld a,0
        adc a,pl_g/256
        ld d,a
        ret
pl_down:                        ; HL: the next row down - in pl_bmp (pl_lin 1: 6 bytes on) or in the
        ld a,(pl_lin)           ; buffer (0: laid out like the screen)
        or a
        jr z,pw_1
        ld a,l
        add a,6
        ld l,a
        ret nc
        inc h
        ret
pw_1:
        inc h
        ld a,h
        and 7
        ret nz
        ld a,l
        add a,32
        ld l,a
        ld a,h
        sub 8
        ld h,a
        ret
