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

