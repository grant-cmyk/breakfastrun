; ROAD_CLEAR's set-up and helpers (see roadclear.asm), here to fill the gap before
; sq4's page
road_clear:
        ld a,(camx)
        and 7
        ld c,a                  ; s
        neg
        and 7                   ; o
        ld b,a
        ld a,0xFF
        jr z,rc_o0
rc_sh:
        srl a
        djnz rc_sh
rc_o0:
        ld (rr_mr+1),a          ; keep the bits after a run: 0xFF >> o
        ld e,a
        srl a
        xor e
        ld (rr_dot+1),a         ; the light dot: 0x80 >> o
        ld a,e
        cpl
        ld (rr_ml+1),a          ; keep the bits before it
        ld a,c                  ; FB: 2 when s = 0, else 1
        cp 1
        ld a,1
        adc a,0
        ld (rr_fb+1),a
        ld hl,(camx)
        call rc_div8
        ld (RC_TX0),a
        ld hl,(camy)
        call rc_div8
        ld (RC_TY),a
        ld a,(camy)
        and 7
        neg
        add a,16
        ld (RC_R0),a
        ld a,WIN_H/8+1
        ld (RC_N),a
        jp rc_row

; RC_RUN: H = first tile + 8, E = (last tile + 1) + 8: clear them on the row's
; even lines, then put back each one's light dot. Keeps BC, DE, HL.
rc_run:
        push bc
        push de
        push hl
        ld a,h
        sub 8
        jr nc,rr_1
        xor a                   ; starts left of the window: from tile 0
rr_1:
        ld d,a
        ld a,e
        sub 9                   ; the last tile
        jr c,rr_out             ; ends left of the window
        cp 23
        jr c,rr_2
        ld a,22                 ; ends right of it: at tile 22
rr_2:
        sub d
        jr c,rr_out
        ld c,a                  ; C = whole bytes between
        ld a,d
rr_fb:
        add a,0                 ; (patched) + FB: the run's first byte
        ld (rr_sb+1),a
        ld de,RC_L
        ld b,4
rr_l:
        ld a,(de)
        inc e
rr_sb:
        add a,0                 ; (patched)
        ld l,a
        ld a,(de)
        inc e
        ld h,a
        ld a,(hl)
rr_ml:
        and 0                   ; (patched) keep the bits before the run
        ld (hl),a
        inc l
        ld a,c
        or a
        jr z,rr_r
        push bc
        ld b,a
        xor a
rr_z:
        ld (hl),a
        inc l
        djnz rr_z
        pop bc
rr_r:
        ld a,(hl)
rr_mr:
        and 0                   ; (patched) keep the bits after it
        ld (hl),a
        djnz rr_l
        ld hl,(RC_L)            ; the light dots, on line 0
        ld a,(rr_sb+1)
        add a,l
        ld l,a
        ld b,c
        inc b
rr_d:
        ld a,(hl)
rr_dot:
        or 0                    ; (patched)
        ld (hl),a
        inc l
        djnz rr_d
rr_out:
        pop hl
        pop de
        pop bc
        ret

rc_addr:                        ; A = buffer row -> DE = its first byte
        ld c,a
        and 7
        ld d,a
        ld a,c
        and 0xC0
        rrca
        rrca
        rrca
        or d
        or BUF_HI
        ld d,a
        ld a,c
        and 0x38
        rlca
        rlca
        ld e,a
        ret

rc_div8:                        ; HL / 8 -> A (under 256)
        srl h
        rr l
        srl h
        rr l
        srl h
        rr l
        ld a,l
        ret
