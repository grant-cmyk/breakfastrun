; The place plate's parts that run rarely (see plateco.asm), in the slower memory under 0x8000.
pl_static:                      ; B = your place, C = your lap: the plate composed in pl_bmp
        ld (pl_key),bc
        push bc
        ld hl,pl_bmp            ; the plate: a clear line, a rounding row, 14 solid, a rounding
        ld c,PL_W               ; row, a clear line - 29 pixels of the 40 across
        ld de,0x0000
        call pf_row
        ld de,0x0380
        call pf_row
        ld b,14
ps_1:
        ld de,0x07C0
        call pf_row
        djnz ps_1
        ld de,0x0380
        call pf_row
        ld de,0x0000
        call pf_row
        pop bc
        push bc
        ld a,14                 ; P and your place
        ld c,b
        ld hl,pl_bmp+3*PL_W+1
        call pl_pair
        pop bc                  ; a space, the lap
        ld a,13
        ld hl,pl_bmp+3*PL_W+2
        call pl_pair
        ld a,12                 ; /3
        ld c,3
        ld hl,pl_bmp+3*PL_W+3
        jp pl_pair
pl_message:                     ; FINAL LAP! on its own plate, straight into the buffer
        xor a
        ld (pl_lin),a
        ld hl,PL_M
        ld bc,7*256+6
        call pl_fill
        ld hl,PL_MT
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
pl_bmp:  defs PL_W*PL_H          ; the plate, composed
