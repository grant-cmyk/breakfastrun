; =====================================================================
; WEIGHT (Grant, 22 Nov 2026: "Damage and impact of cars depends on the type of car - the small car - I think the ladies is
; faster, but if I hit her, my car is heavier so impact to me is small and damage small but higher to her. The tank has a
; bigger impact as it is the heaviest, but is also slightly slower ... tracking the specific strengths and weaknesses of
; each car"). A car's WEIGHT is its driver card's armour (CD_ARM_k: Jane 2, Spike 4, Max and Frank 5, Bruno 9 - as what a
; piece of armour takes, 26 to 77). When two cars touch (bump):
;   - each is kicked away by 2 x KICK x the other's weight / both weights (wk_tab): the heavier one barely moves, the
;     lighter one goes; two alike, KICK each, as before
;   - each takes damage - 4 x the other's weight / its own, in quarter points (wq_tab): Max hitting Jane takes 3 quarters, she
;     takes 6; Bruno's tank takes 1-2 from anyone and gives up to 12 - once in DMG_COOL pictures a car, up to 32 (8 points)
;   - your damage is the mug's (dmg = quarters / 4: it slows you as before); a computer car's takes up to a sixteenth off its
;     push, a 64th for every 8 quarters (wt_slow)
; Kept in each car's row of arm_tab (its third byte the quarters, its fourth the cool-down); arm_new clears them each race,
; and the oil can (arm_mend) mends yours. Only on the breakfast race tape (WEIGHT=1).
; =====================================================================
wt_bump:                        ; (bump, IX = car a touching car b at bump_b): this pair's kicks, and both cars' damage
        ld c,(ix+C_KIND)
        ld hl,(bump_b)
        ld de,C_KIND
        add hl,de
        ld b,(hl)               ; C = a's kind, B = b's
        ld a,(BOOST_T)          ; (NOS - Grant, 22 Nov 2026: "hitting a car in NOS should keep you on your path but knock them":
        or a                    ; while it burns YOU are kind 5 in the tables, three times your weight; your own speed is kept in the bump - wt_kick)
        jr z,wb_n
        ld a,c
        or a
        jr nz,wb_b
        ld c,5
wb_b:   ld a,b
        or a
        jr nz,wb_n
        ld b,5
wb_n:   ld a,c
        cp 5
        ld a,0
        jr nz,wb_k
        inc a
wb_k:   ld (wk_ka),a            ; (1: car a is you on NOS - its speed kept)
        ld a,b
        cp 5
        ld a,0
        jr nz,wb_k2
        inc a
wb_k2:  ld (wk_kb),a
        ld a,c
        call wt_pair
        add a,a
        ld e,a
        ld d,0
        ld hl,wk_tab
        add hl,de
        ld e,(hl)
        inc hl
        ld d,(hl)
        ld (wk_a),de
        ld a,b
        ld b,c
        ld c,a                  ; (now C = b, B = a)
        call wt_pair
        add a,a
        ld e,a
        ld d,0
        ld hl,wk_tab
        add hl,de
        ld e,(hl)
        inc hl
        ld d,(hl)
        ld (wk_b),de
        call wt_hit             ; b hurt by a
        ld a,b
        ld b,c
        ld c,a
wt_hit:                         ; C = the car hurt, B = the other: its damage, once in DMG_COOL pictures
        ld a,c
        cp 5                    ; (you on NOS: your own row)
        jr c,wh_0
        xor a
wh_0:
        add a,a
        add a,a
        add a,a
        add a,(arm_tab+2) AND 255
        ld l,a
        adc a,(arm_tab+2)/256
        sub l
        ld h,a                  ; HL -> its quarters (the cool-down after)
        inc hl
        ld a,(hl)
        or a
        ret nz
        ld (hl),DMG_COOL
        dec hl
        push hl
        ld a,c
        call wt_pair
        ld e,a
        ld d,0
        ld hl,wq_tab
        add hl,de
        ld a,(hl)
        pop hl
        ld e,a
        ld a,c
        or a
        jr z,wh_you
        cp 5
        jr z,wh_you
        push hl                 ; (a computer car: it flickers for WT_FLASH pictures - Grant, 22 Nov 2026: "I hit another car -
        inc hl                  ; like the clown car and it does not seem to take damage")
        inc hl
        ld (hl),WT_FLASH
        pop hl
        ld a,e
        jr wh_add
wh_you: ld a,e                  ; (yours: half - Grant, 22 Nov 2026, "my damage still goes too fast")
        inc a
        srl a
wh_add: add a,(hl)
        cp 33
        jr c,wh_1
        ld a,32
wh_1:   ld (hl),a
        ld e,a
        ld a,c
        or a
        jr z,wh_y
        cp 5
        ret nz
wh_y:   ld a,e                  ; yours: the mug's points
        rrca
        rrca
        and 63
        ld (dmg),a
        ret
wt_pair:                        ; A = C x 6 + B
        ld a,c
        add a,a
        add a,c
        add a,a
        add a,b
        ret
wt_kick:                        ; BC = KICK or -KICK, the way car a goes, A = the axis (C_VX or C_VY): BC = a's kick by the weights
        ld (wk_ax),a            ; that way, HL = b's the other way - but a car that is you on NOS keeps its own speed
        call wt_kick0
        push de
        ld a,(wk_ka)
        or a
        jr z,wkt_b
        push hl
        push ix
        pop hl
        ld a,(wk_ax)
        ld e,a
        ld d,0
        add hl,de
        ld c,(hl)
        inc hl
        ld b,(hl)               ; BC = a's own speed that way
        pop hl
wkt_b:  ld a,(wk_kb)
        or a
        jr z,wkt_x
        ld a,(wk_ax)
        add a,(tb-1) AND 255
        ld e,a
        adc a,(tb-1)/256
        sub e
        ld d,a
        ex de,hl
        ld a,(hl)
        inc hl
        ld h,(hl)
        ld l,a                  ; HL = b's own speed that way
wkt_x:  pop de
        ret
wt_kick0:
        push de
        ld a,b
        rla
        ld hl,(wk_a)
        ld de,(wk_b)
        ld b,h
        ld c,l
        jr c,wkk_n
        ld hl,0
        or a
        sbc hl,de
        pop de
        ret
wkk_n:  ld a,c
        cpl
        ld c,a
        ld a,b
        cpl
        ld b,a
        inc bc
        ex de,hl
        pop de
        ret
wt_tick:                        ; each picture: the five cool-downs and hit flashes run down
        ld hl,arm_tab+3
        ld de,8
        ld b,5
wtk_1:  ld a,(hl)
        or a
        jr z,wtk_2
        dec (hl)
wtk_2:  inc hl
        ld a,(hl)
        or a
        jr z,wtk_3
        dec (hl)
wtk_3:  dec hl
        add hl,de
        djnz wtk_1
        ret
WT_FLASH equ 12                 ; pictures a computer car flickers after it is hurt (about a second at 12.5 a second)
wt_slow:                        ; (physics, IX = a computer car, DE and BC its push): less by a 64th for every 8 quarters (a 32nd, tried first, made
                                ; the race easier - the careful driver 4th, not last: 22 Nov 2026)
        ld a,(ix+C_KIND)
        add a,a
        add a,a
        add a,a
        add a,(arm_tab+2) AND 255
        ld l,a
        adc a,(arm_tab+2)/256
        sub l
        ld h,a
        ld a,(hl)
        rrca
        rrca
        rrca
        and 7
        ret z
wsl_1:  push af
        ld h,d
        ld l,e
        rept 6
        sra h
        rr l
        endm
        ex de,hl
        or a
        sbc hl,de
        ex de,hl
        ld h,b
        ld l,c
        rept 6
        sra h
        rr l
        endm
        push hl
        ld h,b
        ld l,c
        pop bc
        or a
        sbc hl,bc
        ld b,h
        ld c,l
        pop af
        dec a
        jr nz,wsl_1
        ret
wk_a:   dw 0
wk_ka:  db 0
wk_kb:  db 0
wk_ax:  db 0
wk_b:   dw 0
wk_tab:                         ; car a's kick from car b (a x 6 + b; 5 is YOU ON NOS - 3 x your weight)
        dw (2*KICK*CD_ARM_0+(CD_ARM_0+CD_ARM_0)/2)/(CD_ARM_0+CD_ARM_0), (2*KICK*CD_ARM_1+(CD_ARM_0+CD_ARM_1)/2)/(CD_ARM_0+CD_ARM_1), (2*KICK*CD_ARM_2+(CD_ARM_0+CD_ARM_2)/2)/(CD_ARM_0+CD_ARM_2), (2*KICK*CD_ARM_3+(CD_ARM_0+CD_ARM_3)/2)/(CD_ARM_0+CD_ARM_3), (2*KICK*CD_ARM_4+(CD_ARM_0+CD_ARM_4)/2)/(CD_ARM_0+CD_ARM_4), (2*KICK*(3*CD_ARM_0)+(CD_ARM_0+(3*CD_ARM_0))/2)/(CD_ARM_0+(3*CD_ARM_0))   ; car 0 kicked by 0-5
        dw (2*KICK*CD_ARM_0+(CD_ARM_1+CD_ARM_0)/2)/(CD_ARM_1+CD_ARM_0), (2*KICK*CD_ARM_1+(CD_ARM_1+CD_ARM_1)/2)/(CD_ARM_1+CD_ARM_1), (2*KICK*CD_ARM_2+(CD_ARM_1+CD_ARM_2)/2)/(CD_ARM_1+CD_ARM_2), (2*KICK*CD_ARM_3+(CD_ARM_1+CD_ARM_3)/2)/(CD_ARM_1+CD_ARM_3), (2*KICK*CD_ARM_4+(CD_ARM_1+CD_ARM_4)/2)/(CD_ARM_1+CD_ARM_4), (2*KICK*(3*CD_ARM_0)+(CD_ARM_1+(3*CD_ARM_0))/2)/(CD_ARM_1+(3*CD_ARM_0))   ; car 1 kicked by 0-5
        dw (2*KICK*CD_ARM_0+(CD_ARM_2+CD_ARM_0)/2)/(CD_ARM_2+CD_ARM_0), (2*KICK*CD_ARM_1+(CD_ARM_2+CD_ARM_1)/2)/(CD_ARM_2+CD_ARM_1), (2*KICK*CD_ARM_2+(CD_ARM_2+CD_ARM_2)/2)/(CD_ARM_2+CD_ARM_2), (2*KICK*CD_ARM_3+(CD_ARM_2+CD_ARM_3)/2)/(CD_ARM_2+CD_ARM_3), (2*KICK*CD_ARM_4+(CD_ARM_2+CD_ARM_4)/2)/(CD_ARM_2+CD_ARM_4), (2*KICK*(3*CD_ARM_0)+(CD_ARM_2+(3*CD_ARM_0))/2)/(CD_ARM_2+(3*CD_ARM_0))   ; car 2 kicked by 0-5
        dw (2*KICK*CD_ARM_0+(CD_ARM_3+CD_ARM_0)/2)/(CD_ARM_3+CD_ARM_0), (2*KICK*CD_ARM_1+(CD_ARM_3+CD_ARM_1)/2)/(CD_ARM_3+CD_ARM_1), (2*KICK*CD_ARM_2+(CD_ARM_3+CD_ARM_2)/2)/(CD_ARM_3+CD_ARM_2), (2*KICK*CD_ARM_3+(CD_ARM_3+CD_ARM_3)/2)/(CD_ARM_3+CD_ARM_3), (2*KICK*CD_ARM_4+(CD_ARM_3+CD_ARM_4)/2)/(CD_ARM_3+CD_ARM_4), (2*KICK*(3*CD_ARM_0)+(CD_ARM_3+(3*CD_ARM_0))/2)/(CD_ARM_3+(3*CD_ARM_0))   ; car 3 kicked by 0-5
        dw (2*KICK*CD_ARM_0+(CD_ARM_4+CD_ARM_0)/2)/(CD_ARM_4+CD_ARM_0), (2*KICK*CD_ARM_1+(CD_ARM_4+CD_ARM_1)/2)/(CD_ARM_4+CD_ARM_1), (2*KICK*CD_ARM_2+(CD_ARM_4+CD_ARM_2)/2)/(CD_ARM_4+CD_ARM_2), (2*KICK*CD_ARM_3+(CD_ARM_4+CD_ARM_3)/2)/(CD_ARM_4+CD_ARM_3), (2*KICK*CD_ARM_4+(CD_ARM_4+CD_ARM_4)/2)/(CD_ARM_4+CD_ARM_4), (2*KICK*(3*CD_ARM_0)+(CD_ARM_4+(3*CD_ARM_0))/2)/(CD_ARM_4+(3*CD_ARM_0))   ; car 4 kicked by 0-5
        dw (2*KICK*CD_ARM_0+((3*CD_ARM_0)+CD_ARM_0)/2)/((3*CD_ARM_0)+CD_ARM_0), (2*KICK*CD_ARM_1+((3*CD_ARM_0)+CD_ARM_1)/2)/((3*CD_ARM_0)+CD_ARM_1), (2*KICK*CD_ARM_2+((3*CD_ARM_0)+CD_ARM_2)/2)/((3*CD_ARM_0)+CD_ARM_2), (2*KICK*CD_ARM_3+((3*CD_ARM_0)+CD_ARM_3)/2)/((3*CD_ARM_0)+CD_ARM_3), (2*KICK*CD_ARM_4+((3*CD_ARM_0)+CD_ARM_4)/2)/((3*CD_ARM_0)+CD_ARM_4), (2*KICK*(3*CD_ARM_0)+((3*CD_ARM_0)+(3*CD_ARM_0))/2)/((3*CD_ARM_0)+(3*CD_ARM_0))   ; car 5 kicked by 0-5
wq_tab:                         ; car v's damage from car o, quarters (v x 6 + o)
        db (4*CD_ARM_0+CD_ARM_0/2)/CD_ARM_0, (4*CD_ARM_1+CD_ARM_0/2)/CD_ARM_0, (4*CD_ARM_2+CD_ARM_0/2)/CD_ARM_0, (4*CD_ARM_3+CD_ARM_0/2)/CD_ARM_0, (4*CD_ARM_4+CD_ARM_0/2)/CD_ARM_0, (4*(3*CD_ARM_0)+CD_ARM_0/2)/CD_ARM_0   ; car 0 hurt by 0-5
        db (4*CD_ARM_0+CD_ARM_1/2)/CD_ARM_1, (4*CD_ARM_1+CD_ARM_1/2)/CD_ARM_1, (4*CD_ARM_2+CD_ARM_1/2)/CD_ARM_1, (4*CD_ARM_3+CD_ARM_1/2)/CD_ARM_1, (4*CD_ARM_4+CD_ARM_1/2)/CD_ARM_1, (4*(3*CD_ARM_0)+CD_ARM_1/2)/CD_ARM_1   ; car 1 hurt by 0-5
        db (4*CD_ARM_0+CD_ARM_2/2)/CD_ARM_2, (4*CD_ARM_1+CD_ARM_2/2)/CD_ARM_2, (4*CD_ARM_2+CD_ARM_2/2)/CD_ARM_2, (4*CD_ARM_3+CD_ARM_2/2)/CD_ARM_2, (4*CD_ARM_4+CD_ARM_2/2)/CD_ARM_2, (4*(3*CD_ARM_0)+CD_ARM_2/2)/CD_ARM_2   ; car 2 hurt by 0-5
        db (4*CD_ARM_0+CD_ARM_3/2)/CD_ARM_3, (4*CD_ARM_1+CD_ARM_3/2)/CD_ARM_3, (4*CD_ARM_2+CD_ARM_3/2)/CD_ARM_3, (4*CD_ARM_3+CD_ARM_3/2)/CD_ARM_3, (4*CD_ARM_4+CD_ARM_3/2)/CD_ARM_3, (4*(3*CD_ARM_0)+CD_ARM_3/2)/CD_ARM_3   ; car 3 hurt by 0-5
        db (4*CD_ARM_0+CD_ARM_4/2)/CD_ARM_4, (4*CD_ARM_1+CD_ARM_4/2)/CD_ARM_4, (4*CD_ARM_2+CD_ARM_4/2)/CD_ARM_4, (4*CD_ARM_3+CD_ARM_4/2)/CD_ARM_4, (4*CD_ARM_4+CD_ARM_4/2)/CD_ARM_4, (4*(3*CD_ARM_0)+CD_ARM_4/2)/CD_ARM_4   ; car 4 hurt by 0-5
        db (4*CD_ARM_0+(3*CD_ARM_0)/2)/(3*CD_ARM_0), (4*CD_ARM_1+(3*CD_ARM_0)/2)/(3*CD_ARM_0), (4*CD_ARM_2+(3*CD_ARM_0)/2)/(3*CD_ARM_0), (4*CD_ARM_3+(3*CD_ARM_0)/2)/(3*CD_ARM_0), (4*CD_ARM_4+(3*CD_ARM_0)/2)/(3*CD_ARM_0), (4*(3*CD_ARM_0)+(3*CD_ARM_0)/2)/(3*CD_ARM_0)   ; car 5 hurt by 0-5
