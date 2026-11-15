; ARROW_DRAW: the corner arrow (Grant, 15 Nov 2026: "a couple of rows in front of my car, a flashing arrow
; pointing either diagonally right or sharp right to indicate turns. A long straight stretch gets an early
; flashing straight in the direction of the straight"). What it shows comes from arrow_tab, a byte for the
; waypoint your car is heading for (tools/make_world.py works them out from the centre line: 0 none, else
; kind * 8 + direction). It is one of eight frames in the cars' format (tools/make_arrows.py), drawn by
; draw_car's own loop, masked, at a fixed spot of the window (ARROW_X, ARROW_Y below). On for two pictures, off for two: about
; three flashes a second. Into the buffer after the cars and before the gauge, the spoons, the bubble and
; the plate, so it is never over them; the map's box is not copied from the buffer at all. Nothing before
; green or once you have finished.
ARROW_ROWS equ 11
; WHERE IT SHOWS (Grant, 15 Nov 2026: "could you try that it always shows in the middle of the screen - so it
; doesn't jump around"): one fixed spot. The window's exact middle is (96, 76) - but your car sits there at rest
; and within 20 pixels of it at speed, so the arrow would lie on the car. It is three character rows above the
; middle instead; ARROW_Y equ 76 puts it dead centre (docs/design/arrows/v2_t1_centre.png shows that).
ARROW_X equ 96                  ; its middle, in window pixels across (0-191)
ARROW_Y equ 52                  ; ... and down (0-151)
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
        ld a,ARROW_X-8+CAR_U    ; where: always the same spot (ARROW_X, ARROW_Y: its middle, in window pixels)
        ld (wxu),a
        ld a,ARROW_Y-5+BUF_TOP  ; the frame's first line in the buffer
        ld hl,dc_count
        ld (hl),ARROW_ROWS
        jp dc_top               ; (draw_car: cut off at the window's last line, and drawn)
