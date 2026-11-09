; =====================================================================
; BREAKFAST RUN - STAGE 1: one car, one track
; ZX Spectrum 48K, assembled with pasmo.
;
; Keys:  O = steer left   P = steer right   Q = accelerate   A = brake/reverse
;
; What this stage teaches:
;   - drawing a sprite at ANY pixel position (shifting bits across bytes)
;   - XOR drawing: draw once = car appears, draw again = car vanishes
;   - "fixed point" maths: speed in 1/256ths of a pixel, so the car can
;     move 1.75 pixels a frame even though the screen only has whole pixels
;   - momentum: you push the car, friction slows it - that gives the drift
;   - reading the colour under the car (attribute) to know road from grass
; =====================================================================

        org 32768

start:
        xor a
        out (254),a             ; BORDER 0 while we set up

        ld hl,0x4000            ; CLS of the pixels: fill 6144 bytes with 0
        ld de,0x4001
        ld bc,6143
        ld (hl),0
        ldir

        ld hl,track_attrs       ; paint the track: copy 768 colour bytes
        ld de,0x5800            ; straight into attribute memory
        ld bc,768
        ldir

        ld a,4
        out (254),a             ; BORDER 4 (green, like the grass)

        ld hl,100*256           ; car starts on the bottom straight
        ld (xpos),hl            ; x = 100.0 pixels
        ld hl,148*256
        ld (ypos),hl            ; y = 148.0 pixels
        ld hl,0
        ld (vx),hl              ; not moving
        ld (vy),hl
        ld a,16                 ; angle 16 of 64 = facing right
        ld (angle),a

        call draw_new           ; first drawing of the car

; ---------------------------------------------------------------------
; MAIN LOOP - the BASIC equivalent is:
;   10 GO SUB physics: PAUSE 1: (rub out old car): (draw new car): GO TO 10
; ---------------------------------------------------------------------
main:
        call physics            ; work out where the car is now
        halt                    ; wait for the next TV frame (1/50 s)
        ld a,(oldx)             ; rub out the car where it was...
        ld c,a
        ld a,(oldy)
        ld b,a
        ld a,(oldframe)
        call sprite_xor
        call draw_new           ; ...and draw it where it is
        jr main

; draw the car at its current position and remember where we drew it
draw_new:
        ld a,(xpos+1)           ; high byte = whole pixels
        ld c,a
        ld (oldx),a
        ld a,(ypos+1)
        ld b,a
        ld (oldy),a
        ld a,(angle)            ; 64 angles -> 16 pictures: divide by 4
        rrca
        rrca
        and 15
        ld (oldframe),a
        jp sprite_xor

; ---------------------------------------------------------------------
; PHYSICS: keys -> steering and thrust -> friction -> move -> walls
; ---------------------------------------------------------------------
physics:
        ld a,0xDF               ; keyboard half-row Y U I O P
        in a,(0xFE)             ; a key that is DOWN reads as bit = 0
        ld e,a
        bit 1,e                 ; O ?
        jr nz,no_left
        ld a,(angle)
        dec a
        and 63                  ; wrap 0..63, like angle = (angle-1) MOD 64
        ld (angle),a
no_left:
        bit 0,e                 ; P ?
        jr nz,no_right
        ld a,(angle)
        inc a
        and 63
        ld (angle),a
no_right:
        ; look up the push for the way the car faces: thrust_tab + frame*4
        ld a,(angle)
        rrca
        rrca
        and 15
        add a,a
        add a,a
        ld l,a
        ld h,0
        ld de,thrust_tab
        add hl,de
        ld e,(hl)               ; DE = push along x
        inc hl
        ld d,(hl)
        inc hl
        ld c,(hl)               ; BC = push along y
        inc hl
        ld b,(hl)

        ld a,0xFB               ; half-row Q W E R T
        in a,(0xFE)
        bit 0,a                 ; Q = accelerate
        jr nz,no_acc
        ld hl,(vx)
        add hl,de               ; vx = vx + push
        ld (vx),hl
        ld hl,(vy)
        add hl,bc
        ld (vy),hl
no_acc:
        ld a,0xFD               ; half-row A S D F G
        in a,(0xFE)
        bit 0,a                 ; A = brake / reverse (half strength)
        jr nz,no_rev
        sra d                   ; halve the push (sra keeps the sign)
        rr e
        sra b
        rr c
        ld hl,(vx)
        or a                    ; clear carry before sbc
        sbc hl,de
        ld (vx),hl
        ld hl,(vy)
        or a
        sbc hl,bc
        ld (vy),hl
no_rev:
        call surface            ; A = 3 on road, 2 on grass
        ld (fshift),a
        ld hl,(vx)
        call friction
        ld (vx),hl
        ld hl,(vy)
        call friction
        ld (vy),hl

        ; ---- move along x, stop at the screen edge ----
        ld hl,(xpos)
        ld de,(vx)
        add hl,de
        ld a,h
        cp 240                  ; whole pixel 0..239 is allowed
        jr c,x_ok
        bit 7,d                 ; were we moving left (negative)?
        ld hl,0
        jr nz,x_hit             ; yes: we went below 0, sit at 0
        ld hl,239*256           ; no: we went past the right edge
x_hit:
        ld de,0
        ld (vx),de              ; hitting the edge kills the speed
x_ok:
        ld (xpos),hl

        ; ---- move along y, same idea, 0..175 ----
        ld hl,(ypos)
        ld de,(vy)
        add hl,de
        ld a,h
        cp 176
        jr c,y_ok
        bit 7,d
        ld hl,0
        jr nz,y_hit
        ld hl,175*256
y_hit:
        ld de,0
        ld (vy),de
y_ok:
        ld (ypos),hl
        ret

; friction: HL = HL - HL/2^fshift, and tiny speeds become exactly 0
friction:
        ld d,h
        ld e,l
        ld a,(fshift)
        ld b,a
fr_div:
        sra d                   ; DE = DE / 2 (sign kept)
        rr e
        djnz fr_div
        or a
        sbc hl,de
        ld a,h                  ; dead zone: -7..+7 (1/256ths) -> 0
        or a
        jr nz,fr_neg
        ld a,l
        cp 8
        ret nc
        ld hl,0
        ret
fr_neg:
        inc a                   ; H = 0xFF means a small negative number
        ret nz
        ld a,l
        cp 0xF9
        ret c
        ld hl,0
        ret

; surface: read the colour of the cell under the middle of the car
; attribute address = 0x5800 + (row * 32) + column   (like ATTR(row,col))
surface:
        ld a,(ypos+1)
        add a,8                 ; middle of the 16x16 car
        and 0xF8                ; (y DIV 8) * 8 ...
        ld l,a
        ld h,0
        add hl,hl               ; ... * 4  = row * 32
        add hl,hl
        ld a,(xpos+1)
        add a,8
        rrca
        rrca
        rrca
        and 31                  ; column = x DIV 8
        ld e,a
        ld d,0
        add hl,de
        ld de,0x5800
        add hl,de
        ld a,(hl)
        cp GRASS
        ld a,3                  ; road: lose 1/8 of speed each frame
        ret nz
        ld a,2                  ; grass: lose 1/4 - much slower
        ret

; ---------------------------------------------------------------------
; sprite_xor: A = picture 0..15, C = x pixel, B = y pixel
; Draws (or rubs out - XOR does both) a 16x16 picture at any pixel.
; ---------------------------------------------------------------------
sprite_xor:
        ld l,a                  ; DE = sprites + picture * 32
        ld h,0
        add hl,hl
        add hl,hl
        add hl,hl
        add hl,hl
        add hl,hl
        ld de,sprites
        add hl,de
        ex de,hl
        ld a,c
        and 7                   ; how far into its byte the car starts
        ld (shift),a
        ld a,16
        ld (rows),a
spr_row:
        push bc                 ; keep y, x
        call scr_addr           ; HL = screen byte for (x, y)
        ld a,(de)               ; the row's two bytes...
        inc de
        ld b,a
        ld a,(de)
        inc de
        ld c,a
        push de
        ld e,0                  ; ...spill into a third byte when shifted
        ld a,(shift)
        or a
        jr z,spr_put
        ld d,a
spr_sh:
        srl b                   ; slide all 24 bits one pixel right
        rr c
        rr e
        dec d
        jr nz,spr_sh
spr_put:
        ld a,(hl)
        xor b
        ld (hl),a
        inc l
        ld a,(hl)
        xor c
        ld (hl),a
        inc l
        ld a,(hl)
        xor e
        ld (hl),a
        pop de
        pop bc
        inc b                   ; next pixel row down
        ld a,(rows)
        dec a
        ld (rows),a
        jr nz,spr_row
        ret

; scr_addr: B = y (0..191), C = x (0..255)  ->  HL = screen address
; The Spectrum screen is stored in a shuffled order; this unshuffles it:
;   HL = 010 yy yyy  yyy xxxxx  with the y bits in the order 7-6, 2-0, 5-3
scr_addr:
        ld a,b
        and 7                   ; y bits 0-2 -> H bits 0-2
        or 0x40
        ld h,a
        ld a,b
        rrca
        rrca
        rrca
        and 0x18                ; y bits 6-7 -> H bits 3-4
        or h
        ld h,a
        ld a,b
        rlca
        rlca
        and 0xE0                ; y bits 3-5 -> L bits 5-7
        ld l,a
        ld a,c
        rrca
        rrca
        rrca
        and 0x1F                ; x DIV 8 -> L bits 0-4
        or l
        ld l,a
        ret

; ---------------------------------------------------------------------
; variables (the assembler version of LET)
; ---------------------------------------------------------------------
xpos:     dw 0                  ; 8.8 fixed point: high byte = pixel
ypos:     dw 0
vx:       dw 0                  ; speed in 1/256ths of a pixel per frame
vy:       dw 0
angle:    db 0                  ; 0..63, 0 = up, clockwise
oldx:     db 0
oldy:     db 0
oldframe: db 0
fshift:   db 3
shift:    db 0
rows:     db 0

        include "data.asm"

        end start
