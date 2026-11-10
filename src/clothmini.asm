; ---------------------------------------------------------------------
; The cloth's minis (see cf_m00): here to fill the gap before sq4's page.
; Every character row's line 0 has the same y AND 3 (= camy AND 3), so the
; same 3 slots call minis all picture: lines 2, 4, 6 when line 0 is even,
; 3, 5, 7 when odd (line 1 comes from line 0's loader). The minis' kinds
; take turns, P(a), P(b), P(a); only their check row changes, row by row.
; ---------------------------------------------------------------------
cf_init:
        ld a,0xFF               ; the mini slots: written afresh this picture
        ld (CFW_CR),a
        ld hl,cf_slots+2        ; every slot back to nops
        ld b,7
cfi_1:
        ld e,(hl)
        inc hl
        ld d,(hl)
        inc hl
        xor a
        ld (de),a
        inc de
        ld (de),a
        inc de
        ld (de),a
        djnz cfi_1
        ld a,(camy)
        and 3
        ld c,a
        ld hl,cfw_e
        bit 0,a
        jr z,cfi_2
        ld hl,cfw_o
cfi_2:
        ld (cf_wcall+1),hl
        ld a,c                  ; the first mini's kind: (y0 + its line) AND 2
        add a,2
        bit 0,c
        jr z,cfi_3
        inc a
cfi_3:
        and 2
        ld hl,cf_m00
        jr z,cfi_4
        ld hl,cf_m20
cfi_4:
        ld (CFT+0),hl           ; check row 0: a, b, a
        ld (CFT+4),hl
        ld de,17
        add hl,de
        ld (CFT+6),hl           ; check row 1
        ld (CFT+10),hl
        ld hl,cf_m00+cf_m20     ; b: the other kind
        ld de,(CFT+0)
        or a
        sbc hl,de
        ld (CFT+2),hl
        ld de,17
        add hl,de
        ld (CFT+8),hl
        ret
; (cfw_e and cfw_o: clothmini2.asm, after sq4)

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
        ld a,b                  ; x = BOX_X + (62 - (4n - 1)) / 2
        add a,a
        add a,a
        dec a
        neg
        add a,62
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

