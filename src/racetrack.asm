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
;   ALL GRASS    green ink on green paper - whatever pixels it holds, it shows solid green
;   PLAIN ROAD   black ink on black paper - whatever pixels it holds, it shows solid black
;   ROAD, WHITE  white ink on black paper: a bit of limit line, start line, grid or canister in it
;   SOME GRASS   green ink on black paper, the grass in pixels
; NOTHING IS DRAWN in the first two, and they are most of the window: their pixels are left as
; they were, hidden by the colour (ink and paper the same - with the FLASH bit set to say so,
; which shows nothing when both are one colour). So there is no clearing of the picture and no
; copying of all of it to the screen (the speed pass of 16 Nov 2026 - PROJECT-LOG: the first
; build cleared and copied every byte, and made 7 pictures a second).
; A square lies over four 8 x 8 tiles of the world (a 2 x 2 "block"). tools/make_world.py works
; out each block's kind (a map of them, two to a byte), keeps ONE map of the world's tiles, a byte each
; (0 nothing, 1 all grass, then the part-grass pictures, then the white ones), and the pictures.
; A square of the last two kinds is MADE UP from its four tiles' pictures, each line through the
; shift tables (rt_sq) - written whole, straight onto the screen. White never shares a square
; with green: the 10 pixels of run-off see to that (make_world.py checks it).
;
; EACH PICTURE (the main loop, racer.asm):
;   rt_class    the 19 x 24 squares' colours into rt_sh, a copy of the screen's colour squares
;   rt_car      each car, by THE CLASH RULE below - in the back buffer: a square a car is in is
;               made up there first (or cleared, if nothing shows in it), then the car drawn
;   rt_hud      the squares of the things that do not scroll (lights, map, plate, bubble) - in
;               the buffer too
;   rt_show     (when the TV frame comes) row by row down the window: the squares that are in
;               the buffer copied to the screen, the others that show anything made up on the
;               screen itself, then the row's 24 colours - a row's pixels and colours together
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
RT_SH   equ COPIER              ; (0xE800: where the screen-copy routine was - this build has none)
rt_bm   equ RT_SH+21*32         ; rt_car_sq: the car's picture, ORed, by row of squares - 6 bytes (on one page: 0xEAA0)
RT_B    equ RT_SH+21*32+8       ; rt_b, below: 2 bytes x 20 (on one page: 0xEAA8)
RT_DATA equ RT_SH+0x300         ; the pictures, the blocks' kinds and the map (rt_world.asm, copied here by start_once)
RT_PL   equ RT_DATA/256         ; the pictures' first page: line 0 of each, at its number; line 1 in the next page ...
;RT_SH_              ; rt_sh: the colour squares of screen rows 0-20, laid out as on the screen (32 a row). A square
                                ; is at its screen address + RT_SH - 0x5800: the low byte is the same. The window is rows 1-19,
                                ; columns 1-24; the rows and columns round it are margins for cars half out of view.
; A square's colour in rt_sh also says where its pixels are:
;   bit 7 set (FLASH) alone   nothing in it shows: its pixels are not looked at
;   bits 7 and 6 set          as rt_class left it: rt_show makes it up on the screen (and gives it its real colour)
;   bit 7 not set             it is in the back buffer (a car, the arrow or a box is in it): rt_show copies it
; (tools/make_world.py has the five that rt_class writes, in its two colour tables)
RT_GRASS equ 0xA4               ; all grass: green on green
RT_PLAIN equ 0x80               ; plain road: black on black
RT_ROAD  equ 0x07               ; road: white on black
RT_EDGE  equ 0x04               ; some grass: green on black
RT_ROAD_D equ RT_ROAD+0xC0      ; ... those two as rt_class leaves them,
RT_EDGE_D equ RT_EDGE+0xC0
RT_EDGE4_D equ RT_EDGE_D+1      ; and a square that may hold grass OR white: the pixels say which (rt_sq4)
; GRASS IS SLOW. Two numbers to tune (measured: PROJECT-LOG, 16 Nov 2026). Each frame a car is pushed, then loses
; speed / 2^shift; it settles at push x (2^shift - 1): 7 pushes on the road (shift 3).
RT_GRASS_FSH equ 2              ; the friction shift on grass: 2 (a quarter lost each frame; the old table's off-road value)
RT_GRASS_PUSH equ 1             ; ... and the push on grass is halved this many times. 2 and 1: top speed 3 x 1/2 = 1.5 pushes,
                                ; 21% of the road's. (2 and 0: 43%; 1 and 0: 14%; 2 and 2: 11%.)

; the cars' colours (ink), by C_KIND: you red; then cyan, yellow, magenta, white
rt_inks: db 2,5,6,3,7

; RT_NEW: a new race. Every square of rt_sh white on black, in the buffer (the margins stay so).
rt_new:
        ld hl,RT_SH
        ld de,RT_SH+1
        ld bc,21*32-1
        ld (hl),RT_ROAD
        ldir
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

