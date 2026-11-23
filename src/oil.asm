; =====================================================================
; OIL - OIL SPILLS (OIL=1; Grant, 22 Nov 2026: "have oil spills appear. If a car hits an oil spill they spin in the
; direction they were going in without being able to change direction for a brief period - a second or so. We need to
; have 3 or 4 spots where a spill may appear during a lap ... around the race track line ... The oil spill should stay
; on the race track line but should appear randomly and in different places"; "The oil spill will be about the size of
; a car"; of the three drawings, "B").
;   - EIGHT SPOTS on the straights, half on the line the cars drive (spill_spots). Each time YOU start a lap, ONE of
;     them gets a spill, picked at random (spill_pick); the others are dry. (First built 3 or 4 a lap, on the line at the
;     corner entries: every car spun on nearly every one - 12 spins a lap. Grant: "One oil spill a lap is fine, and an
;     oil spill somewhere on a straight just slightly off the racing path".)
;   - A spill is drawn as a car is (draw_car, from a record of its own: spill_rec) - under the cars.
;   - A car whose top left comes within OIL_R - 1 px of a spill's, both ways, SPINS for OIL_T pictures (about a second):
;     no steering, no push - it slides on, a sixteenth slower each picture, its picture turning round ONE WHOLE TURN and
;     OIL_DEF more or less, so it comes out almost facing the way it was (Grant, 23 Nov 2026: "you lose control and deflect
;     ever so slightly off your path, so you end up almost facing the way you were" - it was 1.5 turns: it came out facing
;     back), its path turned an eighth of its speed the same way (about 7 degrees); then OIL_IMM pictures before a spill
;     can catch it again. You hear the crash.
; =====================================================================
OIL_KIND equ 0xEE               ; (spill_rec's kind: draw_car draws the spill for it)
OIL_R   equ 8                   ; (10 until 23 Nov 2026, the spill 15 x 13; now 12 x 12 - Grant: "make the oil spill a little smaller")
OIL_T   equ 12                  ; pictures of spin (12.5 a second)
OIL_IMM equ 12                  ; then this many it cannot spin again
OIL_DEF equ 2                   ; heading steps (of 64) it comes out off the way it was: 11 degrees, either way at random
OIL_STEER equ 4                 ; YOU steering in a spin: up to this many heading steps (22 degrees) either way

spill_new:                        ; a new race: no spills yet (the first come with the green light), nobody spinning
        if OPT_LJ * OPT_MAPHUD  ; (with LINEJ: the judge's 16 bytes before these cleared too - lj_new's work: vars_d0.asm)
        ld hl,line_at
        ld b,spill_spin+NCARS-line_at
slon_1:   ld (hl),0
        inc hl
        djnz slon_1
        ld a,0xFF
        ld (spill_lap),a
        else
        ld hl,spill_on
        ld (hl),0
        inc hl
        ld (hl),0xFF            ; (spill_lap: picks at the first picture of the race)
        ld b,NCARS
slon_1:   inc hl
        ld (hl),0
        djnz slon_1
        endif
        ld a,OIL_KIND
        ld (spill_rec+C_KIND),a
        ret

spill_tick:                       ; each picture (main, with the cars moved): new spills each lap of yours; who is on one
        ld a,(race_on)
        or a
        ret z
        ld a,(cars+C_LAPS)
        ld hl,spill_lap
        cp (hl)
        jr z,slot_0
        ld (hl),a
        or a                    ; (none before you cross the line the first time)
        call nz,spill_pick
slot_0:   ld ix,cars
        ld b,NCARS
slot_1:   push bc
        call spill_row
        ld a,(hl)
        or a
        jr z,slot_try
        dec (hl)
        jr slot_n
slot_try: push hl
        call spill_hit
        pop hl
        jr nc,slot_n
        ld (hl),OIL_T+OIL_IMM
        call spill_go           ; which way it comes out; its path turned a little
        ld a,(ix+C_KIND)
        or a
        jr nz,slot_n
        ld a,SND_CRASH          ; (you: the crash)
        ld (snd_bump),a
        if OPT_SND3             ; (SND3: the whoosh down, 14 frames)
        ld hl,5*256+14
        ld (snd_fxt),hl
        endif
slot_n:   ld de,C_SIZE
        add ix,de
        pop bc
        djnz slot_1
        ret

spill_row:                        ; IX = a car: HL = its spin count
        ld a,(ix+C_KIND)
        add a,spill_spin AND 255
        ld l,a
        adc a,spill_spin/256
        sub l
        ld h,a
        ret

spill_pick:                       ; ONE of the 8 spots, at random (Grant, 22 Nov 2026: "One oil spill a lap is fine"; 3 or 4 before)
        ld b,1
        ld c,0
slop_1:   call rnd
        and 7
        inc a
        ld e,a
        ld d,0x80
slop_2:   rlc d
        dec e
        jr nz,slop_2              ; D = bit (r) of 8
        ld a,(cars+C_LAPS)      ; (not S7 or S8 on your first lap: they are just ahead of the grid)
        cp 2
        jr nc,slop_3
        ld a,d
        and 0xC0
        jr nz,slop_1
slop_3: ld a,c
        and d
        jr nz,slop_1              ; (that one already)
        ld a,c
        or d
        ld c,a
        djnz slop_1
        ld (spill_on),a
        ret

spill_go:                         ; IX = a car that has just hit a spill: its turn, a whole one and OIL_DEF more or less, at
        push hl                   ; random; its path turned an eighth of its speed the same way (HL kept)
        ld a,(ix+C_KIND)          ; (you: not steered out of it yet)
        or a
        jr nz,sgo_0
        ld (spill_kadj),a
sgo_0:
        ld e,(ix+C_VY)
        ld d,(ix+C_VY+1)
        call sgo_8
        ld hl,0
        or a
        sbc hl,de
        ex de,hl                  ; DE = -vy / 8 (clockwise: x's share)
        ld c,(ix+C_VX)
        ld b,(ix+C_VX+1)
        push de
        ld d,b
        ld e,c
        call sgo_8
        ld b,d
        ld c,e                    ; BC = vx / 8 (clockwise: y's share)
        pop de
        call rnd
        rra
        ld a,64+OIL_DEF
        jr c,sgo_cw
        ld hl,0                   ; the other way round
        or a
        sbc hl,de
        ex de,hl
        ld hl,0
        or a
        sbc hl,bc
        ld b,h
        ld c,l
        ld a,64-OIL_DEF
sgo_cw: push af
        ld l,(ix+C_VX)
        ld h,(ix+C_VX+1)
        add hl,de
        ld (ix+C_VX),l
        ld (ix+C_VX+1),h
        ld l,(ix+C_VY)
        ld h,(ix+C_VY+1)
        add hl,bc
        ld (ix+C_VY),l
        ld (ix+C_VY+1),h
        call spill_lrow
        pop af
        ld (hl),a
        pop hl
        ret
sgo_8:  sra d                     ; DE / 8, signed
        rr e
        sra d
        rr e
        sra d
        rr e
        ret
spill_lrow:                       ; IX = a car: HL = what is left of its turn
        ld a,(ix+C_KIND)
        add a,spill_left AND 255
        ld l,a
        adc a,spill_left/256
        sub l
        ld h,a
        ret
spill_left: defs NCARS            ; each car's turn left to do (heading steps of 64)
spill_key: db 0                   ; your steering while you spin (racer.asm tick)
spill_kadj: db 0                  ; how far you have steered this spin (steps, signed)

spill_hit:                        ; IX = a car: CY if it is on a spill
        ld hl,spill_spots
        ld a,(spill_on)
sloh_1:   or a
        ret z                   ; (NC)
        srl a
        push af
        jr nc,sloh_n
        push hl
        ld e,(hl)
        inc hl
        ld d,(hl)
        inc hl
        push hl
        ld l,(ix+C_X)
        ld h,(ix+C_X+1)
        call sloh_near
        pop hl
        jr nc,sloh_x
        ld e,(hl)
        inc hl
        ld d,(hl)
        ld l,(ix+C_Y)
        ld h,(ix+C_Y+1)
        call sloh_near
sloh_x:   pop hl
        jr nc,sloh_n
        pop af
        scf
        ret
sloh_n:   ld de,4
        add hl,de
        pop af
        jr sloh_1
sloh_near:                        ; HL - DE within OIL_R - 1 either way: CY
        or a
        sbc hl,de
        ld de,OIL_R-1
        add hl,de
        ld de,2*OIL_R-1
        or a
        sbc hl,de
        ret

spill_phys:                       ; (physics, first; IX = a car): NZ if it is spinning - moved here, nothing else done
        call spill_row
        ld a,(hl)
        cp OIL_IMM+1
        jr nc,slop_spin
        xor a
        ret
slop_spin:                      ; (A = its count: OIL_IMM + the pictures of spin left, this one too)
        sub OIL_IMM
        ld c,a
        call spill_lrow         ; its picture turns round: what is left of its turn, shared out over the pictures left
        ld a,(ix+C_KIND)        ; YOU can steer out of it (Grant, 23 Nov 2026: "with some clever driving, after the skid you
        or a                    ; can potentially recover"): right turns it a step further, left a step less, a step a picture,
        jr nz,slt_0             ; OIL_STEER steps at most either way (spill_kadj) - enough to come out straight, or further off
        ld a,(spill_key)        ; (your steering in the spin: tick keeps it here)
        and CT_R
        jr z,slt_a
        ld a,(spill_kadj)
        cp OIL_STEER
        jr z,slt_0
        inc a
        ld (spill_kadj),a
        inc (hl)
        jr slt_0
slt_a:  ld a,(spill_key)
        and CT_L
        jr z,slt_0
        ld a,(hl)               ; (a step a picture still to turn, at least)
        cp c
        jr z,slt_0
        jr c,slt_0
        ld a,(spill_kadj)
        cp 0-OIL_STEER AND 255
        jr z,slt_0
        dec a
        ld (spill_kadj),a
        dec (hl)
slt_0:  ld a,(hl)
        ld b,0
slt_1:  cp c
        jr c,slt_2
        sub c
        inc b
        jr slt_1
slt_2:  ld a,(hl)
        sub b
        ld (hl),a
        ld a,b
        add a,(ix+C_ANG)
        and 63
        ld (ix+C_ANG),a
        ld a,(ph_steps)
        ld b,a
        push ix                 ; a sixteenth slower
        pop hl
        ld de,C_VX
        add hl,de
        call slops_16
        call slops_16
slops_m:  ld e,(ix+C_VX)          ; on the way it was going, ph_steps TV frames
        ld d,(ix+C_VX+1)
        ld a,d
        rla
        sbc a,a
        ld c,a
        ld a,(ix+C_XF)
        add a,e
        ld (ix+C_XF),a
        ld a,(ix+C_X)
        adc a,d
        ld (ix+C_X),a
        ld a,(ix+C_X+1)
        adc a,c
        ld (ix+C_X+1),a
        ld e,(ix+C_VY)
        ld d,(ix+C_VY+1)
        ld a,d
        rla
        sbc a,a
        ld c,a
        ld a,(ix+C_YF)
        add a,e
        ld (ix+C_YF),a
        ld a,(ix+C_Y)
        adc a,d
        ld (ix+C_Y),a
        ld a,(ix+C_Y+1)
        adc a,c
        ld (ix+C_Y+1),a
        djnz slops_m
        or 1
        ret
slops_16:                         ; the speed at HL less a sixteenth of it (signed); HL on 2
        ld e,(hl)
        inc hl
        ld d,(hl)
        push hl
        ld h,d
        ld l,e
        sra h
        rr l
        sra h
        rr l
        sra h
        rr l
        sra h
        rr l
        ex de,hl
        or a
        sbc hl,de
        ex de,hl
        pop hl
        ld (hl),d
        dec hl
        ld (hl),e
        inc hl
        inc hl
        ret

spill_draw:                       ; (draw_all, before the cars) each spill out, as a car is drawn
        ld hl,spill_spots
        ld a,(spill_on)
slod_1:   or a
        ret z
        srl a
        push af
        push hl
        jr nc,slod_n
        ld ix,spill_rec
        ld e,(hl)
        inc hl
        ld d,(hl)
        inc hl
        ld (ix+C_X),e
        ld (ix+C_X+1),d
        ld e,(hl)
        inc hl
        ld d,(hl)
        ld (ix+C_Y),e
        ld (ix+C_Y+1),d
        call draw_car
slod_n:   pop hl
        ld de,4
        add hl,de
        pop af
        jr slod_1

spill_spots:                      ; top left of each spill (its middle - 8). ON THE STRAIGHTS, HALF ON THE LINE: its middle 9 px
        dw 515-8,230-8, 497-8,300-8     ; to one side of the line the computer cars drive (Grant, 23 Nov 2026: "slightly off the
        dw 74-8,200-8, 89-8,290-8       ; race line - so partly on partly off"; it was 13 px off - 22 Nov: "an oil spill somewhere
        dw 180-8,106-8, 420-8,86-8      ; on a straight just slightly off the racing path"). The line where each spot is, the
        dw 330-8,422-8, 420-8,405-8     ; middle of the cars measured over two races (scratchpad linespots.py): right 506, 506;
                                        ; left 83, 80; top 97, 95; bottom 413, 414. The spill (12 px) covers 3 to 15 px from the
                                        ; line, a car on the line 8 either side: they overlap, but a car right on the line passes
                                        ; it (middles 9 apart, OIL_R - 1 is 7); one 2 px or more to that side spins. (7 px off,
                                        ; tried first: 4 cars in 5 spun on every spill.)
                                        ; Right, right, left, left, top, top, bottom, bottom - both bottom ones after the line
                                        ; (never on your first lap). S7 was at x 150, before the grid - on NOS canister A (156,
                                        ; 416): Grant, 23 Nov 2026, "make sure it does not sit on top of a NOS". The canisters
                                        ; B (276, 146) and C (76, 146) are 50 px or more from every spot.
                                        ; (The first spots, 8 on the line at the corner entries: docs/design/oil_spill_spots.png.)
        if OPT_MAP40 * OPT_MAPHUD = 0   ; (the breakfast fast tapes: in the D0 strip - vars_d0.asm)
spill_on:   db 0                  ; which of the 8 have a spill (bit 0 = S1)
spill_lap:  db 0                  ; your lap when they were picked
spill_spin: defs NCARS            ; each car (by kind): pictures of spin (and then immunity) left
spill_rec:  defs C_SIZE           ; the record draw_car draws a spill from
        endif
        if OPT_UPPER = 0        ; (UPPER: above the copy routine)
        include "oil_gfx.asm"
        endif
