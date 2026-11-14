; The place plate's code (see below), kept after the page-aligned tables: there is room here
; and none before them (racer.asm includes this after faces.asm).
; ---------------------------------------------------------------------
; THE PLACE PLATE (Grant, 14 Nov 2026: "positional information into the game area, its easier
; for the player to see" - a small solid plate with rounded corners INSIDE the window, top
; right, the table showing all round it; an ordinary figure with a small raised st / nd / rd /
; th, the lap under it in small letters; and a quick message on a second plate below it - FINAL
; LAP! for its 3 seconds: "3 is good build 3"). Into the buffer each picture, like the gauge.
; A plate is FILLED (pl_fill: its rows by how near the top or bottom they are - clear, two
; rounding rows, solid), then its letters are CUT OUT a byte-wide column at a time (pl_cut).
; Not while the start lights hang there.
; ---------------------------------------------------------------------
PL_B    equ BUF + 2*32 + 18     ; the place plate: buffer row 16 (window line 8), bytes 18-22, 24 rows
PL_M    equ BUF + 5*32 + 0x100 + 17     ; the message's: buffer row 41, bytes 17-22, 13 rows
pl_draw:
        ld a,(lt_on)
        or a
        ret nz
        ld hl,PL_B
        ld bc,24*256+5
        call pl_fill
        ld a,(position)         ; the figure: the ROM's own, 8 x 8 (1 before the race)
        or a
        jr nz,pd_1
        inc a
pd_1:
        dec a
        push af
        add a,a
        add a,a
        add a,a
        add a,0x88              ; ("1" is at 0x3D88)
        ld e,a
        ld d,0x3D
        ld hl,PL_B+4*0x100+1
        ld b,8
        call pl_cut
        pop af                  ; st, nd, rd, th (and th)
        cp 3
        jr c,pd_2
        ld a,3
pd_2:
        ld de,pl_suf
        call pd_x5
        ld hl,PL_B+4*0x100+2
        call pl_cut5
        ld hl,PL_B+32+7*0x100+1 ; LAP  /3
        ld de,pl_lap
        ld c,4
        call pl_cols
        ld a,(cars+C_LAPS)      ; and its figure (behind the line at the start: 1)
        or a
        jr z,pd_3
        dec a
        cp 3
        jr c,pd_3
        ld a,2
pd_3:
        ld de,pl_dig
        call pd_x5
        ld hl,PL_B+32+7*0x100+3
        call pl_cut5
        ld a,(msg_timer)        ; FINAL LAP! while the strip says so
        or a
        ret z
        ld hl,PL_M
        ld bc,13*256+6
        call pl_fill
        ld hl,PL_M+4*0x100
        ld de,pl_msg
        ld c,6
pl_cols:                        ; C columns of 5 rows from DE, at HL and on to the right
        push hl
        call pl_cut5
        pop hl
        inc l
        dec c
        jr nz,pl_cols
        ret
pd_x5:                          ; DE += 5 x A
        ld l,a
        add a,a
        add a,a
        add a,l
        add a,e
        ld e,a
        ret nc
        inc d
        ret
pl_cut5:
        ld b,5
pl_cut:                         ; B rows of the column at HL: the bits of (DE) on cut out of the plate
        ld a,(de)
        xor (hl)
        ld (hl),a
        inc de
        call pl_down
        djnz pl_cut
        ret
pl_down:                        ; HL: the next line down (the buffer is laid out like the screen)
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
pl_fill:                        ; HL = its top left byte, B = rows, C = bytes: a plate, 3 pixels in at each side
        ld e,b
pf_1:
        ld a,e                  ; how near the top or the bottom: 0 clear, 1 and 2 the rounded
        sub b                   ; corners, 3 on solid
        ld d,a
        ld a,b
        dec a
        cp d
        jr c,pf_2
        ld a,d
pf_2:
        cp 3
        jr c,pf_3
        ld a,3
pf_3:
        push hl
        push bc
        push de
        ld d,a
        add a,a
        add a,d
        add a,pf_tab AND 255
        ld e,a
        ld a,0
        adc a,pf_tab/256
        ld d,a
        ld a,(de)               ; the left byte,
        ld (hl),a
        inc l
        inc de
        ld a,(de)               ; the middle ones,
        dec c
        dec c
pf_4:
        ld (hl),a
        inc l
        dec c
        jr nz,pf_4
        inc de
        ld a,(de)               ; the right
        ld (hl),a
        pop de
        pop bc
        pop hl
        call pl_down
        djnz pf_1
        ret
pf_tab: db 0x00,0x00,0x00, 0x07,0xFF,0xE0, 0x0F,0xFF,0xF0, 0x1F,0xFF,0xF8
        include "plate.asm"     ; pl_dig (tools/make_plate.py; pl_suf and pl_lap are under 0x8000, pl_msg at TD)

