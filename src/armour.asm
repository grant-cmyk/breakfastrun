; ARMOUR AND WEAPONS (ARMOUR=1; Grant, 17 Nov 2026) - the parts that run every picture. The account of it, and EVERY
; NUMBER TO TUNE, is src/armour_tune.asm; the parts that run rarely are src/armour_low.asm.
; ARM_ROW (IX = a car), ARM_ROW_A (A = which car, 0 you): HL = its row of arm_tab, at its PIECES. Keeps BC, DE.
arm_row:
        ld a,(ix+C_KIND)
arm_row_a:
        add a,a
        add a,a
        add a,a
        add a,(arm_tab+1) AND 255
        ld l,a
        adc a,(arm_tab+1)/256
        sub l
        ld h,a
        ret

; ARM_BUMP (from bump, when two cars touch: IX = one, bump_b = the other, tb = the other's copy): both lose armour by
; how fast they were closing, each by its own rating.
arm_bump:
        if OPT_RACEONLY         ; (RACEONLY, 22 Nov 2026: no COMBAT - it returns at once, as RACE made it)
        ret
        else
        ld l,(ix+C_VX)
        ld h,(ix+C_VX+1)
        ld de,(TB_VX)
        or a
        sbc hl,de
        call abs_hl
        push hl
        ld l,(ix+C_VY)
        ld h,(ix+C_VY+1)
        ld de,(TB_VY)
        or a
        sbc hl,de
        call abs_hl
        pop de
        add hl,de               ; the closing speed: across plus down, 256 = a pixel a TV frame
        rept 8-ARM_DIV
        add hl,hl
        endm
        ld a,h
        add a,ARM_MIN
        ld b,a                  ; B = the damage, for both
        push bc
        ld a,(ix+C_KIND)
        call abp_1
        pop bc
        ld hl,(bump_b)
        ld de,C_KIND
        add hl,de
        ld a,(hl)
abp_1:
        call arm_row_a
        push hl
        inc hl
        inc hl
        inc hl
        inc hl                  ; (bumped a moment ago: it is the same crash)
        ld a,(hl)
        or a
        jr nz,abp_no
        ld (hl),ARM_COOL
        pop hl
        jr arm_hurt
abp_no:
        pop hl
        ret
; ARM_HURT (HL = a car's row, B = damage): its armour takes it; a piece goes (and flashes on the health blocks) each time the
; damage in the piece it is on reaches what a piece takes.
arm_hurt:
        ld a,(hl)
        or a
        ret z                   ; (none left: it limps already)
        ld c,a
        dec hl
        ld d,(hl)               ; D = what a piece takes
        inc hl
        inc hl
        ld a,(hl)
        add a,b
ahh_1:
        cp d
        jr c,ahh_2
        sub d
        inc hl
        ld (hl),ARM_FLASH
        dec hl
        dec c
        jr nz,ahh_1
        xor a
ahh_2:
        ld (hl),a
        dec hl
        ld (hl),c
        ret

; ARM_STUN (HL = a car's row, B = damage): a weapon has hit it - it spins where it is, and loses armour. The crash
; noise; the border red if it is your car.
arm_stun:
        push hl
        inc hl
        inc hl
        inc hl
        ld (hl),SPIN_T
        inc hl
        inc hl
        ld (hl),WPN_SAFE
        inc hl
        inc (hl)
        ld a,SND_CRASH
        ld (snd_bump),a
        pop hl
        ld a,l
        cp (arm_tab+1) AND 255
        jr nz,arm_hurt
        push hl
        push bc
        ld hl,10*256+2
        call flash
        pop bc
        pop hl
        jr arm_hurt
        endif

; ARM_PHYS (from physics, IX = a car): is it spinning? Then it turns on the spot - SPIN_RATE headings for each of this
; move's TV frames - with no speed at all, and physics does nothing else for it (NZ). Z: it is not.
arm_phys:
        if OPT_RACEONLY         ; (RACEONLY, 22 Nov 2026: no COMBAT - it returns at once, as RACE made it)
        xor a
        ret
        else
        call arm_row
        inc hl
        inc hl
        inc hl
        ld a,(hl)
        or a
        ret z
        ld b,a
        ld a,(ph_steps)         ; (no more TV frames than the spin has left: it ends facing the way it began)
        cp b
        jr c,aph_1
        ld a,b
aph_1:
        ld c,a
        ld a,b
        sub c
        ld (hl),a
        ld a,c
        rept SPIN_RATE-1
        add a,c
        endm
        add a,(ix+C_ANG)
        and 63
        ld (ix+C_ANG),a
        xor a
        ld (ix+C_VX),a
        ld (ix+C_VX+1),a
        ld (ix+C_VY),a
        ld (ix+C_VY+1),a
        inc a
        ret
        endif

; ARM_LIMP (from physics, IX = a computer car, DE and BC its push): no armour left - the push halved, and with it the
; car's top speed. (Your car: grip.asm, yg_d2.)
arm_limp:
        if OPT_RACEONLY         ; (RACEONLY, 22 Nov 2026: no COMBAT - it returns at once, as RACE made it)
        ret
        else
        call arm_row
        ld a,(hl)
        or a
        ret nz
        rept ARM_LIMP_SHIFT
        sra d
        rr e
        sra b
        rr c
        endm
        ret
        endif

; ARM_TICK: once a picture, after the cars have moved and bumped. The tank and the clown look for somebody (first, so
; that a piece they knock off flashes in this same picture); the cool-downs run down; a row whose health blocks are flashing is drawn
; again (a car with none left: all the time - its red outlines flash).
arm_tick:
        if OPT_RACEONLY         ; (RACEONLY, 22 Nov 2026: no COMBAT - it returns at once, as RACE made it)
        ret
        else
        call arm_tank
        call arm_clown_t
        ld b,NCARS
atk_1:
        push bc
        ld a,b
        dec a                   ; the place, 4 to 0
        ld e,a
        ld d,0
        ld hl,order
        add hl,de
        ld a,(hl)
        call arm_row_a
        inc hl
        inc hl
        ld a,(hl)
        or a
        jr z,atk_2
        dec (hl)
        push hl
        ld a,e
        call arm_bar_t
        pop hl
atk_2:
        inc hl
        inc hl
        ld a,(hl)
        or a
        jr z,atk_3
        dec (hl)
atk_3:
        inc hl
        ld a,(hl)
        or a
        jr z,atk_4
        dec (hl)
atk_4:
        pop bc
        djnz atk_1
        ret                     ; (the mug that showed your armour has gone: the health blocks in the race order show it)
; ARM_CLOWN_T: the clown's wheels, once a picture.
arm_clown_t:
        ld ix,cars+ARM_CLOWN*C_SIZE
        ld hl,wh_out
        ld a,(hl)
        or a
        jr z,acl_in
        dec (hl)
        call arm_can            ; they are out: does a car touch one?
        ret nz
        ld b,NCARS
acl_1:
        push bc
        ld a,b
        dec a
        cp (ix+C_KIND)
        jr z,acl_n
        ld (acl_c+1),a
        call arm_iy
        call arm_rel
        jr c,acl_n
        ld bc,WH_LEN/2*256+WH_REACH/2
        call arm_box
        jr nc,acl_n
acl_c:  ld a,0
        call arm_row_a
        push hl
        ld de,A_WSAFE
        add hl,de
        ld a,(hl)
        pop hl
        or a
        jr nz,acl_n             ; (hit a moment ago)
        ld b,WHEEL_DMG
        call arm_stun
        ld hl,wh_hits
        inc (hl)
acl_n:
        pop bc
        djnz acl_1
        ret
acl_in:
        inc hl                  ; (wh_cool is the byte after)
        ld a,(hl)
        or a
        jr z,acl_2
        dec (hl)
        ret
acl_2:
        call arm_can
        ret nz
        ld a,(wh_ammo)          ; no wheel-outs left this race
        or a
        ret z
        ld hl,wh_tg             ; one car a picture: is it alongside?
        call arm_next
        call arm_rel
        ret c
        ld bc,WH_SEE_LEN/2*256+WH_SEE/2
        call arm_box
        ret nc
; ARM_WHEELS: the wheels go out (for WH_TIME pictures; not again for WH_COOL).
arm_wheels:
        ld hl,wh_ammo           ; (one fewer)
        dec (hl)
        ld hl,WH_TIME+256*WH_COOL
        ld (wh_out),hl
        ld hl,wh_outs
        inc (hl)
        ld hl,24*256+5          ; a short low beep
        ld (snd_fxt),hl
        ret

; ARM_TANK: the tank's gun, once a picture. A shell in the air is moved; if there is none and the gun has cooled, he
; looks at one other car (a different one each picture): in line ahead and near enough? Then he fires.
arm_tank:
        ld a,(sh_life)
        or a
        jr nz,sh_move
        ld ix,cars+ARM_TANK*C_SIZE
        ld hl,sh_cool
        ld a,(hl)
        or a
        jr z,atn_1
        dec (hl)
        ret
atn_1:
        call arm_can
        ret nz
        ld a,(sh_ammo)          ; none left this race
        or a
        ret z
        if TANK_STRAIGHT        ; his nose square to the screen, give or take a step: the shell goes straight
        ld a,(ix+C_ANG)
        inc a
        and 15
        cp 3
        ret nc
        endif
        ld hl,sh_tg
        call arm_next
        call arm_rel            ; HL = how far ahead, DE = how far to the side (32 = a pixel)
        ret c
        ld a,h                  ; ahead of him by 16 pixels or more (not level, not behind)
        sub 2
        cp 0x7E
        ret nc
        ld bc,TANK_RANGE/2*256+TANK_AIM/2
        call arm_box
        ret nc
        call arm_fire           ; (armour_low.asm: it happens once in a while)
; SH_MOVE: the shell flies - a step for each of this picture's TV frames. It ends at a car (which spins and loses
; armour), at the end of its range, or on the grass (looked at once a picture).
sh_move:
        ld a,(dt)
        ld b,a
shm_1:
        push bc
        ld hl,sh_rec+C_XF
        ld de,(sh_vx)
        call sh_add
        ld de,(sh_vy)
        call sh_add
        ld hl,sh_life
        dec (hl)
        jr z,shm_x
        ld iy,cars
        ld c,0
shm_c:
        ld a,(sh_own)
        cp c
        jr z,shm_n
        ld l,(iy+C_X)
        ld h,(iy+C_X+1)
        ld de,(sh_rec+C_X)
        call shm_near
        jr nc,shm_n
        ld l,(iy+C_Y)
        ld h,(iy+C_Y+1)
        ld de,(sh_rec+C_Y)
        call shm_near
        jr nc,shm_n
        ld a,c                  ; a hit
        call arm_row_a
        ld b,SHELL_DMG
        call arm_stun
        ld hl,sh_hits
        inc (hl)
        xor a
        ld (sh_life),a
shm_x:
        pop bc
        ret
shm_n:
        ld de,C_SIZE
        add iy,de
        inc c
        ld a,c
        cp NCARS
        jr nz,shm_c
        pop bc
        djnz shm_1
        ld ix,sh_rec            ; on the grass? it ends there
        call surface
        cp 3
        ret z
        xor a
        ld (sh_life),a
        ret
shm_near:                       ; carry: HL and DE are within SHELL_HIT - 1 of each other
        or a
        sbc hl,de
        call abs_hl
        ld a,h
        or a
        ret nz
        ld a,l
        cp SHELL_HIT
        ret
sh_add:                         ; the three bytes at HL (fraction, whole pixels) += DE; HL to the next three
        ld a,d
        add a,a
        sbc a,a
        ld c,a
        ld a,(hl)
        add a,e
        ld (hl),a
        inc hl
        ld a,(hl)
        adc a,d
        ld (hl),a
        inc hl
        ld a,(hl)
        adc a,c
        ld (hl),a
        inc hl
        ret

; ARM_CAN (IX = a car with a weapon): may it use it now? Z: yes - the race is on, it has not finished, it is not spinning.
arm_can:
        ld a,(race_on)
        or a
        jr z,acn_no
        ld a,(ix+C_LAPS)
        cp LAPS+1
        jr nc,acn_no
        call arm_row
        inc hl
        inc hl
        inc hl
        ld a,(hl)
        or a
        ret
acn_no:
        or 1
        ret
; ARM_NEXT (IX = a car, HL = its count): IY = the next other car, a different one each time.
arm_next:
        ld a,(hl)
an_1:
        inc a
        cp NCARS
        jr c,an_2
        xor a
an_2:
        cp (ix+C_KIND)
        jr z,an_1
        ld (hl),a
arm_iy:                         ; A = a car: IY = its record
        ld iy,cars
        or a
        ret z
        ld de,C_SIZE
an_3:
        add iy,de
        dec a
        jr nz,an_3
        ret
; ARM_REL (IX = a car, IY = another): where the other is, seen from the first - HL = how far AHEAD of it along its
; heading (less than 0: behind), DE = how far to its SIDE; 32 = a pixel. Carry: over 126 pixels off across or down
; (too far to matter). About 900 T.
arm_rel:
        ld l,(iy+C_X)
        ld h,(iy+C_X+1)
        ld e,(ix+C_X)
        ld d,(ix+C_X+1)
        call arl_h
        ret c
        ld (arl_dx),a
        ld l,(iy+C_Y)
        ld h,(iy+C_Y+1)
        ld e,(ix+C_Y)
        ld d,(ix+C_Y+1)
        call arl_h
        ret c
        ld (arl_dy),a
        ld a,(ix+C_ANG)
        call heading_push       ; E across, C down: 64 the way it points
        ld a,c
        ld (arl_hy),a
        ld a,e
        ld (arl_hx),a
        ld bc,(arl_dx)          ; (C = across to it / 2, B = the heading's across)
        call mul8s
        push hl
        ld bc,(arl_dy)
        call mul8s
        pop de
        add hl,de
        push hl                 ; ahead
        ld a,(arl_hx)
        ld b,a
        ld a,(arl_dy)
        ld c,a
        call mul8s
        push hl
        ld a,(arl_hy)
        ld b,a
        ld a,(arl_dx)
        ld c,a
        call mul8s
        pop de
        ex de,hl
        or a
        sbc hl,de
        ex de,hl                ; DE = to the side
        pop hl
        or a
        ret
arl_h:                          ; HL - DE -> A = half of it, as a signed byte; carry if it is not within 126
        or a
        sbc hl,de
        ld de,126
        add hl,de
        ld a,h
        or a
        scf
        ret nz
        ld a,l
        cp 253
        ccf
        ret c
        sub 126
        sra a
        or a
        ret
; ARM_BOX (HL = ahead, DE = to the side, from arm_rel; B, C = how far each may be, in steps of 2 pixels): carry if the
; other car is within both.
arm_box:
        call abx_1
        cp b
        ret nc
        ex de,hl
        call abx_1
        cp c
        ret
abx_1:
        call abs_hl
        add hl,hl
        add hl,hl
        ld a,h
        ret
        endif

; ARM_DRAW: once a picture, after the cars are drawn and before the fixed boxes: the shell and the clown's wheels.
; Each is made of DOTS (arm_dot), which go by the cars' rule for the colour squares - see arm_dot.
arm_draw:
        if OPT_RACEONLY         ; (RACEONLY, 22 Nov 2026: no COMBAT - it returns at once, as RACE made it)
        ret
        else
        ld a,(sh_life)
        or a
        jr z,adr_w
        ld a,SHELL_INK
        ld (rt_ink),a
        ld hl,(sh_rec+C_X)
        ld de,(sh_rec+C_Y)
        call arm_dot
adr_w:
        ld a,(wh_out)
        or a
        ret z
        ld ix,cars+ARM_CLOWN*C_SIZE
        ld a,(rt_inks+ARM_CLOWN)
        ld (rt_ink),a
        ld a,(ix+C_ANG)
        call heading_push       ; E across, C down: the way he points. His side is (- down, across)
        ld a,e
        call adw_sc
        ld b,a
        ld a,c
        call adw_sc
        neg
        ld d,a
        ld e,b                  ; D, E = across and down to a wheel's outer end
        call adw_2
        ld a,d                  ; and three quarters of the way out: with the first, a bar 6 pixels long each side
        call adw_q
        ld d,a
        ld a,e
        call adw_q
        ld e,a
adw_2:
        call adw_1
        ld a,d
        neg
        ld d,a
        ld a,e
        neg
        ld e,a
adw_1:
        push de
        ld l,(ix+C_X)
        ld h,(ix+C_X+1)
        ld a,d
        call adw_add
        push hl
        ld l,(ix+C_Y)
        ld h,(ix+C_Y+1)
        ld a,e
        call adw_add
        ex de,hl
        pop hl
        call arm_dot
        pop de
        ret
adw_sc:                         ; A (64 = the way he points) -> A = WH_DRAW pixels of it
        sra a
        ld l,a
        add a,a
        add a,l                 ; x 3 / 2
        if WH_DRAW = 12
        sra a
        sra a
        sra a
        else
        .error adw_sc: WH_DRAW is 12 (64 x 3 / 16) - change the sums here with it
        endif
        ret
adw_q:                          ; A -> three quarters of A
        ld l,a
        sra a
        sra a
        neg
        add a,l
        ret
adw_add:                        ; HL += A (signed)
        ld c,a
        add a,a
        sbc a,a
        ld b,a
        add hl,bc
        ret

; ARM_DOT (HL, DE = a place in the world, given as a car's own x and y are: the dot is put where that car's middle
; would be; rt_ink = its colour): a dot 3 x 3 in the back buffer, if it is inside the window. Keeps IX.
; THE COLOUR SQUARES (two colours a square): the dot is held inside ONE square (moved up to 2 pixels if it would
; straddle two). If nothing was showing in that square (plain road, or all grass) the square is brought into the
; buffer by the cars' own rule (rq_cell) and takes the dot's colour - on black for the road, on green for grass.
; If a car is already in the square, or grass and road share it, the square's colours are NOT changed: the dot shows in
; that car's colour, or in the grass's green.
arm_dot:
        ld bc,(camx)
        or a
        sbc hl,bc
        ld bc,16+8-1
        add hl,bc               ; its left pixel's x in the buffer (the window starts at 16)
        ld a,h
        or a
        ret nz
        ld a,l
        cp 16
        ret c
        cp WIN_W*8+16-2
        ret nc
        ld c,a
        ex de,hl
        ld de,(camy)
        or a
        sbc hl,de
        ld de,BUF_TOP+8-1
        add hl,de               ; its top line in the buffer (the window starts at BUF_TOP)
        ld a,h
        or a
        ret nz
        ld a,l
        cp BUF_TOP
        ret c
        cp BUF_TOP+WIN_H-2
        ret nc
        ld b,a
        rrca                    ; HL = its square in rt_sh
        rrca
        rrca
        and 0x1F
        rrca
        rrca
        rrca
        ld l,a
        and 3
        add a,RT_SH/256
        ld h,a
        ld a,c
        rrca
        rrca
        rrca
        and 0x1F
        dec a
        ld e,a
        ld a,l
        and 0xE0
        add a,e
        ld l,a
        ld a,(hl)
        add a,a
        jr nc,ado_1             ; in the buffer already (a car's square): its colours stay
        push bc
        call rq_setpg
        call rq_cell
        pop bc
ado_1:
        ld a,c                  ; across, inside the square: 0 to 5
        and 7
        cp 6
        jr c,ado_2
        ld a,5
ado_2:
        ld e,0xE0
        or a
        jr z,ado_4
ado_3:
        srl e
        dec a
        jr nz,ado_3
ado_4:
        ld a,b                  ; and down
        and 7
        cp 6
        jr c,ado_5
        ld a,b
        and 0xF8
        or 5
        ld b,a
ado_5:
        call buf_addr
        ld a,(hl)
        or e
        ld (hl),a
        inc h
        ld a,(hl)
        or e
        ld (hl),a
        inc h
        ld a,(hl)
        or e
        ld (hl),a
        ret
        endif

; each car's row (arm_row): what a piece of its armour takes - from its card (cd_arm, src/cards.asm) - and the 7 bytes the
; game keeps for it
arm_tab:
        db CD_ARM_0, ARM_PIECES,0,0,0,0,0,0
        db CD_ARM_1, ARM_PIECES,0,0,0,0,0,0
        db CD_ARM_2, ARM_PIECES,0,0,0,0,0,0
        db CD_ARM_3, ARM_PIECES,0,0,0,0,0,0
        db CD_ARM_4, ARM_PIECES,0,0,0,0,0,0
