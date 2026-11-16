; ARROW_DRAW: the corner arrow (Grant, 15 Nov 2026: "a couple of rows in front of my car, a flashing arrow
; pointing either diagonally right or sharp right to indicate turns. A long straight stretch gets an early
; flashing straight in the direction of the straight"). What it shows comes from arrow_tab, a byte for the
; waypoint your car is heading for (tools/make_world.py works them out from the centre line: 0 none, else
; kind * 8 + direction). It is one of eight pictures (tools/make_arrows.py), masked, at a fixed spot of the
; window (below). On for two pictures, off for two: about
; three flashes a second. Into the buffer after the cars and before the gauge, the spoons, the bubble and
; the plate, so it is never over them; the map's box is not copied from the buffer at all. Nothing before
; green or once you have finished.
; WHERE AND HOW BIG (Grant, 16 Nov 2026: "lets try on the arrow that it is just above the pitstop messages, and
; slightly larger"): a field of 24 x 15 pixels - the arrow in it is 15 long and 13 across (it was 11 x 9) -
; over the crew chief's bubble, whether he is talking or not: window bytes 10-12 (pixels 80-103; the bubble is
; 48-127, its middle 88, its words' middle 96) and lines 111-125 (the bubble's top is line 128: the arrow's foot
; is 2 or 3 above it). On a byte boundary, so it needs no shifting: five pictures are kept (ARROW_F: up,
; up-right, right, up-left, left; a page each of the buffer's unused strips; 6 bytes a row - keep, ink for each
; of the 3 bytes) and the three that point down are drawn from the last row back. (It was at (96, 52), above the
; window's middle, on 15 Nov; before that 32 pixels ahead of your car.)
ARROW_ROWS equ 15
ARROW_W equ 24
ARROW_COL equ 10                ; the window's byte column of its first byte
ARROW_TOP equ 111               ; the window's line of its first row
ARROW_X equ ARROW_COL*8+ARROW_W/2       ; its middle, in window pixels: (92, 118)
ARROW_Y equ ARROW_TOP+ARROW_ROWS/2
ARROW_BR equ BUF_TOP+ARROW_TOP  ; ... and in the back buffer: the row, and the address of its first byte
ARROW_BUF equ BUF + (ARROW_BR AND 0xC0)*32 + (ARROW_BR AND 7)*256 + (ARROW_BR AND 0x38)*4 + 2 + ARROW_COL
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
        and 7                   ; the direction: which picture, and whether from the last row back (bit 3)
        ld e,a
        ld d,0
        ld hl,aw_tab
        add hl,de
        ld a,(hl)
        ld c,d                  ; C = what to add to the picture's address after a row's 6 bytes: nothing ...
        ld e,ARROW_F AND 255
        bit 3,a
        jr z,aw_1
        ld c,256-12             ; ... or back two rows
        ld e,(ARROW_F AND 255) + 6*(ARROW_ROWS-1)
aw_1:
        and 7
        add a,ARROW_F/256
        ld d,a
        if OPT_RT
        push de                 ; RACETRACK: its squares' ink yellow (racetrack.asm)
        push bc
        call rt_arrow
        pop bc
        pop de
        endif
        ld hl,ARROW_BUF
        ld b,ARROW_ROWS
aw_row:
        call aw_byte
        call aw_byte
        call aw_byte
        ld a,e
        add a,c
        ld e,a
        dec l
        dec l
        dec l
        inc h                   ; the next line down (the buffer is laid out like the screen)
        ld a,h
        and 7
        jr nz,aw_2
        ld a,l
        add a,32
        ld l,a
        jr c,aw_2
        ld a,h
        sub 8
        ld h,a
aw_2:
        djnz aw_row
        ret
aw_byte:                        ; a byte of the buffer: what is kept of it, then the ink
        ld a,(de)
        inc e
        and (hl)
        ld (hl),a
        ld a,(de)
        inc e
        or (hl)
        ld (hl),a
        inc l
        ret
aw_tab: db 0, 1, 2, 1+8, 0+8, 3+8, 4, 3     ; up, up-right, right, down-right, down, down-left, left, up-left
