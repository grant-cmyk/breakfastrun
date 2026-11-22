; RL_LINE's helpers and numbers (race.asm): in the program, or under 0x8000 on the race-only tapes (race_low.asm)
rl_64:                          ; A = HL / 64, held to -RL_MAX..RL_MAX (HL within +-8191)
        add hl,hl
        add hl,hl
        ld a,h
        or a
        jp m,rl_64n
        cp RL_MAX+1
        ret c
        ld a,RL_MAX
        ret
rl_64n: cp 256-RL_MAX
        ret nc
        ld a,256-RL_MAX
        ret
rl_bend:                        ; A = a waypoint (one either side of 0..NWP-1 is fine): D, E = its bend's x, y (2W - P - N)
        ld c,a
        dec a
        call rl_at
        ld d,(hl)               ; P
        inc hl
        inc hl
        ld e,(hl)
        ld a,c
        inc a
        call rl_at
        ld a,d                  ; + N
        add a,(hl)
        ld d,a
        inc hl
        inc hl
        ld a,e
        add a,(hl)
        ld e,a
        ld a,c
        call rl_at
        ld a,(hl)               ; 2W less them
        add a,a
        sub d
        ld d,a
        inc hl
        inc hl
        ld a,(hl)
        add a,a
        sub e
        ld e,a
        ret
rl_at:                          ; A = a waypoint, -2..NWP+1: HL -> its x, y in wp_tab (C, D, E kept)
        or a
        jp p,rl_a1
        add a,NWP
rl_a1:  cp NWP
        jr c,rl_a2
        sub NWP
rl_a2:  push de
        add a,a
        add a,a
        ld l,a
        ld h,0
        ld de,wp_tab
        add hl,de
        pop de
        ret
rl_driver: db AI_RC_LINE, AI_RY_LINE, AI_RM_LINE, AI_RW_LINE
rl_lines:                       ; the bend it came out of, the bend here, the bend it is going into
        db AI_L0_OUT, AI_L0_NOW, AI_L0_IN       ; 0 THE CLASSIC: out - in - out
        db AI_L1_OUT, AI_L1_NOW, AI_L1_IN       ; 1 LATE: deep on the outside, the inside only on the way out
        db AI_L2_OUT, AI_L2_NOW, AI_L2_IN       ; 2 WIDE: the outside all the way round
        db AI_L3_OUT, AI_L3_NOW, AI_L3_IN       ; 3 EARLY: in early, wide on the way out
rl_wsel: db 0
rl_k:   db 0
rl_w:   dw 0
rl_ox:  dw 0
rl_oy:  dw 0
