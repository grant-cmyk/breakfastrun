; =====================================================================
; BREAKFAST RUN - STAGE 2: the track scrolls, the car stays in the middle
; ZX Spectrum 48K, assembled with pasmo.
;
; Keys:  O = steer left   P = steer right   Q = accelerate   A = brake/reverse
;
; How the scrolling works (the big idea of this stage):
;   1. The world is a MAP of 8x8 TILES (64 x 48 of them = 512 x 384 pixels),
;      far bigger than the screen. A "camera" says which part we look at.
;   2. Every frame we build the picture in a BACK BUFFER (ordinary RAM the
;      TV never shows), tile by tile, shifted by however many pixels the
;      camera is part-way into a tile. Then the car goes on top.
;   3. Then we COPY the finished picture to the screen in one go, so you
;      never see it half built.
;   The window is one colour pair: colour on a Spectrum belongs to 8x8
;   blocks, which cannot follow a scroll that moves 1 pixel at a time.
;
; Timing: building a frame takes longer than 1/50 s, so the car's physics
; runs once for EVERY TV frame that passed (read from the FRAMES counter).
; The car keeps the same real speed however long the drawing takes.
; =====================================================================

BUF_HI  equ 0xC0        ; back buffer: 26 pages from 0xC000, one page per
                        ; 8-pixel column, one byte per pixel row
TAB_HI  equ 0xDA        ; shift tables: 16 pages from 0xDA00
WIN_COL equ 4           ; window on screen: columns 4..27 (24 bytes wide)
WIN_Y   equ 32          ; pixel rows 32..159 (128 high)
WIN_W   equ 24
WIN_H   equ 128
FRAMES  equ 23672       ; ROM counter, +1 every TV frame (1/50 s)

        org 32768

start:
        ld a,6
        out (254),a             ; BORDER 6 (yellow: the kitchen table)
        ld hl,0x4000            ; clear the pixels
        ld de,0x4001
        ld bc,6143
        ld (hl),0
        ldir
        ld hl,0x5800            ; whole screen yellow paper...
        ld de,0x5801
        ld bc,767
        ld (hl),0x30
        ldir
        ld hl,0x5800+4*32+WIN_COL   ; ...and the window bright white, black ink
        ld b,16                 ; 16 character rows = 128 pixels
win_attr:
        push bc
        push hl
        ld d,h
        ld e,l
        inc de
        ld (hl),0x78
        ld bc,WIN_W-1
        ldir
        pop hl
        ld de,32
        add hl,de
        pop bc
        djnz win_attr

        call make_tables
        call make_row_table

        ld hl,STARTX            ; put the car on the start line
        ld (carx),hl
        ld hl,STARTY
        ld (cary),hl
        xor a
        ld (carx_f),a
        ld (cary_f),a
        ld hl,0
        ld (vx),hl
        ld (vy),hl
        ld a,STARTA
        ld (angle),a
        ld a,(FRAMES)
        ld (last_frame),a

; ---------------------------------------------------------------------
; MAIN LOOP
; ---------------------------------------------------------------------
main:
        ld a,(last_frame)       ; how many TV frames since last time?
        ld b,a
        ld a,(FRAMES)
        ld (last_frame),a
        sub b
        jr nz,have_dt
        halt                    ; none yet: wait for one
        jr main
have_dt:
        cp 5
        jr c,dt_ok
        ld a,4                  ; never catch up more than 4 frames at once
dt_ok:
        ld (dt),a
        ld b,a
phys_loop:
        push bc
        call physics            ; one physics step per TV frame
        pop bc
        djnz phys_loop

        call camera             ; where is the window looking?
        call draw_tiles         ; build the picture in the back buffer
        call draw_car           ; car on top, in the middle
        halt                    ; start copying just after the TV frame begins
        call copy_to_screen     ; show it
        call clear_buffer       ; wipe the buffer for the next picture
        ld hl,(renders)         ; count pictures drawn (the tests read this)
        inc hl
        ld (renders),hl
        jr main

; ---------------------------------------------------------------------
; make_tables: for each shift s = 0..7, two 256-byte tables:
;   page TAB_HI+2s   : A[b] = b >> (8-s)  the part spilling into the LEFT byte
;   page TAB_HI+2s+1 : B[b] = b << s      the part staying in the RIGHT byte
; Looking a shifted byte up in a table is much faster than shifting it.
; ---------------------------------------------------------------------
make_tables:
        ld d,TAB_HI             ; D = page being filled
        ld c,0                  ; C = s
mt_s:
        ld e,0                  ; E = b
mt_b:
        ld a,8                  ; A[b]: shift right 8-s times
        sub c
        ld b,a
        ld a,e
mt_r:
        srl a
        djnz mt_r
        ld h,d
        ld l,e
        ld (hl),a
        ld a,c                  ; B[b]: shift left s times
        or a
        ld a,e
        jr z,mt_l_done
        ld b,c
mt_l:
        add a,a
        djnz mt_l
mt_l_done:
        inc h
        ld (hl),a
        inc e
        jr nz,mt_b
        inc d
        inc d
        inc c
        ld a,c
        cp 8
        jr nz,mt_s
        ret

; ---------------------------------------------------------------------
; PHYSICS - one TV frame's worth: keys, push, friction, move, world edge
; ---------------------------------------------------------------------
physics:
        ld a,0xDF               ; Y U I O P
        in a,(0xFE)
        ld e,a
        bit 1,e                 ; O = left
        jr nz,no_left
        ld a,(angle)
        dec a
        and 63
        ld (angle),a
no_left:
        bit 0,e                 ; P = right
        jr nz,no_right
        ld a,(angle)
        inc a
        and 63
        ld (angle),a
no_right:
        ld a,(angle)            ; push for the way we face: thrust_tab + frame*4
        rrca
        rrca
        and 15
        add a,a
        add a,a
        ld l,a
        ld h,0
        ld de,thrust_tab
        add hl,de
        ld e,(hl)
        inc hl
        ld d,(hl)
        inc hl
        ld c,(hl)
        inc hl
        ld b,(hl)
        ld a,0xFB               ; Q = accelerate
        in a,(0xFE)
        bit 0,a
        jr nz,no_acc
        ld hl,(vx)
        add hl,de
        ld (vx),hl
        ld hl,(vy)
        add hl,bc
        ld (vy),hl
no_acc:
        ld a,0xFD               ; A = brake / reverse at half strength
        in a,(0xFE)
        bit 0,a
        jr nz,no_rev
        sra d
        rr e
        sra b
        rr c
        ld hl,(vx)
        or a
        sbc hl,de
        ld (vx),hl
        ld hl,(vy)
        or a
        sbc hl,bc
        ld (vy),hl
no_rev:
        call surface            ; 3 on the road, 2 off it
        ld (fshift),a
        ld hl,(vx)
        call friction
        ld (vx),hl
        ld hl,(vy)
        call friction
        ld (vy),hl

        ld hl,carx_f            ; x = x + vx
        ld de,(vx)
        call add_v
        ld hl,(carx)            ; keep inside the world: 0..495
        ld de,MAPW*8-16
        or a
        sbc hl,de
        jr c,x_ok
        ld hl,0
        ld a,(vx+1)
        bit 7,a
        jr nz,x_set
        ld hl,MAPW*8-17
x_set:
        ld (carx),hl
        ld hl,0
        ld (vx),hl
x_ok:
        ld hl,cary_f            ; y = y + vy
        ld de,(vy)
        call add_v
        ld hl,(cary)            ; 0..367
        ld de,MAPH*8-16
        or a
        sbc hl,de
        jr c,y_ok
        ld hl,0
        ld a,(vy+1)
        bit 7,a
        jr nz,y_set
        ld hl,MAPH*8-17
y_set:
        ld (cary),hl
        ld hl,0
        ld (vy),hl
y_ok:
        ret

; add_v: the 3-byte position at HL (fraction, pixel low, pixel high)
; plus the speed DE (whole pixels in D, 1/256ths in E, can be negative)
add_v:
        ld a,(hl)
        add a,e                 ; fractions first; carry goes up
        ld (hl),a
        inc hl
        ld c,0                  ; sign-extend D into C (0 or 255)
        bit 7,d                 ; (BIT and DEC leave the carry alone)
        jr z,av_pos
        dec c
av_pos:
        ld a,(hl)
        adc a,d
        ld (hl),a
        inc hl
        ld a,(hl)
        adc a,c
        ld (hl),a
        ret

; friction: HL = HL - HL/2^fshift; tiny speeds become exactly 0
friction:
        ld d,h
        ld e,l
        ld a,(fshift)
        ld b,a
fr_div:
        sra d
        rr e
        djnz fr_div
        or a
        sbc hl,de
        ld a,h
        or a
        jr nz,fr_neg
        ld a,l
        cp 8
        ret nc
        ld hl,0
        ret
fr_neg:
        inc a
        ret nz
        ld a,l
        cp 0xF9
        ret c
        ld hl,0
        ret

; surface: look up the tile under the middle of the car in surface_map
surface:
        ld hl,(cary)
        ld de,8
        add hl,de
        call row_offset         ; HL = (y DIV 8) * MAPW
        push hl
        ld hl,(carx)
        ld de,8
        add hl,de
        srl h                   ; x DIV 8
        rr l
        srl h
        rr l
        srl h
        rr l
        pop de
        add hl,de
        ld de,surface_map
        add hl,de
        ld a,(hl)
        or a
        ld a,3
        ret z
        ld a,2
        ret

; row_offset: HL = pixel y  ->  HL = (y DIV 8) * MAPW  (MAPW = 72 = 8 * 9)
row_offset:
        ld a,l
        and 0xF8                ; (y DIV 8) * 8
        ld l,a
        ld d,h
        ld e,l
        add hl,hl               ; * 8 ...
        add hl,hl
        add hl,hl
        add hl,de               ; ... + 1 = * 9   ->  row * 72
        ret

; ---------------------------------------------------------------------
; CAMERA: put the car in the middle of the window, unless that would
; show past the edge of the world
; ---------------------------------------------------------------------
camera:
        ld hl,(carx)
        ld de,88                ; window is 192 wide, car is 16: 88 to its left
        or a
        sbc hl,de
        jr nc,cx_pos
        ld hl,0
cx_pos:
        ld de,MAPW*8-200        ; furthest right we may look
        call clamp_hl
        ld (camx),hl
        ld hl,(cary)
        ld de,56                ; window is 128 high: 56 above the car
        or a
        sbc hl,de
        jr nc,cy_pos
        ld hl,0
cy_pos:
        ld de,MAPH*8-136
        call clamp_hl
        ld (camy),hl
        ret

clamp_hl:                       ; HL = smaller of HL and DE
        push hl
        or a
        sbc hl,de
        pop hl
        ret c
        ex de,hl
        ret

; ---------------------------------------------------------------------
; DRAW_TILES: 25 x 17 tiles into the back buffer, shifted by the camera.
; A tile whose number is 0 is blank, so it is skipped - most of the
; table is empty, which is what makes this fast enough.
; ---------------------------------------------------------------------
draw_tiles:
        ld a,(camx)
        and 7                   ; s = pixels into the tile, sideways
        add a,a
        add a,TAB_HI
        ld (dt_tab+1),a         ; patch the table page into the code below
        ld hl,(camy)            ; IX = world_map + (camy/8)*MAPW + camx/8
        call row_offset
        push hl
        ld hl,(camx)
        srl h
        rr l
        srl h
        rr l
        srl h
        rr l
        pop de
        add hl,de
        ld de,world_map
        add hl,de
        push hl
        pop ix
        ld a,(camy)
        and 7
        neg
        add a,8                 ; first buffer row = 8 - (camy AND 7)
        ld l,a
        push ix                 ; map pointer goes into the SHADOW HL (EXX swaps
        exx                     ; BC, DE, HL with a second set - a free extra
        pop hl                  ; set of registers for the loop's bookkeeping)
        exx
        ld a,17                 ; 17 rows of tiles
dt_row:
        ld (dt_rows),a
        ld h,BUF_HI
        exx
        ld b,25                 ; 25 tiles across (counted in shadow B)
dt_col:
        ld a,(hl)               ; (shadow set) tile number from the map
        inc hl
        exx                     ; back to the drawing registers
        or a
        jp z,dt_next            ; blank: nothing to draw
        rlca                    ; DE = tiles + number * 8
        rlca
        rlca
        ld d,a
        and 0xF8
        ld e,a
        ld a,d
        and 7
        add a,tiles/256
        ld d,a
dt_tab:
        ld b,0                  ; (patched) B = this shift's table page
        rept 8                  ; one pixel row of the tile, 8 times:
        ld a,(de)               ;   the tile's byte
        inc e
        ld c,a
        ld a,(bc)               ;   left part, into this column
        or (hl)
        ld (hl),a
        inc b
        inc h
        ld a,(bc)               ;   right part, into the next column
        or (hl)
        ld (hl),a
        dec b
        dec h
        inc l                   ;   next pixel row down
        endm
        ld a,l
        sub 8
        ld l,a
dt_next:
        inc h                   ; next column page
        exx
        dec b                   ; (shadow B) 25 tiles
        jp nz,dt_col
        ld de,MAPW-25           ; (shadow HL) next map row
        add hl,de
        exx
        ld a,l
        add a,8
        ld l,a
        ld a,(dt_rows)
        dec a
        jp nz,dt_row
        ret

; ---------------------------------------------------------------------
; DRAW_CAR: OR the car into the back buffer at its place in the window
; ---------------------------------------------------------------------
draw_car:
        ld hl,(carx)            ; window x = carx - camx (0..191)
        ld de,(camx)
        or a
        sbc hl,de
        ld c,l
        ld hl,(cary)            ; window y = cary - camy (0..127)
        ld de,(camy)
        or a
        sbc hl,de
        ld a,l
        add a,8                 ; buffer row
        ld b,a
        ld a,(angle)            ; DE = sprites + frame * 32
        rrca
        rrca
        and 15
        ld l,a
        ld h,0
        add hl,hl
        add hl,hl
        add hl,hl
        add hl,hl
        add hl,hl
        ld de,sprites
        add hl,de
        ex de,hl
        ld a,c                  ; column page = BUF_HI + 1 + x/8
        rrca
        rrca
        rrca
        and 31
        add a,BUF_HI+1
        ld h,a
        ld l,b
        ld a,c
        and 7
        ld (shift),a
        ld b,16
dc_row:
        push bc
        ld a,(de)
        inc de
        ld b,a
        ld a,(de)
        inc de
        ld c,a
        push de
        ld e,0
        ld a,(shift)
        or a
        jr z,dc_put
        ld d,a
dc_sh:
        srl b
        rr c
        rr e
        dec d
        jr nz,dc_sh
dc_put:
        ld a,(hl)
        or b
        ld (hl),a
        inc h
        ld a,(hl)
        or c
        ld (hl),a
        inc h
        ld a,(hl)
        or e
        ld (hl),a
        dec h
        dec h
        inc l
        pop de
        pop bc
        djnz dc_row
        ret

; ---------------------------------------------------------------------
; COPY_TO_SCREEN: buffer rows 8..135 -> the window on screen
; ---------------------------------------------------------------------
copy_to_screen:
        ld ix,row_table         ; screen address of each window line
        ld l,8                  ; first buffer row
cs_row:
        ld e,(ix+0)
        ld d,(ix+1)
        inc ix
        inc ix
        ld h,BUF_HI+1
        rept WIN_W
        ld a,(hl)
        ld (de),a
        inc h                   ; next column page
        inc e                   ; next screen byte
        endm
        inc l
        ld a,l
        cp 8+WIN_H
        jp nz,cs_row
        ret

; ---------------------------------------------------------------------
; CLEAR_BUFFER: zero rows 8..135 of the 24 shown columns with PUSH.
; PUSH writes 2 bytes in 11 T-states - the fastest way to fill memory.
; We point the stack pointer INTO the buffer and push zeros downwards.
; Interrupts may stay on: anything the interrupt pushes lands below SP,
; on rows we are about to clear anyway (or on spare rows never shown).
; ---------------------------------------------------------------------
clear_buffer:
        ld (save_sp),sp
        ld de,0
        ld a,BUF_HI+1
cb_col:
        ld h,a
        ld l,8+WIN_H            ; push goes downwards from here to row 8
        ld sp,hl
        rept WIN_H/2
        push de
        endm
        inc a
        cp BUF_HI+1+WIN_W
        jp nz,cb_col
        ld sp,(save_sp)
        ret

; make_row_table: screen address of window lines 0..127
make_row_table:
        ld ix,row_table
        ld b,WIN_Y
mr_loop:
        ld c,WIN_COL*8
        call scr_addr
        ld (ix+0),l
        ld (ix+1),h
        inc ix
        inc ix
        inc b
        ld a,b
        cp WIN_Y+WIN_H
        jr nz,mr_loop
        ret

; scr_addr: B = y, C = x  ->  HL = screen address (see stage 1)
scr_addr:
        ld a,b
        and 7
        or 0x40
        ld h,a
        ld a,b
        rrca
        rrca
        rrca
        and 0x18
        or h
        ld h,a
        ld a,b
        rlca
        rlca
        and 0xE0
        ld l,a
        ld a,c
        rrca
        rrca
        rrca
        and 0x1F
        or l
        ld l,a
        ret

; ---------------------------------------------------------------------
; variables
; ---------------------------------------------------------------------
carx_f:   db 0                  ; car x: fraction, then whole pixels (word)
carx:     dw 0
cary_f:   db 0
cary:     dw 0
vx:       dw 0                  ; speed, 8.8 fixed point
vy:       dw 0
angle:    db 0                  ; 0..63, 0 = up, clockwise
camx:     dw 0
camy:     dw 0
fshift:   db 3
shift:    db 0
last_frame: db 0
dt:       db 0                  ; TV frames the last picture took
renders:  dw 0
dt_rows:  db 0
dt_cols:  db 0
save_sp:  dw 0
row_table: defs WIN_H*2

        include "data.asm"
        include "world.asm"
code_end:

        if MAPW - 72
        .error row_offset assumes the map is 72 tiles wide
        endif
        if code_end > BUF_HI*256
        .error code and data run into the back buffer
        endif

        end start
