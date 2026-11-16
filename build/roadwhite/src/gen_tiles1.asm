; GEN_TILES1.ASM - TILE1=1 bash build.sh: ONE tile routine instead of gen_tiles.asm's eight (about 1 KB less).
; tdraw_one: OR one tile (DE = its 8 bytes) into the buffer at HL, shifted through the tables at page B.
; A tile crosses into the next character row after its line V-1, V = camy AND 7 - the same line for every
; tile of a picture. So once a picture td_patch writes a CALL td_step over that line's "INC H, LD A,(DE), INC E"
; (3 bytes; the row before's are put back): td_step does those three and the step. A tile costs a CALL and a RET more.
tdraw_one:
        ld a,(de)               ; tile byte
        inc e
        or a                    ; a blank line: nothing to draw
        jr z,t1_0
        ld c,a
        ld a,(bc)               ; part for the left byte
        or (hl)
        ld (hl),a
        inc b
        inc l
        ld a,(bc)               ; part for the right byte
        or (hl)
        ld (hl),a
        dec b
        dec l
t1_0:
        inc h                   ; next pixel row  <- td_site(1)
        ld a,(de)               ; tile byte
        inc e
        or a                    ; a blank line: nothing to draw
        jr z,t1_1
        ld c,a
        ld a,(bc)               ; part for the left byte
        or (hl)
        ld (hl),a
        inc b
        inc l
        ld a,(bc)               ; part for the right byte
        or (hl)
        ld (hl),a
        dec b
        dec l
t1_1:
        inc h                   ; next pixel row  <- td_site(2)
        ld a,(de)               ; tile byte
        inc e
        or a                    ; a blank line: nothing to draw
        jr z,t1_2
        ld c,a
        ld a,(bc)               ; part for the left byte
        or (hl)
        ld (hl),a
        inc b
        inc l
        ld a,(bc)               ; part for the right byte
        or (hl)
        ld (hl),a
        dec b
        dec l
t1_2:
        inc h                   ; next pixel row  <- td_site(3)
        ld a,(de)               ; tile byte
        inc e
        or a                    ; a blank line: nothing to draw
        jr z,t1_3
        ld c,a
        ld a,(bc)               ; part for the left byte
        or (hl)
        ld (hl),a
        inc b
        inc l
        ld a,(bc)               ; part for the right byte
        or (hl)
        ld (hl),a
        dec b
        dec l
t1_3:
        inc h                   ; next pixel row  <- td_site(4)
        ld a,(de)               ; tile byte
        inc e
        or a                    ; a blank line: nothing to draw
        jr z,t1_4
        ld c,a
        ld a,(bc)               ; part for the left byte
        or (hl)
        ld (hl),a
        inc b
        inc l
        ld a,(bc)               ; part for the right byte
        or (hl)
        ld (hl),a
        dec b
        dec l
t1_4:
        inc h                   ; next pixel row  <- td_site(5)
        ld a,(de)               ; tile byte
        inc e
        or a                    ; a blank line: nothing to draw
        jr z,t1_5
        ld c,a
        ld a,(bc)               ; part for the left byte
        or (hl)
        ld (hl),a
        inc b
        inc l
        ld a,(bc)               ; part for the right byte
        or (hl)
        ld (hl),a
        dec b
        dec l
t1_5:
        inc h                   ; next pixel row  <- td_site(6)
        ld a,(de)               ; tile byte
        inc e
        or a                    ; a blank line: nothing to draw
        jr z,t1_6
        ld c,a
        ld a,(bc)               ; part for the left byte
        or (hl)
        ld (hl),a
        inc b
        inc l
        ld a,(bc)               ; part for the right byte
        or (hl)
        ld (hl),a
        dec b
        dec l
t1_6:
        inc h                   ; next pixel row  <- td_site(7)
        ld a,(de)               ; tile byte
        inc e
        or a                    ; a blank line: nothing to draw
        jr z,t1_7
        ld c,a
        ld a,(bc)               ; part for the left byte
        or (hl)
        ld (hl),a
        inc b
        inc l
        ld a,(bc)               ; part for the right byte
        or (hl)
        ld (hl),a
        dec b
        dec l
t1_7:
        ret
TD_ROW  equ t1_1-t1_0           ; a line's bytes
td_step:
        inc h
        ld a,l                  ; into the next character row:
        add a,32
        ld l,a
        jr c,tds_1              ; (carry: next third - H is already right)
        ld a,h
        sub 8
        ld h,a
tds_1:
        ld a,(de)
        inc e
        ret
; TD_PATCH (A = camy AND 7): the step where this picture needs it. Nothing to do when it is where it was.
td_patch:
        ld hl,td_cur
        cp (hl)
        ret z
        ld c,a
        ld a,(hl)
        ld (hl),c
        or a
        jr z,tdp_1
        call td_site            ; the old place: its three instructions back
        ld (hl),0x24            ; inc h
        inc hl
        ld (hl),0x1A            ; ld a,(de)
        inc hl
        ld (hl),0x1C            ; inc e
tdp_1:
        ld a,c
        or a
        ret z                   ; (0: the tile never crosses)
        call td_site
        ld (hl),0xCD            ; call td_step
        inc hl
        ld (hl),td_step AND 255
        inc hl
        ld (hl),td_step/256
        ret
td_site:                        ; HL = the INC H after line A-1: t1_0 + TD_ROW * (A - 1)
        ld hl,t1_0-TD_ROW
        ld de,TD_ROW
tdt_1:
        add hl,de
        dec a
        jr nz,tdt_1
        ret
td_cur: db 0                    ; where the step is now (0: nowhere)
