; =====================================================================
; RACE MODE (RACEMODE=1; Grant, 18 Nov 2026: "Now I need a game option - combat or race. Race produces a bunch of the same
; looking cars, but different colours and numbers ... the idea is to make it competitive so you don't run away with it").
; The title's M chooses (rmode, title.asm: 1 RACE, 0 COMBAT; RACE to start with, kept from race to race). COMBAT is the
; armour tape's game exactly. RACE:
;   - every car is the racer (MAX's car) in its own colour, with its number on its roof (num_draw): YOU 7, CYAN 3,
;     YELLOW 4, MAGENTA 5, WHITE 9
;   - every computer car on MAX's card (race_low.asm) and driven by the RACE drivers (ai_tune.asm, AI_R_...)
;   - no armour lost, no shells, no wheels, no drivers steering at other cars: a bump is just a bump
;   - the race order shows, right of each car, its gap to the car ahead (rg_draw) where the health blocks were
;   - ELASTIC=1 (the second race tape): el_tick, below
; =====================================================================
NUM_DX  equ 5                   ; the number's box: 5 x 7 pixels, this far into the car's 16 x 16 (across, down)
NUM_DY  equ 5

; NUM_DRAW (IX = a car, just drawn by rt_car): RACE - its number on its roof. A box of the car's own ink, 5 x 7 pixels,
; NUM_DX, NUM_DY into the car's 16 x 16 and always upright, with the digit (3 x 5) cut out of it in black - read the same at
; every heading. Only when the whole car is in the window (at the edge it is left off: no sums for cutting it).
; (The box reaches a pixel or two past the car's outline at some headings; the car's colour squares are decided from the car
; alone, so in about 1 picture in 100 a pixel of it can fall in a square of the track's colours - for that one picture.)
num_draw:
        ld a,(rmode)
        or a
        ret z
        ld l,(ix+C_X)
        ld h,(ix+C_X+1)
        ld de,(camx)
        or a
        sbc hl,de
        ld a,h
        or a
        ret nz
        ld a,l
        cp WIN_W*8-15           ; the whole car in the window, across
        ret nc
        add a,16+NUM_DX-1
        ld c,a                  ; C = the box's buffer x - 1 (its first byte; draw_car's "u")
        ld l,(ix+C_Y)
        ld h,(ix+C_Y+1)
        ld de,(camy)
        or a
        sbc hl,de
        ld a,h
        or a
        ret nz
        ld a,l
        cp WIN_H-15             ; ... and down
        ret nc
        add a,BUF_TOP+NUM_DY
        ld b,a
        call buf_addr           ; HL = the box's first line, first byte
        ld a,c
        cpl                     ; the shift table: (15 - u) AND 7, as draw_car
        and 7
        add a,a
        add a,TAB_HI
        ld b,a
        ld a,(ix+C_KIND)
        ld e,a
        add a,a
        add a,e
        add a,a                 ; kind * 6
        add a,nd_font AND 255
        ld e,a
        adc a,nd_font/256
        sub e
        ld d,a                  ; DE = its digit (a clear line first)
        ld a,7
nd_row:
        ex af,af'
        ld a,(de)               ; the digit's holes on this line
        inc de
        push de
        ld e,a
        cpl
        and 0xF8
        ld c,a                  ; the box's ink
        ld a,(bc)
        or (hl)
        ld d,a
        ld c,e
        ld a,(bc)
        cpl
        and d
        ld (hl),a               ; column k: (it OR ink) AND NOT holes
        inc b
        inc l
        ld a,(bc)
        cpl
        ld d,a
        ld a,e
        cpl
        and 0xF8
        ld c,a
        ld a,(bc)
        or (hl)
        and d
        ld (hl),a               ; column k + 1
        dec b
        dec l
        pop de
        inc h                   ; the next line down (screen layout)
        ld a,h
        and 7
        jr nz,nd_nx
        ld a,l
        add a,32
        ld l,a
        jr c,nd_nx
        ld a,h
        sub 8
        ld h,a
nd_nx:  ex af,af'
        dec a
        jr nz,nd_row
        ret
; the five numbers, 3 x 5, in the middle of the box's five pixels (bits 6-4): a clear line, the digit's five; the next
; one's clear line is the last line of the box
nd_font:
        db 0, 0x70,0x10,0x10,0x20,0x20         ; 7  YOU (red)
        db 0, 0x70,0x10,0x30,0x10,0x70         ; 3  CYAN
        db 0, 0x50,0x50,0x70,0x10,0x10         ; 4  YELLOW
        db 0, 0x70,0x40,0x70,0x10,0x70         ; 5  MAGENTA
        db 0, 0x70,0x50,0x70,0x10,0x70         ; 9  WHITE
        db 0

        if OPT_ELASTIC
; EL_TICK (ELASTIC=1; every picture, after the places are worked out): RACE - each computer car's two pushes (its row in
; race_low.asm) set afresh from the cars' progress (prog: laps x waypoints + waypoints passed): one 64th more for every
; 2^EL_SH waypoints it is behind the leader, up to EL_MAX; EL_EASE less if it is ahead of you. Once any car has finished,
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
        cp (hl)                 ; carry: this car is ahead of you
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
