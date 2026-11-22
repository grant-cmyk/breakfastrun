; =====================================================================
; LINEJ - THE FINISH LINE'S JUDGE (LINEJ=1, breakfast fast tapes; Grant, 22 Nov 2026: "I definitely was second over the
; line and yet I was marked as third. So the game is not recording the finish order correctly - this is not the first time
; I have seen this"). A car's lap is counted when it reaches the waypoint at the line (lap_and_inc) - a computer car within
; REACH of its aim point, 5-18 px BEFORE the drawn line (x 288-295); you within 40 px of the waypoint, looked at every other
; picture, 2 px before to 9 px after it (measured, 22 Nov 2026). In a close finish a computer car up to 20-30 px behind you
; was counted first. Now the PLACES are given by the drawn line itself: each picture, a car on its last lap (or counted in
; already) whose middle has crossed LJ_X since the last picture, on the bottom straight, is given the next place
; (line_at). progress (racer.asm) puts the cars over the line in that order; you are "in" when you cross it.
; Every car is judged the same way, every picture (the cars move about 10 px a picture: a car 2 or 3 px ahead of another
; over the line in the same picture is given the place by its order in the cars - you first).
; =====================================================================
LJ_X    equ 292-8               ; the line's middle, as the car's left edge (its middle is x + 8)

        if OPT_OIL = 0          ; (OIL: spill_new clears these too)
lj_new:                         ; a new race: nobody over (line_px from the grid: all before the line)
        ld hl,line_at
        ld b,16
ljn_1:  ld (hl),0
        inc hl
        djnz ljn_1
        ret
        endif

line_judge:                     ; each picture, with the cars moved
        ld ix,cars
        ld hl,line_px
        ld b,NCARS
lj_1:   push bc
        ld e,(ix+C_X)
        ld d,(ix+C_X+1)         ; DE = its x now
        ld c,(hl)
        ld (hl),e
        inc hl
        ld b,(hl)               ; BC = at the last picture
        ld (hl),d
        inc hl
        push hl
        ld hl,LJ_X-1
        or a
        sbc hl,bc
        jr c,lj_n               ; (it was over already)
        ld hl,LJ_X-1
        sbc hl,de               ; (carry clear)
        jr nc,lj_n              ; (not over yet)
        ld l,(ix+C_Y)           ; on the bottom straight (y 348-467)?
        ld h,(ix+C_Y+1)
        ld de,0x10000-348
        add hl,de
        ld de,120
        or a
        sbc hl,de
        jr nc,lj_n
        ld a,(ix+C_LAPS)        ; the end of its last lap: counted in already, or on its last lap heading for the line's waypoint
        cp LAPS+1
        jr nc,lj_y
        cp LAPS
        jr nz,lj_n
        ld a,(ix+C_WP)          ; (heading for a waypoint in the second half of the lap: your waypoint can lag well behind
        sub WS+1                ; where you are when you cut corners - 22 Nov 2026, you over the line second and not seen,
        jr nc,lj_w              ; when only the line's own waypoint, then the last four, counted. Just over the line at the
        add a,NWP               ; START of the last lap a car heads for WS+1: passed 0)
lj_w:   cp NWP/2
        jr c,lj_n
lj_y:   ld a,(ix+C_KIND)
        ld hl,line_at
        add a,l
        ld l,a
        jr nc,lj_y1
        inc h
lj_y1:  ld a,(hl)
        or a
        jr nz,lj_n              ; (placed already)
        ld a,(line_cnt)
        inc a
        ld (line_cnt),a
        ld (hl),a
lj_n:   pop hl
        ld de,C_SIZE
        add ix,de
        pop bc
        djnz lj_1
        ret

lj_prog:                        ; (progress, IX = a car): NZ and A = its progress if it is over the line (250 - its place)
        ld e,(ix+C_KIND)
        ld d,0
        ld hl,line_at
        add hl,de
        ld a,(hl)
        or a
        ret z
        ld a,250
        sub (hl)
        ld l,0
        ret                     ; (NZ: 245 to 249)
        if OPT_OIL
dc_oil:                         ; (draw_car: the spill's frame - oil.asm; down here, the program is full)
        ld de,oil_gfx
        ld b,OIL_B
        ld a,OIL_ROWS
        jp dc_frame
        endif
