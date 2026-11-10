; the cloth's minis, continued (see clothmini.asm)
; CFW_E / CFW_O: HL -> this row's 3 minis: into slots 2, 4, 6 (or 3, 5, 7)
cfw_e:
        ld a,0xCD
        ld (cf_s2),a
        ld (cf_s4),a
        ld (cf_s6),a
        ld e,(hl)
        inc hl
        ld d,(hl)
        inc hl
        ld (cf_s2+1),de
        ld e,(hl)
        inc hl
        ld d,(hl)
        inc hl
        ld (cf_s4+1),de
        ld e,(hl)
        inc hl
        ld d,(hl)
        ld (cf_s6+1),de
        ret
cfw_o:
        ld a,0xCD
        ld (cf_s3),a
        ld (cf_s5),a
        ld (cf_s7),a
        ld e,(hl)
        inc hl
        ld d,(hl)
        inc hl
        ld (cf_s3+1),de
        ld e,(hl)
        inc hl
        ld d,(hl)
        inc hl
        ld (cf_s5+1),de
        ld e,(hl)
        inc hl
        ld d,(hl)
        ld (cf_s7+1),de
        ret
