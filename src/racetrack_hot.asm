; =====================================================================
; RACETRACK - the parts that run for every square of every picture (rt_class, rt_sq, rt_show, rt_car). They sit in
; the program, above 0x8000, NOT with the rest of racetrack.asm in the room under 0x8000: the Spectrum holds the
; processor up whenever it reads memory below 0x8000 while the TV picture is being drawn, and code there runs about
; a quarter slower. (17 Nov 2026: this move alone was worth - see PROJECT-LOG. Things that run rarely - the driver
; strip, the title's car, the place plate, the faces, the small letters - went down there in exchange: racer.asm.)
; racetrack.asm has the description, the numbers and the parts that run once a picture or less.
; =====================================================================
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
        or a
        ld a,0xD9               ; (EXX: sq_bot's first instruction)
        jr nz,rcl_fold
        ld a,0xC9               ; none below the fold (one picture in eight): rt_sq ends at the fold - a RET there. (The lower
rcl_fold:                       ; pair's pointer is then not moved on: nothing of those tiles is used in such a picture.)
        ld (sq_bot),a
        ld a,c
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
        ld a,OPT_RTROWS+1
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
        ld a,OPT_RTROWS
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
        if OPT_RTROWS < WIN_H/8 ; A SMALLER PLAY WINDOW (RT_ROWS): the window's rows below the ones that scroll are a black band.
        ld b,WIN_H/8-OPT_RTROWS ; Each picture its squares start as plain black (nothing in them shows); the mini-map, the mug,
rcl_band:                       ; the spoons and the crew chief's bubble then mark their own, as ever (rt_hud). The cars never
        ld a,RT_PLAIN           ; mark them (rq_cell), so a car goes out of sight under the band.
        rept WIN_W
        ld (hl),a
        inc l
        endm
        ld a,l
        add a,32-WIN_W
        ld l,a
        jr nc,rcl_bn
        inc h
rcl_bn:
        djnz rcl_band
        endif
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
rt_sq_in:                       ; (rt_dir comes in here, the other registers already in hand)
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
        ld (save_sp),sp         ; (it ends through copy_done, as the copy routine it stands in for does: the tests wait there)
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
        cp 0x40                 ; (0x80 to 0xBF - bit 7 alone, nothing in it shows - and only they, overflow here: one test)
        call po,rt_any          ; (bit 7 not set: it is in the buffer. Bits 7 and 6: rt_class's own, made up on the screen)
        ldi                     ; its colour, and on to the next
        endm
        ld de,32-WIN_W
        add hl,de
        ld a,(rt_cnt)
        dec a
        jp nz,sh_row
        jp copy_done
; RT_DIR: a square to make up on the screen (HL = it in rt_sh, A = its colour x 2). Keeps HL.
rt_dir:
        cp (RT_EDGE4_D*2) AND 255
        jr z,sd_4
        rrca
        and 0x3F
        ld (hl),a               ; the colour it shows in
sd_sh:  ld h,0x40               ; (patched: this row's page of the screen)
        ld a,l
        exx
        sub c
        call nz,sd_adj          ; (not the square the map's pointers are at)
        inc c
        call rt_sq_in
sd_hh:  ld h,RT_SH/256          ; (patched: this row's page of rt_sh)
        ld e,l
sd_at:  ld d,0x58               ; (patched: ... and of the screen's colours)
        ret
sd_adj:
        ld c,a                  ; that many tiles on
        ld b,0
        add hl,bc
        ex de,hl
        add hl,bc
        ex de,hl
        exx
        ld a,l
        exx
        ld c,a
        ret
sd_4:
        ld a,l
        exx
        sub c
        call nz,sd_adj
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
        ret
; RT_ANY (from rt_show, A = a square's colour): made up on the screen, or - RT_CP - its 8 lines copied from the buffer
rt_any:
        add a,a
        jr c,rt_dir
rt_cp:
        cp RT_LEAVE*2
        jr z,cp_lv
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
        ret
cp_lv:                          ; a fixed box's square that has not changed (RT_LEAVE): its pixels stay as they are on the
        ld a,(de)               ; screen, and so does its colour (DE is at it: the colour is read back, for the LDI that follows)
        ld (hl),a
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
        ld (rt_slow),a          ; (a car out of sight never gets to rt_car_sq)
        call draw_car
        xor a
        ld (rt_probe),a
        ld a,(rt_mixed)
        or a
        jr nz,rtc_rim
        ld a,(rt_slow)
        or a
        jp nz,draw_car
; RT_CAR_INK: THE SHORT CUT (17 Nov 2026) for a car alone on plain squares - nearly every car. Every square it has a
; pixel in was cleared for it a moment ago (rq_cell), so there is nothing under it to cut a hole in: only its ink is
; put in, from the rows rt_car_sq was given, without going through draw_car's working-out a second time. The buffer
; ends up exactly as draw_car would leave it (a pair of bytes is passed over when its MASK is empty, as there).
rt_car_ink:
        ld a,(wxu)
        ld c,a
        cpl                     ; the shift table: (15 - u) AND 7, as draw_car
        and 7
        add a,a
        add a,TAB_HI
        ex af,af'
        ld a,c
        and 0xF8
        ld c,a
        ld a,(dc_row0)
        ld b,a
        call buf_addr
        ex af,af'
        ld b,a
rci_rows: ld de,0               ; (patched by rt_car_sq: the picture's rows)
        ld a,(dc_count)
rci_row:
        ex af,af'
        ld a,(de)               ; the mask: only to see if this pair of bytes is empty
        inc de
        or a
        jr z,rci_a
        ld a,(de)
        ld c,a
        ld a,(bc)               ; the ink: column k ...
        or (hl)
        ld (hl),a
        inc b
        inc l
        ld a,(bc)               ; ... and column k+1
        or (hl)
        ld (hl),a
        dec b
        dec l
rci_a:
        inc de
        inc l
        ld a,(de)
        inc de
        or a
        jr z,rci_b
        ld a,(de)
        ld c,a
        ld a,(bc)
        or (hl)
        ld (hl),a
        inc b
        inc l
        ld a,(bc)
        or (hl)
        ld (hl),a
        dec b
        dec l
rci_b:
        inc de
        dec l
        inc h                   ; the next line down (screen layout)
        ld a,h
        and 7
        jr nz,rci_s
        ld a,l
        add a,32
        ld l,a
        jr c,rci_s
        ld a,h
        sub 8
        ld h,a
rci_s:
        ld a,(dc_flip)          ; (a picture read upside down: back two rows)
        or a
        jr z,rci_f
        ld a,e
        sub 8
        ld e,a
        jr nc,rci_f
        dec d
rci_f:
        ex af,af'
        dec a
        jp nz,rci_row
        ret
rtc_rim:
        call rq_ring            ; (the squares the rim may reach: into the buffer)
        ld a,0x7E               ; "OR (HL)" becomes "LD A,(HL)" at the four places draw_car puts the ink in: mask only
        call rtc_patch
        ld a,(wxu)
        ld (rt_u),a             ; (where the car is across, before the four passes move it)
        ld l,(ix+C_X)
        ld h,(ix+C_X+1)
        push hl
        dec hl
        sub 192                 ; THE WINDOW'S EDGES (17 Nov 2026): a part of the car that is out of sight beyond an edge must
        cp 16                   ; not put its rim one pixel into view. So: one pixel left - the window's last column is kept
        ld bc,0x0100+25*8       ; as it was if the car reaches past the right edge (buffer byte 25, bit 0) ...
        call rtc_xk
        inc hl
        inc hl
        ld a,(rt_u)
        cp 15
        ld bc,0x8000+2*8        ; ... one pixel right - the first column, if it reaches past the left edge ...
        call rtc_xk
        pop hl
        ld (ix+C_X),l
        ld (ix+C_X+1),h
        ld l,(ix+C_Y)
        ld h,(ix+C_Y+1)
        push hl
        ld a,(dc_row0)
        ld c,a                  ; C = the car's first line in the buffer
        ld a,(dc_count)
        add a,c
        ld b,a                  ; B = the line after its last
        push bc
        dec hl
        cp BUF_TOP+WIN_H
        ld a,BUF_TOP+WIN_H-1    ; ... one pixel up - the window's last line, if the car runs on below it ...
        call rtc_yk
        pop bc
        inc hl
        inc hl
        ld a,c
        cp BUF_TOP
        sbc a,a
        inc a                   ; (Z: the car starts above the window)
        ld a,BUF_TOP            ; ... one pixel down - the first line, if it starts above it
        call rtc_yk
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
; RTC_XK (HL = the x for this pass; carry: the car reaches past the window's edge on that side - then BC = the bit, and
; 8 x the buffer byte, of the window's edge column): the pass, and that column's pixels on the car's lines put back after
rtc_xk:
        jr nc,rtc_x
        push hl
        ld (rk_c+1),bc
        call rk_at
rk_s:   ld a,(hl)
        ld (de),a
        call rk_next
        djnz rk_s
        pop hl
        call rtc_x
        push hl
rk_c:   ld bc,0
        ld a,b
        ld (rk_m+1),a
        call rk_at
rk_b:   ld a,(de)
        xor (hl)
rk_m:   and 0
        xor (hl)                ; (the edge's bit as it was kept, the byte's others as they are now)
        ld (hl),a
        call rk_next
        djnz rk_b
        pop hl
        ret
rk_at:
        ld a,(dc_row0)
        ld b,a
        call buf_addr
        ld a,(dc_count)
        ld b,a
        ld de,rt_keep
        ret
rk_next:
        inc de
        inc h                   ; the next line down (screen layout, as draw_car steps)
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
; RTC_YK (HL = the y for this pass; Z: the car reaches past the window's top or bottom - then A = the window's edge line
; in the buffer): the pass, and that line's three bytes under the car put back after
rtc_yk:
        jr nz,rtc_y
        push hl
        ld (rk_ln+1),a
        ld b,a
        call rk_vat
        ld de,rt_keep
        ldi
        ldi
        ldi
        pop hl
        call rtc_y
        push hl
rk_ln:  ld b,0
        call rk_vat
        ex de,hl
        ld hl,rt_keep
        ldi
        ldi
        ldi
        pop hl
        ret
rk_vat:
        ld a,(rt_u)
        and 0xF8
        ld c,a
        jp buf_addr
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
        ld (rci_rows+1),de      ; (the picture's rows: rt_car_ink draws from them)
        xor a
        ld (rt_slow),a          ; (so far a car alone on plain squares: rq_cell says if not)
        ex de,hl                ; HL = the picture's rows
        ld de,rq_gf
        ld a,(dc_flip)          ; (a picture read upside down: its rows are read last byte first, upwards)
        or a
        jr z,rq_g0
        inc hl
        inc hl
        inc hl
        ld de,rq_gb
rq_g0:
        ld (rq_gc+1),de
        ld a,(dc_count)
        ld d,a                  ; D = the picture's rows to go
        ld a,(dc_row0)
        cpl
        and 7
        inc a                   ; the first row of squares has 8 - (its first line AND 7) of them
        call rq_g1
        ld (rt_bm),bc
        ld a,8
        call rq_g1
        ld (rt_bm+2),bc
        ld a,8
        call rq_g1
        ld (rt_bm+4),bc
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
        call rq_setpg
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
        jr z,rq_s0
        push de
        call rq_cell
        pop de
        jr rq_s1
rq_s0:
        ld a,h                  ; (pixels in the margin, which is never cleared: no short cut)
        ld (rt_slow),a
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
        ld de,32                ; the next row of squares. (17 Nov 2026: the 32 is added BEFORE stepping back two squares. HL's low
        add hl,de               ; byte alone is stepped, and for a car at the window's left edge on a row of squares that starts a
        dec l                   ; page of rt_sh - rows 0, 8 and 16 - "back two" wrapped round the page and the 32 then carried into
        dec l                   ; the next one: the car's colour went into squares 8 rows lower, or into the pictures above rt_sh.)
        pop de
        inc e
        inc e
        ld a,(rt_cnt)
        dec a
        ld (rt_cnt),a
        jr nz,rq_band
        ret
; RQ_G1: up to A of the picture's rows (D = how many are left) ORed together: C = their left 8 pixels (mask and ink), B = their right 8
rq_g1:
        ld bc,0
        inc d
        dec d
        ret z
        cp d
        jr c,rq_g2
        ld a,d
rq_g2:
        ld e,a
        ld a,d
        sub e
        ld d,a
rq_gc:  jp rq_gf                ; (patched: rq_gf or rq_gb)
rq_gf:
        ld a,(hl)
        inc hl
        or (hl)
        inc hl
        or c
        ld c,a
        ld a,(hl)
        inc hl
        or (hl)
        inc hl
        or b
        ld b,a
        dec e
        jr nz,rq_gf
        ret
rq_gb:
        ld a,(hl)
        dec hl
        or (hl)
        dec hl
        or b
        ld b,a
        ld a,(hl)
        dec hl
        or (hl)
        dec hl
        or c
        ld c,a
        dec e
        jr nz,rq_gb
        ret
; RQ_SETPG (HL = a square in rt_sh): its row of squares' page of the buffer, for rq_cell - before rq_cell is called for
; any square of a row. Keeps all but A.
rq_setpg:
        ld a,h
        sub RT_SH/256
        add a,a
        add a,a
        add a,a
        add a,BUF_HI
        ld (rq_pg+1),a
        ret
; RQ_CELL (HL = a square in rt_sh, rt_ink = the colour): the rule for one square. First the square is brought into the
; back buffer if it is not there: cleared if nothing in it showed, made up (rt_sq_buf) if rt_class left it for rt_show.
; Keeps HL, C.
rq_cell:
        if OPT_RTROWS < WIN_H/8 ; (a smaller play window, RT_ROWS: a square in the band, or below it, is not the car's)
        ld a,h
        cp (RT_SH+32+OPT_RTROWS*32)/256
        jr c,rq_c0
        jr nz,rq_cs
        ld a,l
        cp (RT_SH+32+OPT_RTROWS*32) AND 255
        jr c,rq_c0
rq_cs:
        ld a,h
        ld (rt_slow),a
        ret
rq_c0:
        endif
        ld a,(hl)
        cp RT_PLAIN
        jr nz,rq_any
        ld a,h                  ; PLAIN ROAD, nothing in it showing - nearly every square a car is in: its 8 lines in the
        ex af,af'               ; buffer cleared and the car's colour on black, here and now (as rq_hid and rq_road do)
rq_pg:  ld h,BUF_HI             ; (patched by rq_band: this row of squares' page of the buffer)
        inc l
        xor a
        rept 7
        ld (hl),a
        inc h
        endm
        ld (hl),a
        dec l
        ex af,af'
        ld h,a
        ld a,(rt_ink)
        ld (hl),a
        ret
rq_any:
        add a,a
        jr nc,rq_slow           ; in the buffer already (another car has it, or the arrow)
        jp p,rq_hid             ; nothing in it shows
        call rt_sq_buf
rq_slow:
        ld a,h                  ; (not a plain square cleared for this car alone: no short cut for it - rt_car_ink)
        ld (rt_slow),a
        ld a,(hl)
        add a,a
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
        ld a,h
        sub RT_SH/256
        add a,a
        add a,a
        add a,a
        add a,BUF_HI
        ld d,a
        ld e,l
        inc e
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
        ld de,0x10000-OPT_RTROWS*32
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

; RT_PTIME (from pl_draw, the lap time's figures about to be cut afresh): which of the time's three columns of the plate
; (m: | ss | .t - bytes 1, 2, 3 of its 5) show a different character from the last time: bits 1, 2, 3 of rt_pch.
rt_ptime:
        ld hl,time_txt
        ld de,rt_pt
        ld c,0
        call rpt_1              ; m
        jr z,rpt_a
        set 1,c
rpt_a:
        inc hl                  ; (the colon)
        call rpt_1              ; s, tens
        jr z,rpt_b
        set 2,c
rpt_b:
        call rpt_1              ; s, units
        jr z,rpt_c
        set 2,c
rpt_c:
        inc hl                  ; (the point)
        call rpt_1              ; tenths
        jr z,rpt_d
        set 3,c
rpt_d:
        ld a,(rt_pch)
        or c
        ld (rt_pch),a
        ret
rpt_1:
        ld a,(de)
        cp (hl)
        ld a,(hl)
        ld (de),a
        inc hl
        inc de
        ret                     ; (Z: the same character as before)
; RT_PLATE (pl_draw's last step): the plate from pl_bmp into the buffer - only as much of it as has changed since it last
; went to the screen. All of it (rt_fx bit 3: a new race, the start lights just gone, your place or lap changed); or the
; squares of the time's columns that changed (their two rows of squares); or nothing - rt_hud has marked all 15 squares
; RT_LEAVE, and the ones that are to go to the screen are made RT_ROAD (white on black, in the buffer) here.
RPL_SQ  equ RT_SH+(WIN_Y/8)*32+WIN_COL+19       ; the plate's first square: the window's row 0, column 19
rt_plate:
        ld hl,rt_fx
        bit 3,(hl)
        jr nz,rpl_all
        ld a,(rt_pch)
        or a
        ret z
        rra
        ld c,a
        ld hl,RPL_SQ+32
        ld b,3
rpl_1:
        inc l
        srl c
        jr nc,rpl_2
        ld (hl),RT_ROAD         ; this column's square in the plate's second row, and the one under it
        ld a,l
        add a,32
        ld l,a
        ld (hl),RT_ROAD
        sub 32
        ld l,a
rpl_2:
        djnz rpl_1
        xor a
        ld (rt_pch),a
        ld hl,pl_bmp+6*PL_W     ; the plate's rows 6-17: buffer rows 16-27 (the second and third rows of squares)
        ld de,BUF+2*32+21
        ld b,PL_H-6
        call pd_4
        jr rpl_w
rpl_all:
        res 3,(hl)
        xor a
        ld (rt_pch),a
        ld hl,RPL_SQ
        ld bc,0x0305
        ld a,RT_ROAD
        call rt_attrs
        ld hl,BUF+1*32+21       ; the 2 lines above the plate's picture (buffer rows 8-9)
        ld de,0
        ld b,2
        call rw_lines
        ld hl,pl_bmp
        ld de,PL_B
        ld b,PL_H
        call pd_4
rpl_w:
        ld hl,BUF+3*32+4*256+21 ; ... and the 4 below it (rows 28-31)
        ld de,0
        ld b,4
        jp rw_lines
        if ((RPL_SQ+32) / 256) - ((RPL_SQ+32+32+5) / 256)
        .error the plate's second and third rows of squares must be on one page of rt_sh
        endif
rt_fx:    db 0xFF               ; the fixed boxes that must go to the screen afresh: bit 0 the mini-map (map_update sets
                                ; it), bit 1 the mug (hud_pre), bit 3 all of the plate; rt_new sets them all
rt_pch:   db 0                  ; the plate's time: its columns that have changed (rt_ptime)
rt_pt:    db 0,0,0,0            ; ... and the four figures it shows
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
rt_slow:  db 0                  ; not 0: the car is not alone on plain squares cleared for it (no short cut: rt_car_ink)
rt_u:     db 0                  ; rt_car: the car's place across (wxu) before the rim's passes
rt_keep:  defs 28               ; rt_car: the pixels of the window's edge kept through a pass of the rim (a byte a line of the car, 27 at most)
; RT_B (above the colours): for each of the 20 rows of tiles in view, where the tile under screen column 0 is in the map
