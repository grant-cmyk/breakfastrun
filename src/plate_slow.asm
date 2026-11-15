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
; HUD_PRE, each picture before the canisters and the gauge are drawn (Grant, 14 Nov 2026: "make
; the NOS bottles in the bottom right red ink and the health lightning bolt magenta. So these
; would need a decent mask to prevent colour clash"). They do not scroll, so their colour cells
; can have an ink of their own - as long as nothing else is in those cells: the gauge's 3 x 2
; cells are written whole by dmg_draw; a canister's 1 x 2 are cleared here when you hold it
; (and are the window's own colour again when you do not).
HP_AT   equ 0x5800 + (WIN_Y/8 + WIN_H/8 - 2)*32 + WIN_COL   ; the window's last two cell rows on the screen
HP_NB   equ BUF + 0x800*2 + 2*32 + 2 + WIN_W - 1            ; the first canister's upper cell in the buffer (its last byte)
hud_pre:
        ld a,0x2B               ; the gauge: magenta on the table's cyan
        ld hl,HP_AT
        ld (hl),a
        inc l
        ld (hl),a
        inc l
        ld (hl),a
        ld l,(HP_AT + 32) AND 255
        ld (hl),a
        inc l
        ld (hl),a
        inc l
        ld (hl),a
        ld a,(INV)              ; the canisters: red
        ld hl,HP_AT + WIN_W - 1
        ld de,HP_NB
        call hp_slot
        ld a,(INV+1)
        ld hl,HP_AT + WIN_W - 2
        ld de,HP_NB - 1
        call hp_slot
        ld a,(INV+2)
        ld hl,HP_AT + WIN_W - 3
        ld de,HP_NB - 2
hp_slot:                        ; A = the slot (0: empty), HL = its upper cell on the screen, DE = in the buffer
        or a
        ld a,WIN_ATTR2
        jr z,hp_2
        ex de,hl                ; held: its two cells cleared (16 lines of the one byte)
        xor a
        ld b,8
hp_0:
        ld (hl),a
        inc h
        djnz hp_0
        ld a,h
        sub 8
        ld h,a
        ld a,l
        add a,32
        ld l,a
        xor a
        ld b,8
hp_1:
        ld (hl),a
        inc h
        djnz hp_1
        ex de,hl
        ld a,0x2A
hp_2:
        ld (hl),a
        ld bc,32
        add hl,bc
        ld (hl),a
        ret
WIN_ATTR2 equ 0x29              ; the window's own colours: blue on cyan
pl_key:  dw 0                   ; the place and lap pl_bmp was composed for
pl_lin:  db 0                   ; pl_down's rows: 1 in pl_bmp, 0 in the buffer
pl_bmp:  defs PL_W*PL_H          ; the plate, composed

; DMG_MAKE: the health gauge composed for damage A (HL = dmg_sh) into dmg_bmp: DMG_ROWS rows of 3
; bytes - the outline, and the fill in every row but the first C (dmg_emp: it empties from the top).
dmg_make:
        ld (hl),a
        add a,dmg_emp AND 255
        ld l,a
        ld a,0
        adc a,dmg_emp/256
        ld h,a
        ld c,(hl)
        ld hl,dmg_heart         ; for each byte: the outline, the fill
        ld de,dmg_bmp
        ld b,DMG_ROWS
dk_1:
        push bc
        ld b,3
dk_2:
        ld a,(hl)
        inc hl
        inc c
        dec c
        jr nz,dk_3
        or (hl)
dk_3:
        inc hl
        ld (de),a
        inc de
        djnz dk_2
        pop bc
        ld a,c
        or a
        jr z,dk_4
        dec c
dk_4:
        djnz dk_1
        ret
dmg_sh:  db 0xFF                 ; the damage dmg_bmp shows (0xFF: none yet)
dmg_bmp: defs 3*DMG_ROWS
dmg_emp: db 2,3,4,5,6,7,9,11,16         ; rows without fill (the first is clear) for damage 0 to 8
        include "dmgicon.asm"   ; dmg_heart: the icon's art (tools/make_damage_icons.py)
pl_tl:   dw 0xFFFF               ; the lap time (frames) the plate's figures were last cut for
