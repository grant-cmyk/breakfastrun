; CNOS - the chasers' NOS: the part under 0x8000 (cn_new, the helpers, the data). The rule: cnos.asm.

cn_new:                         ; a new race: both cans full, nothing burning
        ld hl,cn_burn
        ld b,cn_end-cn_burn
cnn_1:  ld (hl),0xFF            ; (cn_used: 0xFF, no lap yet; the rest set to 0 below)
        inc hl
        djnz cnn_1
        xor a
        ld (cn_burn),a
        ld (cn_wait),a
        ret

cn_bend:                        ; A = a waypoint: CY if its bend is under CN_STR (|x| + |y|)
        call rl_bend
        ld a,d
        call cn_abs
        ld d,a
        ld a,e
        call cn_abs
        add a,d
        cp CN_STR
        ret
cn_abs: or a
        ret p
        neg
        ret
cn_row:                         ; A = a kind: HL = its card row (the rows card_push reads: cdp_tab's)
        add a,a
        add a,a
        add a,a
        ld e,a
        ld d,0
        ld hl,(cdp_tab+1)
        add hl,de
        ret
        if OPT_MAP40 * OPT_MAPHUD = 0   ; (the breakfast fast tapes: in the D0 strip - vars_d0.asm)
cn_burn: db 0                   ; pictures of NOS left (one car at a time)
cn_wait: db 0                   ; pictures before the next may light
cn_who:  db 0                   ; whose
cn_k:    db 0
cn_sv:   db 0,0,0,0,0,0         ; the burner's grip (2), brake speed, 4/5 top, two pushes, as they were
cn_used: db 0,0,0,0,0           ; each kind: the lap its can went on (0xFF: not yet)
cn_end:
        endif
