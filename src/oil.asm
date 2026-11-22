; =====================================================================
; OIL - OIL SPILLS (OIL=1; Grant, 22 Nov 2026: "have oil spills appear. If a car hits an oil spill they spin in the
; direction they were going in without being able to change direction for a brief period - a second or so. We need to
; have 3 or 4 spots where a spill may appear during a lap ... around the race track line ... The oil spill should stay
; on the race track line but should appear randomly and in different places"; "The oil spill will be about the size of
; a car"; of the three drawings, "B").
;   - EIGHT SPOTS on the straights, just off the line the cars drive (spill_spots). Each time YOU start a lap, ONE of
;     them gets a spill, picked at random (spill_pick); the others are dry. (First built 3 or 4 a lap, on the line at the
;     corner entries: every car spun on nearly every one - 12 spins a lap. Grant: "One oil spill a lap is fine, and an
;     oil spill somewhere on a straight just slightly off the racing path".)
;   - A spill is drawn as a car is (draw_car, from a record of its own: spill_rec) - under the cars.
;   - A car whose top left comes within OIL_R - 1 px of a spill's, both ways, SPINS for OIL_T pictures (about a second):
;     no steering, no push - it slides on the way it was going, a sixteenth slower each picture, its picture turning
;     round; then OIL_IMM pictures before a spill can catch it again. You hear the crash.
; =====================================================================
OIL_KIND equ 0xEE               ; (spill_rec's kind: draw_car draws the spill for it)
OIL_R   equ 10
OIL_T   equ 12                  ; pictures of spin (12.5 a second)
OIL_IMM equ 12                  ; then this many it cannot spin again
OIL_ROT equ 2                   ; heading steps (of 64) a TV frame while it spins: about 1.5 turns

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
        ld a,(ix+C_KIND)
        or a
        jr nz,slot_n
        ld a,SND_CRASH          ; (you: the crash)
        ld (snd_bump),a
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
        ld a,(cars+C_LAPS)      ; (not S8 on your first lap: it is just ahead of the grid)
        cp 2
        jr nc,slop_3
        bit 7,d
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
slop_spin:
        ld a,(ph_steps)
        ld b,a
        rept OIL_ROT
        add a,b
        endm
        sub b
        add a,(ix+C_ANG)        ; its picture turns round
        and 63
        ld (ix+C_ANG),a
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

spill_spots:                      ; top left of each spill (its middle - 8). ON THE STRAIGHTS, 13 px to one side of the line the
        dw 519-8,230-8, 493-8,300-8     ; computer cars drive (Grant, 22 Nov 2026: "an oil spill somewhere on a straight just
        dw 68-8,200-8, 94-8,290-8       ; slightly off the racing path"; the line measured from four races: the right straight
        dw 180-8,110-8, 420-8,82-8      ; at x 506, the left at 81, the top at y 95-97, the bottom at 411-415 - each road 72 px
        dw 150-8,424-8, 420-8,402-8     ; across). Right, right, left, left, top, top, bottom (before the grid), bottom (after the
                                        ; line: never on your first lap). A car on the line passes it; one a little off hits it.
                                        ; (The first spots, 8 on the line at the corner entries: docs/design/oil_spill_spots.png.)
        if OPT_MAP40 * OPT_MAPHUD = 0   ; (the breakfast fast tapes: in the D0 strip - vars_d0.asm)
spill_on:   db 0                  ; which of the 8 have a spill (bit 0 = S1)
spill_lap:  db 0                  ; your lap when they were picked
spill_spin: defs NCARS            ; each car (by kind): pictures of spin (and then immunity) left
spill_rec:  defs C_SIZE           ; the record draw_car draws a spill from
        endif
        include "oil_gfx.asm"
