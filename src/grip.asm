; =====================================================================
; YOU_GRIP (IX = your car): the tyre-grip model from the Skid Lab (Grant, 10 Nov
; 2026: "I will go with your recommendations" - its starting settings).
; Your speed is kept as FORWARDS (vf, where the car points) and SIDEWAYS (vs):
;   - steering turns the car, not the speed: (vf, vs) turn the other way by
;     one heading step (5.625 degrees), with shifts - no multiplying
;   - the engine and drag only change vf (push 0.25, drag 1/8: top speed 1.75)
;   - the tyres cancel vs, but only up to their GRIP a frame (0.085 px): under
;     it the car follows its nose; over it the car SLIDES, and sliding tyres
;     hold 65% of that; holding Q uses 35% of the grip (the friction circle)
;   - a slide never adds speed: over the top speed, vf gives way
; Then the world speed (C_VX, C_VY) = vf along the heading + vs across it, and
; the usual code moves the car. Anything else that changes the world speed - a
; bump, an O, the world's edge, a test - is seen next frame, and (vf, vs) are
; worked out again from it. Multiplying uses quarter squares (sqtab):
; a * b = sq(a + b) - sq(|a - b|), sq(n) = n * n / 4.
; =====================================================================
G_GRIP   equ 22                 ; 0.085 px a frame of sideways speed (8.8)
G_SLIDE  equ 14                 ; ... 65% of it while sliding
G_Q      equ 14                 ; ... 65% while you hold Q (35% to the engine)
G_QSLIDE equ 9                  ; ... both
G_PUSH   equ 64                 ; 0.25 a frame (with drag 1/8: top speed 1.75)
G_TOP    equ 448                ; 1.75 px a frame

you_grip:
        ld a,(ix+C_ANG)         ; this heading's sine and cosine (/128), worked
        inc a                   ; out again only when the heading changes
        ld hl,yg_tang           ; (yg_tang = heading + 1; 0 = none yet)
        cp (hl)
        jr z,yg_tok
        ld (hl),a
        dec a
        call trig
        ld (yg_s),bc            ; C = |sin|, B = its sign (1 = negative)
        ld a,(ix+C_ANG)
        add a,16
        call trig
        ld (yg_c),bc
yg_tok:
        ld l,(ix+C_VX)          ; the world speed changed outside? (a bump, an
        ld h,(ix+C_VX+1)        ; O, the edge, a test)
        ld de,(yg_vx)
        or a
        sbc hl,de
        jp nz,yg_derive
        ld l,(ix+C_VY)
        ld h,(ix+C_VY+1)
        ld de,(yg_vy)
        or a
        sbc hl,de
        jp nz,yg_derive
        ld a,(yg_ang)           ; turned one step? turn (vf, vs) the other way
        ld b,a
        ld a,(ix+C_ANG)
        sub b
        and 63
        jp z,yg_forces
        cp 1
        jp z,yg_right
        cp 63
        jp z,yg_left
yg_derive:                      ; vf = vx sin - vy cos, vs = vx cos + vy sin
        ld l,(ix+C_VX)
        ld h,(ix+C_VX+1)
        ld bc,(yg_s)
        call smul
        push hl
        ld l,(ix+C_VY)
        ld h,(ix+C_VY+1)
        ld bc,(yg_c)
        call smul
        pop de
        ex de,hl
        or a
        sbc hl,de
        ld (yg_vf),hl
        ld l,(ix+C_VX)
        ld h,(ix+C_VX+1)
        ld bc,(yg_c)
        call smul
        push hl
        ld l,(ix+C_VY)
        ld h,(ix+C_VY+1)
        ld bc,(yg_s)
        call smul
        pop de
        add hl,de
        ld (yg_vs),hl
        jp yg_forces
yg_right:                       ; heading +1 step: vf' = vf C + vs S, vs' = vs C - vf S
        call yg_rot
        ld hl,(yg_t1)           ; vf C
        ld de,(yg_t4)           ; vs S
        add hl,de
        ld (yg_vf),hl
        ld hl,(yg_t3)           ; vs C
        ld de,(yg_t2)           ; vf S
        or a
        sbc hl,de
        ld (yg_vs),hl
        jp yg_forces
yg_left:                        ; heading -1 step: vf' = vf C - vs S, vs' = vs C + vf S
        call yg_rot
        ld hl,(yg_t1)
        ld de,(yg_t4)
        or a
        sbc hl,de
        ld (yg_vf),hl
        ld hl,(yg_t3)
        ld de,(yg_t2)
        add hl,de
        ld (yg_vs),hl
yg_forces:
        ld a,(ix+C_ANG)
        ld (yg_ang),a
        ; ---- the engine and drag: forwards only ----
        ld hl,(yg_vf)
        ld de,G_PUSH
        ld a,(BOOST_T)          ; NOS: twice the push (and the top speed)
        or a
        jr z,yg_p1
        ld de,2*G_PUSH
yg_p1:
        ld a,(ix+C_CTRL)
        and CT_GO+CT_BRK
        jr z,yg_drag
        cp CT_GO
        jr z,yg_padd            ; Q: the full push
        sra d                   ; A, or Q and A: half
        rr e
        cp CT_BRK
        jr nz,yg_padd           ; Q and A: half forwards
        or a                    ; A: half backwards
        sbc hl,de
        jr yg_drag
yg_padd:
        add hl,de
yg_drag:
        ld d,h                  ; vf -= vf >> C_FSH (1/8 on the road, 1/4 off it)
        ld e,l
        ld b,(ix+C_FSH)
yg_d1:
        sra d
        rr e
        djnz yg_d1
        or a
        sbc hl,de
        ld a,(ix+C_CTRL)        ; rolling to a stop: tiny speeds are 0
        and CT_GO+CT_BRK
        jr nz,yg_d2
        call yg_tiny
yg_d2:
        ld (yg_vf),hl
        ; ---- the tyres: sideways speed, up to the grip a frame ----
        ld a,(yg_sl)            ; grip: sliding?  holding Q?
        add a,a
        ld b,a
        ld a,(ix+C_CTRL)
        and CT_GO
        jr z,yg_g1
        inc b
yg_g1:
        ld a,b
        ld hl,yg_gtab
        add a,l
        ld l,a
        jr nc,yg_g2
        inc h
yg_g2:
        ld e,(hl)
        ld d,0                  ; DE = the grip this frame
        ld hl,(yg_vs)
        bit 7,h
        jr nz,yg_neg
        or a                    ; vs >= 0: more than the grip?
        sbc hl,de
        jr c,yg_grip
        jr z,yg_grip
        jr yg_slide
yg_neg:
        add hl,de               ; vs < 0: more than the grip the other way?
        bit 7,h
        jr z,yg_grip
yg_slide:
        ld (yg_vs),hl           ; sliding: only the grip's worth goes
        ld a,1
        jr yg_g3
yg_grip:
        ld hl,0                 ; gripping: the car follows its nose
        ld (yg_vs),hl
        xor a
yg_g3:
        ld (yg_sl),a
        or a                    ; the hiss: harder for a bigger slide
        jr z,yg_g4
        ld hl,(yg_vs)
        call abs_hl
        ld a,1
        ld de,128
        or a
        sbc hl,de
        ld a,1
        jr c,yg_g4
        inc a
        ld de,128
        sbc hl,de
        jr c,yg_g4
        inc a
yg_g4:
        ld (snd_skid),a
        ; ---- never faster than the top speed: vf gives way ----
        ld hl,(yg_vf)           ; m = larger of |vf|, |vs| + half the smaller
        call abs_hl
        push hl
        ld hl,(yg_vs)
        call abs_hl
        pop de
        or a
        sbc hl,de
        add hl,de
        jr nc,yg_c1
        ex de,hl
yg_c1:
        srl d
        rr e
        add hl,de
        ld de,G_TOP
        ld a,(BOOST_T)
        or a
        jr z,yg_c2
        ld de,2*G_TOP
yg_c2:
        or a
        sbc hl,de               ; HL = how far over
        jr c,yg_world
        jr z,yg_world
        ex de,hl                ; DE = the excess: take it off |vf|
        ld hl,(yg_vf)
        bit 7,h
        jr nz,yg_c3
        or a
        sbc hl,de
        jr nc,yg_c4
        ld hl,0
        jr yg_c4
yg_c3:
        add hl,de
        bit 7,h
        jr nz,yg_c4
        ld hl,0
yg_c4:
        ld (yg_vf),hl
yg_world:                       ; vx = vf sin + vs cos, vy = vs sin - vf cos
        ld hl,(yg_vf)           ; nothing changed since last frame (straight on
        ld de,(yg_pvf)          ; at a steady speed): the world speed stands
        or a
        sbc hl,de
        jr nz,yg_w1
        ld hl,(yg_vs)
        ld de,(yg_pvs)
        or a
        sbc hl,de
        jr nz,yg_w1
        ld a,(ix+C_ANG)
        ld hl,yg_pang
        cp (hl)
        jr nz,yg_w1
        ld hl,(yg_vx)
        ld (ix+C_VX),l
        ld (ix+C_VX+1),h
        ld hl,(yg_vy)
        ld (ix+C_VY),l
        ld (ix+C_VY+1),h
        ret
yg_w1:
        ld hl,(yg_vf)
        ld (yg_pvf),hl
        ld hl,(yg_vs)
        ld (yg_pvs),hl
        ld a,(ix+C_ANG)
        ld (yg_pang),a
        ld a,h                  ; gripping (no sideways speed): two multiplies
        or l
        jr nz,yg_w2
        ld hl,(yg_vf)
        ld bc,(yg_s)
        call smul
        ld (ix+C_VX),l
        ld (ix+C_VX+1),h
        ld (yg_vx),hl
        ld hl,(yg_vf)
        ld bc,(yg_c)
        call smul
        ex de,hl
        ld hl,0
        or a
        sbc hl,de
        ld (ix+C_VY),l
        ld (ix+C_VY+1),h
        ld (yg_vy),hl
        ret
yg_w2:
        ld hl,(yg_vf)
        ld bc,(yg_s)
        call smul
        push hl
        ld hl,(yg_vs)
        ld bc,(yg_c)
        call smul
        pop de
        add hl,de
        ld (ix+C_VX),l
        ld (ix+C_VX+1),h
        ld (yg_vx),hl
        ld hl,(yg_vs)
        ld bc,(yg_s)
        call smul
        push hl
        ld hl,(yg_vf)
        ld bc,(yg_c)
        call smul
        pop de
        ex de,hl
        or a
        sbc hl,de
        ld (ix+C_VY),l
        ld (ix+C_VY+1),h
        ld (yg_vy),hl
        ret
yg_tiny:                        ; HL: -8..8 (1/32 px) becomes 0
        ld de,8
        add hl,de
        ld a,h
        or a
        jr nz,yt_1
        ld a,l
        cp 17
        jr nc,yt_1
        ld hl,8
yt_1:
        or a
        sbc hl,de
        ret
yg_gtab: db G_GRIP, G_Q, G_SLIDE, G_QSLIDE

; YG_ROT: one heading step's turn, by shifts: C = cos 5.625 = 1 - 1/256 - 1/1024,
; S = sin 5.625 = 1/16 + 1/32 + 1/256 (0.0977). T1 = vf C, T2 = vf S, T3 = vs C, T4 = vs S
yg_rot:
        ld hl,(yg_vf)
        call mul_c
        ld (yg_t1),hl
        ld hl,(yg_vf)
        call mul_s
        ld (yg_t2),hl
        ld hl,(yg_vs)
        call mul_c
        ld (yg_t3),hl
        ld hl,(yg_vs)
        call mul_s
        ld (yg_t4),hl
        ret
mul_s:                          ; HL = HL/16 + HL/32 + HL/256 (shifts written out:
        sra h                   ; the calls cost more than the shifts)
        rr l
        sra h
        rr l
        sra h
        rr l
        sra h
        rr l                    ; /16
        ld d,h
        ld e,l
        sra h
        rr l                    ; /32
        add hl,de               ; /16 + /32
        ld a,d                  ; + /256 = (/16) / 16
        sra d
        rr e
        sra d
        rr e
        sra d
        rr e
        sra d
        rr e
        add hl,de
        ret
mul_c:                          ; HL = HL - HL/256 - HL/1024
        ld e,h                  ; DE = HL / 256 (signed)
        ld a,h
        rla
        sbc a,a
        ld d,a
        push hl
        ld h,d
        ld l,e
        sra h                   ; /1024
        rr l
        sra h
        rr l
        add hl,de               ; /256 + /1024
        ex de,hl
        pop hl
        or a
        sbc hl,de
        ret

; TRIG: A = heading 0..63 (0 = up, clockwise) -> C = |sin| / 128, B = 1 if negative
trig:
        and 63
        ld b,0
        bit 5,a                 ; 32..63: negative
        jr z,tg_1
        inc b
tg_1:
        ld c,a
        and 15
        bit 4,c                 ; 16..31 and 48..63: the quarter runs down
        jr z,tg_2
        neg
        add a,16
tg_2:
        add a,trig_t AND 255
        ld l,a
        ld a,0
        adc a,trig_t/256
        ld h,a
        ld c,(hl)
        ret
trig_t: db 0,13,25,37,49,60,71,81,91,99,106,113,118,122,126,127,128   ; 128 sin(n x 5.625)

; SMUL: HL (signed 8.8) x (C / 128), negated if B = 1 -> HL
smul:
        bit 7,h
        jr z,sm_1
        ld a,b                  ; |HL|, and the sign flips
        xor 1
        ld b,a
        xor a
        sub l
        ld l,a
        sbc a,a
        sub h
        ld h,a
sm_1:
        ld a,h                  ; |HL| over 1023: 1023 (3.99 px a frame)
        cp 4
        jr c,sm_2
        ld hl,1023
sm_2:
        srl h                   ; A = |HL| / 4
        rr l
        srl h
        rr l
        ld e,l
        ld d,c
        call qmul               ; HL = (|v| / 4) x C / 32 = |v| x C / 128
        ld a,b
        or a
        ret z
        xor a
        sub l
        ld l,a
        sbc a,a
        sub h
        ld h,a
        ret

; QMUL: E (0..255) x D (0..128) -> HL = E x D / 32, by quarter squares (B, C kept):
; sqtab holds n * n / 128, so the / 32 comes free (within 1/256 of a pixel)
qmul:
        push bc
        ld a,e
        sub d
        jr nc,qm_1
        neg
qm_1:
        ld l,a                  ; sq(|a - b|)
        ld h,0
        add hl,hl
        ld bc,sqtab
        add hl,bc
        ld a,(hl)
        inc hl
        ld h,(hl)
        ld l,a
        push hl
        ld a,e                  ; sq(a + b)
        add a,d
        ld l,a
        ld a,0
        adc a,a
        ld h,a
        add hl,hl
        add hl,bc
        ld a,(hl)
        inc hl
        ld h,(hl)
        ld l,a
        pop de
        or a
        sbc hl,de
        pop bc
        ret
