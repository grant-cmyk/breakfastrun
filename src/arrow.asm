; ARROW_DRAW: the corner arrow (Grant, 15 Nov 2026: "a couple of rows in front of my car, a flashing arrow
; pointing either diagonally right or sharp right to indicate turns. A long straight stretch gets an early
; flashing straight in the direction of the straight"). What it shows comes from arrow_tab, a byte for the
; waypoint your car is heading for (tools/make_world.py works them out from the centre line: 0 none, else
; kind * 8 + direction). It is one of eight frames in the cars' format (tools/make_arrows.py), drawn by
; draw_car's own loop, masked, its middle 32 pixels ahead of your car's middle along its heading
; (thrust_tab's quarter-pixel push for the heading, halved). On for two pictures, off for two: about
; three flashes a second. Into the buffer after the cars and before the gauge, the spoons, the bubble and
; the plate, so it is never over them; the map's box is not copied from the buffer at all. Nothing before
; green or once you have finished.
ARROW_ROWS equ 11
arrow_draw:
        ld a,(renders)
        and 2
        ret z
        ld a,(race_on)
        or a
        ret z
        ld a,(you_done)
        or a
        ret nz
        ld a,(cars+C_WP)
        add a,arrow_tab AND 255 ; (the table is on one page: checked at the end of the file)
        ld l,a
        ld h,arrow_tab/256
        ld a,(hl)
        or a
        ret z
        and 7                   ; the frame: ARROW_F + 0x100 * (direction / 2), + 44 for an odd one
        rra
        ld e,ARROW_F AND 255
        jr nc,ad_1
        ld e,(ARROW_F AND 255) + ARROW_ROWS*4
ad_1:
        add a,ARROW_F/256
        ld d,a
        ld a,(cars+C_ANG)       ; where: thrust_tab's entry for the heading (4 bytes each: dx, dy as words - the
        and 0x3C                ; low bytes are -64..64)
        add a,thrust_tab AND 255
        ld l,a
        ld h,thrust_tab/256
        ld b,(hl)
        inc l
        inc l
        ld c,(hl)
        sra b
        sra c
        ld a,(cars+C_X)         ; (your car is in the window: a byte holds its place there)
        ld hl,camx
        sub (hl)
        add a,b
        add a,CAR_U
        cp WIN_W*8+14
        ret nc
        ld (wxu),a
        ld a,(cars+C_Y)
        ld hl,camy
        sub (hl)
        add a,c
        add a,BUF_TOP+3         ; the frame's first line in the buffer: its middle, line 5, is the spot
        ld hl,dc_count
        ld (hl),ARROW_ROWS
        jp dc_top               ; (draw_car: cut off at the window's last line, and drawn)
