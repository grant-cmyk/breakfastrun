; =====================================================================
; BREAKFAST RUN - STAGE 4: five cars (you and four computer cars)
; ZX Spectrum 48K, assembled with pasmo.
;
; Keys:  O = steer left   P = steer right   Q = accelerate   A = brake/reverse
;
; New in this stage:
;   - EVERY car is the same record (see "the car record" below) and goes
;     through the same physics. The only difference is who presses its
;     buttons: the keyboard for you, the driving code for the computer.
;   - The computer drives at WAYPOINTS round the track, aiming a little to
;     one side of each (a different side each time), thinks only every
;     few frames, and now and then makes a MISTAKE: turns in late, lifts
;     off, or wobbles the wrong way.
;   - Cars that touch bounce away from each other.
;   - Cars are drawn with a MASK, so a black car stays readable on black
;     track lines: clear a car-shaped hole (plus a 1px edge), then ink.
;
; Kept from stage 2: the scrolling world, back buffer, physics once per TV
; frame. See PROJECT-LOG.md for why each piece is the way it is.
; =====================================================================

BUF     equ 0xC000      ; back buffer, 6 KB, laid out EXACTLY like the screen
BUF_HI  equ 0xC0        ; (so the next pixel row down is INC H, and a row
                        ; copies to the screen as one block). Window pixel
                        ; (0,0) is buffer row 16, byte 2; the rows and bytes
                        ; around it are margins for cars half out of view.
TAB_HI  equ 0xD8        ; shift tables: 16 pages 0xD8..0xE7
PACE_FR equ 3           ; show a new picture every 3 TV frames, steadily
NCARS   equ 5           ; you + 4 computer cars
COPIER  equ 0xE800      ; the screen-copy code is WRITTEN HERE at start-up (5.6 KB)
WIN_COL equ 4           ; window on screen: columns 4..27 (24 bytes wide)
WIN_Y   equ 32          ; pixel rows 32..159 (128 high)
WIN_W   equ 24
WIN_H   equ 128
FRAMES  equ 23672       ; ROM counter, +1 every TV frame (1/50 s)

; ---- the car record: one block of bytes per car (offsets from IX) ----
C_XF    equ 0           ; x: fraction
C_X     equ 1           ;    whole pixels (2 bytes), top-left of the 16x16 car
C_YF    equ 3           ; y: fraction
C_Y     equ 4           ;    whole pixels (2 bytes)
C_VX    equ 6           ; speed x, 8.8 fixed point (2 bytes)
C_VY    equ 8           ; speed y
C_ANG   equ 10          ; heading 0..63, 0 = up, clockwise
C_CTRL  equ 11          ; buttons this frame: bit0 left, 1 right, 2 go, 3 brake
C_FSH   equ 12          ; friction shift (3 road, 2 off-road)
C_WP    equ 13          ; computer: waypoint it is heading for
C_OFFX  equ 14          ; computer: aim this far to the side of it (signed)
C_OFFY  equ 15
C_MIST  equ 16          ; computer: frames of mistake left (0 = none)
C_MKIND equ 17          ;           which mistake: 1 late turn, 2 lift, 3 wobble
C_THINK equ 18          ; computer: frames until it next decides how to steer
C_PACE  equ 19          ; computer: accelerates on PACE of every 8 frames
C_REACT equ 20          ; computer: thinking turns it lets go by (0 = every 4 frames)
C_ERR   equ 21          ; computer: chance of a mistake at each waypoint /256
C_KIND  equ 22          ; which picture: 0 you, 1 CPU A, 2 CPU B
C_STEER equ 23          ; computer: steering it decided on (bit0 L, bit1 R)
C_EASE  equ 24          ; computer: 1 = target well off to the side, ease off
C_SIZE  equ 25

CT_L    equ 1
CT_R    equ 2
CT_GO   equ 4
CT_BRK  equ 8

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
        ld b,16
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
        ld hl,cars_init         ; copy the starting records into place
        ld de,cars
        ld bc,NCARS*C_SIZE
        ldir
        call make_copier        ; the program writes its own copy routine
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
        halt
        jr main
have_dt:
        cp 5
        jr c,dt_ok
        ld a,4
dt_ok:
        ld (dt),a
        ld b,a
tick_loop:
        push bc
        call tick               ; one TV frame of everything moving
        pop bc
        djnz tick_loop

        call camera
        call draw_tiles
        ld ix,cars+(NCARS-1)*C_SIZE ; computer cars first, yours last (on top)
        ld b,NCARS
draw_all:
        push bc
        call draw_car
        ld de,0x10000-C_SIZE
        add ix,de
        pop bc
        djnz draw_all
wait_show:
        halt                    ; wait until 3 TV frames have passed since the
        ld a,(last_shown)       ; last picture went up: a steady rhythm looks
        ld b,a                  ; smoother than one that jumps between 3 and 4
        ld a,(FRAMES)
        sub b
        cp PACE_FR
        jr c,wait_show
        ld a,(FRAMES)
        ld (last_shown),a
        call copy_to_screen     ; straight after the interrupt, ahead of the beam
        call clear_buffer
        ld hl,(renders)
        inc hl
        ld (renders),hl
        jr main

; tick: one TV frame - read keys, let the computer drive, move, bump
tick:
        ld hl,(ticks)
        inc hl
        ld (ticks),hl
        call read_keys          ; your buttons -> your car's C_CTRL
        ld ix,cars+C_SIZE       ; the computer drives cars 1..NCARS-1
        ld b,NCARS-1
tk_ai:
        push bc
        call ai_drive
        ld de,C_SIZE
        add ix,de
        pop bc
        djnz tk_ai
        ld ix,cars              ; everyone moves
        ld b,NCARS
tk_ph:
        push bc
        call physics
        ld de,C_SIZE
        add ix,de
        pop bc
        djnz tk_ph
        jp bump_all             ; bumps: every pair (gen_bumps.asm)

read_keys:
        ld c,0
        ld a,0xDF               ; Y U I O P
        in a,(0xFE)
        bit 1,a                 ; O
        jr nz,rk1
        set 0,c
rk1:
        bit 0,a                 ; P
        jr nz,rk2
        set 1,c
rk2:
        ld a,0xFB               ; Q
        in a,(0xFE)
        bit 0,a
        jr nz,rk3
        set 2,c
        ld a,1
        ld (race_on),a          ; first press of Q starts the race
rk3:
        ld a,0xFD               ; A
        in a,(0xFE)
        bit 0,a
        jr nz,rk4
        set 3,c
rk4:
        ld a,c
        ld (cars+C_CTRL),a
        ret

; ---------------------------------------------------------------------
; make_tables: for each shift s = 0..7, two 256-byte tables:
;   page TAB_HI+2s   : A[b] = b >> (8-s)   (part in the left byte)
;   page TAB_HI+2s+1 : B[b] = b << s       (part in the right byte)
; ---------------------------------------------------------------------
make_tables:
        ld d,TAB_HI
        ld c,0
mt_s:
        ld e,0
mt_b:
        ld a,8
        sub c
        ld b,a
        ld a,e
mt_r:
        srl a
        djnz mt_r
        ld h,d
        ld l,e
        ld (hl),a
        ld a,c
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
; PHYSICS (IX = car): buttons -> steering and push -> friction -> move
; ---------------------------------------------------------------------
physics:
        ld e,(ix+C_CTRL)
        bit 0,e
        jr z,ph_nl
        ld a,(ix+C_ANG)
        dec a
        and 63
        ld (ix+C_ANG),a
ph_nl:
        bit 1,e
        jr z,ph_nr
        ld a,(ix+C_ANG)
        inc a
        and 63
        ld (ix+C_ANG),a
ph_nr:
        push de
        ld a,(ix+C_ANG)         ; BC, DE = push for the way the car faces
        call heading_push
        pop hl                  ; L = buttons
        ; work out this frame's push: Q = full push, A = half push backwards,
        ; both = half push, neither = none
        ld a,l
        and CT_GO+CT_BRK
        jr nz,ph_some
        ld d,a                  ; no buttons: no push
        ld e,a
        ld b,a
        ld c,a
        jr ph_push_set
ph_some:
        cp CT_GO
        jr z,ph_push_set        ; Q alone: the full push as it is
        sra d                   ; otherwise half of it...
        rr e
        sra b
        rr c
        cp CT_BRK
        jr nz,ph_push_set       ; Q and A: half forwards
        xor a                   ; A alone: half, backwards (negate DE, BC)
        sub e
        ld e,a
        sbc a,a
        sub d
        ld d,a
        xor a
        sub c
        ld c,a
        sbc a,a
        sub b
        ld b,a
ph_push_set:
        ld a,(ticks)            ; look at the ground under the car on one
        add a,(ix+C_KIND)       ; frame in 4 (the cars take turns): it
        and 3                   ; cannot change much in 4 frames
        jr nz,ph_surf_kept
        push bc
        push de
        call surface
        pop de
        pop bc
        ld (ix+C_FSH),a
ph_surf_kept:
        ld a,(ix+C_FSH)
        ld (fshift),a
        ; ---- x: speed += push, friction, position += speed; each value is
        ;      read from the car record once and written back once ----
        ld l,(ix+C_VX)
        ld h,(ix+C_VX+1)
        add hl,de
        call friction           ; (keeps BC: the y push)
        ld (ix+C_VX),l
        ld (ix+C_VX+1),h
        ld d,0                  ; D = top byte of the speed, sign-extended
        bit 7,h
        jr z,ph_xp
        dec d
ph_xp:
        ld a,(ix+C_XF)          ; 24-bit add: fraction, then whole pixels
        add a,l                 ; (LD, BIT, DEC and JR leave the carry alone)
        ld (ix+C_XF),a
        ld a,(ix+C_X)
        adc a,h
        ld (ix+C_X),a
        ld a,(ix+C_X+1)
        adc a,d
        ld (ix+C_X+1),a
        cp (MAPW*8-16)/256      ; keep inside the world (x 0..MAPW*8-17): a
        jr c,ph_xok             ; high byte below the limit's is fine (the
        jr nz,ph_xout           ; usual case); above it, or negative: out
        ld a,(ix+C_X)
        cp (MAPW*8-16) AND 255
        jr c,ph_xok
ph_xout:
        ld hl,0
        bit 7,(ix+C_VX+1)
        jr nz,ph_xset
        ld hl,MAPW*8-17
ph_xset:
        ld (ix+C_X),l
        ld (ix+C_X+1),h
        xor a
        ld (ix+C_VX),a
        ld (ix+C_VX+1),a
ph_xok:
        ; ---- y: the same, with the y push in BC ----
        ld l,(ix+C_VY)
        ld h,(ix+C_VY+1)
        add hl,bc
        call friction
        ld (ix+C_VY),l
        ld (ix+C_VY+1),h
        ld d,0
        bit 7,h
        jr z,ph_yp
        dec d
ph_yp:
        ld a,(ix+C_YF)
        add a,l
        ld (ix+C_YF),a
        ld a,(ix+C_Y)
        adc a,h
        ld (ix+C_Y),a
        ld a,(ix+C_Y+1)
        adc a,d
        ld (ix+C_Y+1),a
        cp (MAPH*8-16)/256
        jr c,ph_yok
        jr nz,ph_yout
        ld a,(ix+C_Y)
        cp (MAPH*8-16) AND 255
        jr c,ph_yok
ph_yout:
        ld hl,0
        bit 7,(ix+C_VY+1)
        jr nz,ph_yset
        ld hl,MAPH*8-17
ph_yset:
        ld (ix+C_Y),l
        ld (ix+C_Y+1),h
        xor a
        ld (ix+C_VY),a
        ld (ix+C_VY+1),a
ph_yok:
        ret

; heading_push: A = heading 0..63 -> DE = push x, BC = push y (8.8)
heading_push:
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
        ret

; add_v: the 3-byte position at HL (fraction, pixel low, pixel high)
; plus the speed DE (can be negative)
add_v:
        ld a,(hl)
        add a,e
        ld (hl),a
        inc hl
        ld c,0
        bit 7,d
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
        sra d                   ; DE = HL / 4 ...
        rr e
        sra d
        rr e
        ld a,(fshift)
        cp 2
        jr z,fr_div
        sra d                   ; ... or / 8 on the road
        rr e
fr_div:
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

; surface (IX = car): A = 3 on the road, 2 off it
; The surface map has one BIT per tile, MAPW/8 bytes a row.
surface:
        ld a,(ix+C_Y)           ; tile row = (y + 8) DIV 8
        add a,8
        ld l,a
        ld a,(ix+C_Y+1)
        adc a,0
        ld h,a
        srl h
        rr l
        srl h
        rr l
        srl h
        rr l
        ld e,l                  ; row * 9  (= row * 8 + row)
        ld d,0
        add hl,hl
        add hl,hl
        add hl,hl
        add hl,de
        ld a,(ix+C_X)           ; tile column = (x + 8) DIV 8
        add a,8
        ld e,a
        ld a,(ix+C_X+1)
        adc a,0
        ld d,a
        srl d
        rr e
        srl d
        rr e
        srl d
        rr e
        ld a,e
        and 7
        ld b,a                  ; bit number from the left
        srl e                   ; byte = column DIV 8
        srl e
        srl e
        add hl,de
        ld de,surface_map
        add hl,de
        ld a,(hl)
        inc b
su_bit:
        rla                     ; shift the tile's bit out into carry
        djnz su_bit
        ld a,3
        ret nc                  ; 0 = road
        ld a,2
        ret

; ---------------------------------------------------------------------
; AI_DRIVE (IX = a computer car): decide its buttons for this frame.
; Like a person: look at where to go next, turn towards it, mostly hold
; the decision for a few frames, and sometimes get it wrong.
; ---------------------------------------------------------------------
ai_drive:
        ld a,(race_on)          ; the race starts when you first press Q
        or a
        jr nz,ai_racing
        ld (ix+C_CTRL),a        ; until then: sit on the grid
        ret
ai_racing:
        ; ---- 1. in the middle of a mistake? ----
        ld a,(ix+C_MIST)
        or a
        jr z,ai_no_mist
        dec (ix+C_MIST)
        ld a,(ix+C_MKIND)
        cp 1
        jr nz,ai_m2
        call pace_gate          ; late turn-in: no steering, keeps going
        jp ai_set
ai_m2:
        cp 2
        jr nz,ai_m3
        ld a,(ix+C_STEER)       ; lift: steers but no throttle - loses time
        jp ai_set
ai_m3:
        call pace_gate          ; wobble: steers the wrong way
        ld b,a
        ld a,(ix+C_STEER)
        xor CT_L+CT_R
        and CT_L+CT_R
        or b
        jp ai_set

ai_no_mist:
        ; ---- 2. the computer cars TAKE TURNS to think: car k may decide on
        ;         frames where (ticks - k) AND 3 = 0, so only one car does the
        ;         expensive part each frame. REACT = turns it lets go by. ----
        ld a,(ticks)
        sub (ix+C_KIND)
        and 3
        jp nz,ai_throttle
        ld a,(ix+C_THINK)
        or a
        jr z,ai_decide
        dec (ix+C_THINK)
        jp ai_throttle
ai_decide:
        ; ---- 3. a decision frame: look ahead, steer ----
        ld a,(ix+C_REACT)
        ld (ix+C_THINK),a
        ; where am I aiming?  waypoint + this lap's offset
        call wp_delta           ; DE = dx, BC = dy from car centre to aim point
        push de                 ; keep them: manhattan uses DE and BC
        push bc
        call manhattan          ; reached it?  (|dx| + |dy| < 24)
        ld de,24
        or a
        sbc hl,de
        jr nc,ai_check_next
        pop bc
        pop de
        call next_waypoint      ; yes: aim at the next one
        call wp_delta
        jr ai_have_target
ai_check_next:
        ; overshot it?  if the NEXT waypoint is nearer, move on (no U-turns)
        ld (dist_cur),hl        ; distance to current - 24
        ld a,(ix+C_WP)
        push af
        call wp_inc
        call wp_delta
        call manhattan
        pop af
        ld (ix+C_WP),a
        ex de,hl                ; DE = distance to next
        ld hl,(dist_cur)
        ld bc,24
        add hl,bc               ; HL = distance to current
        or a
        sbc hl,de
        jr c,ai_keep            ; current still nearer: keep it
        jr z,ai_keep
        pop bc
        pop de
        call next_waypoint
        call wp_delta
        jr ai_have_target
ai_keep:
        pop bc                  ; the current waypoint's dx, dy again
        pop de
ai_have_target:
        call scale_to_byte      ; D = dx, B = dy, both -63..63
        ld a,(ix+C_ANG)         ; heading vector: hx = E, hy = C (-64..64)
        push de
        push bc
        call heading_push
        ld a,e
        ld (hx),a
        ld a,c
        ld (hy),a
        pop bc
        pop de
        ld a,d
        ld (tdx),a
        ld a,b
        ld (tdy),a
        ; cross = hx*dy - hy*dx   (>0: target is to the right)
        ld a,(hx)
        ld b,a
        ld a,(tdy)
        ld c,a
        call mul8s
        push hl
        ld a,(hy)
        ld b,a
        ld a,(tdx)
        ld c,a
        call mul8s
        ex de,hl
        pop hl
        or a
        sbc hl,de
        ld (cross),hl
        ; dot = hx*dx + hy*dy   (>0: target is ahead)
        ld a,(hx)
        ld b,a
        ld a,(tdx)
        ld c,a
        call mul8s
        push hl
        ld a,(hy)
        ld b,a
        ld a,(tdy)
        ld c,a
        call mul8s
        pop de
        add hl,de
        ld (dot),hl
        ; ease off the throttle when the target is behind, or more than
        ; 45 degrees off (|cross| > dot) - kept per car in C_EASE
        ld (ix+C_EASE),1
        bit 7,h
        jr nz,ai_ease_set
        push hl
        ld hl,(cross)
        call abs_hl
        ex de,hl
        pop hl
        or a
        sbc hl,de
        jr c,ai_ease_set
        ld (ix+C_EASE),0
ai_ease_set:
        ld hl,(dot)
        ; straight on if ahead and |cross| * 4 < dot  (within about 14 degrees)
        bit 7,h
        jr nz,ai_turn
        ld hl,(cross)
        call abs_hl
        add hl,hl
        add hl,hl
        ld de,(dot)
        or a
        sbc hl,de
        ld a,0
        jr c,ai_steer_set
ai_turn:
        ld hl,(cross)
        bit 7,h
        ld a,CT_L
        jr nz,ai_steer_set
        ld a,CT_R
ai_steer_set:
        ld (ix+C_STEER),a

ai_throttle:
        ; ---- 4. throttle: PACE frames in every 8 (slower than you),
        ;         and every other frame only while easing off ----
        call pace_gate
        ld b,a
        ld a,(ix+C_EASE)
        or a
        jr z,ai_go
        ld a,(ticks)
        and 1
        jr z,ai_go
        ld b,0
ai_go:
        ld a,(ix+C_STEER)
        or b
ai_set:
        ld (ix+C_CTRL),a
        ret

; pace_gate (IX): A = CT_GO on PACE of every 8 frames, else 0
pace_gate:
        ld a,(ticks)
        add a,(ix+C_KIND)       ; the two cars pulse out of step
        and 7
        cp (ix+C_PACE)
        ld a,0
        ret nc
        ld a,CT_GO
        ret

; next_waypoint: move on, pick a new aiming offset, maybe start a mistake
next_waypoint:
        call wp_inc
        call rnd                ; offset -8..+7 pixels each way: a different
        and 15                  ; line through every corner
        sub 8
        ld (ix+C_OFFX),a
        call rnd
        and 15
        sub 8
        ld (ix+C_OFFY),a
        call rnd                ; a mistake?  ERR chances in 256
        cp (ix+C_ERR)
        ret nc
        call rnd
        and 3
        jr nz,nw_kind
        inc a
nw_kind:
        cp 3
        jr c,nw_k
        ld a,3
nw_k:
        ld (ix+C_MKIND),a
        call rnd
        and 15
        add a,8                 ; lasts 8..23 frames
        ld (ix+C_MIST),a
        ld hl,(mistakes)
        inc hl
        ld (mistakes),hl
        ret

wp_inc:
        ld a,(ix+C_WP)
        inc a
        cp NWP
        jr c,wpi1
        xor a
wpi1:
        ld (ix+C_WP),a
        ret

; wp_delta (IX): DE = aimx - (carx + 8), BC = aimy - (cary + 8)
wp_delta:
        ld a,(ix+C_WP)
        add a,a
        add a,a
        ld l,a
        ld h,0
        ld de,waypoints
        add hl,de
        ld e,(hl)
        inc hl
        ld d,(hl)
        inc hl
        ld c,(hl)
        inc hl
        ld b,(hl)
        push bc
        ld a,(ix+C_OFFX)        ; + offset (sign-extended)
        call sext
        ex de,hl
        add hl,de
        ld e,(ix+C_X)
        ld d,(ix+C_X+1)
        or a
        sbc hl,de
        ld de,8
        or a
        sbc hl,de
        pop bc
        push hl
        ld a,(ix+C_OFFY)
        call sext
        add hl,bc
        ld e,(ix+C_Y)
        ld d,(ix+C_Y+1)
        or a
        sbc hl,de
        ld de,8
        or a
        sbc hl,de
        ld b,h
        ld c,l
        pop de
        ret

sext:                           ; HL = A sign-extended to 16 bits
        ld l,a
        ld h,0
        bit 7,a
        ret z
        dec h
        ret

manhattan:                      ; HL = |DE| + |BC|
        ex de,hl
        call abs_hl
        push hl
        ld h,b
        ld l,c
        call abs_hl
        pop de
        add hl,de
        ret

abs_hl:
        bit 7,h
        ret z
        ex de,hl
        ld hl,0
        or a
        sbc hl,de
        ret

; scale_to_byte: halve DE and BC together until both fit -63..63;
; returns D = dx byte, B = dy byte. (63, so that heading + target never
; passes 127, which the quarter-squares multiply needs.)
scale_to_byte:
stb_loop:
        ld h,d
        ld l,e
        call fits_byte
        jr nz,stb_halve
        ld h,b
        ld l,c
        call fits_byte
        jr z,stb_done
stb_halve:
        sra d
        rr e
        sra b
        rr c
        jr stb_loop
stb_done:
        ld d,e
        ld b,c
        ret

fits_byte:                      ; Z set if HL is in -63..63
        ld a,h
        or a
        jr nz,fb_neg
        ld a,l
        cp 64
        jr nc,fb_no
        xor a
        ret
fb_neg:
        inc a
        jr nz,fb_no
        ld a,l
        cp 0xC1
        jr c,fb_no
        xor a
        ret
fb_no:
        or 1
        ret

; mul8s: HL = B * C, both signed, |B + C| and |B - C| no more than 127.
; Quarter squares: B*C = (B+C)^2/4 - (B-C)^2/4, both read from the sq4
; table - about 140 T, against about 450 T for a shift-and-add loop.
mul8s:
        ld a,b
        add a,c                 ; B + C
        jp p,mq1
        neg
mq1:
        ld l,a
        ld h,sq4/256
        ld e,(hl)
        set 7,l
        ld d,(hl)               ; DE = (B+C)^2 / 4
        ld a,b
        sub c                   ; B - C
        jp p,mq2
        neg
mq2:
        ld l,a
        ld c,(hl)
        set 7,l
        ld b,(hl)               ; BC = (B-C)^2 / 4
        ex de,hl
        or a
        sbc hl,bc
        ret

; rnd: A = a pseudo-random byte (16-bit xorshift)
rnd:
        push hl
        ld hl,(seed)
        ld a,h
        rra
        ld a,l
        rra
        xor h
        ld h,a
        ld a,l
        rra
        ld a,h
        rra
        xor l
        ld l,a
        xor h
        ld h,a
        ld (seed),hl
        pop hl
        ret

; ---------------------------------------------------------------------
; BUMP (IX = car a, HL = car b): if they overlap, they bounce apart.
; (Car b is copied to "tb" and back, so only IX is needed - IY belongs
; to the ROM's interrupt routine and must not be touched.)
; tb mirrors offsets 1..9 of a car: x(2), y frac, y(2), vx(2), vy(2)
; ---------------------------------------------------------------------
TB_X    equ tb
TB_Y    equ tb+3
TB_VX   equ tb+5
TB_VY   equ tb+7
KICK    equ 0x00C0          ; bounce speed: 0.75 pixels a frame
bump:
        ld (bump_b),hl
        inc hl                  ; quick look: are they within 11 pixels in x?
        ld a,(ix+C_X)
        sub (hl)
        ld e,a
        inc hl
        ld a,(ix+C_X+1)
        sbc a,(hl)
        ld d,a                  ; DE = ax - bx
        ld a,e
        add a,11                ; within 11 means 0..22 after adding 11
        ld e,a
        ld a,d
        adc a,0
        ret nz
        ld a,e
        cp 23
        ret nc
        inc hl                  ; ... and in y?
        inc hl
        ld a,(ix+C_Y)
        sub (hl)
        ld e,a
        inc hl
        ld a,(ix+C_Y+1)
        sbc a,(hl)
        ld d,a
        ld a,e
        add a,11
        ld e,a
        ld a,d
        adc a,0
        ret nz
        ld a,e
        cp 23
        ret nc
        ld hl,(bump_b)          ; touching: copy car b out to work on it
        inc hl
        ld de,tb
        ld bc,9
        ldir
        ld l,(ix+C_X)           ; dx = a - b
        ld h,(ix+C_X+1)
        ld de,(TB_X)
        or a
        sbc hl,de
        ld (bdx),hl
        call abs_hl
        ld de,12
        or a
        sbc hl,de
        ret nc                  ; 12 or more apart sideways: not touching
        ld l,(ix+C_Y)           ; dy = a - b
        ld h,(ix+C_Y+1)
        ld de,(TB_Y)
        or a
        sbc hl,de
        ld (bdy),hl
        call abs_hl
        ld de,12
        or a
        sbc hl,de
        ret nc
        ld hl,(bumps)           ; touching: count it (the tests read this)
        inc hl
        ld (bumps),hl
        ; touching: bounce apart. Along whichever way they are further
        ; apart, each car is kicked away from the other at KICK speed and
        ; nudged 2 pixels; their speed the other way is kept.
        ld hl,(bdx)
        call abs_hl
        push hl
        ld hl,(bdy)
        call abs_hl
        pop de                  ; HL = |dy|, DE = |dx|
        or a
        sbc hl,de
        jr c,bu_x
        ld hl,(bdy)             ; along y: a below b (dy >= 0) goes down
        ld de,2
        ld bc,KICK
        bit 7,h
        jr z,bu_y1
        ld de,0xFFFE
        ld bc,0x10000-KICK
bu_y1:
        ld (ix+C_VY),c          ; a: kicked away
        ld (ix+C_VY+1),b
        ld hl,0                 ; b: kicked the other way
        or a
        sbc hl,bc
        ld (TB_VY),hl
        ld l,(ix+C_Y)           ; and nudged apart
        ld h,(ix+C_Y+1)
        add hl,de
        ld (ix+C_Y),l
        ld (ix+C_Y+1),h
        ld hl,(TB_Y)
        or a
        sbc hl,de
        ld (TB_Y),hl
        jr bu_write
bu_x:
        ld hl,(bdx)             ; along x: a right of b (dx >= 0) goes right
        ld de,2
        ld bc,KICK
        bit 7,h
        jr z,bu_x1
        ld de,0xFFFE
        ld bc,0x10000-KICK
bu_x1:
        ld (ix+C_VX),c
        ld (ix+C_VX+1),b
        ld hl,0
        or a
        sbc hl,bc
        ld (TB_VX),hl
        ld l,(ix+C_X)
        ld h,(ix+C_X+1)
        add hl,de
        ld (ix+C_X),l
        ld (ix+C_X+1),h
        ld hl,(TB_X)
        or a
        sbc hl,de
        ld (TB_X),hl
bu_write:
        ld hl,tb                ; car b back where it lives
        ld de,(bump_b)
        inc de
        ld bc,9
        ldir
        ret

; ---------------------------------------------------------------------
; CAMERA: put your car in the middle of the window
; ---------------------------------------------------------------------
camera:
        ld hl,(cars+C_X)
        ld de,88
        or a
        sbc hl,de
        jr nc,cx_pos
        ld hl,0
cx_pos:
        ld de,MAPW*8-200
        call clamp_hl
        ld (camx),hl
        ld hl,(cars+C_Y)
        ld de,56
        or a
        sbc hl,de
        jr nc,cy_pos
        ld hl,0
cy_pos:
        ld de,MAPH*8-136
        call clamp_hl
        ld (camy),hl
        ret

clamp_hl:
        push hl
        or a
        sbc hl,de
        pop hl
        ret c
        ex de,hl
        ret

; ---------------------------------------------------------------------
; DRAW_TILES: the non-blank tiles in view (from each map row's list) into
; the back buffer, shifted by the camera. Blank table costs nothing.
; ---------------------------------------------------------------------
draw_tiles:
        ld a,(camx)
        and 7
        add a,a
        add a,TAB_HI
        ld b,a                  ; B = shift table page, kept all the way
        ld a,(camy)             ; pick the tile routine for this camy AND 7
        and 7
        ld l,a
        add a,a
        add a,tdraw_table AND 255
        ld e,a
        ld a,0
        adc a,tdraw_table/256
        ld d,a
        ld a,(de)
        ld (dt_call+1),a
        inc de
        ld a,(de)
        ld (dt_call+2),a
        ld a,16                 ; first tile row starts at buffer row 16 - v
        sub l
        push bc
        ld b,a
        ld c,8                  ; byte 1 (x = 8): window column -1
        call buf_addr
        pop bc
        ld (tr_base),hl
        ld hl,(camx)            ; C' = first tile column in view
        srl h
        rr l
        srl h
        rr l
        srl h
        rr l
        ld a,l
        exx
        ld c,a
        exx
        ld hl,(camy)            ; list pointer for the first tile row
        srl h
        rr l
        srl h
        rr l
        srl h
        rr l
        add hl,hl
        ld de,row_index
        add hl,de
        ld (dt_rowp),hl
        ld a,17                 ; 17 rows of tiles
dt_row:
        ld (dt_rows),a
        ld hl,(dt_rowp)         ; this row's list
        ld e,(hl)
        inc hl
        ld d,(hl)
        inc hl
        ld (dt_rowp),hl
        ex de,hl
        push hl
        exx
        pop hl                  ; HL' = the list
        ld b,(hl)               ; B' = how many tiles in it
        inc hl
        ld a,b
        or a
        jr z,dt_row_done
dt_tile:
        ld a,(hl)               ; column
        inc hl
        sub c                   ; - first column in view
        jr c,dt_skip            ; left of the window
        cp 25
        jr nc,dt_row_done       ; right of it: the rest of the list is too
        ex af,af'               ; A' = column within the window
        ld a,(hl)               ; tile number
        inc hl
        exx
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
        ex af,af'
        ld hl,(tr_base)         ; HL = this tile's top-left byte
        add a,l
        ld l,a
dt_call:
        call 0                  ; (patched) tdraw_0 .. tdraw_7
        exx
        dec b
        jr nz,dt_tile
        jr dt_row_done
dt_skip:
        inc hl
        dec b
        jr nz,dt_tile
dt_row_done:
        exx
        ld hl,(tr_base)         ; next tile row: 8 pixel rows = 32 bytes on,
        ld a,l                  ; or the next third of the layout
        add a,32
        ld l,a
        jr nc,dt_nt
        ld a,h
        add a,8
        ld h,a
dt_nt:
        ld (tr_base),hl
        ld a,(dt_rows)
        dec a
        jp nz,dt_row
        ret

; ---------------------------------------------------------------------
; DRAW_CAR (IX = car): masked, into the back buffer, if it is in view.
;   buffer = (buffer AND NOT mask) OR ink, for each of 16 rows
; ---------------------------------------------------------------------
draw_car:
        ld l,(ix+C_X)           ; window x = car x - camx
        ld h,(ix+C_X+1)
        ld de,(camx)
        or a
        sbc hl,de
        ld de,15                ; visible if -15 <= wx <= 191
        add hl,de
        ld a,h
        or a
        ret nz
        ld a,l
        cp 191+15+1
        ret nc
        ld (wxu),a              ; u = wx + 15, 0..206 (never negative)
        ld l,(ix+C_Y)
        ld h,(ix+C_Y+1)
        ld de,(camy)
        or a
        sbc hl,de
        ld de,15                ; visible if -15 <= wy <= 127
        add hl,de
        ld a,h
        or a
        ret nz
        ld a,l
        cp 127+15+1
        ret nc
        inc a                   ; buffer row = 16 + wy = 1 + (wy + 15)
        ld (dc_row0),a
        ; picture: car_data + kind*1024 + heading*64
        ld a,(ix+C_ANG)
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
        add hl,hl
        ld a,(ix+C_KIND)
        add a,a
        add a,a
        add a,h
        ld h,a
        ld de,car_data
        add hl,de
        ex de,hl                ; DE = this car's rows
        ld a,(ix+C_ANG)         ; skip the empty rows at the top: car_rows
        rrca                    ; says the first row and how many
        rrca
        and 15
        add a,a
        add a,car_rows AND 255
        ld l,a
        ld a,0
        adc a,car_rows/256
        ld h,a
        ld a,(hl)
        ld (dc_first),a
        inc hl
        ld a,(hl)
        ld (dc_count),a
        ld a,(dc_first)
        add a,a
        add a,a
        add a,e                 ; DE += first * 4
        ld e,a
        jr nc,dc_f1
        inc d
dc_f1:
        ; shift table t = (-wx) AND 7 = (15 - u) AND 7
        ; first byte = window column (wx - 1) DIV 8, + 2 = u DIV 8
        ld a,(wxu)
        ld c,a
        ld a,15
        sub c
        and 7
        add a,a
        add a,TAB_HI
        ld (dc_tab),a
        ld a,c                  ; C = byte * 8 for buf_addr
        and 0xF8
        ld c,a
        ld a,(dc_first)         ; buffer row = 1 + (wy + 15) + first
        ld b,a
        ld a,(dc_row0)
        add a,b
        ld b,a
        call buf_addr
        ld a,(dc_tab)
        ld b,a
        ld a,(dc_count)
dc_loop:
        ld (dc_n),a
        ; left byte of the row: columns k and k+1
        ld a,(de)               ; mask byte
        inc de
        ld c,a
        ld a,(bc)               ;   cut the hole: column k ...
        cpl
        and (hl)
        ld (hl),a
        inc b
        inc l
        ld a,(bc)               ;   ... and column k+1
        cpl
        and (hl)
        ld (hl),a
        ld a,(de)               ; ink byte
        inc de
        ld c,a
        ld a,(bc)               ;   ink: column k+1 ...
        or (hl)
        ld (hl),a
        dec b
        dec l
        ld a,(bc)               ;   ... and column k
        or (hl)
        ld (hl),a
        inc l
        ; right byte of the row: columns k+1 and k+2
        ld a,(de)               ; mask byte
        inc de
        ld c,a
        ld a,(bc)               ;   cut the hole: column k ...
        cpl
        and (hl)
        ld (hl),a
        inc b
        inc l
        ld a,(bc)               ;   ... and column k+1
        cpl
        and (hl)
        ld (hl),a
        ld a,(de)               ; ink byte
        inc de
        ld c,a
        ld a,(bc)               ;   ink: column k+1 ...
        or (hl)
        ld (hl),a
        dec b
        dec l
        ld a,(bc)               ;   ... and column k
        or (hl)
        ld (hl),a
        dec l
        inc h                   ; next pixel row down (screen layout)
        ld a,h
        and 7
        jr nz,dc_same
        ld a,l                  ; crossed into the next character row
        add a,32
        ld l,a
        jr c,dc_same
        ld a,h
        sub 8
        ld h,a
dc_same:
        ld a,(dc_n)
        dec a
        jp nz,dc_loop
        ret

; ---------------------------------------------------------------------
; COPY_TO_SCREEN: the window part of the buffer -> the screen, with the
; POP/PUSH code that make_copier wrote at COPIER. It moves the stack pointer, so
; interrupts are off while it runs: it starts just after an interrupt and
; takes well under a frame, so no interrupt is missed. IY goes back to the
; value the ROM's interrupt routine needs.
; ---------------------------------------------------------------------
copy_to_screen:
        di
        ld (save_sp),sp
        jp COPIER
copy_done:
        ld sp,(save_sp)
        ld iy,23610
        ei
        ret

; CLEAR_BUFFER: zero buffer rows 16..143 (what the window shows) with PUSH.
; In the screen layout those are: third 2 character rows 0-1, all of
; third 1, third 0 character rows 2-7 - cleared in that order, so anything
; an interrupt pushes below SP lands on bytes still to be cleared, or on
; margin rows that are never shown.
clear_buffer:
        ld (save_sp),sp
        ld de,0
        ld b,8
        ld hl,BUF+0x1000+64     ; third 2: 64 bytes on each of 8 lines
cb_t2:
        ld sp,hl
        rept 32
        push de
        endm
        inc h
        djnz cb_t2
        ld sp,BUF+0x1000        ; third 1: all 2048 bytes
        ld b,16
cb_t1:
        rept 64
        push de
        endm
        djnz cb_t1
        ld b,8
        ld hl,BUF+0x0800        ; third 0: bytes 64..255 of each line
cb_t0:
        ld sp,hl
        rept 96
        push de
        endm
        dec h
        djnz cb_t0
        ld sp,(save_sp)
        ret

; ---------------------------------------------------------------------
; MAKE_COPIER: write the screen-copy routine into memory at COPIER.
; Code is just bytes, so a program can write code. For each window row,
; twice (12 bytes at a time) it writes:
;   ld sp,<buffer row>  pop af,bc,de,hl,ix,iy   (12 bytes off the buffer)
;   ld sp,<screen row+12> push iy,ix,hl,de,bc,af (12 bytes onto the screen)
; and finally  jp copy_done.  5,635 bytes: too big to carry on the tape
; for nothing, and every address in it is worked out here.
; ---------------------------------------------------------------------
make_copier:
        ld de,COPIER
        xor a
mc_row:
        ld (mc_y),a
        xor a
        call mc_half            ; bytes 0..11 of the row
        ld a,12
        call mc_half            ; bytes 12..23
        ld a,(mc_y)
        inc a
        cp WIN_H
        jr nz,mc_row
        ld a,0xC3               ; jp copy_done
        ld (de),a
        inc de
        ld hl,copy_done
        ld a,l
        ld (de),a
        inc de
        ld a,h
        ld (de),a
        ret
mc_half:                        ; A = 0 or 12: which half of the row
        ld (mc_h),a
        add a,2                 ; source: buffer row 16 + y, byte 2 + half
        add a,a
        add a,a
        add a,a
        ld c,a
        ld a,(mc_y)
        add a,16
        ld b,a
        call buf_addr
        call mc_ldsp
        ld hl,mc_pops
        ld bc,8
        ldir
        ld a,(mc_h)             ; destination: screen row 32 + y, byte 4 + half,
        add a,WIN_COL           ; plus 12 because PUSH works downwards
        add a,a
        add a,a
        add a,a
        ld c,a
        ld a,(mc_y)
        add a,WIN_Y
        ld b,a
        call scr_addr
        ld bc,12
        add hl,bc
        call mc_ldsp
        ld hl,mc_pushes
        ld bc,8
        ldir
        ret
mc_ldsp:                        ; write "ld sp,HL"
        ld a,0x31
        ld (de),a
        inc de
        ld a,l
        ld (de),a
        inc de
        ld a,h
        ld (de),a
        inc de
        ret
mc_pops:   db 0xF1,0xC1,0xD1,0xE1,0xDD,0xE1,0xFD,0xE1   ; pop af,bc,de,hl,ix,iy
mc_pushes: db 0xFD,0xE5,0xDD,0xE5,0xE5,0xD5,0xC5,0xF5   ; push iy,ix,hl,de,bc,af

; buf_addr: B = buffer row, C = x  ->  HL = address (screen layout at BUF)
buf_addr:
        call scr_addr
        ld a,h
        add a,BUF_HI-0x40
        ld h,a
        ret

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
; the starting line-up (copied into "cars" at the start)
;   x frac, x, y frac, y, vx, vy, heading, buttons, friction,
;   waypoint, offset x, offset y, mistake, kind of mistake, think,
;   PACE, REACT, ERR, picture, steering, ease off
; CPU A: faster (6 of 8), thinks every 4 frames, few mistakes.
; CPU B: slower (5 of 8), thinks every 8 frames, more mistakes.
; CPU C: faster (6 of 8), thinks every 8 frames, some mistakes.
; CPU D: slower (5 of 8), thinks every 4 frames but sloppy - the most mistakes.
; ---------------------------------------------------------------------
cars_init:
        db 0
        dw STARTX
        db 0
        dw STARTY
        dw 0,0
        db STARTA,0,3, 0,0,0, 0,0,0, 8,0,0, 0,0,0
        db 0
        dw CPU0X
        db 0
        dw CPU0Y
        dw 0,0
        db STARTA,0,3, CPU0WP,0,0xFC, 0,0,0, 6,0,14, 1,0,0
        db 0
        dw CPU1X
        db 0
        dw CPU1Y
        dw 0,0
        db STARTA,0,3, CPU1WP,0,4, 0,0,0, 5,1,24, 2,0,0
        db 0
        dw CPU2X
        db 0
        dw CPU2Y
        dw 0,0
        db STARTA,0,3, CPU2WP,0,0xFE, 0,0,0, 6,1,18, 3,0,0
        db 0
        dw CPU3X
        db 0
        dw CPU3Y
        dw 0,0
        db STARTA,0,3, CPU3WP,0,2, 0,0,0, 5,0,34, 4,0,0
cars_init_end:

; ---------------------------------------------------------------------
; variables
; ---------------------------------------------------------------------
cars:     defs NCARS*C_SIZE     ; you, CPU A, B, C, D
camx:     dw 0
camy:     dw 0
fshift:   db 3
last_frame: db 0
dt:       db 0
renders:  dw 0
ticks:    dw 0
mistakes: dw 0
race_on:  db 0
seed:     dw 0x1234
hx:       db 0
hy:       db 0
tdx:      db 0
tdy:      db 0
cross:    dw 0
dot:      dw 0
msign:    db 0
bu_off:   db 0
wxu:      db 0
bump_b:   dw 0
bdx:      dw 0
bdy:      dw 0
bumps:    dw 0
tb:       defs 9
dc_row0:  db 0
dc_ink:   db 0
dc_first: db 0
dc_count: db 0
dist_cur: dw 0
bo_n:     db 0
mc_y:     db 0
mc_h:     db 0
dc_n:     db 0
dt_rows:  db 0
save_sp:  dw 0
last_shown: db 0
tr_base:  dw 0
dt_rowp:  dw 0
dc_tab:   db 0

        include "data.asm"
        include "world.asm"
        include "gen_tiles.asm"
        include "gen_bumps.asm"
code_end:

        if MAPW - 72
        .error surface assumes the map is 72 tiles (9 bytes of bits) wide
        endif
        if NCARS*C_SIZE - (cars_init_end - cars_init)
        .error cars_init does not hold NCARS records
        endif
        if code_end > BUF_HI*256
        .error code and data run into the back buffer
        endif

        end start
