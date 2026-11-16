; =====================================================================
; ROADWHITE - A TRIAL (Grant, 16 Nov 2026: "Try E as a trial tape. Is it possible to have the road
; have less busy dithering - or no dithering?"). Option E of docs/design/road_edge_options.png:
; the ROAD is shown on WHITE paper, the table stays cyan, the ink stays blue everywhere.
; Only in builds made with ROADW=1 or ROADW=2 (build.sh): OPT_ROADW 0 leaves the game as it was.
;
; It is done with the screen's COLOUR SQUARES. Each 8 x 8 square of the play window is white if what
; is under it is mostly road, cyan if not. The road is known from the surface map the cars' grip
; uses (one bit for each 8 x 8 tile of the world). The window scrolls a pixel at a time and colour
; cannot: so the squares take the tiles the view is NEAREST to (the camera's place + 4, over 8). The
; colour's edge is then never more than 4 pixels from the road's true edge - half a square - and
; it steps a whole square as the view passes the half-way point. (Rounding down instead would let
; it stray up to 7 pixels, always to the same side.)
;
;   rw_masks  after the cloth is filled: when the view has moved on to other tiles, the window's
;             19 rows of 24 squares are worked out again - 3 bytes a row (rw_m), a bit a square,
;             1 = table. (ROADW=2: then rw_plain takes the cloth's dots off the road squares.)
;   rw_attrs  straight after the picture has been copied to the screen: every 8 squares whose
;             byte has changed (rw_masks marks them) get their colours written. On a straight almost
;             nothing changes, and nothing is written.
;
; WHY AFTER THE COPY: the copy already runs a little behind the TV's beam at the foot of the
; window; anything done before it would make that worse. So the colours of a new picture arrive one
; TV frame (1/50 s) after its pixels - a square that changes does so once, cleanly, a moment late.
;
; OTHER THINGS IN THE WINDOW. The mini-map, the corner arrow, the place plate, the breakfast things
; and the O's are pixels only: they keep their blue ink on whichever paper is under them. Some
; squares have colours of their own: the start lights (black boxes), the crew chief's white bubble,
; the damage gauge (magenta) and the spoons (red). Rows that may hold those are written the careful
; way (rw_safe): only a square whose paper is cyan or white, and not bright, has its paper changed,
; and its ink is left alone - so the gauge and the spoons stand on the road's white too, and the
; lights and the bubble are not touched. rw_state watches for them coming and going. Nothing
; outside the window is written.
; =====================================================================
RW_ROWS equ WIN_H/8             ; the window's rows of squares (19)
RW_AT   equ 0x5800 + (WIN_Y/8)*32 + WIN_COL     ; its first square's colour on the screen

; RW_NEW: a new race. win_cells has just made every square of the window cyan.
rw_new:
        ld hl,rw_m              ; "all table" is what is up, and no row is waiting
        ld b,RW_ROWS
rn_1:
        ld (hl),0xFF
        inc hl
        ld (hl),0xFF
        inc hl
        ld (hl),0xFF
        inc hl
        ld (hl),0
        inc hl
        djnz rn_1
        ld hl,0xFFFF            ; and the squares are to be worked out afresh
        ld (rw_org),hl
        ld a,h
        ld (rw_sig),a
        ret

; RW_MASKS: the window's squares for this picture's camera, into rw_m; each 8 squares that are
; not as they were are marked, for rw_attrs.
rw_masks:
        ld hl,(camx)            ; E = the tile nearest the window's left edge
        call rm_near
        ld e,l
        ld hl,(camy)            ; D = ... and its top
        call rm_near
        ld d,l
        ld hl,(rw_org)          ; the same tiles as last picture: rw_m stands
        or a
        sbc hl,de
        if OPT_ROADW = 2
        jp z,rw_plain
        else
        ret z
        endif
        ld (rw_org),de
        ld l,d                  ; the surface map: 9 bytes a row, a bit a tile, the leftmost on the left
        ld h,0
        ld b,h
        ld c,l
        add hl,hl
        add hl,hl
        add hl,hl
        add hl,bc
        ld a,e
        rrca
        rrca
        rrca
        and 0x1F
        ld c,a
        add hl,bc
        ld bc,surface_map
        add hl,bc
        ld b,h
        ld c,l                  ; BC = the byte that holds the first tile's bit
        ld a,e                  ; the bits are moved left by the tile's place in its byte, with the
        and 7                   ; shift tables the cars are drawn with (make_tables):
        add a,a                 ; page H: b << s, page H-1: b >> (8-s), the next byte's part
        add a,TAB_HI+1
        ld h,a
        ld de,rw_m
rm_row:
        push de
        pop ix                  ; IX = the row's 4 bytes
        ld a,(bc)
        ld l,a
        ld a,(hl)
        ex af,af'
        inc bc
        ld a,(bc)
        ld l,a
        dec h
        ex af,af'
        or (hl)
        inc h
        ex de,hl
        cp (hl)                 ; as it was?
        jr z,$+11
        ld (hl),a
        ld a,h                  ; no: its 8 squares are to be written
        ld (rw_dirty),a
        set 4,(ix+3)
        inc hl
        ex de,hl
        ld a,(hl)
        ex af,af'
        inc bc
        ld a,(bc)
        ld l,a
        dec h
        ex af,af'
        or (hl)
        inc h
        ex de,hl
        cp (hl)                 ; as it was?
        jr z,$+11
        ld (hl),a
        ld a,h                  ; no: its 8 squares are to be written
        ld (rw_dirty),a
        set 5,(ix+3)
        inc hl
        ex de,hl
        ld a,(hl)
        ex af,af'
        inc bc
        ld a,(bc)
        ld l,a
        dec h
        ex af,af'
        or (hl)
        inc h
        ex de,hl
        cp (hl)                 ; as it was?
        jr z,$+11
        ld (hl),a
        ld a,h                  ; no: its 8 squares are to be written
        ld (rw_dirty),a
        set 6,(ix+3)
        inc hl
        ex de,hl
        inc de
        ld a,c                  ; the map's next row (9 bytes on; 3 are done)
        add a,6
        ld c,a
        jr nc,rm_1
        inc b
rm_1:
        ld a,e
        cp (rw_m+RW_ROWS*4) AND 255
        jr nz,rm_row
        if OPT_ROADW = 2
        jp rw_plain
        else
        ret
        endif
rm_near:                        ; HL = (HL + 4) / 8
        ld bc,4
        add hl,bc
        srl h
        rr l
        srl h
        rr l
        srl h
        rr l
        ret

; RW_ATTRS: the colours of the squares that are marked, to the screen.
rw_attrs:
        call rw_state
        ld hl,rw_dirty          ; nothing has changed since the last picture
        ld a,(hl)
        or a
        ret z
        ld (hl),0
        ld hl,rw_m+3
        ld de,4
        ld b,RW_ROWS
ra_row:
        ld a,(hl)
        and 0x70
        jr nz,ra_w
ra_next:
        add hl,de
        djnz ra_row
        ret
ra_w:
        push hl
        push bc
        ld a,(hl)               ; which of its three bytes (bits 4-6), and the row's kind (bits 0-1)
        ld ixl,a
        and 3
        ld (hl),a
        dec hl
        ld a,(hl)
        dec hl
        ld e,(hl)
        dec hl
        ld d,(hl)               ; D, E, A = the three bytes
        push af
        ld a,RW_ROWS            ; HL = the row's first square on the screen
        sub b
        rrca
        rrca
        rrca
        ld c,a
        and 3
        add a,RW_AT/256
        ld h,a
        ld a,c
        and 0xE0
        add a,RW_AT AND 255
        ld l,a
        jr nc,ra_1
        inc h
ra_1:
        ld bc,0x1039            ; (B: the bit that is cyan paper and not white; C: blue on white)
        ld a,ixl                ; the kind's bit 0: squares 0-15 the careful way
        bit 4,a
        call ra_put
        ld d,e
        ld a,ixl
        bit 5,a
        call ra_put
        pop af
        ld d,a
        ld a,ixl                ; the kind's bit 1: squares 16-23 the careful way
        rra
        bit 5,a
        call ra_put
        pop bc
        pop hl
        ld de,4
        jr ra_next
ra_put:                         ; 8 squares from HL by D - if they have changed (NZ); A's bit 0: the careful way
        jr nz,ra_p1
        ld a,l
        add a,8
        ld l,a
        ret
ra_p1:
        rra
        jr c,rw_safe

; RW_FAST: 8 squares from HL, by D's bits from the left - 1: the table's blue on cyan, 0: the
; road's blue on white. (B = 0x10, C = 0x39.)
rw_fast:
        ld a,d
        inc a
        jr z,rf_table           ; all 8 the table
        dec a
        jr z,rf_road            ; all 8 the road
        rept 8
        rlc d
        sbc a,a
        and b
        xor c
        ld (hl),a
        inc l
        endm
        ret
rf_table:
        ld a,b
rf_road:
        xor c                   ; (A was 0: the road's 0x39; or B: the table's 0x29)
        rept 8
        ld (hl),a
        inc l
        endm
        ret

; RW_SAFE: the same, the careful way: only a square whose paper is cyan or white (and not bright,
; not flashing) is touched, and only its paper - its ink stays. (B = 0x10.)
rw_safe:
        scf                     ; (a 1 follows the 8 bits through D: D is 0 when they are done)
        rl d
rs_l:
        jr c,rs_t
        ld a,(hl)
        or b
        and 0xF8
        cp 0x38
        jr nz,rs_n
        set 4,(hl)              ; the road: white paper
        jr rs_n
rs_t:
        ld a,(hl)
        or b
        and 0xF8
        cp 0x38
        jr nz,rs_n
        res 4,(hl)              ; the table: cyan paper
rs_n:
        inc l
        sla d
        jr nz,rs_l
        ret

; RW_STATE: are the start lights up, is the crew chief's bubble up, what spoons are held? When any
; of that changes, the rows they are in are marked: which are written the careful way, and to be
; written afresh at once (their squares may just have been given back the window's cyan).
rw_state:
        ld a,(msg_timer)
        or a
        jr z,rt_1
        ld a,2
rt_1:
        ld c,a                  ; bit 1: the bubble
        ld hl,(INV)
        ld a,(INV+2)
        add a,l
        add a,h
        add a,a
        add a,a
        or c
        ld c,a
        ld a,(lt_on)
        or a
        jr z,rt_2
        inc c                   ; bit 0: the lights
rt_2:
        ld hl,rw_sig
        ld a,(hl)
        cp c
        ret z
        ld (hl),c
        ld a,c
        rrca
        sbc a,a
        and 3
        or 0x70                 ; (bits 4-6: all of the row is to be written)
        ld hl,rw_m+3            ; the lights: the window's rows 0-2
        ld de,4
        ld (hl),a
        add hl,de
        ld (hl),a
        add hl,de
        ld (hl),a
        ld a,c
        and 2
        jr z,rt_3
        ld a,3
rt_3:
        or 0x70
        ld hl,rw_m+(RW_ROWS-3)*4+3      ; the bubble: the last row but one and the row above it; the gauge
        ld (hl),a                       ; and the spoons: the last two rows' last 8 squares, always
        add hl,de
        or 2
        ld (hl),a
        add hl,de
        ld (hl),0x72
        ld (rw_dirty),a
        ret

        if OPT_ROADW = 2
; RW_PLAIN (ROADW=2: no dots on the road): the cloth's dots are taken off the very squares that are
; shown white, straight after cloth_fill and before anything is drawn on the cloth. A square is one
; byte of 8 lines of the back buffer; the cloth's odd lines are blank already, so 4 bytes a square
; are cleared - a whole byte of the map's bits at a time where all 8 squares are road.
RP_LINE macro                   ; 8 bytes of a line cleared (A = 0)
        ld (hl),a
        inc l
        ld (hl),a
        inc l
        ld (hl),a
        inc l
        ld (hl),a
        inc l
        ld (hl),a
        inc l
        ld (hl),a
        inc l
        ld (hl),a
        inc l
        ld (hl),a
        inc l
        endm
rw_plain:
        ld de,rw_m
        ld a,(camy)             ; the first dotted line of a square: the world's even lines
        and 1
        add a,BUF_HI+(BUF_TOP/64)*8
        ld b,a                  ; B = that line's page, for this row of squares
        ld h,a
        ld l,(BUF_TOP AND 0x38)*4+2
        ld ixl,RW_ROWS
rwp_row:
        call rwp_byte
        call rwp_byte
        call rwp_byte
        inc de                  ; (the row's 4th byte is its mark)
        ld a,l                  ; the next row of squares (24 bytes are done of the 32)
        add a,8
        ld l,a
        jr nc,rwp_1
        ld a,b                  ; ... in the buffer's next third
        add a,8
        ld b,a
        ld h,a
rwp_1:
        dec ixl
        jr nz,rwp_row
        ret
rwp_byte:
        ld a,(de)
        inc de
        xor 0xFF                ; 1: road
        jr nz,rwp_some
        ld a,l                  ; none of the 8
        add a,8
        ld l,a
        ret
rwp_some:
        inc a
        jr nz,rwp_mixed
        ld c,l                  ; all 8 (A = 0): line by line
        RP_LINE
        ld l,c
        inc h
        inc h
        RP_LINE
        ld l,c
        inc h
        inc h
        RP_LINE
        ld l,c
        inc h
        inc h
        RP_LINE
        ld h,b
        ret
rwp_mixed:
        dec a
        ld c,a
        xor a
        rept 8                  ; square by square: its 4 dotted lines, down
        sla c
        jr nc,$+13
        ld (hl),a
        inc h
        inc h
        ld (hl),a
        inc h
        inc h
        ld (hl),a
        inc h
        inc h
        ld (hl),a
        ld h,b
        inc l
        endm
        ret
        endif

rw_org:   dw 0xFFFF             ; the tiles rw_m was worked out for (low: across, high: down)
rw_dirty: db 0                  ; 1: rw_m or the marked rows have changed since the colours were written
rw_sig:   db 0xFF               ; the lights, the bubble and the spoons as rw_state last saw them
rw_m:     defs RW_ROWS*4,0xFF   ; the squares, 4 bytes a row: 3 of bits (1: table), then bits 4, 5, 6 - the 1st, 2nd,
                                ; 3rd of them has changed, its 8 squares' colours are to be written;
                                ; bit 0 - the row's squares 0-15 the careful way, bit 1 - 16-23
