; THE DRIVER CARDS' CODE (CARDS=1; Grant, 17 Nov 2026) - what a car's card does to a computer car (card_push), and the
; drivers who go looking for the other cars (card_near). The numbers: src/cards.asm (from tools/driver_cards.txt, by
; tools/make_cards.py) and the CARDS part of src/ai_tune.asm. Your own car's card goes in through grip.asm's numbers.
; ---------------------------------------------------------------------
; CARD_PUSH (CARDS; IX = a computer car; DE, BC = the plain push for the way it faces): THE CAR'S CARD (Grant, 17 Nov
; 2026: "their acceleration, speed and grip/turning as ratings out of 10 ... so the game can have these apply in the
; game"). Each computer car has a row in cd_tab (src/cards.asm, made by tools/make_cards.py from
; tools/driver_cards.txt - never typed in here):
;   GRIP    the speed its tyres start to slide at when it steers (skid's own rule, below: it was 1.0 px a frame for all)
;   BRAKE   the speed it must come down to before it will turn: while it is steering (or its driver is easing off for
;           a corner - C_EASE: the target well off its nose) and it is going faster than this, it gets no push and half
;           the road's friction - it loses a sixteenth of its speed a TV frame, and WITH NO PUSH IT GOES STRAIGHT ON the
;           way it was going, whatever way it points: too fast into a corner and it runs wide. So a car with little grip
;           must turn in early and crawl round; one with a lot never lifts. A tidy driver's BRAKE is the GRIP speed; a
;           clumsy one's is higher, and the car then slides as well (the driver's margin: AI_x_SLIP in ai_tune.asm)
;   ACCEL   the push up to four fifths of its top speed, and SPEED the push above that (which sets the top speed:
;           7 pushes), each as so many 64ths more or less than the plain push
; Out: DE, BC the car's push; carry set if it is braking (skid is then not called). About 1,400 T a car a picture with its multiplies (less for a car whose push is the plain one, or one that is braking).
; ---------------------------------------------------------------------
card_push:
        call sk_speed           ; HL = its speed, roughly (BC, DE kept)
        srl h
        rr l
        srl h
        rr l                    ; L = speed / 4 (64 = 1 px a frame)
        ld a,h
        or a
        jr z,cdp_1
        ld l,255
cdp_1:
        ld a,l
        ld (cd_v),a
        push de
        ld a,(ix+C_KIND)        ; its row: kind * 8
        add a,a
        add a,a
        add a,a
        ld e,a
        ld d,0
cdp_tab: ld hl,cd_tab-8         ; (RACE mode: race.asm points it at race_low.asm's rows)
        add hl,de
        ld e,(hl)               ; GRIP: where it starts to slide
        inc hl
        ld d,(hl)
        inc hl
        ld (skc_v+1),de
        pop de
        ld a,(cd_v)             ; over its braking speed, and steering, or easing off for a corner, or braking already?
        cp (hl)                 ; brake - and once it has begun it brakes all the way down to that speed
        push hl
        inc hl
        inc hl
        inc hl
        inc hl                  ; (the row's seventh byte: 1 while it is braking)
        jr c,cdp_free
        ld a,(ix+C_CTRL)
        and CT_L+CT_R
        or (ix+C_EASE)
        or (hl)
        jr z,cdp_free
        ld (hl),1
        pop hl
        ld hl,fshift            ; (half the road's friction: a sixteenth of its speed a TV frame, about a fifth a picture -
        inc (hl)                ; the whole of it took nearly half in one picture, far below the speed asked for)
        ld de,0
        ld b,d
        ld c,d
        scf
        ret
cdp_free:
        ld (hl),0
        pop hl
        inc hl
        ld a,(cd_v)             ; under four fifths of its top speed: the ACCEL push; over: the SPEED push
        cp (hl)
        inc hl
        jr c,cdp_3
        inc hl
cdp_3:
        ld a,(hl)
        or a
        ret z                   ; (0: the plain push as it is - and no carry)
        ld (cd_k),a
        push bc
        ex de,hl
        call cdp_sc
        ex (sp),hl
        call cdp_sc
        ld b,h
        ld c,l
        pop de
        or a
        ret
cdp_sc:                         ; HL = a push (-64 to 64) -> HL = that push x (64 + K) / 64, K the card's number
        push hl
        ld b,l
        ld a,(cd_k)
        ld c,a
        call mul8s
        ld de,32
        add hl,de
        add hl,hl
        add hl,hl
        ld a,h
        ld l,a
        add a,a
        sbc a,a
        ld h,a
        pop de
        add hl,de
        ret
; ---------------------------------------------------------------------
; CARD_NEAR (CARDS; IX = a computer car that has just reached a waypoint and picked its line to the next): THE DRIVERS
; WHO GO LOOKING FOR YOU (Grant's cards: BRUNO "likes to get in the way", SPIKE "almost seems to want to hit other
; cars"). Such a driver has two numbers in cd_near (ai_tune.asm: AI_x_NEAR, AI_x_PULL): if another car is within NEAR
; pixels of it (across plus down), its line to the next waypoint is moved towards that car, by up to PULL pixels each
; way - it drifts over to the side of the road the other car is on. NEAR 0: the driver minds its own business.
; A driver whose PULL has 128 added LUNGES as well: one time in four that it finds a car that near, it steers straight
; at it for AI_LUNGE of its turns (two TV frames each), throttle down.
; Only when it reaches a waypoint (about 3 times a second), so it costs next to nothing: 300 to 1,000 T each time.
; ---------------------------------------------------------------------
card_near:
        if OPT_RACEONLY         ; (RACEONLY, 22 Nov 2026: no driver goes looking for the other cars - it returns, as RACE made it)
        ret
        else
        ld a,(ix+C_KIND)
        add a,a
        ld e,a
        ld d,0
        ld hl,cd_near-2
        add hl,de
        ld a,(hl)
        or a
        ret z
        ld (cdn_r+1),a
        inc hl
        ld a,(hl)
        ld (cdn_f+1),a
        and 0x7F
        ld (cdn_p+1),a
        ld iy,cars
        ld b,NCARS
cdn_car:
        push bc
        ld l,(iy+C_X)           ; how far across and down the other car is
        ld h,(iy+C_X+1)
        ld e,(ix+C_X)
        ld d,(ix+C_X+1)
        or a
        sbc hl,de
        call cdn_byte
        ld c,a                  ; C = across (-127 to 127)
        ld l,(iy+C_Y)
        ld h,(iy+C_Y+1)
        ld e,(ix+C_Y)
        ld d,(ix+C_Y+1)
        or a
        sbc hl,de
        call cdn_byte
        ld b,a                  ; B = down
        or c
        jr z,cdn_next           ; (itself)
        ld a,b
        call cdn_abs
        ld e,a
        ld a,c
        call cdn_abs
        add a,e
cdn_r:  cp 0                    ; within NEAR?
        jr nc,cdn_next
        ld a,c
        call cdn_clamp
        ld (ix+C_OFFX),a
        ld a,b
        call cdn_clamp
        ld (ix+C_OFFY),a
        pop bc
cdn_f:  ld a,0                  ; a driver who LUNGES (PULL + 128)? one time in four ...
        rla
        ret nc
        call rnd
        and 3
        ret nz
        ld a,(ix+C_ANG)         ; ... it steers AT the other car for a moment: which side is it on? the way the car
        call heading_push       ; points (E across, C down) against the way to the other car (the line's pull, just set):
        ld a,c                  ; hx * dy - hy * dx, more than 0 if it is to the right
        ld (cdn_hy+1),a
        ld b,e
        ld c,(ix+C_OFFY)
        call mul8s
        push hl
cdn_hy: ld b,0
        ld c,(ix+C_OFFX)
        call mul8s
        pop de
        ex de,hl
        or a
        sbc hl,de
        ld a,3+CT_R             ; (a "mistake" of kind 4 or 5: steer left, or right, with the throttle down - ai_drive)
        bit 7,h
        jr z,cdn_l1
        ld a,3+CT_L
cdn_l1:
        ld (ix+C_MKIND),a
        ld (ix+C_MIST),AI_LUNGE
        ret
cdn_next:
        ld de,C_SIZE
        add iy,de
        pop bc
        dec b
        jp nz,cdn_car
        ret
cdn_byte:                       ; HL -> A, kept to -127..127
        ld a,h
        or a
        jr z,cdn_b1
        inc a
        ld a,0x81
        ret nz                  ; far below nothing
        bit 7,l
        ret z
        ld a,l
        ret
cdn_b1:
        bit 7,l
        ld a,l
        ret z
        ld a,0x7F
        ret
cdn_abs:
        or a
        ret p
        neg
        ret
cdn_clamp:                      ; A kept to -PULL..PULL
        or a
        jp m,cdn_c1
cdn_p:  cp 0
        ret c
        ld a,(cdn_p+1)
        ret
cdn_c1:
        neg
        call cdn_p
        neg
        ret
        endif
cd_v:   db 0                    ; the car's speed / 4
cd_k:   db 0                    ; its push's number
cd_near:                        ; NEAR, PULL for CYAN, GREEN, PINK, WHITE (ai_tune.asm)
        db AI_C_NEAR,AI_C_PULL, AI_G_NEAR,AI_G_PULL, AI_P_NEAR,AI_P_PULL, AI_W_NEAR,AI_W_PULL
        if OPT_SIMPLE           ; SIMPLE (C1): YOUR card row - card_push reads row kind 0 at cd_tab - 8: MAX's racer as the computer
you_card:                       ; cars' rows are (where it slides; no braking; ACCEL to SPEED at 4/5 top; its two pushes) - su_apply
        dw YOU_SL               ; raises them for the set-up you pick. Tuned 22 Nov 2026 so that the careful autopilot does as it
        db 255, CD_R_VSW, YOU_KA AND 255, YOU_KS AND 255, 0, 0  ; did on the grip model (laps 24.4 s, last, ~8 s behind):
        endif                   ; it slides sooner than the computer cars' MAX card (tyres poor to start, as yours were),
        include "cards.asm"     ; the cards' numbers (tools/make_cards.py)
        if OPT_SIMPLE           ; (These EQUs AFTER cards.asm: pasmo takes an EQU's value where it stands - before it, CD_R_SLIDE
YOU_SL  equ CD_R_SLIDE*45/64    ; was 0: slide 0, sliding always. 22 Nov 2026.) Its pushes are the MAX card's as the computer cars
YOU_KA  equ CD_R_KA             ; have it - 8/64 less at first made you the slowest car on the straights (Grant, 23 Nov 2026:
YOU_KS  equ CD_R_KS             ; "my car is definitely the slowest of the lot"); 4 less, tried next, put him last ("Right now
                                ; I'm coming last") - so as the computer cars have it, the balance he liked
        endif
