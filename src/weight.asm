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
        ld a,b
        ld (wk_ca),a            ; (the kinds, for the damage - wt_kick works out who hit whom first)
        ld a,c
        ld (wk_cb),a
        ret
wt_hit:                         ; C = the car hurt, B = the other: its damage, once in DMG_COOL pictures (the hitter's quarter went: 22 Nov 2026)
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
wh_you: ld a,e                  ; (yours: a quarter - Grant, 22 Nov 2026, "my damage still goes too fast", then "reduce the
        add a,3                 ; damage again my car gets"; a half before)
        srl a
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
wt_kick:                        ; BC = KICK or -KICK, the way car a goes, A = the axis (C_VX or C_VY): BC = a's new speed that way,
        push de                 ; (DE, racer.asm's 2-pixel nudge apart, kept: without it the cars were thrown up to 160 px)
        call wt_kick1
        pop de
        ret
wt_kick1:
        ld (wk_ax),a            ; HL = b's - BY HOW THE HIT HAPPENED (Grant, 22 Nov 2026: "if I hit the side of another car from
        call wt_kick0           ; the front of my car that that car shifts sideways - so more impact on them, a small impact on
        ld (wk_kav),bc          ; me ... If someone hits you from behind you actually don't get damage and actually get pushed
        ld (wk_kbv),hl          ; forward ... I can basically therefore ram a car off the road by aiming into their side"):
        push ix                 ;   each car's speed TOWARDS the other along the axis (ta, tb). Both over WK_TH: head-on - both
        pop hl                  ;   kicked by the weights and both hurt in full, as before. Else the quicker one is the HITTER:
        ld a,(wk_ax)            ;   it keeps three quarters of its own speed (all of it on NOS) and takes no damage (a quarter of its
        ld e,a                  ;   damage until Grant, 22 Nov 2026 evening); the one hit, if it was moving away (hit from behind), is pushed on by its kick and
        ld d,0                  ;   not hurt; if not (hit in the side, or standing), it is kicked away and hurt in full.
        add hl,de               ;   You on NOS are always the hitter.
        ld e,(hl)
        inc hl
        ld d,(hl)
        ld (wk_va),de
        ld a,(wk_ax)
        add a,(tb-1) AND 255
        ld l,a
        adc a,(tb-1)/256
        sub l
        ld h,a
        ld e,(hl)
        inc hl
        ld d,(hl)
        ld (wk_vb),de
        ld a,(wk_kav+1)         ; a's kick < 0: b lies the + way of a - ta = va, tb = -vb; else ta = -va, tb = vb
        rla
        ld hl,(wk_va)
        call nc,wk_neg
        ld (wk_ta),hl
        ld a,(wk_kav+1)
        rla
        ld hl,(wk_vb)
        call c,wk_neg
        ld (wk_tb),hl
        ld a,(wk_ka)
        or a
        jr nz,wk_ahit
        ld a,(wk_kb)
        or a
        jr nz,wk_bhit
        ld hl,(wk_ta)           ; who hit whom: the quicker towards the other (wk_who FF: b)
        ld de,(wk_tb)
        call wk_lt
        sbc a,a
        ld (wk_who),a
        ld hl,(wk_ta)
        ld de,(wk_tb)
        or a
        jr z,wk_h1
        ex de,hl
wk_h1:  ld (wk_big),hl          ; head-on? the slower one also over WK_TH towards the other AND at least half the quicker's
        ex de,hl                ; speed - a car crossing your path with a little drift towards you is hit in the side
        ld (wk_sm),hl           ; (22 Nov 2026: it was head-on, and you bounced back off it)
        ld de,WK_TH
        call wk_lt
        jr c,wk_roles
        ld hl,(wk_sm)
        add hl,hl
        ld de,(wk_big)
        call wk_lt
        jr c,wk_roles
        call wk_hurt_b          ; head-on: both hurt in full, both kicked
        call wk_hurt_a
        ld bc,(wk_kav)
        ld hl,(wk_kbv)
        ret
wk_roles:
        ld a,(wk_who)
        or a
        jr nz,wk_bhit
wk_ahit:                        ; a hit b
        ld hl,(wk_va)
        ld a,(wk_ka)
        or a
        call z,wk_q34
        push hl                 ; (a's speed - the hitter takes NO damage: Grant, 22 Nov 2026, "If you hit the side of a car with
                                ; the front, you get no damage"; a quarter before)
        ld hl,(wk_tb)           ; (moving away means faster than WK_TH: a car crossing in front of you with a little drift
        ld de,0x10000-WK_TH     ; away from you is hit in the side - 22 Nov 2026)
        call wk_lt
        jr nc,wka_s
        ld hl,(wk_vb)           ; b was moving away: pushed on, not hurt
        ld de,(wk_kbv)
        add hl,de
        pop bc
        ret
wka_s:                          ; b hit in the side (or standing, or slower towards a): kicked away, hurt in full
        call wk_hurt_b
        ld hl,(wk_kbv)
        pop bc
        ret
wk_bhit:                        ; b hit a
        ld hl,(wk_vb)
        ld a,(wk_kb)
        or a
        call z,wk_q34
        push hl                 ; (b's speed - the hitter takes NO damage: Grant, 22 Nov 2026, "If you hit the side of a car with
                                ; the front, you get no damage"; a quarter before)
        ld hl,(wk_ta)
        ld de,0x10000-WK_TH
        call wk_lt
        jr nc,wkb_s
        ld hl,(wk_va)
        ld de,(wk_kav)
        add hl,de
        ld b,h
        ld c,l
        pop hl
        ret
wkb_s:
        call wk_hurt_a
        ld bc,(wk_kav)
        pop hl
        ret
wk_hurt_a:                      ; a hurt by b
        ld a,(wk_ca)
        ld c,a
        ld a,(wk_cb)
        ld b,a
        jp wt_hit
wk_hurt_b:
        ld a,(wk_cb)
        ld c,a
        ld a,(wk_ca)
        ld b,a
        jp wt_hit
wk_neg:                         ; HL = -HL
        ld a,h
        cpl
        ld h,a
        ld a,l
        cpl
        ld l,a
        inc hl
        ret
wk_q34:                         ; HL = HL less a quarter of it (signed)
        ld d,h
        ld e,l
        sra d
        rr e
        sra d
        rr e
        or a
        sbc hl,de
        ret
wk_lt:                          ; carry: HL < DE, signed (HL, DE changed)
        ld a,h
        xor 0x80
        ld h,a
        ld a,d
        xor 0x80
        ld d,a
        or a
        sbc hl,de
        ret
WK_TH   equ 64                  ; (a quarter of a pixel a TV frame towards the other: under it a car is not driving into it)
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
wk_ca:  db 0
wk_cb:  db 0
wk_kav: dw 0
wk_kbv: dw 0
wk_va:  dw 0
wk_vb:  dw 0
wk_ta:  dw 0
wk_tb:  dw 0
wk_big: dw 0
wk_sm:  dw 0
wk_who: db 0
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
