; =====================================================================
; HEAD32 and MIRROR (Grant, 22 Nov 2026: "smoothness can be improved with more angles of drawing ... what if we compromised
; to 32? ... lets do a space search then ... 32 should be fine"). Kept under 0x8000 (the room the mirrored frames leave).
;   HEAD32: the racer is drawn at 32 headings (tools/make_data.py; big_tab holds its 32 first); a computer car between two
;           of the push table's 16 headings is pushed their average (hp_avg), so it goes the way its picture points
;   MIRROR: a computer car's heading that is another's frame turned left for right is made from that frame, into dm_buf,
;           as it is drawn (dc_mirror) - not your car's: in RACE every car is yours, so RACE never pays for it
; =====================================================================
        if OPT_HEAD32
; HP_AVG (heading_push, A = a heading with bit 1 set: half-way between two of the 16): DE, BC = the average of the pushes
; either side (its length 2% under the table's 64 - unnoticed)
hp_avg:
        push af
        call hp_16
        pop af
        push de
        push bc
        add a,4
        call hp_16
        pop hl
        add hl,bc
        sra h
        rr l
        ld b,h
        ld c,l
        pop hl
        add hl,de
        sra h
        rr l
        ex de,hl
        ret
        endif

        if OPT_MIRROR
; DC_MIRROR (draw_car and the title's car, A = a frame's rows with bit 6 set - and bit 7 too if it is upside down as well -,
; DE = the frame it is made from: its first row, or its last if upside down): that frame turned left for right, top row
; first, in dm_buf (rev_tab: each byte's bits the other way round; a row's two halves change places). Out: DE = dm_buf,
; A = the rows (bits 6 and 7 clear). BC and HL kept. The same frame as last time is not made again (dm_src).
dc_mirror:
        push bc
        push hl
        ld c,a
        and 0x3F
        push af
        ld hl,(dm_src)
        or a
        sbc hl,de
        jr nz,dm_new
        ld a,(dm_fl)
        cp c
        jr z,dm_done
dm_new: ld (dm_src),de
        ld a,c
        ld (dm_fl),a
        and 0x3F
        ld (dm_n),a
        ld bc,dm_buf
        ld h,rev_tab/256
dm_row: inc bc                  ; (the row's left half goes to its right: write that first)
        inc bc
        ld a,(de)
        inc de
        ld l,a
        ld a,(hl)
        ld (bc),a
        inc bc
        ld a,(de)
        inc de
        ld l,a
        ld a,(hl)
        ld (bc),a
        dec bc
        dec bc
        dec bc
        ld a,(de)
        inc de
        ld l,a
        ld a,(hl)
        ld (bc),a
        inc bc
        ld a,(de)
        inc de
        ld l,a
        ld a,(hl)
        ld (bc),a
        inc bc
        inc bc
        inc bc
        ld a,(dm_fl)            ; upside down: back up two rows (the one just read and the one above it)
        rla
        jr nc,dm_fw
        ld a,e
        sub 8
        ld e,a
        jr nc,dm_fw
        dec d
dm_fw:  ld a,(dm_n)
        dec a
        ld (dm_n),a
        jr nz,dm_row
dm_done:
        pop af
        ld de,dm_buf
        pop hl
        pop bc
        ret
dm_src: dw 0
dm_fl:  db 0
dm_n:   db 0
        endif
