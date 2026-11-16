; =====================================================================
; RACETRACK - A TRIAL (Grant, 16 Nov 2026: "The breakfast table dithering is not working. So we're
; going to scrap the table idea, and make a traditional race track instead ... I want the track to
; be black. The outside of the track will be green"). Only in builds made with RACETRACK=1
; (build.sh -> build/racer_racetrack.tap): OPT_RT 0 leaves the game as it was, byte for byte.
;
; THE LOOK. The road is black. The grass is solid green and starts 10 pixels beyond the road's
; edge; its edge follows the true curve to the pixel. A dashed white limit line runs just inside
; the road's edge. No cloth, no cereal O's, no breakfast things. Each car has its own colour.
;
; HOW, WITH TWO COLOURS A SQUARE. The screen's colour squares are 8 x 8 and do not scroll; the
; picture scrolls a pixel at a time. So each picture every square of the window is decided afresh:
;   ALL GRASS   green ink on green paper - whatever pixels it holds, it shows solid green. NOTHING
;               is drawn there: most of the grass costs no time at all.
;   NO GRASS    white ink on black paper: the limit line, the start line and the grid show white.
;   SOME GRASS  green ink on black paper, and the grass is drawn there in pixels.
; A square lies over four 8 x 8 tiles of the world (a 2 x 2 "block"); tools/make_world.py works
; out for every block which of the three it is (src/rt_world.asm: runs along each row), and the
; grass's pixels: a picture for each tile that is part grass, and for an all-grass tile only the
; quarters of it that share a square with road. White never shares a square with green: the 10
; pixels of run-off see to that (make_world.py checks it), so the line is never tinted.
;
; EACH PICTURE (the main loop, racer.asm):
;   rt_clear    the back buffer's window lines to nothing (the cloth's fill went: this is in its place)
;   rt_class    the 19 x 24 squares' colours into rt_sh, a copy of the screen's colour squares
;   rt_grass    the grass's pixels into the buffer
;   rt_resolve  the squares that may hold grass OR white: the pixels say which
;   draw_tiles  the limit line, the start line, the grid, the canisters - as it always drew the map
;   rt_car      each car, by THE CLASH RULE below
;   rt_hud      the squares of the things that do not scroll (lights, map, plate, bubble)
;   rt_attr_a, the screen copy, rt_attr_b   the colours go to the screen WITH the pixels: the top
;               rows' colours just before their pixels are copied, the bottom rows' just after -
;               the TV's beam overtakes the copy near the foot of the window, and this way each
;               row's colours and pixels change in the same TV frame (see RT_SPLIT)
;
; THE CLASH RULE (rule 4 of tools/make_racetrack_clash_score.py, the one Grant chose), for each
; square a car is in:
;   no grass in it     its ink becomes the car's colour (a bit of limit line there takes it too);
;                      your car is drawn last, so it wins a shared square
;   all grass          the car's colour on green paper
;   grass and road     the scenery is NOT changed: the car is drawn in the square's green, its body
;                      black, with a 1-pixel black rim round it (the car's mask cut 1 pixel
;                      up, down, left and right before the car is drawn)
; The road never turns green and the grass never black because a car is near.
; =====================================================================
RT_SH   equ COPIER+0x200 ; (0xEA00: above the looped copy routine)
RT_AL   equ RT_SH+21*32     ; rt_al, below
RT_DATA equ RT_SH+0x400     ; the grass's rows and pictures (rt_world.asm, copied here by start_once): the rows' index,
gtiles  equ RT_DATA         ; then the part-grass tiles' pictures from number 16 (so both are found from here)
;RT_SH_              ; rt_sh: the colour squares of screen rows 0-20, laid out as on the screen (32 a row). A square
                                ; is at its screen address + RT_SH - 0x5800: the low byte is the same. The window is rows 1-19,
                                ; columns 1-24; the rows and columns round it are margins for cars half out of view.
RT_GRASS equ 0x24               ; all grass: green on green
RT_ROAD  equ 0x07               ; no grass: white on black
RT_EDGE  equ 0x04               ; some grass: green on black
RT_SPLIT equ 13                 ; rows whose colours go up before the pixels are copied (the rest after): the copy runs
                                ; 339 T a line against the beam's 224, from about 5,000 T after the interrupt - the
                                ; beam passes it near row 13
RT_GRASS_FSH equ 1              ; GRASS IS SLOW: the friction shift on grass. Each frame a car loses speed / 2^shift:
                                ; 3 on the road (1/8), and here 1 (1/2) - so the same push gives a quarter of the road's
                                ; top speed. 2 would be a half (the old table's off-road value).

; the cars' colours (ink), by C_KIND: you red; then cyan, yellow, magenta, white
rt_inks: db 2,5,6,3,7

; RT_NEW: a new race. Every square of rt_sh black with white ink.
rt_new:
        ld hl,RT_SH
        ld de,RT_SH+1
        ld bc,21*32-1
        ld (hl),RT_ROAD
        ldir
        ret

; RT_CLEAR: the buffer's window lines, bytes 0-25, to nothing - with the stack pointer, as the cloth was filled (an
; interrupt's 6 bytes land in the margin of the line before: harmless). A row of squares that is all grass is left as it
; is: nothing in it shows (rt_class notes those rows in rt_dead; a car or a box there clears its own squares).
rt_clear:
        ld (rt_sp),sp
        ld ixh,BUF_HI
        ld ixl,(BUF_TOP/8)*32+26
        ld hl,0
        ld de,rt_dead
        ld b,WIN_H/8
rtc_row:
        ld a,(de)
        inc de
        or a
        jr z,rtc_live
        ld a,ixh                ; all grass: on to the next row
        add a,8
        ld ixh,a
        jp rtc_next
rtc_live:
        rept 8
        ld sp,ix
        rept 13
        push hl
        endm
        inc ixh
        endm
rtc_next:
        ld a,ixl                ; the next character row: 32 bytes on, and back up its 8 lines -
        add a,32                ; unless that was the last row of a third of the buffer
        ld ixl,a
        jr c,rtc_third
        ld a,ixh
        sub 8
        ld ixh,a
rtc_third:
        dec b
        jp nz,rtc_row
        ld sp,(rt_sp)
        ret

; RT_CLASS: the window's squares for this picture's camera into rt_sh, from the runs of each row
; of blocks (rt_world.asm). The squares that may hold grass or white are listed (rt_al) for
; rt_resolve. Also: where the grass's rows start (rt_rowp), and the pixel shifts.
rt_class:
        ld hl,(camx)
        ld a,l
        and 7
        ld b,a                  ; the left byte's share of a tile: its first (camx AND 7) pixels -
        ld a,0                  ; E = those low bits, D = the right byte's (the rest)
        jr z,rcl_m1
rcl_m0:
        scf
        rla
        djnz rcl_m0
rcl_m1:
        ld e,a
        cpl
        ld d,a
        ld (rt_mlr),de
        srl h
        rr l
        srl h
        rr l
        srl h
        rr l
        ld a,l
        ld (rt_c0),a            ; the first block column in view
        ld hl,(camy)
        ld a,l
        and 7
        ld (rt_v),a
        srl h
        rr l
        srl h
        rr l
        srl h
        rr l
        add hl,hl
        ld de,gtiles            ; (the rows' index is in the first 128 bytes of the grass pictures' page)
        add hl,de
        ld (rt_rowp),hl
        ld ix,RT_AL
        xor a
        ld (rt_aln),a
        ld hl,rt_dead
        ld (rt_deadp),hl
        ld hl,RT_SH+32+1        ; the window's first square
        ld a,WIN_H/8
rcl_row:
        ld (rt_cnt),a
        push hl
        ex de,hl
        ld hl,(rt_rowp)
        ld a,(hl)
        inc hl
        ld h,(hl)
        ld l,a                  ; HL = the row: the run that holds column 24, the column it starts at, how many runs; the runs
        ld a,(rt_c0)
        cp 24
        jr c,rcl_f0
        inc hl                  ; a window from column 24 on starts at that run
        sub (hl)
        ld c,a                  ; C = blocks still to pass over
        dec hl
        ld a,(hl)
        add a,3
        jr rcl_f1
rcl_f0:
        ld c,a
        ld a,3
rcl_f1:
        add a,l
        ld l,a
        jr nc,rcl_f2
        inc h
rcl_f2:
        ex de,hl                ; DE = the runs, HL = the row's first square
        push hl
        ld hl,(rt_deadp)        ; (the row's note for rt_clear: 0 unless one run of grass fills it)
        ld (hl),0
        pop hl
        ld b,WIN_W              ; B = squares still to fill
        inc c
        dec c
        jr z,rcl_next
rcl_skip:
        ld a,(de)
        inc de
        and 63
        inc a                   ; the run's length
        sub c
        jr z,rcl_next           ; (it ends where the window starts)
        jr nc,rcl_have          ; A = how much of it is in view
        neg
        ld c,a
        jr rcl_skip
rcl_next:
        ld a,(de)
        inc de
        and 63
        inc a
rcl_have:
        cp b                    ; no more than the squares left
        jr c,rcl_h1
        ld a,b
rcl_h1:
        ld c,a                  ; C = squares of this run
        ld a,b
        sub c
        ld b,a                  ; B = squares left after it
        dec de
        ld a,(de)
        inc de
        and 0xC0                ; the kind: 0 all grass, 0x40 no grass, 0x80 some, 0xC0 some - or white
        jr z,rcl_g
        cp 0x80
        jr c,rcl_r
        jr z,rcl_e
        ld (ix+0),l             ; grass or white: listed (where, how many)
        ld (ix+1),h
        ld (ix+2),c
        inc ix
        inc ix
        inc ix
        ld a,(rt_aln)
        inc a
        ld (rt_aln),a
rcl_e:
        ld a,RT_EDGE
        jr rcl_fill
rcl_r:
        ld a,RT_ROAD
        jr rcl_fill
rcl_g:
        ld a,c                  ; all 24 of the row grass: nothing in it will show - noted for rt_clear
        cp WIN_W
        ld a,RT_GRASS
        jr nz,rcl_fill
        push hl
        ld hl,(rt_deadp)
        ld (hl),1
        pop hl
rcl_fill:
        ex af,af'               ; the colour: C squares of it, into the row of 24 "LD (HL),A, INC L" below
        ld a,c
        add a,a
        neg
        add a,rcl_blk_end AND 255
        ld (rcl_j+1),a
        ex af,af'
rcl_j:  jp rcl_blk_end
rcl_blk:
        rept WIN_W
        ld (hl),a
        inc l
        endm
rcl_blk_end:
        ld a,b
        or a
        jp nz,rcl_next
        ld hl,(rt_deadp)
        inc hl
        ld (rt_deadp),hl
        ld hl,(rt_rowp)
        inc hl
        inc hl
        ld (rt_rowp),hl
        pop hl
        ld de,32
        add hl,de
        ld a,(rt_cnt)
        dec a
        jp nz,rcl_row
        ret
        if (rcl_blk / 256) - (rcl_blk_end / 256)
        .error rt_class: the row of LD (HL),A must be on one page (rcl_j is given its low byte only)
        endif

; RT_GRASS: the grass's pixels - draw_tiles' loop over the rows' grass lists. A number from 16 up
; is a part-grass tile's picture (drawn like any tile: tdraw_one, gen_tiles1.asm); 1-15 is an
; all-grass tile's quarters (rt_rim).
rt_grass:
        ld a,(camx)
        and 7
        add a,a
        add a,TAB_HI
        ld b,a                  ; B = the shift tables' page, kept all the way
        ld (rt_tab),a
        ld a,(camy)
        and 7
        ld l,a
        push hl
        push bc
        call td_patch           ; (the tile routine's step into the next character row, for this picture)
        pop bc
        pop hl
        ld a,BUF_TOP
        sub l
        push bc
        ld b,a
        ld c,8
        call buf_addr
        pop bc
        ld (tr_base),hl
        ld a,(rt_c0)
        exx
        ld c,a                  ; C' = the first tile column in view
        exx
        ld hl,(rt_rowp)         ; (rt_class left it WIN_H/8 rows on)
        ld de,0x10000-2*(WIN_H/8)
        add hl,de
        ld (dt_rowp),hl
        ld a,WIN_H/8+1
rg_row:
        ld (dt_rows),a
        ld hl,(dt_rowp)
        ld e,(hl)
        inc hl
        ld d,(hl)
        inc hl
        ld (dt_rowp),hl
        ex de,hl
        inc hl
        inc hl
        ld e,(hl)               ; past the runs, to the grass list
        ld d,0
        inc hl
        add hl,de
        push hl
        exx
        pop hl                  ; HL' = the list
        ld b,(hl)               ; B' = how many tiles in it
        inc hl
        ld a,c
        cp 24
        ld a,(hl)               ; (how many of them are left of column 24: a window from there on passes over them at once)
        inc hl
        jr c,rg_all
        ld e,a
        ld a,b
        sub e
        ld b,a
        ld d,0
        add hl,de
        add hl,de
rg_all:
        ld a,b
        or a
        jr z,rg_row_done
rg_tile:
        ld a,(hl)               ; column
        inc hl
        sub c
        jr c,rg_skip            ; left of the window
        cp WIN_W+1
        jr nc,rg_row_done       ; right of it: the rest of the list is too
        ex af,af'
        ld a,(hl)               ; number
        inc hl
        exx
        cp 16
        jr c,rg_rim
        rlca                    ; DE = gtiles + number * 8
        rlca
        rlca
        ld d,a
        and 0xF8
        ld e,a
        ld a,d
        and 7
        add a,gtiles/256
        ld d,a
        ex af,af'
        ld hl,(tr_base)
        add a,l
        ld l,a
        call tdraw_one
rg_back:
        exx
        dec b
        jr nz,rg_tile
        jr rg_row_done
rg_skip:
        inc hl
        dec b
        jr nz,rg_tile
rg_row_done:
        exx
        ld hl,(tr_base)         ; the next tile row: 32 bytes on, or the next third
        ld a,l
        add a,32
        ld l,a
        jr nc,rg_nt
        ld a,h
        add a,8
        ld h,a
rg_nt:
        ld (tr_base),hl
        ld a,(dt_rows)
        dec a
        jp nz,rg_row
        ret
rg_rim:
        ld c,a                  ; C = the quarters
        ex af,af'
        ld hl,(tr_base)
        add a,l
        ld l,a
        call rt_rim
        ld a,(rt_tab)
        ld b,a
        jr rg_back

; RT_RIM: an all-grass tile's quarters (C: 1 top-left, 2 top-right, 4 bottom-left, 8 bottom-right)
; ORed into the buffer; HL = the tile's first line, its left byte. The tile's first (camy AND 7)
; lines are in one character row, the rest in the next; its first (camx AND 7) pixels in the
; left byte, the rest in the right.
rt_rim:
        ld a,(rt_v)
        or a
        jr z,rr_bot
        ld b,a
        ld a,c
        and 3
        jr z,rr_skip
        call rr_part
        jr rr_cross
rr_skip:
        ld a,h
        add a,b
        ld h,a
rr_cross:
        ld a,l                  ; into the next character row
        add a,32
        ld l,a
        jr c,rr_bot             ; (carry: the next third - H is already right)
        ld a,h
        sub 8
        ld h,a
rr_bot:
        ld a,(rt_v)
        neg
        add a,8
        ld b,a
        ld a,c
        rrca
        rrca
        and 3
        ret z
rr_part:                        ; B lines from HL: A = 1 the left byte, 2 the right, 3 both
        ld de,(rt_mlr)
        cp 2
        jr z,rr_r
        jr nc,rr_lr
rr_l:
        ld a,(hl)
        or e
        ld (hl),a
        inc h
        djnz rr_l
        ret
rr_r:
        inc l
rr_r1:
        ld a,(hl)
        or d
        ld (hl),a
        inc h
        djnz rr_r1
        dec l
        ret
rr_lr:
        ld a,(hl)
        or e
        ld (hl),a
        inc l
        ld a,(hl)
        or d
        ld (hl),a
        dec l
        inc h
        djnz rr_lr
        ret

; RT_BUFSQ: DE = the buffer's first byte of the square whose colour is at HL in rt_sh.
rt_bufsq:
        ld a,h
        sub RT_SH/256
        add a,a
        add a,a
        add a,a
        add a,BUF_HI
        ld d,a
        ld e,l
        inc e
        ret

; RT_RESOLVE: after the grass, before anything white is drawn: each listed square with no grass
; pixel in it is a road square - white ink.
rt_resolve:
        ld a,(rt_aln)
        or a
        ret z
        ld b,a
        ld ix,RT_AL
rs_e:
        ld l,(ix+0)
        ld h,(ix+1)
        ld c,(ix+2)
rs_c:
        call rt_bufsq
        ex de,hl
        ld a,(hl)
        rept 7
        inc h
        or (hl)
        endm
        ex de,hl
        jr nz,rs_n
        ld (hl),RT_ROAD
rs_n:
        inc l
        dec c
        jr nz,rs_c
        inc ix
        inc ix
        inc ix
        djnz rs_e
        ret

; RT_CAR (IX = a car): the car by the clash rule. draw_car is first run as far as knowing where
; the car's picture falls (rt_probe: it then comes to rt_car_sq, below, which decides the squares
; and comes straight back here); then, if a square of grass-and-road is under it, the car's mask
; alone is cut at 1 pixel left, right, up and down - the black rim; then the car is drawn.
rt_car:
        ld a,(ix+C_KIND)
        add a,rt_inks AND 255
        ld l,a
        ld a,0
        adc a,rt_inks/256
        ld h,a
        ld a,(hl)
        ld (rt_ink),a
        xor a
        ld (rt_mixed),a
        inc a
        ld (rt_probe),a
        call draw_car
        xor a
        ld (rt_probe),a
        ld a,(rt_mixed)
        or a
        jp z,draw_car
        ld a,0x7E               ; "OR (HL)" becomes "LD A,(HL)" at the four places draw_car puts the ink in: mask only
        call rtc_patch
        ld l,(ix+C_X)
        ld h,(ix+C_X+1)
        push hl
        dec hl
        call rtc_x
        inc hl
        inc hl
        call rtc_x
        pop hl
        ld (ix+C_X),l
        ld (ix+C_X+1),h
        ld l,(ix+C_Y)
        ld h,(ix+C_Y+1)
        push hl
        dec hl
        call rtc_y
        inc hl
        inc hl
        call rtc_y
        pop hl
        ld (ix+C_Y),l
        ld (ix+C_Y+1),h
        ld a,0xB6
        call rtc_patch
        jp draw_car
rtc_x:
        ld (ix+C_X),l
        ld (ix+C_X+1),h
        jr rtc_d
rtc_y:
        ld (ix+C_Y),l
        ld (ix+C_Y+1),h
rtc_d:
        push hl
        call draw_car
        pop hl
        ret
rtc_patch:
        ld (dc_ink0),a
        ld (dc_ink1),a
        ld (dc_ink2),a
        ld (dc_ink3),a
        ret

; RT_CAR_SQ (from draw_car, once the picture's place is known: wxu, dc_row0, dc_count): the
; squares the car's 16-wide picture falls in - 2 or 3 across, 1 to 3 down - each by the rule.
; It does not go back into draw_car: its RET is draw_car's own.
rt_car_sq:
        pop af                  ; (the way back into draw_car)
        ld a,(wxu)              ; the picture's 16 pixels start at buffer x = wxu + 1
        inc a
        ld c,a
        add a,15
        rrca
        rrca
        rrca
        and 0x1F
        ld b,a                  ; B = its last byte column
        ld a,c
        rrca
        rrca
        rrca
        and 0x1F                ; A = its first
        jr nz,rq_c1
        inc a                   ; (byte 0 has no square in rt_sh)
rq_c1:
        ld c,a                  ; C = first byte column (1 up)
        ld a,b
        sub c
        ret c
        inc a
        ld e,a                  ; E = columns
        ld a,(dc_count)
        ld b,a
        ld a,(dc_row0)
        ld d,a
        add a,b
        dec a
        rrca
        rrca
        rrca
        and 0x1F
        ld b,a                  ; B = the last character row (of the buffer: 0-19)
        ld a,d
        rrca
        rrca
        rrca
        and 0x1F
        ld d,a                  ; D = the first
        ld a,b
        sub d
        inc a
        ld b,a                  ; B = rows
        ld a,d                  ; HL = the first square in rt_sh: row D, column C - 1
        rrca
        rrca
        rrca
        ld l,a
        and 3
        add a,RT_SH/256
        ld h,a
        ld a,l
        and 0xE0
        add a,c
        dec a
        ld l,a
rq_row:
        push bc
        push hl
        ld b,e
rq_col:
        push bc
        push de
        call rq_cell
        pop de
        pop bc
        inc l
        djnz rq_col
        pop hl
        ld bc,32
        add hl,bc
        pop bc
        djnz rq_row
        ret
rq_cell:
        ld a,(hl)
        cp RT_EDGE
        jr z,rq_amb
        and 0x38
        jr z,rq_road
rq_grass:                       ; all grass: nothing but the car in it, the car's colour on green (unless another car has it
        ld a,(hl)               ; already: that car's pixels stay)
        cp RT_GRASS
        jr nz,rq_gset
rq_grass_c:
        call rt_bufsq
        xor a
        rept 7
        ld (de),a
        inc d
        endm
        ld (de),a
rq_gset:
        ld a,(rt_ink)
        or 0x20
        ld (hl),a
        ret
rq_road:                        ; no grass: the car's colour on black
        ld a,(rt_ink)
        ld (hl),a
        ret
rq_amb:                         ; green on black: what do its pixels say?
        call rt_bufsq
        ld a,(de)
        or a
        jr z,rq_z
        inc a
        jr nz,rq_mix
        ld b,7                  ; all set so far: all grass?
rq_f:
        inc d
        ld a,(de)
        inc a
        jr nz,rq_mix
        djnz rq_f
        jr rq_grass_c
rq_z:
        ld b,7                  ; nothing so far: no grass?
rq_z1:
        inc d
        ld a,(de)
        or a
        jr nz,rq_mix
        djnz rq_z1
        jr rq_road
rq_mix:
        ld a,1                  ; grass and road: the square stays as it is, and the car gets its rim
        ld (rt_mixed),a
        ret

; RT_HUD: the squares of the things that do not scroll, after the cars and before those things
; are drawn. The mini-map and the place plate stand on black boxes of their own (white ink); the
; start lights and the crew chief's bubble keep their colours (their own routines, writing to
; rt_sh instead of the screen for once: attr_addr's page is switched).
rt_hud:
        ld hl,RT_SH+(WIN_Y/8+16)*32+WIN_COL     ; the mini-map: the window's rows 16-18, columns 0-2
        ld bc,0x0303
        call rt_attrs
        ld hl,BUF+0x1000+1*32+2 ; ... their 24 lines of 3 bytes cleared (buffer rows 136-159)
        ld bc,0x0303
        call rt_wipe
        ld a,(lt_on)
        or a
        jr nz,rh_lights
        ld hl,RT_SH+(WIN_Y/8)*32+WIN_COL+19     ; the place plate: rows 0-2, columns 19-23
        ld bc,0x0305
        call rt_attrs
        ld hl,BUF+1*32+21       ; ... the 2 lines above the plate's picture and the 4 below it (pl_draw writes the 18 between
        ld de,0                 ; whole): buffer rows 8-9 and 28-31
        ld b,2
        call rw_lines
        ld hl,BUF+3*32+4*256+21
        ld b,4
        call rw_lines
        jr rh_1
rh_lights:
        call rh_on
        call lights_attr
        call rh_off
rh_1:
        ld a,(msg_timer)
        or a
        ret z
        call rh_on
        ld a,0x78
        call msg_cells
rh_off:
        ld a,0x58
        jr rh_set
rh_on:
        ld a,RT_SH/256
rh_set:
        ld (aa_hi+1),a
        ret
; RT_ATTRS: B rows x C columns of rt_sh from HL: white on black.
rt_attrs:
        ld de,32
rat_r:
        push hl
        ld a,c
rat_c:
        ld (hl),RT_ROAD
        inc l
        dec a
        jr nz,rat_c
        pop hl
        add hl,de
        djnz rat_r
        ret
; RT_WIPE: B rows of squares, C bytes wide (3 or 5), from HL in the buffer (a row's first line): cleared.
; RW_LINES: B lines of 5 bytes from HL (within one row of squares).
rt_wipe:
        ld de,0
rwp_r:
        push bc
        push hl
        ld b,8
        ld a,c
        cp 5
        jr z,rwp_5
rwp_3:
        ld (hl),d
        inc l
        ld (hl),d
        inc l
        ld (hl),d
        dec l
        dec l
        inc h
        djnz rwp_3
        jr rwp_n
rwp_5:
        call rw_lines
rwp_n:
        pop hl
        ld a,l                  ; the next row of squares: 32 bytes on, or the next third
        add a,32
        ld l,a
        jr nc,rwp_1
        ld a,h
        add a,8
        ld h,a
rwp_1:
        pop bc
        djnz rwp_r
        ret
rw_lines:
        ld (hl),d
        inc l
        ld (hl),d
        inc l
        ld (hl),d
        inc l
        ld (hl),d
        inc l
        ld (hl),d
        ld a,l
        sub 4
        ld l,a
        inc h
        djnz rw_lines
        ret

; RT_ARROW (from arrow_draw, when it is about to draw): the corner arrow's 3 x 3 squares take yellow ink, by the cars'
; rule (rq_cell) - so in a grass-and-road square it shows in the grass's green.
rt_arrow:
        ld a,6
        ld (rt_ink),a
        ld hl,RT_SH+(WIN_Y/8+ARROW_TOP/8)*32+WIN_COL+ARROW_COL
        ld c,3
ra_r:
        ld b,3
ra_c:
        push bc
        call rq_cell
        pop bc
        inc l
        djnz ra_c
        ld a,l
        add a,32-3
        ld l,a
        jr nc,ra_1
        inc h
ra_1:
        dec c
        jr nz,ra_r
        ret

; RT_ATTR_A, RT_ATTR_B: rt_sh's window squares to the screen - the first RT_SPLIT rows, the rest.
rt_attr_a:
        ld hl,RT_SH+32+1
        ld de,0x5800+32+1
        ld a,RT_SPLIT
        jr rta_row
rt_attr_b:
        ld hl,RT_SH+32*(RT_SPLIT+1)+1
        ld de,0x5800+32*(RT_SPLIT+1)+1
        ld a,WIN_H/8-RT_SPLIT
rta_row:
        rept WIN_W
        ldi
        endm
        ld bc,32-WIN_W
        add hl,bc
        ex de,hl
        add hl,bc
        ex de,hl
        dec a
        jr nz,rta_row
        ret

rt_sp:    dw 0
rt_deadp: dw 0
rt_dead:  defs WIN_H/8          ; each row of squares: 1 - all grass (nothing in it shows: rt_clear leaves it)
rt_rowp:  dw 0                  ; the grass rows' index, as rt_class walks it
rt_mlr:   dw 0                  ; low byte: the left byte's bits of a tile (its first camx AND 7 pixels); high: the right's
rt_c0:    db 0                  ; the first block column in view
rt_v:     db 0                  ; camy AND 7
rt_cnt:   db 0
rt_tab:   db 0                  ; the shift tables' page for this picture
rt_ink:   db 0                  ; the colour of the car being drawn
rt_probe: db 0                  ; 1: draw_car goes to rt_car_sq once it knows where the picture falls
rt_mixed: db 0                  ; 1: a grass-and-road square is under the car
rt_aln:   db 0                  ; rt_al: how many entries
; RT_AL: 3 bytes x up to 96 - the squares that may hold grass or white: address in rt_sh, how many in a row
