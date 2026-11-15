; =====================================================================
; BRIDGE.ASM - the crossover (track 5, A FRIDGE TOO FAR). Assembled only when OPT_BRIDGE is 1
; (TRACK=5 bash build.sh); tracks 1-3 have none of it.
;
; The upper road runs down the screen at x BR_X0..BR_X1, from the foot of the ramp up (BR_Y0) over the
; level deck (BR_Y1..BR_Y2) to the foot of the ramp down (BR_Y3). The lower road goes under the deck
; from right to left at y BR_M0..BR_M1, and is covered from x BR_H0 to BR_H1. (world.asm has the numbers.)
;
;   LEVELS   each car has a level (LVL + its number): 0 on the table, 1 on the bridge. A car on the
;            table that comes onto the first 16 px of either ramp goes up to 1; a car on the bridge
;            that leaves by either ramp's foot comes back to 0. Cars only bump others on their own level.
;   WALLS    level 1: x is kept between the kerb walls. Level 0: under the deck y is kept between the
;            tunnel's walls, and beside the ramps the car is put back outside the bridge.
;   RAMPS    level 1 on a ramp: the slope pulls the car downhill, RAMP_G a TV frame - slower up, faster down.
;   DRAWING  a car on level 0 under the cover is not drawn; half under, it is drawn and the part under
;            the cover put back as it was (draw_car_b).
;   O'S      this track keeps no O map (its memory went to the bridge): o_at finds an O in the row lists.
; =====================================================================
LVL     equ 0x5E00              ; the cars' levels, 5 bytes; and
RMP     equ LVL+8               ; and whether each is on a ramp: 1 the ramp up, 0xFF the ramp down, 0 neither; and
BR_SAVE equ 0x5E10              ; 72 bytes: the buffer under a half-hidden car (the bottom of the stack's
                                ; page: the stack, from 0x5F00 down, has been seen 56 bytes deep)
RAMP_SHIFT equ 3                ; THE RAMPS: on the ramp up a car's push and top speed are less by 1 / 2^RAMP_SHIFT (3: an eighth,
                                ; 12.5%), on the ramp down more by as much - you and the computer cars alike (ramp_adj)

lv_reset:                       ; a new race: everyone on the table
        ld hl,LVL
        ld b,13
lv_r0:
        ld (hl),0
        inc hl
        djnz lv_r0
        ret

lv_all:                         ; once a picture, after the cars have moved, before they bump
        ld ix,cars
        ld b,NCARS
lv_1:
        push bc
        call lv_car
        ld de,C_SIZE
        add ix,de
        pop bc
        djnz lv_1
        ret

lv_q:                           ; A = (HL + 8) / 4: a car's middle, in 4 px steps
        ld bc,8
        add hl,bc
        srl h
        rr l
        srl h
        rr l
        ld a,l
        ret
lv_xy:                          ; IX = car: D, E = its middle's x, y in 4 px steps; HL -> its level, A = the level (Z: on the table)
        ld l,(ix+C_X)
        ld h,(ix+C_X+1)
        call lv_q
        ld d,a
        ld l,(ix+C_Y)
        ld h,(ix+C_Y+1)
        call lv_q
        ld e,a
        ld a,(ix+C_KIND)
        add a,LVL AND 255
        ld l,a
        ld h,LVL/256
        ld a,(hl)
        or a
        ret

lv_car:
        call lv_xy
        jr z,lv_low
        ld a,e                  ; ---- on the bridge ----
        sub BR_Y0/4
        cp (BR_Y3-BR_Y0)/4
        jr c,lv_up
        ld (hl),0               ; off the foot of a ramp: on the table again
        ld c,0
        jr lv_r
lv_up:
        ld c,1                  ; on the ramp up,
        cp (BR_Y1-BR_Y0)/4
        jr c,lv_r
        dec c                   ; the level deck,
        cp (BR_Y2-BR_Y0)/4
        jr c,lv_r
        dec c                   ; or the ramp down
lv_r:
        ld a,l
        add a,RMP-LVL
        ld l,a
        ld (hl),c
lv_wall:                        ; the kerb walls: x from BR_X0 - 2 to BR_X1 - 14 (the car is 16 wide)
        ld a,(ix+C_X+1)
        or a
        jr nz,lv_wr
        ld a,(ix+C_X)
        cp BR_X0-2
        jr c,lv_wl
        cp BR_X1-13
        ret c
lv_wr:
        ld a,BR_X1-14
lv_kl:
        ld hl,0x10000-KICK
        jr lv_wset
lv_wl:
        ld a,BR_X0-2
lv_kr:
        ld hl,KICK
lv_wset:                        ; put at x = A, kicked off the wall at HL
        ld (ix+C_X),a
        ld (ix+C_X+1),0
        ld (ix+C_VX),l
        ld (ix+C_VX+1),h
        jp ocb_snd              ; (you: the bonk, the damage, the border - as off an O)

lv_low:                         ; ---- on the table ----
        ld a,e
        sub BR_Y0/4
        cp (BR_Y3-BR_Y0)/4
        ret nc                  ; above or below the whole bridge
        ld b,a                  ; B = (y - BR_Y0) / 4
        ld a,d
        sub (BR_X0-36)/4
        cp (BR_X1-BR_X0+72)/4
        ret nc                  ; well to one side of it
        ld c,a                  ; C = (x - (BR_X0 - 36)) / 4
        sub 9
        cp (BR_X1-BR_X0)/4
        jr nc,lv_l2
        ld a,b                  ; on the upper road's width: the first 16 px of either ramp is the way on
        cp 4
        jr c,lv_on
        cp (BR_Y3-BR_Y0)/4-4
        jr c,lv_l2
lv_on:
        ld (hl),1
        ret
lv_l2:
        ld a,b                  ; the tunnel (and its wings, 36 px out each side): y from BR_M0 - 4 to BR_M1 - 12
        sub (BR_M0-4-BR_Y0)/4
        cp (BR_M1-BR_M0)/4+2
        jr nc,lv_l3
        ld l,(ix+C_Y)
        ld h,(ix+C_Y+1)
        ld de,BR_M0-4
        or a
        sbc hl,de
        jr c,lv_tlo
        ld a,l
        cp BR_M1-BR_M0-7
        ret c
        ld de,BR_M1-12
        ld hl,0x10000-KICK
        jr lv_tset
lv_tlo:
        ld hl,KICK
lv_tset:
        ld (ix+C_Y),e
        ld (ix+C_Y+1),d
        ld (ix+C_VY),l
        ld (ix+C_VY+1),h
        jp ocb_snd
lv_l3:
        ld a,c                  ; beside a ramp or the deck's ends: solid from x BR_X0 - 8 to BR_X1 + 8
        sub 7
        cp (BR_X1-BR_X0)/4+4
        ret nc
        cp (BR_X1-BR_X0)/8+2
        ld a,BR_X0-17
        jr c,lv_kl
        ld a,BR_X1
        jr lv_kr

; RAMP_ADJ (IX = car, HL = a push or a top speed): on the ramp up HL less 1 / 2^RAMP_SHIFT of itself, on the
; ramp down more by as much; anywhere else as it is. Uses A, DE.
ramp_adj:
        ld a,(ix+C_KIND)
        add a,RMP AND 255
        ld e,a
        ld d,RMP/256
        ld a,(de)
        or a
        ret z
        ld d,h
        ld e,l
        rept RAMP_SHIFT
        sra d
        rr e
        endm
        dec a
        jr z,ra_up
        add hl,de
        ret
ra_up:
        or a
        sbc hl,de
        ret
ramp_push:                      ; a computer car's push (DE, BC), from physics
        push bc
        ex de,hl
        call ramp_adj
        ex (sp),hl
        call ramp_adj
        ld b,h
        ld c,l
        pop de
        ret
ramp_top:                       ; your top speed (HL), from you_grip (DE kept)
        push de
        call ramp_adj
        pop de
        ret

lv_same:                        ; bump (IX = car a, HL = car b): Z if they are on the same level
        push hl
        ld de,C_KIND
        add hl,de
        ld a,(hl)
        add a,LVL AND 255
        ld e,a
        ld d,LVL/256
        ld a,(de)
        ld c,a
        ld a,(ix+C_KIND)
        add a,LVL AND 255
        ld e,a
        ld a,(de)
        cp c
        pop hl
        ret

; O_AT: is tile (column C, row B) a cereal O?  CY = yes. From the row's list (count, then column,
; tile pairs, left to right). BC kept.
o_at:
        ld a,b
        cp MAPH
        ccf
        ret nc
        ld l,b
        ld h,0
        add hl,hl
        ld de,row_index
        add hl,de
        ld e,(hl)
        inc hl
        ld d,(hl)
        ex de,hl
        ld a,(hl)
        or a
        ret z
        ld e,a
oa_1:
        inc hl
        ld a,(hl)
        inc hl
        cp c
        jr z,oa_2
        jr nc,oa_no             ; (past it)
        dec e
        jr nz,oa_1
oa_no:
        or a
        ret
oa_2:
        ld a,(hl)
        cp O_TILE
        jr nz,oa_no
        scf
        ret
; OC_QUICK: any O in tiles (C, B), (C+1, B), (C, B+1), (C+1, B+1)?  CY = maybe
oc_quick:
        call o_at
        ret c
        inc c
        call o_at
        dec c
        ret c
        inc b
        call o_at
        jr c,oq_b1
        inc c
        call o_at
        dec c
oq_b1:
        dec b
        ret

; DRAW_CAR_B (IX = car): draw_car, but a car on the table is hidden where the bridge covers the
; lower road (x BR_H0..BR_H1, in the tunnel): wholly under, it is not drawn; half under, it is drawn
; and then the covered part of the buffer is put back as it was.
dcb_draw:
        jp draw_car
draw_car_b:
        call lv_xy
        jr nz,dcb_draw          ; on the bridge: drawn as ever, over the deck
        ld a,e
        sub (BR_M0-4)/4
        cp (BR_M1-BR_M0)/4+2
        jr nc,dcb_draw          ; not in the tunnel's lane
        ld a,(ix+C_X+1)
        or a
        jr nz,dcb_draw
        ld a,(ix+C_X)           ; the car's picture is x .. x + 15
        cp BR_H0-16
        jr c,dcb_draw
        cp BR_H1+1
        jr nc,dcb_draw
        cp BR_H0+1
        ld c,BR_H0+1            ; C = the cover's edge + 1, B = 0: hidden right of it / 0xFF: hidden left of it
        ld b,0
        jr c,dcb_part
        cp BR_H1-16
        ret c                   ; wholly under: nothing to draw
        ld c,BR_H1+1
        dec b
dcb_part:
        ld l,a                  ; u = x - camx + 15: the picture's first buffer byte is u / 8 (as draw_car)
        ld h,0
        ld de,(camx)
        or a
        sbc hl,de
        ld de,15
        add hl,de
        ld a,h
        or a
        ret nz                  ; out of view
        ld a,l
        cp WIN_W*8+14
        ret nc
        ld e,a                  ; E = u
        and 0xF8
        ld (dcb_x+1),a
        ld a,e
        and 7
        add a,c
        sub (ix+C_X)            ; N = edge + 1 - x + (u AND 7): the pixels from the first byte's left to the edge
        ld c,a
        ld hl,dcb_m0+1          ; the three bytes' masks (1 = under the cover), into the code below
        ld d,3
dcb_mk:
        ld a,c                  ; this byte: n = N clipped to 0..8 pixels left of the edge
        bit 7,a
        jr z,dcb_k1
        xor a
dcb_k1:
        cp 9
        jr c,dcb_k2
        ld a,8
dcb_k2:
        push bc
        ld b,a
        inc b
        ld a,0xFF
        jr dcb_k4
dcb_k3:
        srl a
dcb_k4:
        djnz dcb_k3             ; A = 0xFF >> n: the pixels right of the edge
        pop bc
        xor b                   ; (hidden to the left: the others)
        ld (hl),a
        inc hl
        inc hl
        inc hl
        inc hl
        inc hl
        ld a,c
        sub 8
        ld c,a
        dec d
        jr nz,dcb_mk
        ld l,(ix+C_Y)           ; buffer row y - camy + BUF_TOP - 4, 24 rows from there
        ld h,(ix+C_Y+1)
        ld de,(camy)
        or a
        sbc hl,de
        ld de,BUF_TOP-4
        add hl,de
        bit 7,h
        jr z,dcb_r1
        ld hl,0                 ; (off the top: from the buffer's first row)
dcb_r1:
        ld a,h
        or a
        ret nz
        ld a,l
        cp 168
        ret nc                  ; below the window
        ld b,a
dcb_x:
        ld c,0
        call buf_addr           ; HL = the box's first byte
        push hl
        ld de,BR_SAVE           ; keep the 24 rows of 3 bytes
        ld bc,72
dcb_s1:
        push hl
        ldi
        ldi
        ldi
        pop hl
        call dcb_down
        ld a,b
        or c
        jr nz,dcb_s1
        call draw_car
        pop hl
        ld de,BR_SAVE
        ld b,24
dcb_p1:
        push hl
dcb_m0:
        ld c,0
        call dcb_put
        ld c,0
        call dcb_put
        ld c,0
        call dcb_put
        pop hl
        call dcb_down
        djnz dcb_p1
        ret
dcb_put:                        ; the buffer byte at HL: its bits in C back to the kept byte's
        ld a,(de)
        xor (hl)
        and c
        xor (hl)
        ld (hl),a
        inc de
        inc l
        ret
dcb_down:                       ; HL one pixel row down the buffer (screen layout)
        inc h
        ld a,h
        and 7
        ret nz
        ld a,l
        add a,32
        ld l,a
        ret c
        ld a,h
        sub 8
        ld h,a
        ret
