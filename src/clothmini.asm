; ---------------------------------------------------------------------
; The cloth's minis (see cf_m00): here to fill the gap before sq4's page.
; Every character row's line 0 has the same y AND 3 (= camy AND 3), so the
; same 3 slots call minis all picture: lines 2, 4, 6 when line 0 is even,
; 3, 5, 7 when odd (line 1 comes from line 0's loader). The minis' kinds
; take turns, P(a), P(b), P(a); only their check row changes, row by row.
; ---------------------------------------------------------------------
cf_init:
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
