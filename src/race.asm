; =====================================================================
; RACE MODE (RACEMODE=1; Grant, 18 Nov 2026: "Now I need a game option - combat or race. Race produces a bunch of the same
; looking cars, but different colours and numbers ... the idea is to make it competitive so you don't run away with it").
; The title's M chooses (rmode, title.asm: 1 RACE, 0 COMBAT; RACE to start with, kept from race to race). COMBAT is the
; armour tape's game exactly. RACE:
;   - every car is the racer (MAX's car), told apart by its colour (a number on the roof was tried, 3 x 5 pixels in a
;     box: Grant, 18 Nov 2026, "Number won't be legible - that's fine" - so there are no numbers)
;   - every computer car on MAX's top speed and acceleration, with more grip (race_low.asm; ai_tune.asm, AI_R_GRIP), and
;     driven by the RACE drivers (ai_tune.asm, AI_R_...)
;   - no armour lost, no shells, no wheels, no drivers steering at other cars: a bump is just a bump
;   - the race order shows, right of each car, its gap to the car ahead (rg_draw) where the health blocks were
;   - ELASTIC=1 (the second race tape): el_tick, below
; =====================================================================

        if OPT_ELASTIC
; EL_TICK (ELASTIC=1; every picture, after the places are worked out): RACE - each computer car's two pushes (its row in
; race_low.asm) set afresh from the cars' progress (prog: laps x waypoints + waypoints passed): one 64th more for every
; 2^EL_SH waypoints it is behind the leader, up to EL_MAX; EL_EASE less if it is more than EL_AHEAD waypoints
; ahead of you. Once any car has finished,
; no car is "behind" any more (only the easing is left).
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
el_e:   add a,0
        push af
        add a,CD_R_KA
        ld (de),a
        inc de
        pop af
        add a,CD_R_KS
        ld (de),a
        ld a,e
        add a,7
        ld e,a
        jr nc,el_4
        inc d
el_4:   ld a,l
        cp (prog+NCARS-1) AND 255
        jr nz,el_1
        ret
        endif
