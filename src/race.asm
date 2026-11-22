; =====================================================================
; RACE MODE (RACEMODE=1; Grant, 18 Nov 2026: "Now I need a game option - combat or race. Race produces a bunch of the same
; looking cars, but different colours and numbers ... the idea is to make it competitive so you don't run away with it").
; The title's M chooses (rmode, title.asm: 1 RACE, 0 COMBAT; RACE to start with, kept from race to race). COMBAT is the
; armour tape's game exactly. RACE:
;   - every car is the racer (MAX's car), told apart by its colour (a number on the roof was tried, 3 x 5 pixels in a
;     box: Grant, 18 Nov 2026, "Number won't be legible - that's fine" - so there are no numbers)
;   - every computer car on MAX's card with its own small differences (race_low.asm; ai_tune.asm, AI_Rx_GRIP, _KA,
;     _KS), and each driven by its own RACE driver (ai_tune.asm, AI_Rx_...: cyan the smooth one, yellow the late
;     braker, magenta the wide one, white the erratic one)
;   - no armour lost, no shells, no wheels, no drivers steering at other cars: a bump is just a bump
;   - the race order shows, right of each car, its gap to the car ahead (rg_draw) where the health blocks were
;   - ELASTIC=1 (the second race tape): el_tick, below
; =====================================================================

        if OPT_ELASTIC
; EL_TICK (ELASTIC=1; every picture, after the places are worked out): RACE - each computer car's two pushes (its row in
; race_low.asm: its own pushes plus the band, the band kept in the row's eighth byte) set afresh from the cars' progress
; (prog: laps x waypoints + waypoints passed): one 64th more for every 2^EL_SH waypoints it is behind the leader, up to
; EL_MAX; EL_EASE less if it is more than EL_AHEAD waypoints ahead of you. Once any car has finished, no car is
; "behind" any more (only the easing is left).
el_tick:
        ld a,(rmode)
        or a
        ret z
        ld hl,order
        ld e,(hl)
        ld d,0
        ld hl,prog
        add hl,de
        ld c,(hl)               ; C = the leader's progress
        ld a,(fin_count)
        or a
        jr z,el_0
        ld c,d
el_0:   ld hl,prog
        ld b,(hl)               ; B = yours
        ld de,cd_race+4
el_1:   inc hl
        ld a,b
        add a,EL_AHEAD
        cp (hl)                 ; carry: this car is more than EL_AHEAD waypoints ahead of you
        sbc a,a
        and EL_EASE
        neg
        ld (el_e+1),a
        ld a,c
        sub (hl)                ; waypoints behind the leader
        jr nc,el_2
        xor a
el_2:
        rept EL_SH
        srl a
        endm
        cp EL_MAX
        jr c,el_3
        ld a,EL_MAX
el_3:
el_e:   add a,0                 ; A = its rubber band now; the row's eighth byte holds the one in its pushes already
        ex de,hl                ; (each car's pushes are its own since 19 Nov 2026: the band goes on top of them)
        push de
        ld d,a
        inc hl
        inc hl
        inc hl
        sub (hl)                ; the change
        ld (hl),d
        dec hl
        dec hl
        ld e,a
        add a,(hl)
        ld (hl),a               ; its SPEED push
        dec hl
        ld a,e
        add a,(hl)
        ld (hl),a               ; its ACCEL push
        ld de,8
        add hl,de               ; the next car's row
        pop de
        ex de,hl
        ld a,l
        cp (prog+NCARS-1) AND 255
        jr nz,el_1
        ret
        endif

; RL_LINE (RACE mode; IX = a computer car that has just picked its next waypoint, C_WP, and its small random offset): ITS
; OWN LINE THROUGH THE BENDS (Grant, 22 Nov 2026: "need the other cars to try different tracks - so their route around
; the track is not identical - some take a corner a bit wide, some late"). Each waypoint's BEND is worked out from the
; waypoints themselves - 2W - P - N, W the waypoint and P, N the ones either side: nothing on a straight, up to about 40
; pixels at the sharpest, pointing to the OUTSIDE of the bend. The driver's line (ai_tune.asm, AI_Rx_LINE and the four
; lines AI_L_...) is three weights, in 64ths: the bend it has just come out of, the bend at this waypoint, the bend it is
; going into (a fourth, SIDE - a little to one side even on the straights - was written and left out: the catch-up tape
; had no room for it, 22 Nov 2026). Their sum, over 64, is added to the aim point, held to RL_MAX pixels each way. A positive weight
; takes the car to the outside, a negative one to the inside. The erratic one (AI_RW_LINE = 255) takes one of the four
; lines at random at every waypoint on a straight, so each bend its own way. About 1,100 T, three times a second a car.
RL_MAX  equ 14
rl_line:
        ld a,(rmode)
        or a
        ret z
        ld e,(ix+C_KIND)
        ld d,0
        ld hl,rl_driver-1
        add hl,de
        ld a,(hl)               ; A = the line it drives (0-3), or 255: one of them, bend by bend
        cp 255
        jr nz,rl_have
        ld a,(ix+C_WP)          ; (the erratic one: is this waypoint on a straight? then pick again)
        call rl_bend
        ld a,d
        or a
        jp p,rl_w1
        neg
rl_w1:  ld b,a
        ld a,e
        or a
        jp p,rl_w2
        neg
rl_w2:  add a,b
        cp 8
        jr nc,rl_keep
        call rnd
        and 3
        ld (rl_wsel),a
rl_keep:
        ld a,(rl_wsel)
rl_have:
        ld l,a
        add a,a
        add a,l
        ld e,a
        ld d,0
        ld hl,rl_lines
        add hl,de
        ld (rl_w),hl
        ld hl,0
        ld (rl_ox),hl
        ld (rl_oy),hl
        ld a,(ix+C_WP)
        dec a
        ld (rl_k),a
        ld b,3
rl_each:
        push bc
        ld a,(rl_k)
        call rl_bend            ; D, E = the bend at rl_k
        ld hl,(rl_w)
        ld a,(hl)               ; the weight
        inc hl
        ld (rl_w),hl
        push af
        push de
        ld b,a
        ld c,d
        call mul8s
        ld de,(rl_ox)
        add hl,de
        ld (rl_ox),hl
        pop de
        pop af
        ld b,a
        ld c,e
        call mul8s
        ld de,(rl_oy)
        add hl,de
        ld (rl_oy),hl
        ld hl,rl_k
        inc (hl)
        pop bc
        djnz rl_each
        ld hl,(rl_ox)
        call rl_64
        add a,(ix+C_OFFX)
        ld (ix+C_OFFX),a
        ld hl,(rl_oy)
        call rl_64
        add a,(ix+C_OFFY)
        ld (ix+C_OFFY),a
        ret
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
