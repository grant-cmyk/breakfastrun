; The place plate's parts that run rarely (see plateco.asm), in the slower memory under 0x8000.
pl_static:                      ; B = your place, C = your lap: the plate composed in pl_bmp
        ld (pl_key),bc
        push bc
        ld hl,pl_bmp
        ld bc,18*256+6
        call pl_fill
        ld de,0x3E80            ; P, the ROM's own letter, 8 x 8
        ld hl,pl_bmp+4*6+1
        ld b,8
        call pl_cut
        pop bc
        push bc
        ld a,b                  ; and your place's figure beside it ("0" is at 0x3D80)
        add a,a
        add a,a
        add a,a
        add a,0x80
        ld e,a
        ld d,0x3D
        ld hl,pl_bmp+4*6+2
        ld b,8
        call pl_cut
        pop bc                  ; a gap, then the lap, small: n/3
        ld a,13
        ld hl,pl_bmp+5*6+3
        call pl_pair
        ld a,12
        ld c,3
        ld hl,pl_bmp+5*6+4
        jp pl_pair
pl_message:                     ; FINAL LAP! on its own plate, straight into the buffer
        xor a
        ld (pl_lin),a
        ld hl,PL_M
        ld bc,7*256+6
        call pl_fill
        ld hl,PL_M+4*0x100
        ld de,pl_msg
        ld c,6
pl_cols:                        ; C columns of 5 rows from DE, at HL and on to the right
        push hl
        ld b,5
        call pl_cut
        pop hl
        inc l
        dec c
        jr nz,pl_cols
        ret
pl_cut:                         ; B rows of the column at HL: the bits of (DE) on cut out of the plate
        ld a,(de)
        xor (hl)
        ld (hl),a
        inc de
        call pl_down
        djnz pl_cut
        ret
pl_fill:                        ; HL = its top left byte, B = its solid rows, C = bytes: a clear line, two
        ld de,0x0000            ; rounding rows, the solid rows, two rounding rows, a clear line
        call pf_row
        ld de,0x07E0
        call pf_row
        ld de,0x0FF0
        call pf_row
pf_1:
        ld de,0x1FF8            ; (3 pixels in at each side)
        call pf_row
        djnz pf_1
        ld de,0x0FF0
        call pf_row
        ld de,0x07E0
        call pf_row
        ld de,0x0000
pf_row:                         ; a row: D its left byte, E its right, solid between (clear if D is 0)
        push hl
        push bc
        ld (hl),d
        inc hl
        ld a,d
        or a
        jr z,pf_2
        ld a,0xFF
pf_2:
        ld b,c
        dec b
        dec b
pf_3:
        ld (hl),a
        inc hl
        djnz pf_3
        ld (hl),e
        pop bc
        pop hl
        jp pl_down
pl_key:  dw 0                   ; the place and lap pl_bmp was composed for
pl_lin:  db 0                   ; pl_down's rows: 1 in pl_bmp, 0 in the buffer
pl_bmp:  defs 6*24              ; the plate, composed
