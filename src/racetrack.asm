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

; RT_CLASS: the window's squares for this picture's camera into rt_sh, from the map of the blocks' kinds (rt_world.asm:
; two blocks to a byte, turned into the two colours by two tables). Also, once a picture: the shift tables' pages, how
; many of a square's lines come from the upper pair of tiles and how many from the lower (rt_sq's entries), and for
; each row of tiles in view where its row of the map is (rt_b).
rt_class:
        ld hl,(camx)
        ld a,l
        and 7
        add a,a
        add a,TAB_HI            ; the page of a tile's left-hand part (its first camx AND 7 pixels: the square to its left)
        ld (sq_bl1+1),a
        ld (sq_bl2+1),a
        ld (sq_bl3+1),a
        ld (sq_bl4+1),a
        ld (sq_bl5+1),a
        ld (sq_bl6+1),a
        ld (s4_b2+1),a
        ld (s4_b4+1),a
        ld d,a
        ld e,0xFF
        ld a,(de)               ; ... and that part of an all-grass tile
        ld (sq_mb1+1),a
        ld (sq_mb2+2),a
        ld (sq_mb3+1),a
        ld (sq_mb4+2),a
        inc d                   ; the same for its right-hand part
        ld a,d
        ld (sq_br1+1),a
        ld (sq_br2+1),a
        ld (s4_b1+1),a
        ld (s4_b3+1),a
        ld a,(de)
        ld (sq_ma1+1),a
        ld (sq_ma2+2),a
        ld (sq_ma3+1),a
        ld (sq_ma4+2),a
        srl h
        rr l
        srl h
        rr l
        srl h
        rr l
        ld a,l
        ld (rt_c0),a            ; the first tile column in view
        ld a,(camy)
        and 7
        ld hl,rt_v
        cp (hl)
        jp z,rcl_same           ; (the fold is where it was: nothing to patch)
        ld (hl),a
        ld c,a                  ; C = the lines below the fold (from the lower pair of tiles: their lines 0 up)
        ld (sq_sv+1),a
        add a,RT_PL
        ld (sq_dt1+1),a         ; the upper pair's first line used
        ld (sq_dt2+1),a
        ld (sq_dt3+1),a
        ld (sq_dt4+1),a
        ld (s4_d1+1),a
        ld (s4_d2+1),a
        ld a,8
        sub c
        ld b,a                  ; B = the lines above the fold
        ld (sq_st+1),a
        ld hl,rt_w1e            ; where to come into each run of 8 lines for that many
        ld de,0x10000-6
        call rt_ent
        ld (sq_tw1+1),hl
        ld (sq_tw2+1),hl
        ld (sq_tw3+1),hl
        ld a,c
        ld hl,rt_w1e
        call rt_ent
        ld (sq_bw1+1),hl
        ld (sq_bw2+1),hl
        ld (sq_bw3+1),hl
        ld a,c
        ld hl,rt_o1e
        ld de,0x10000-7
        call rt_ent
        ld (sq_bo1+1),hl
        ld a,b
        ld hl,rt_o1e
        call rt_ent
        ld (sq_to1+1),hl
        ld a,b
        ld hl,rt_wke
        ld de,0x10000-8
        call rt_ent
        ld (sq_tk1+1),hl
        ld (sq_tk2+1),hl
        ld a,c
        ld hl,rt_wke
        call rt_ent
        ld (sq_bk1+1),hl
        ld (sq_bk2+1),hl
        ld a,c
        ld hl,rt_ze
        ld de,0x10000-2
        call rt_ent
        ld (sq_bz1+1),hl
        ld (sq_bz2+1),hl
        ld a,c
        ld hl,rt_ore
        call rt_ent
        ld (s4_c3+1),hl
        ld (s4_c4+1),hl
        ld a,b
        ld hl,rt_ore
        call rt_ent
        ld (s4_c1+1),hl
        ld (s4_c2+1),hl
        ld a,b
        ld hl,rt_ze
        call rt_ent
        ld (sq_tz1+1),hl
        ld (sq_tz2+1),hl
rcl_same:
        ld hl,(camy)
        srl h
        rr l
        srl h
        rr l
        srl h
        rr l
        push hl
        add hl,hl
        ld de,RT_MAPR
        add hl,de               ; rt_b: for each of the 20 rows of tiles in view, where the tile under screen column 0 is
        ld a,(rt_c0)            ; in the map (the window's first column is screen column 1)
        dec a
        ld c,a
        add a,a
        sbc a,a
        ld b,a                  ; BC = the first tile column in view - 1
        ld de,RT_B
        ld a,WIN_H/8+1
rcl_b:
        ex af,af'
        ld a,(hl)
        inc hl
        push hl
        ld h,(hl)
        ld l,a
        add hl,bc
        ex de,hl
        ld (hl),e
        inc l
        ld (hl),d
        inc l
        ex de,hl
        pop hl
        inc hl
        ex af,af'
        dec a
        jr nz,rcl_b
        pop hl                  ; the first row of blocks in view: its kinds are at RT_CLS + 36 x row
        add hl,hl
        add hl,hl
        ld e,l
        ld d,h
        add hl,hl
        add hl,hl
        add hl,hl
        add hl,de               ; x 36
        ld de,RT_CLS
        add hl,de
        ld a,(rt_c0)
        srl a
        ld e,a
        ld d,0
        ld a,d
        adc a,a                 ; (the bit that fell off: an odd first column starts half-way through a byte -
        ld (rt_odd),a           ; then 13 bytes are turned into screen columns 0-25, and the two margins put back)
        add hl,de
        ex de,hl                ; DE = the kinds
        ld hl,RT_SH+32+1        ; the window's first square
        ld b,RT_CLT/256
        ld a,WIN_H/8
rcl_row:
        ex af,af'
        ld a,(rt_odd)
        or a
        jr z,rcl_even
        dec l
        ld a,(de)
        inc de
        ld c,a
        ld a,(bc)               ; the left block's colour
        ld (hl),a
        inc l
        inc b
        ld a,(bc)               ; the right one's
        ld (hl),a
        inc l
        dec b
rcl_even:
        rept WIN_W/2
        ld a,(de)
        inc de
        ld c,a
        ld a,(bc)
        ld (hl),a
        inc l
        inc b
        ld a,(bc)
        ld (hl),a
        inc l
        dec b
        endm
        ld a,(rt_odd)
        or a
        jr z,rcl_e2
        dec l                   ; an odd start: the margins (screen columns 0 and 25) are not the window's
        ld (hl),RT_ROAD
        ld a,l
        sub WIN_W+1
        ld l,a
        ld (hl),RT_ROAD
        add a,WIN_W+1
        ld l,a
        ld a,e                  ; (13 bytes read, 23 on to the next row's)
        add a,36-WIN_W/2-1
        ld e,a
        jr nc,rcl_nx
        inc d
        jr rcl_nx
rcl_e2:
        ld a,e                  ; (12 bytes read)
        add a,36-WIN_W/2
        ld e,a
        jr nc,rcl_nx
        inc d
rcl_nx:
        ld a,l                  ; the next row's first square
        add a,32-WIN_W
        ld l,a
        jr nc,rcl_n2
        inc h
rcl_n2:
        ex af,af'
        dec a
        jp nz,rcl_row
        ret
; RT_ENT: HL = HL + A x DE (A = 0 to 8 lines, DE = minus a line's bytes): where to come into a run of 8 lines. Keeps BC, DE.
rt_ent:
        or a
        ret z
ren_1:
        add hl,de
        dec a
        jr nz,ren_1
        ret

; RT_SQ: one square made up from its four tiles, written whole. HL = where (its first line: in the buffer or on the
; screen); the other HL = the upper-left tile in the map, the other DE = the lower-left (both are left one tile on).
; The lines above the fold come from the upper pair of tiles, from their line camy AND 7 down; the rest from the lower
; pair's first lines. In each pair the left-hand tile gives the square its right-hand part and the other way about. A
; tile is nothing (0), all grass (1: its part is the same bits every line) or a picture, whose part of each line comes
; through the shift tables - so a pair is one of nine cases, each done the quickest way. Uses IXL; the other BC too.
rt_sq:
        exx
        ld a,(hl)               ; the upper-left tile
        inc hl
        ld b,(hl)               ; the upper-right
        exx
        cp 2
        jr nc,sq_tp
        or a
        jr z,sq_tn
        exx                     ; --- all grass on the left
        ld a,b
        exx
        cp 2
        jr nc,sq_tgp
        or a
sq_ma1: ld a,0                  ; (patched: an all-grass left-hand tile's part)
        jr z,sq_tz1
        ld a,0xFF
sq_tz1: call rt_ze              ; (patched: the lines above the fold) the same byte down them
        jp sq_bot
sq_tgp:
        ld e,a
sq_dt4: ld d,RT_PL
sq_bl5: ld b,TAB_HI
sq_ma2: ld ixl,0
sq_tk1: call rt_wke             ; the picture's part, with the grass's
        jp sq_bot
sq_tn:
        exx                     ; --- nothing on the left
        ld a,b
        exx
        cp 2
        jr nc,sq_tnp
        or a
        jr z,sq_tz2
sq_mb1: ld a,0                  ; (patched: an all-grass right-hand tile's part)
sq_tz2: call rt_ze
        jp sq_bot
sq_tnp:
        ld e,a
sq_dt3: ld d,RT_PL
sq_bl2: ld b,TAB_HI
sq_tw1: call rt_w1e
        jp sq_bot
sq_tp:
        ld e,a                  ; --- a picture on the left
sq_dt1: ld d,RT_PL              ; (patched: its line at the square's top)
sq_br1: ld b,TAB_HI+1           ; (patched)
        exx
        ld a,b
        exx
        cp 2
        jr nc,sq_tpp
        or a
        jr z,sq_tw2
sq_mb2: ld ixl,0
sq_tk2: call rt_wke
        jp sq_bot
sq_tw2: call rt_w1e
        jp sq_bot
sq_tpp:
sq_tw3: call rt_w1e             ; two pictures: the left one's part written,
        exx
        ld a,b
        exx
        ld e,a
sq_dt2: ld d,RT_PL
sq_bl1: ld b,TAB_HI
        ld a,h                  ; (back up to the square's first line)
sq_st:  sub 8
        ld h,a
sq_to1: call rt_o1e             ; the right one's ORed in
sq_bot:                         ; HL is at the fold
        exx
        ex de,hl
        ld a,(hl)               ; the lower-left tile
        inc hl
        ld b,(hl)               ; the lower-right
        ex de,hl
        exx
        cp 2
        jr nc,sq_bp
        or a
        jr z,sq_bn
        exx
        ld a,b
        exx
        cp 2
        jr nc,sq_bgp
        or a
sq_ma3: ld a,0
        jr z,sq_bz1
        ld a,0xFF
sq_bz1: jp rt_ze
sq_bgp:
        ld e,a
        ld d,RT_PL
sq_bl6: ld b,TAB_HI
sq_ma4: ld ixl,0
sq_bk1: jp rt_wke
sq_bn:
        exx
        ld a,b
        exx
        cp 2
        jr nc,sq_bnp
        or a
        jr z,sq_bz2
sq_mb3: ld a,0
sq_bz2: jp rt_ze
sq_bnp:
        ld e,a
        ld d,RT_PL
sq_bl4: ld b,TAB_HI
sq_bw1: jp rt_w1e
sq_bp:
        ld e,a
        ld d,RT_PL
sq_br2: ld b,TAB_HI+1
        exx
        ld a,b
        exx
        cp 2
        jr nc,sq_bpp
        or a
        jr z,sq_bw2
sq_mb4: ld ixl,0
sq_bk2: jp rt_wke
sq_bw2: jp rt_w1e
sq_bpp:
sq_bw3: call rt_w1e
        exx
        ld a,b
        exx
        ld e,a
        ld d,RT_PL
sq_bl3: ld b,TAB_HI
        ld a,h
sq_sv:  sub 0
        ld h,a
sq_bo1: jp rt_o1e
; a tile's part, 8 lines of it (come in part-way for fewer): DE = the tile's line in the pictures (a page a line),
; B = the shift table's page, HL = where. RT_W1 writes; RT_WK writes it ORed with IXL; RT_O1 ORs it into what is
; there; RT_Z writes A
rt_w1:
        rept 8
        ld a,(de)
        inc d
        ld c,a
        ld a,(bc)
        ld (hl),a
        inc h
        endm
rt_w1e: ret
rt_wk:
        rept 8
        ld a,(de)
        inc d
        ld c,a
        ld a,(bc)
        or ixl
        ld (hl),a
        inc h
        endm
rt_wke: ret
rt_o1:
        rept 8
        ld a,(de)
        inc d
        ld c,a
        ld a,(bc)
        or (hl)
        ld (hl),a
        inc h
        endm
rt_o1e: ret
rt_z:
        rept 8
        ld (hl),a
        inc h
        endm
rt_ze:  ret
; RT_OR: A = up to 8 lines of a picture ORed together (HL = its line in the pictures; come in with A = 0)
rt_or:
        rept 8
        or (hl)
        inc h
        endm
rt_ore: ret

; RT_SQ4: a square that may hold grass or something white (never both): made up like any other, and A = its colour -
; white on black if a white tile's part in it has a pixel, green on black if not. (A white tile's number is RT_W0 or more;
; its part of the square is the same lines and the same shift as rt_sq uses, ORed together and looked up once.)
rt_sq4:
        call rt_sq
        exx
        dec hl
        ld a,(hl)               ; the upper-left tile
        inc hl
        exx
        cp RT_W0
        jr c,s4_1
        ld l,a
s4_d1:  ld h,RT_PL              ; (patched, as sq_dt1)
s4_b1:  ld b,TAB_HI+1
        xor a
s4_c1:  call rt_ore             ; (patched: the lines above the fold)
        ld c,a
        ld a,(bc)
        or a
        jr nz,s4_w
s4_1:
        exx
        ld a,(hl)               ; the upper-right
        exx
        cp RT_W0
        jr c,s4_2
        ld l,a
s4_d2:  ld h,RT_PL
s4_b2:  ld b,TAB_HI
        xor a
s4_c2:  call rt_ore
        ld c,a
        ld a,(bc)
        or a
        jr nz,s4_w
s4_2:
        exx
        dec de
        ld a,(de)               ; the lower-left
        inc de
        exx
        cp RT_W0
        jr c,s4_3
        ld l,a
        ld h,RT_PL
s4_b3:  ld b,TAB_HI+1
        xor a
s4_c3:  call rt_ore
        ld c,a
        ld a,(bc)
        or a
        jr nz,s4_w
s4_3:
        exx
        ld a,(de)               ; the lower-right
        exx
        cp RT_W0
        jr c,s4_g
        ld l,a
        ld h,RT_PL
s4_b4:  ld b,TAB_HI
        xor a
s4_c4:  call rt_ore
        ld c,a
        ld a,(bc)
        or a
        jr nz,s4_w
s4_g:
        ld a,RT_EDGE
        ret
s4_w:
        ld a,RT_ROAD
        ret

; RT_SQ_BUF: HL = a square of rt_sh as rt_class left it: made up in the back buffer, and its colour then says so
; (RT_ROAD or RT_EDGE). For the squares a car, its rim or the arrow is in. Keeps HL, BC, IX.
rt_sq_buf:
        push ix
        push bc
        push hl
        ld a,l
        rlca
        rlca
        rlca
        and 7
        ld c,a
        ld a,h
        sub RT_SH/256
        add a,a
        add a,a
        add a,a
        ld b,a                  ; B = the third of the screen x 8
        or c                    ; A = the screen row (1-19)
        add a,a
        add a,(RT_B-2) AND 255
        exx
        ld l,a
        ld h,RT_B/256
        ld e,(hl)
        inc l
        ld d,(hl)
        inc l
        ld a,(hl)
        inc l
        ld h,(hl)
        ld l,a                  ; the row of tiles under the square's top, and the one below it
        exx
        ld a,l
        and 31
        exx
        ld c,a
        ld b,0
        add hl,bc
        ex de,hl
        add hl,bc               ; the other HL = the upper-left tile, the other DE = the lower-left
        exx
        ld a,b
        add a,BUF_HI
        ld b,(hl)               ; B = the colour it has
        ld h,a
        inc l                   ; HL = the square in the buffer
        ld a,b
        cp RT_EDGE4_D
        jr z,sb_4
        and 0x3F
        push af
        call rt_sq
        pop af
        jr sb_e
sb_4:
        call rt_sq4
sb_e:
        pop hl
        ld (hl),a
        pop bc
        pop ix
        ret
        if (RT_B / 256) - ((RT_B + 39) / 256)
        .error rt_b must be on one page
        endif

; RT_SHOW: the picture to the screen (the main loop calls it when the TV frame has come). Row by row down the window:
; each square that shows anything - copied from the back buffer if it is there, made up on the screen if not - and
; straight after it that square's colour. So a square's pixels and its colour always change together (within a few
; T-states: the TV's beam all but never sees one without the other), and a square whose colour hides it is never touched. Interrupts stay on (nothing here moves the stack pointer).
; Along a row the other HL and DE are at the map's tiles for the square whose low byte is the other C (rt_dir moves
; them on to the square it is given).
rt_show:
        ld hl,RT_B
        ld (rt_bp),hl
        ld hl,RT_SH+32+1
        ld a,WIN_H/8
sh_row:
        ld (rt_cnt),a
        ld a,h                  ; the row's pages: of rt_sh, of the screen, of the buffer
        ld (sd_hh+1),a
        ld (sd_hh2+1),a
        ld (cp_hh+1),a
        sub RT_SH/256
        add a,a
        add a,a
        add a,a
        add a,0x40
        ld (sd_sh+1),a
        ld (sd_sh2+1),a
        ld (cp_sh+1),a
        add a,BUF_HI-0x40
        ld (cp_bh+1),a
        ld e,l                  ; DE = the row's colours on the screen: each square's goes up as soon as its pixels are there
        ld a,h
        sub (RT_SH-0x5800)/256
        ld d,a
        ld (sd_at+1),a
        ld (sd_at2+1),a
        ld (cp_at+1),a
        ld a,l
        exx
        ld c,a
        ld hl,(rt_bp)           ; the row's two rows of tiles in the map
        ld e,(hl)
        inc l
        ld d,(hl)
        inc l
        ld (rt_bp),hl
        ld a,(hl)
        inc l
        ld h,(hl)
        ld l,a
        inc hl                  ; (rt_b is for screen column 0)
        inc de
        ex de,hl
        exx
        rept WIN_W
        ld a,(hl)
        add a,a
        call nc,rt_cp           ; (bit 7 not set: it is in the buffer)
        call m,rt_dir           ; (bits 7 and 6: rt_class's own. Bit 7 alone: nothing in it shows)
        ldi                     ; its colour, and on to the next
        endm
        ld de,32-WIN_W
        add hl,de
        ld a,(rt_cnt)
        dec a
        jp nz,sh_row
        ret
; RT_DIR: a square to make up on the screen (HL = it in rt_sh, A = its colour x 2). Keeps HL.
rt_dir:
        cp (RT_EDGE4_D*2) AND 255
        jr z,sd_4
        rrca
        and 0x3F
        ld (hl),a               ; the colour it shows in
        ld a,l
        exx
        ld b,a
        sub c
        jr z,sd_1
        ld c,a                  ; (not the square the map's pointers are at: that many tiles on)
        ld a,b
        ld b,0
        add hl,bc
        ex de,hl
        add hl,bc
        ex de,hl
        ld b,a
sd_1:
        ld c,b
        inc c
        exx
sd_sh:  ld h,0x40               ; (patched: this row's page of the screen)
        call rt_sq
sd_hh:  ld h,RT_SH/256          ; (patched: this row's page of rt_sh)
        ld e,l
sd_at:  ld d,0x58               ; (patched: ... and of the screen's colours)
        xor a
        ret
sd_4:
        ld a,l
        exx
        ld b,a
        sub c
        jr z,sd_5
        ld c,a
        ld a,b
        ld b,0
        add hl,bc
        ex de,hl
        add hl,bc
        ex de,hl
        ld b,a
sd_5:
        ld c,b
        inc c
        exx
sd_sh2: ld h,0x40
        call rt_sq4
        ex af,af'               ; (rt_sq4 used L: the square's low byte is the other C, less one)
        exx
        ld a,c
        exx
        dec a
        ld l,a
        ex af,af'
sd_hh2: ld h,RT_SH/256
        ld (hl),a
        ld e,l
sd_at2: ld d,0x58
        xor a
        ret
; RT_CP: the square's 8 lines from the buffer to the screen (and the sign flag off: it is not for rt_dir)
rt_cp:
        ld e,l
        inc e
cp_bh:  ld d,BUF_HI             ; (patched)
cp_sh:  ld h,0x40               ; (patched)
        rept 7
        ld a,(de)
        ld (hl),a
        inc d
        inc h
        endm
        ld a,(de)
        ld (hl),a
cp_hh:  ld h,RT_SH/256          ; (patched)
        ld e,l
cp_at:  ld d,0x58               ; (patched)
        xor a
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
        call rq_ring            ; (the squares the rim may reach: into the buffer)
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

; RT_CAR_SQ (from draw_car, once the picture's place is known: wxu, dc_row0, dc_count, DE = its rows): the squares the
; car's picture really has pixels in - up to 3 across, 3 down - each by the rule. First the picture's rows are gathered
; (mask and ink ORed) for each row of squares they fall in: 2 bytes for each of 3 (rt_bm). Then, with the picture's place
; across (0-7 pixels into its first byte), each row's 16 pixels are looked at as the 3 squares they lie in.
; It does not go back into draw_car: its RET is draw_car's own.
rt_car_sq:
        pop af                  ; (the way back into draw_car)
        ld hl,rt_bm
        xor a
        ld b,6
rq_z0:
        ld (hl),a
        inc l
        djnz rq_z0
        ld a,(dc_count)
        ld b,a
        ld a,(dc_row0)
        ld c,a                  ; C = the buffer line of the row in hand
        and 0xF8
        ld (rq_r0+1),a          ; (the first line of the first row of squares)
rq_acc:
        ld a,c
rq_r0:  sub 0
        rrca
        rrca
        and 6                   ; 2 x which row of squares (0-2)
        add a,rt_bm AND 255
        ld l,a
        ld h,rt_bm/256
        ld a,(de)               ; the row's left 8 pixels: mask, ink
        inc de
        or (hl)
        ld (hl),a
        ld a,(de)
        inc de
        or (hl)
        ld (hl),a
        inc l
        ld a,(de)               ; and its right 8
        inc de
        or (hl)
        ld (hl),a
        ld a,(de)
        inc de
        or (hl)
        ld (hl),a
        ld a,(dc_flip)          ; (a picture read upside down: back two rows)
        or a
        jr z,rq_fw
        ld a,e
        sub 8
        ld e,a
        jr nc,rq_fw
        dec d
rq_fw:
        inc c
        djnz rq_acc
        ld a,(wxu)              ; the picture's 16 pixels start at buffer x = wxu + 1
        inc a
        ld e,a
        and 7
        ld b,a
        ld a,0xFF               ; C = the bits of a picture byte that stay in its own square
        jr z,rq_k1
rq_k0:
        add a,a
        djnz rq_k0
rq_k1:
        ld c,a
        ld a,e
        rrca
        rrca
        rrca
        and 0x1F
        ld (rq_col0),a          ; the picture's first byte column
        ld e,a
        ld a,(dc_row0)          ; HL = the square in rt_sh of its first line and that column (- 1: byte 2 is column 1)
        rrca
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
        ld a,l
        and 0xE0
        add a,e
        dec a
        ld l,a
        ld (rq_tl),hl           ; (the 3 x 3's first square: rq_ring)
        ld a,3
        ld (rt_cnt),a
        ld de,rt_bm
rq_band:
        push de
        ld a,(de)
        ld b,a
        inc e
        ld a,(de)
        ld e,a
        ld d,b                  ; D, E = this row of squares' left and right picture bytes
        ld a,d
        and c
        jr z,rq_s1
        ld a,(rq_col0)          ; (byte 0 has no square)
        or a
        jr z,rq_s1
        push de
        call rq_cell
        pop de
rq_s1:
        inc l
        ld a,c
        cpl
        and d
        ld b,a
        ld a,e
        and c
        or b
        jr z,rq_s2
        push de
        call rq_cell
        pop de
rq_s2:
        inc l
        ld a,c
        cpl
        and e
        call nz,rq_cell
        dec l
        dec l
        ld de,32
        add hl,de
        pop de
        inc e
        inc e
        ld a,(rt_cnt)
        dec a
        ld (rt_cnt),a
        jr nz,rq_band
        ret
; RQ_CELL (HL = a square in rt_sh, rt_ink = the colour): the rule for one square. First the square is brought into the
; back buffer if it is not there: cleared if nothing in it showed, made up (rt_sq_buf) if rt_class left it for rt_show.
; Keeps HL, C.
rq_cell:
        ld a,(hl)
        add a,a
        jr nc,rq_inb            ; in the buffer already (another car has it, or the arrow)
        jp p,rq_hid             ; nothing in it shows
        call rt_sq_buf
        ld a,(hl)
        add a,a
rq_inb:
        cp RT_EDGE*2
        jr z,rq_amb
        and 0x70                ; (its paper)
        jr z,rq_road
        jr rq_gset              ; a car on the grass has it: that car's pixels stay
rq_hid:
        push af
        call rq_clr
        pop af
        jr z,rq_road            ; (it was plain road)
rq_gset:                        ; all grass: the car's colour on green
        ld a,(rt_ink)
        or 0x20
        ld (hl),a
        ret
rq_grass_c:                     ; all grass by its pixels: nothing but the car in it
        call rq_clr
        jr rq_gset
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
rq_clr:                         ; the square at HL in rt_sh: its 8 lines in the buffer cleared
        call rt_bufsq
        xor a
        rept 7
        ld (de),a
        inc d
        endm
        ld (de),a
        ret

; RQ_RING (a car that gets its rim): the rim's black pixels may fall in a square the car itself has no pixel in. So every
; square within one of the car's 3 x 3 that rt_class left for rt_show is made up in the buffer first, where the rim is cut.
rq_ring:
        ld hl,(rq_tl)
        inc l                   ; (the 3 x 3's middle column: always a real column of its row)
        ld de,0x10000-32
        add hl,de               ; from the row above
        ld b,5
rr_row:
        push bc
        push hl
        ld de,0x10000-(RT_SH+32)
        add hl,de
        jr nc,rr_nx             ; above the window
        ld de,0x10000-(WIN_H/8)*32
        add hl,de
        jr c,rr_nx              ; below it
        pop hl
        push hl
        dec l
        dec l
        ld b,5
rr_sq:
        ld a,l
        and 31
        jr z,rr_n1              ; left of the window
        cp WIN_W+1
        jr nc,rr_n1             ; right of it
        ld a,(hl)
        add a,a
        jr nc,rr_n1             ; in the buffer already
        call m,rt_sq_buf        ; (not if nothing in it shows)
rr_n1:
        inc l
        djnz rr_sq
rr_nx:
        pop hl
        ld de,32
        add hl,de
        pop bc
        djnz rr_row
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

rq_col0:  db 0
rq_tl:    dw 0                  ; rt_car_sq: the first of the car's 3 x 3 squares in rt_sh
rt_bp:    dw 0                  ; rt_show: where it is in rt_b
rt_c0:    db 0                  ; the first tile column in view
rt_odd:   db 0                  ; ... 1 if that is odd
rt_v:     db 0xFF               ; camy AND 7 as rt_sq's entries were last set for (0xFF: not yet)
rt_cnt:   db 0
rt_ink:   db 0                  ; the colour of the car being drawn
rt_probe: db 0                  ; 1: draw_car goes to rt_car_sq once it knows where the picture falls
rt_mixed: db 0                  ; 1: a grass-and-road square is under the car
; RT_B (above the colours): for each of the 20 rows of tiles in view, where the tile under screen column 0 is in the map
