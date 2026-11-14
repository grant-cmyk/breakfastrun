; =====================================================================
; BREAKFAST RUN - STAGE 6: the race screen (side panel, message bar, lap strip)
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
BUFC    equ BUF+0x1280  ; race-order variables, in the buffer's unused bottom rows
        ; (defined up here: code before hud.asm uses equs built on it, and pasmo
        ; would give that code a stale first-pass value)
cloth_pat equ BUFC+64    ; 4 kinds of dotted cloth line, 8 bytes each (32-aligned)
TAB_HI  equ 0xD8        ; shift tables: 16 pages 0xD8..0xE7
PACE_FR equ 3           ; show a new picture every 3 TV frames, steadily
NCARS   equ 5           ; you + 4 computer cars
LAPS    equ 3           ; laps in a race
REACH   equ 24          ; a computer car has reached a waypoint within this (|dx|+|dy|)
COPIER  equ 0xE800      ; the screen-copy code is WRITTEN HERE at start-up (5.6 KB)
WIN_COL equ 1           ; window on screen: columns 1..22 (22 bytes wide)
        include "options.asm"   ; OPT_TALL (always 1 now: which tables sit in the program)
WIN_Y   equ 8                   ; the window: 176 x 144, pixel rows 8..151 - everything above
WIN_W   equ 22                  ; the driver strip but the frame's top band (Grant, 14 Nov 2026:
WIN_H   equ 144                 ; "take the very top row of the display as well"; it was 120
                                ; high on 9 Nov, 128 and 136 earlier on 14 Nov)
MSG_ROW equ 23                  ; the message bar: the bottom row, until the new layout is built
BUF_TOP equ 8                   ; the window's first line in the back buffer. The map's tiles
                                ; are drawn up to 8 lines past its last line: buffer rows
                                ; 152-159 are left free for that, and the tables kept in the
                                ; buffer start at row 160 (a taller window once drew tiles
                                ; over them: "the road shape has broken", Grant, 14 Nov 2026)
BAND_Y  equ (WIN_Y+WIN_H)/8+1    ; the text rows under the window: LAP, TIME, BEST
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
C_PACE  equ 19          ; computer: accelerates on PACE of every 16 frames
C_REACT equ 20          ; computer: thinking turns it lets go by (0 = every 4 frames)
C_ERR   equ 21          ; computer: chance of a mistake at each waypoint /256
C_KIND  equ 22          ; which picture: 0 you, 1 CPU A, 2 CPU B
C_STEER equ 23          ; computer: steering it decided on (bit0 L, bit1 R)
C_EASE  equ 24          ; computer: 1 = target well off to the side, ease off
C_LAPS  equ 25          ; times past the start line (1 = on lap 1)
C_LST   equ 26          ; race clock when it last crossed the line (2 bytes)
C_SIZE  equ 28

CT_L    equ 1
CT_R    equ 2
CT_GO   equ 4
CT_BRK  equ 8

        org 0x5F00              ; big-car frames, below the program (8.25 KB, loaded
        include "bigcars.asm"   ; with it in one block; the loader's CLEAR goes below)
        if $ > 0x8000
        .error the big cars run past 0x8000
        endif
        org 32768

start:                          ; once, when the program is loaded: the set-up
        jp start_once           ; runs from the start-up area (it is needed once)
new_race:                       ; every race (Q after the finish comes here)
        ld hl,race_vars         ; every race starts from zero (a new race
        ld de,race_vars+1       ; after FINISHED jumps back to here)
        ld bc,race_vars_end-race_vars-1
        ld (hl),0
        ldir
        ld hl,shown_order       ; "nothing shown yet" for the race order
        ld b,NCARS
st_so:
        ld (hl),0xFF
        inc hl
        djnz st_so
        ld hl,0xFFFF
        ld (best_lap),hl
        call gaps_reset
        call hud_init
        ld hl,cars_init         ; copy the starting records into place
        ld de,cars
        ld bc,NCARS*C_SIZE
        ldir
        ld a,(FRAMES)
        ld (last_frame),a

; ---------------------------------------------------------------------
; MAIN LOOP
; ---------------------------------------------------------------------
main:
        ld a,(race_over)        ; the race is over: the chequered flag, once,
        cp 1                    ; then everything stops until Q (Grant)
        jr c,main_go
        jr nz,main_wait
        inc a
        ld (race_over),a
        call race_box
main_wait:
        call hud_over           ; Q: a new race
        halt
        jr main
main_go:
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
        ; the computer cars MOVE once a picture: all its TV frames in one call
        ; (physics steps the speed and position ph_steps times). They are only
        ; seen once a picture, so they look the same as when each was moved
        ; every frame - and the push, the skid and the edges are worked out
        ; once, not three times (the speed pass, 13 Nov 2026: 26k T -> 14k).
        ; They still THINK frame by frame (tick), and your car moves every frame.
        ld a,(dt)
        ld (ph_steps),a
        ld ix,cars+C_SIZE
        ld b,NCARS-1
cpu_move:
        push bc
        call physics
        ld de,C_SIZE
        add ix,de
        pop bc
        djnz cpu_move
        call bumps_o            ; cars that touch, and the cereal O's

        call race_progress      ; your waypoints and laps, everyone's progress
        call hud_update         ; the panel, message bar and lap strip
        call camera
        call cloth_fill         ; the tablecloth, as the camera sees it
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
        ld a,(lt_on)            ; the start lights, while they are up
        or a
        call nz,lights_draw
        call nos_draw           ; the NOS canisters you hold, in the window's corner
        ld a,(last_shown)       ; did this picture run over the rhythm?
        ld b,a
        ld a,(FRAMES)
        sub b
        ld hl,pace
        cp (hl)
        jr c,ws_in_time
        jr z,ws_in_time
        ld a,(pace_skip)        ; GO's picture is a busy one-off: late or not,
        or a                    ; it does not set the pace
        jr nz,ws_skip
        ld (hl),PACE_FR+1       ; yes: settle on 4 frames for a while (a
        ld a,25                 ; steady 4 looks smoother than 3,4,3,4)
        ld (pace_hold),a
        jr wait_show
ws_skip:
        xor a
        ld (pace_skip),a
ws_in_time:
        ld a,(pace_hold)        ; in time: after a while at 4, try 3 again
        or a
        jr z,wait_show
        dec a
        ld (pace_hold),a
        jr nz,wait_show
        ld (hl),PACE_FR
wait_show:
        call snd_wait           ; wait - playing the engine meanwhile, or HALT
        ld a,(last_shown)       ; since the last picture went up
        ld b,a
        ld a,(FRAMES)
        sub b
        ld hl,pace
        cp (hl)
        jr c,wait_show
        ld a,(FRAMES)
        ld (last_shown),a
        call copy_to_screen     ; straight after the interrupt, ahead of the beam
        call snd_picture        ; this picture's engine pitch; the crash fades
        ld hl,(renders)
        inc hl
        ld (renders),hl
        jp main

; tick: one TV frame - read keys, let the computer drive, move, bump
tick:
        ld hl,(ticks)
        inc hl
        ld (ticks),hl
        ld a,(race_on)          ; the race clock runs from your first Q to
        or a                    ; the finish
        jr z,tk_clock
        ld a,(race_over)
        or a
        jr nz,tk_clock
        ld hl,(race_time)
        inc hl
        ld (race_time),hl
tk_clock:
        ld hl,BOOST_T           ; the NOS burns down, a frame at a time
        ld a,(hl)
        or a
        jr z,tk_nb
        dec (hl)
tk_nb:
        call read_keys          ; your buttons -> your car's C_CTRL
        ld a,(race_on)          ; before green: Q starts the lights, but your
        or a                    ; car stays on the grid
        jr nz,tk_on
        ld (cars+C_CTRL),a
tk_on:
        ld a,(cars+C_LAPS)      ; finished: no more buttons - your car rolls
        cp LAPS+1               ; to a stop a little over the line
        jr c,tk_you
        xor a
        ld (cars+C_CTRL),a
tk_you:
        ld ix,cars              ; you: every TV frame
        ld a,1
        ld (ph_steps),a
        call physics
        ld ix,cars+C_SIZE       ; the computer cars THINK on alternate frames
        ld b,NCARS-1            ; (cars 2 and 4 on one, 1 and 3 on the other);
tk_ai:                          ; they are moved once a picture, a whole
        push bc                 ; picture's frames at a time (main: cpu_move).
        ld a,(ix+C_LAPS)        ;
        cp LAPS+1               ; A computer car that has finished rolls to a
        jr nc,tk_in             ; stop too, while the others come in
        ld a,(ticks)
        add a,(ix+C_KIND)
        and 1
        call z,ai_drive
        jr tk_rest
tk_in:
        ld (ix+C_CTRL),0
tk_rest:
        ld de,C_SIZE
        add ix,de
        pop bc
        djnz tk_ai
        ret
; BUMPS_O: once a picture, after everyone has moved (it was on alternate TV
; frames: the computer cars only move once a picture now, and nobody moves
; far enough in a picture to get through a car or an O untested - the speed
; pass of 14 Nov 2026): every pair of cars (gen_bumps.asm), then the O's
bumps_o:
        call bump_all
        ld ix,cars              ; and off the cereal O's
        ld b,NCARS
tk_o:
        push bc
        ld a,(ix+C_KIND)        ; a computer car that has bounced off O's O_FREE times
        or a                    ; since its last waypoint is wedged against them (Grant,
        jr z,tk_o0              ; 14 Nov 2026: "the tank got stuck ... in between the
        add a,o_hits AND 255    ; loops/circles and could not get out"): the O's let it
        ld l,a                  ; through until it reaches the waypoint
        ld a,0
        adc a,o_hits/256
        ld h,a
        ld a,(hl)
        cp O_FREE
        jr nc,tk_o1
        push hl
        call o_check
        pop hl
        jr nc,tk_o1
        inc (hl)
        jr tk_o1
tk_o0:
        call o_check
        jr nc,tk_o1
        ld a,1                  ; you: the crew chief may say so
        ld (HIT_O),a
tk_o1:
        ld de,C_SIZE
        add ix,de
        pop bc
        djnz tk_o
        ret

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
        jr nz,rk_qup
        set 2,c
        ld a,(q_free)           ; first press of Q starts the lights - a new
        or a                    ; press: the Q that started this race (after
        jr z,rk3                ; the last one finished) has to be let go.
        ld a,(start_go)         ; (the race itself starts on green:
        or a                    ; start_lights in hud.asm)
        jr nz,rk3
        inc a
        ld (start_go),a
        ld a,(FRAMES)
        ld (start_f0),a
        jr rk3
rk_qup:
        ld a,1
        ld (q_free),a
rk3:
        ld a,0xFD               ; A
        in a,(0xFE)
        bit 0,a
        jr nz,rk4
        set 3,c
rk4:
        ld a,c
        ld (cars+C_CTRL),a
        ld a,0x7F               ; SPACE: fire a NOS canister (a new press)
        in a,(0xFE)
        and 1
        ld hl,SPACE_UP
        jr nz,rk_spup
        cp (hl)                 ; (A = 0: was it up?)
        ret z
        ld (hl),a
        jp nos_fire
rk_spup:
        ld (hl),a
        ret

; ---------------------------------------------------------------------
; PHYSICS (IX = car): buttons -> steering and push -> friction -> move
; ---------------------------------------------------------------------
physics:
        ld e,(ix+C_CTRL)
        ld a,(ph_steps)         ; steering: one heading step per frame
        ld d,a
        bit 0,e
        jr z,ph_nl
        ld a,(ix+C_ANG)
        sub d
        and 63
        ld (ix+C_ANG),a
ph_nl:
        bit 1,e
        jr z,ph_nr
        ld a,(ix+C_ANG)
        add a,d
        and 63
        ld (ix+C_ANG),a
ph_nr:
        ld a,(ix+C_KIND)        ; you: no push here (the grip model has its own)
        or a
        jp z,ph_snap
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
        ld a,(ix+C_KIND)        ; look at the ground under the car now and then
        or a                    ; (it cannot change much in a few frames): you,
        ld a,(ticks)            ; one frame in 4; a computer car, every other
        jr z,ph_s4              ; picture (they take turns)
        ld a,(renders)
        add a,(ix+C_KIND)
        or 2
ph_s4:
        and 3
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
        ld a,(ix+C_KIND)        ; you: the grip model works out your speed
        or a                    ; (grip.asm); below only moves the car - no
        jr nz,ph_cpu            ; push here, and no friction (fshift 0)
        call you_grip
        xor a
        ld (fshift),a
        ld d,a
        ld e,a
        ld b,a
        ld c,a
        jr ph_nb
ph_cpu:
        call skid               ; fast and turning: it slides (DE, BC, fshift)
        ld a,(ix+C_KIND)        ; NOS: you, twice the push (so twice the top
        or a                    ; speed while it burns)
        jr nz,ph_nb
        ld a,(BOOST_T)
        or a
        jr z,ph_nb
        sla e
        rl d
        sla c
        rl b
ph_nb:
        ld (ph_px),de           ; the pushes, kept for the second frame
        ld (ph_py),bc
        ; ---- x: speed += push, friction, position += speed; each value is
        ;      read from the car record once and written back once; all of
        ;      it ph_steps times (2 for a computer car) ----
        ld l,(ix+C_VX)
        ld h,(ix+C_VX+1)
        ld a,(ph_steps)
phx_step:
        ld (ph_cnt),a
        ld de,(ph_px)
        add hl,de
        call friction
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
        ld a,(ph_cnt)
        dec a
        jr nz,phx_step
        ld (ix+C_VX),l
        ld (ix+C_VX+1),h
        ld a,(ix+C_X+1)
        cp (MAPW*8-16)/256      ; keep inside the world (x 0..MAPW*8-17): a
        jr c,ph_xok             ; high byte below the limit's is fine (the
        jr nz,ph_xout           ; usual case); above it, or negative: out
        ld a,(ix+C_X)
        cp (MAPW*8-16) AND 255
        jr c,ph_xok
ph_xout:
        ld hl,0                 ; out at the top/left (the position went
        bit 7,(ix+C_X+1)        ; negative): 0; at the far edge: the limit.
        jr nz,ph_xset           ; (It went by the speed's sign: a car pushed back
                                ; while past the far edge was sent to 0 - Jane
                                ; got stuck at the bottom, 10 Nov 2026)
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
        ld a,(ph_steps)
phy_step:
        ld (ph_cnt),a
        ld de,(ph_py)
        add hl,de
        call friction
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
        ld a,(ph_cnt)
        dec a
        jr nz,phy_step
        ld (ix+C_VY),l
        ld (ix+C_VY+1),h
        ld a,(ix+C_Y+1)
        cp (MAPH*8-16)/256
        jr c,ph_yok
        jr nz,ph_yout
        ld a,(ix+C_Y)
        cp (MAPH*8-16) AND 255
        jr c,ph_yok
ph_yout:
        ld hl,0                 ; out at the top/left (the position went
        bit 7,(ix+C_Y+1)        ; negative): 0; at the far edge: the limit.
        jr nz,ph_yset           ; (It went by the speed's sign: a car pushed back
                                ; while past the far edge was sent to 0 - Jane
                                ; got stuck at the bottom, 10 Nov 2026)
        ld hl,MAPH*8-17
ph_yset:
        ld (ix+C_Y),l
        ld (ix+C_Y+1),h
        xor a
        ld (ix+C_VY),a
        ld (ix+C_VY+1),a
ph_yok:
        ret

; PH_SNAP (you): the car can point 64 ways but has 16 pictures, so between pictures it
; ran up to 11 degrees off the way its picture points - which looks like sliding to one
; side for ever (Grant, 14 Nov 2026: "the car drift is still there ... once the car is
; facing a direction it should stay true to the direction it is facing"). So when you let
; go of the steering, the heading carries on the way you were turning, a step a frame, to
; the next heading that has a picture, and stops there: the car goes where it points.
ph_snap:
        ld a,e
        and CT_L+CT_R
        jr z,ph_sn1
        rra                     ; steering: remember which way (left: -1, right: +1)
        sbc a,a
        or 1
        ld (ph_dir),a
        jp ph_push_set
ph_sn1:
        ld a,(ix+C_ANG)
        ld d,a
        and 3
        jp z,ph_push_set        ; on a pictured heading already
        ld a,(ph_dir)
        add a,d
        and 63
        ld (ix+C_ANG),a
        jp ph_push_set

; ---------------------------------------------------------------------
; SKID (IX = car; DE, BC = this frame's push): friction takes 1/8 of the speed
; each frame, sideways as much as forwards, so a car grips. Fast and turning,
; halve both the friction and the push: the top speed is the same (push /
; friction), but the sideways speed now dies away half as fast - the car
; keeps sliding the way it was going and drifts round the corner (Grant,
; 10 Nov 2026). From SKID_V2 the same again: sideways speed dies at 1/32 a
; frame, then 1/64 - a long slide (Grant asked for more). No multiplying; only while
; turning fast.
; ---------------------------------------------------------------------
SKID_VC   equ 256               ; the computer cars: from 1.0 px a frame, as before
SKID_STEP equ 64                ; and more for each 0.25 faster (Grant: more skid)
SKID_N    equ 3                 ; at most 3 steps: sideways speed dies at 1/64
skid:                           ; (the computer cars: you have the grip model)
        ld a,(ix+C_CTRL)        ; a computer car: only while turning fast
        and CT_L+CT_R
        ret z
        call sk_speed           ; HL = speed
        push de
        ld de,SKID_VC
        or a
        sbc hl,de
        pop de
        ret c                   ; slow: it grips
        ld a,SKID_N             ; up to SKID_N steps, each SKID_STEP faster
skc_lv:
        call sk_half
        push de
        ld de,SKID_STEP
        or a
        sbc hl,de
        pop de
        ret c
        dec a
        jr nz,skc_lv
        ret
sk_half:                        ; half the push (DE, BC) and half the friction
        sra d
        rr e
        sra b
        rr c
        push hl
        ld hl,fshift
        inc (hl)
        pop hl
        ret
sk_speed:                       ; HL = speed, roughly: the larger of |vx|, |vy|
        push bc                 ; plus half the smaller (BC, DE kept)
        push de
        ld l,(ix+C_VX)
        ld h,(ix+C_VX+1)
        call abs_hl
        push hl
        ld l,(ix+C_VY)
        ld h,(ix+C_VY+1)
        call abs_hl
        pop de
        or a
        sbc hl,de
        add hl,de
        jr nc,sks_1
        ex de,hl
sks_1:
        srl d
        rr e
        add hl,de
        pop de
        pop bc
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

; friction: HL = HL - HL/2^fshift; tiny speeds become exactly 0
friction:
        ld a,(fshift)           ; 0: none (you - the grip model did it)
        or a
        ret z
        ld d,h
        ld e,l
        sra d                   ; DE = HL / 4 off the road, / 8 on it,
        rr e                    ; / 8, / 16 or / 32 while sliding
        sra d
        rr e
        ld a,(fshift)           ; (RR sets the flags: compare after each)
        cp 3
        jr c,fr_div             ; 2: / 4
        sra d
        rr e
        cp 3
        jr z,fr_div             ; 3: / 8
        sra d                   ; 4: / 16
        rr e
        cp 5
        jr c,fr_div
        sra d                   ; 5: / 32 (a long slide on the road)
        rr e
        cp 6
        jr c,fr_div
        sra d                   ; 6: / 64 (the longest)
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
        call manhattan          ; reached it?  (|dx| + |dy| < its reach)
        push hl
        call ai_style           ; HL -> this car's driving style
        ld e,(hl)               ; S_REACH: turns in for the next one this far out
        ld d,0
        pop hl
        or a
        sbc hl,de
        jr nc,ai_check_next
        pop bc
        pop de
        call next_waypoint      ; yes: aim at the next one
        call wp_delta
        jr ai_have_target
ai_check_next:
        ; overshot it?  if the NEXT waypoint is nearer, move on (no U-turns).
        ; Only worth asking when the current one is near (within 64).
        ld de,64-REACH
        push hl
        or a
        sbc hl,de
        pop hl
        jr nc,ai_keep
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
        ld bc,REACH
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
        jr nz,ai_ease_set       ; behind it: everyone eases off
        push hl
        call ai_style
        inc hl
        inc hl
        inc hl
        ld a,(hl)               ; S_EASE: 0 late braker, 1 at 45 deg, 2 at 27
        ld (ai_s),a
        ld hl,(cross)
        call abs_hl
        ex de,hl
        pop hl
        ld a,(ai_s)
        or a
        jr z,ai_ease_off        ; the late braker: only when it is behind
        dec a
        jr z,ai_e45
        ex de,hl                ; |cross| * 2 > dot: about 27 degrees off
        add hl,hl
        ex de,hl
ai_e45:
        or a
        sbc hl,de
        jr c,ai_ease_set
ai_ease_off:
        ld (ix+C_EASE),0
ai_ease_set:
        ld hl,(dot)
        ; straight on if ahead and |cross| * 4 < dot  (within about 14 degrees)
        bit 7,h
        jr nz,ai_turn
        call ai_style
        inc hl
        inc hl
        inc hl
        inc hl
        ld b,(hl)               ; S_FUSS: 2 smooth (lets 14 deg go), 3 twitchy (7)
        ld hl,(cross)
        call abs_hl
ai_fuss:
        add hl,hl
        djnz ai_fuss
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
        ld a,(ticks)            ; every other one of its own frames
        and 2
        jr z,ai_go
        ld b,0
ai_go:
        ld a,(ix+C_STEER)
        or b
ai_set:
        ld (ix+C_CTRL),a
        ret

; ai_style (IX): HL -> the car's driving style, 5 bytes (by its kind).
; Each computer car mixes the ways of driving differently (Grant, 10 Nov):
;   S_REACH  turn-in: how near a waypoint counts as reached (bigger = turns
;            for the next one earlier, cutting the corner)
;   S_LINE   mask, half: how far its line wanders from the centre (tidy..wild)
;   S_EASE   braking: 0 only when the target is behind, 1 at 45 degrees off,
;            2 at about 27 degrees (early and careful)
;   S_FUSS   steering: 2 lets 14 degrees go (smooth), 3 only 7 (twitchy)
; with PACE (throttle, of 8), ERR (mistakes) and REACT in cars_init.
ai_style:
        ld a,(ix+C_KIND)
        ld l,a
        add a,a
        add a,a
        add a,l                 ; kind * 5
        ld l,a
        ld h,0
        ld de,ai_styles-5
        add hl,de
        ret
; pace_gate (IX): A = CT_GO on PACE of every 16 frames, else 0
pace_gate:
        ld a,(ticks)            ; counted in the car's own frames (it thinks
        add a,(ix+C_KIND)       ; on every other one): PACE of 16 of them,
        rrca                    ; the frames off spread evenly through the 16
        and 15                  ; (bit-reversed count) - in a block they made
        push hl                 ; the car surge and slow
        ld l,a
        ld h,0
        push de
        ld de,rev4
        add hl,de
        pop de
        ld a,(hl)
        pop hl
        cp (ix+C_PACE)
        ld a,0
        ret nc
        ld a,CT_GO
        ret


; next_waypoint: move on, pick a new aiming offset, maybe start a mistake
next_waypoint:
        call lap_and_inc
        ld a,(ix+C_KIND)        ; (and its count of O's bounced off starts again)
        add a,o_hits AND 255
        ld l,a
        ld a,0
        adc a,o_hits/256
        ld h,a
        ld (hl),0
        call ai_style           ; S_LINE: how far its line wanders, each way -
        inc hl                  ; a different line through every corner
        ld c,(hl)               ; mask (3, 7 or 15)
        inc hl
        ld b,(hl)               ; half of it, rounded up
        call rnd
        and c
        sub b
        ld (ix+C_OFFX),a
        call rnd
        and c
        sub b
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
        and 7
        add a,4                 ; lasts 4..11 of its frames (8..23 TV frames)
        ld (ix+C_MIST),a
        ld hl,(mistakes)
        inc hl
        ld (mistakes),hl
        ret

; lap_and_inc: the car has reached its waypoint - count a lap if it is the
; first one after the start line, then aim at the next
lap_and_inc:
        call cp_hook            ; a checkpoint?  the gap to the leader
        ld a,(ix+C_WP)
        cp WS
        jr nz,wp_inc
        inc (ix+C_LAPS)
        call lap_timed
        ld a,(ix+C_LAPS)        ; over the line for the last time: note the
        cp LAPS+1               ; order the cars come in
        call z,car_in
wp_inc:                         ; (also used just to look one waypoint ahead)
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
        ld de,wp_tab
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
; O_CHECK (IX = car): the cereal O's are solid (Grant, 10 Nov 2026). An O fills
; one tile; its centre is 4 px into it. Any O centre within 8 px of the car's
; centre is one of the 4 tiles nearest it: look at those in the O map, and on
; the first one close enough, kick the car away from it like a bump - along
; whichever way it is further off - with a crash if it is you.
; ---------------------------------------------------------------------
o_check:
        ld l,(ix+C_X)           ; HL = car centre x - 4
        ld h,(ix+C_X+1)
        ld de,4
        add hl,de
        ld (oc_x),hl
        srl h
        rr l
        srl h
        rr l
        srl h
        rr l
        ld c,l                  ; C = first tile column
        ld l,(ix+C_Y)
        ld h,(ix+C_Y+1)
        add hl,de
        ld (oc_y),hl
        srl h
        rr l
        srl h
        rr l
        srl h
        rr l
        ld b,l                  ; B = first tile row
        call oc_quick           ; (almost always: no O in the 4 tiles - done)
        ret nc
        call oc_try
        ret c
        inc c
        call oc_try
        ret c
        inc b
        call oc_try
        ret c
        dec c
        jr oc_try               ; (the fourth tile: oc_quick sits between)
; OC_QUICK: any O in tiles (C, B), (C+1, B), (C, B+1), (C+1, B+1)? CY = maybe (then
; the full check), NC = none. Both columns' bits read at once with a 2-bit mask
; across the byte pair (most checks end here: ~250 T, against ~1,900 for four
; oc_try's - Grant's speed pass, 10 Nov 2026). The car stays inside the world, so
; the tiles are inside the map (a mask over a row's end reads the next row's
; first byte: at worst a needless full check).
oc_quick:
        ld l,b                  ; HL = omap + row * 9 + column / 8
        ld h,0
        ld e,l
        ld d,h
        add hl,hl
        add hl,hl
        add hl,hl
        add hl,de
        ld a,c
        rrca
        rrca
        rrca
        and 31
        ld e,a
        add hl,de
        ld de,omap
        add hl,de
        ld a,c                  ; DE = the 2-bit mask for columns C, C+1
        and 7
        add a,a
        add a,oq_mask AND 255
        ld e,a
        ld a,0
        adc a,oq_mask/256
        ld d,a
        ld a,(de)
        inc de
        push af                 ; (A' would do, but the cloth fill owns it)
        ld a,(de)
        ld e,a                  ; E = the mask's right byte, D = its left byte
        pop af
        ld d,a
        ld a,(hl)               ; row B: the left byte, the right byte
        and d
        jr nz,oq_maybe
        inc hl
        ld a,(hl)
        and e
        jr nz,oq_maybe
        ld a,l                  ; row B+1: 9 bytes on from each (here: the
        add a,9                 ; right byte, then back one for the left)
        ld l,a
        jr nc,oq_1
        inc h
oq_1:
        ld a,(hl)               ; (the right byte)
        and e
        jr nz,oq_maybe
        dec hl
        ld a,(hl)               ; (the left byte)
        and d
        ret z                   ; (NC: none)
oq_maybe:
        scf
        ret
oq_mask:                        ; column C AND 7 -> left byte, right byte
        db 0xC0,0x00, 0x60,0x00, 0x30,0x00, 0x18,0x00, 0x0C,0x00, 0x06,0x00, 0x03,0x00, 0x01,0x80

oc_try:                         ; tile (C, B): an O, close enough? CY = bounced
        push bc
        ld a,b                  ; byte = omap + row * 9 + column / 8
        cp MAPH
        jr nc,oc_no
        ld l,a
        ld h,0
        ld e,l
        ld d,h
        add hl,hl
        add hl,hl
        add hl,hl
        add hl,de
        ld a,c
        cp MAPW
        jr nc,oc_no
        rrca
        rrca
        rrca
        and 31
        ld e,a
        add hl,de
        ld de,omap
        add hl,de
        ld a,c
        and 7
        inc a
        ld e,a
        ld a,(hl)
oc_bit:
        rla
        dec e
        jr nz,oc_bit
        jr nc,oc_no             ; no O there
        ld l,c                  ; dx = (centre x - 4) - 8 * column
        ld h,0
        add hl,hl
        add hl,hl
        add hl,hl
        ex de,hl
        ld hl,(oc_x)
        or a
        sbc hl,de
        ld (oc_dx),hl
        call oc_near
        jr nc,oc_no
        ld l,b                  ; dy, the same
        ld h,0
        add hl,hl
        add hl,hl
        add hl,hl
        ex de,hl
        ld hl,(oc_y)
        or a
        sbc hl,de
        ld (oc_dy),hl
        call oc_near
        jr nc,oc_no
        call oc_bounce
        pop bc
        scf
        ret
oc_no:
        pop bc
        or a
        ret
oc_near:                        ; HL within -7..7?  CY = yes
        ld de,8
        add hl,de               ; 1..15 if near
        ld a,h
        or a
        ret nz                  ; (NC)
        ld a,l
        or a
        ret z
        cp 16
        ret                     ; CY if below 16
oc_bounce:                      ; kick away along the larger of dx, dy
        ld hl,(oc_dx)
        call abs_hl
        push hl
        ld hl,(oc_dy)
        call abs_hl
        pop de
        or a
        sbc hl,de               ; |dy| - |dx|
        jr nc,ocb_y
        ld hl,(oc_dx)
        ld de,KICK
        ld b,2
        bit 7,h
        jr z,ocb_x1
        ld de,0x10000-KICK
        ld b,0xFE
ocb_x1:
        ld (ix+C_VX),e
        ld (ix+C_VX+1),d
        ld a,b                  ; C = the nudge's sign byte
        rla
        sbc a,a
        ld c,a
        ld a,(ix+C_X)          ; nudged 2 px clear
        add a,b
        ld (ix+C_X),a
        ld a,(ix+C_X+1)
        adc a,c
        ld (ix+C_X+1),a
        jr ocb_snd
ocb_y:
        ld hl,(oc_dy)
        ld de,KICK
        ld b,2
        bit 7,h
        jr z,ocb_y1
        ld de,0x10000-KICK
        ld b,0xFE
ocb_y1:
        ld (ix+C_VY),e
        ld (ix+C_VY+1),d
        ld a,b                  ; C = the nudge's sign byte
        rla
        sbc a,a
        ld c,a
        ld a,(ix+C_Y)          ; nudged 2 px clear
        add a,b
        ld (ix+C_Y),a
        ld a,(ix+C_Y+1)
        adc a,c
        ld (ix+C_Y+1),a
ocb_snd:
        push ix
        pop hl
        ld de,cars
        or a
        sbc hl,de
        ret nz
        ld hl,2*256+6           ; you: a bonk - a note that falls, 6 frames (Grant's pick from
        ld (snd_fxt),hl         ; the Sound Lab, 14 Nov 2026: B2)
        ld hl,5*256+2           ; and the border red, a moment
        jp flash

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
TOUCH   equ 15              ; cars touch closer than this in x and y (12 for the 16 x 16
                            ; cars; 15 for the 20 x 20 ones, Grant 10 Nov 2026)
bump:
        ld (bump_b),hl
        inc hl                  ; quick look: are they within TOUCH-1 pixels in x?
        ld a,(ix+C_X)
        sub (hl)
        ld e,a
        inc hl
        ld a,(ix+C_X+1)
        sbc a,(hl)
        ld d,a                  ; DE = ax - bx
        ld a,e
        add a,TOUCH-1           ; within TOUCH-1 means 0..2*TOUCH-2 after adding it
        ld e,a
        ld a,d
        adc a,0
        ret nz
        ld a,e
        cp 2*TOUCH-1
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
        add a,TOUCH-1
        ld e,a
        ld a,d
        adc a,0
        ret nz
        ld a,e
        cp 2*TOUCH-1
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
        ld de,TOUCH
        or a
        sbc hl,de
        ret nc                  ; TOUCH or more apart sideways: not touching
        ld l,(ix+C_Y)           ; dy = a - b
        ld h,(ix+C_Y+1)
        ld de,(TB_Y)
        or a
        sbc hl,de
        ld (bdy),hl
        call abs_hl
        ld de,TOUCH
        or a
        sbc hl,de
        ret nc
        ld hl,(bumps)           ; touching: count it (the tests read this)
        inc hl
        ld (bumps),hl
        push ix                 ; your car in it?  a crunch
        pop hl
        ld de,cars
        or a
        sbc hl,de
        jr z,bp_you
        ld hl,(bump_b)
        sbc hl,de               ; (carry is clear: cars <= IX)
        jr nz,bp_snd
bp_you:
        ld a,SND_CRASH
        ld (snd_bump),a
        ld hl,10*256+2          ; a crash: the border red for a fifth of a second
        call flash
bp_snd:
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
        ld de,WIN_W*4-8         ; window is 176 wide, car is 16: 80 to its left
        or a
        sbc hl,de
        jr nc,cx_pos
        ld hl,0
cx_pos:
        ld de,MAPW*8-200
        call clamp_hl
        ld (camx),hl
        ld hl,(cars+C_Y)
        ld de,WIN_H/2-8         ; the car in the middle, top to bottom
        or a
        sbc hl,de
        jr nc,cy_pos
        ld hl,0
cy_pos:
        ld de,MAPH*8-WIN_H-8
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
        ld a,BUF_TOP            ; first tile row starts at buffer row BUF_TOP - v
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
        ld a,WIN_H/8+1          ; rows of tiles
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
        cp WIN_W+1
        jr nc,dt_row_done       ; right of it: the rest of the list is too
        ex af,af'               ; A' = column within the window
        ld a,(hl)               ; tile number
        inc hl
        exx
        cp TM_FIRST             ; a breakfast thing: drawn with its mask
        jr nc,dt_mask
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
dt_back:
        exx
        dec b
        jr nz,dt_tile
        jr dt_row_done
dt_skip:
        inc hl
        dec b
        jr nz,dt_tile
        jr dt_row_done
dt_mask:                        ; IX = its mask, DE = its picture, HL = where
        ld l,a
        sub TM_FIRST
        ld e,a
        ld d,0
        ld ix,tmask_idx
        add ix,de
        ld a,l
        ld l,(ix+0)             ; which mask
        ld h,d
        add hl,hl
        add hl,hl
        add hl,hl
        ld de,tmask
        add hl,de
        push hl
        pop ix
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
        ld hl,(tr_base)
        add a,l
        ld l,a
        call tdraw_m
        jr dt_back
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

; TDRAW_M: one masked tile - a breakfast thing on the tablecloth.
; IX = its mask, DE = its picture, HL = top-left byte, B = shift page.
;   buffer = (buffer AND NOT mask) OR picture, both shifted, 8 lines
; Not unrolled like tdraw_0..7: only a few are ever in view.
tdraw_m:
        ld a,8
tdm_line:
        ex af,af'
        ld a,(de)
        or (ix+0)
        jr z,tdm_next           ; nothing on this line
        ld c,(ix+0)             ; left byte: clear under the mask...
        ld a,(bc)
        cpl
        and (hl)
        ld (hl),a
        ld a,(de)               ; ...then the picture
        ld c,a
        ld a,(bc)
        or (hl)
        ld (hl),a
        inc b                   ; right byte, the same
        inc l
        ld c,(ix+0)
        ld a,(bc)
        cpl
        and (hl)
        ld (hl),a
        ld a,(de)
        ld c,a
        ld a,(bc)
        or (hl)
        ld (hl),a
        dec b
        dec l
tdm_next:
        inc de
        inc ix
        inc h                   ; next pixel line; past a character row's
        ld a,h                  ; 8th, on to the next row (or third)
        and 7
        jr nz,tdm_ok
        ld a,h
        sub 8
        ld h,a
        ld a,l
        add a,32
        ld l,a
        jr nc,tdm_ok
        ld a,h
        add a,8
        ld h,a
tdm_ok:
        ex af,af'
        dec a
        jr nz,tdm_line
        ret

; ---------------------------------------------------------------------
; DRAW_CAR (IX = car): masked, into the back buffer, if it is in view.
;   buffer = (buffer AND NOT mask) OR ink, for each row
; The big cars (Grant, 10 Nov 2026): a 21 x 21 frame - the 20 x 20 car and its
; 1px halo - at car position - 2, so the car's middle stays at position + 8.
; Each row is 3 bytes of picture over 4 of buffer. Rows above the buffer or
; into the driver strip's blocks (buffer row 152 on) are cut off; a car more
; than 14 px out of the window's left edge is not drawn (its last few columns
; would fall before the start of the buffer row).
; ---------------------------------------------------------------------
draw_car:
        ld l,(ix+C_X)           ; window x = car x - camx
        ld h,(ix+C_X+1)
        ld de,(camx)
        or a
        sbc hl,de
        ld de,CAR_U             ; u = the frame's buffer x - 1: the frame is at wx - 3 for the
        add hl,de               ; big cars (CAR_U 12), at wx for the small (15); buffer x 0 = window x -16
        ld a,h
        or a
        ret nz
        ld a,l
        cp 190                  ; wx -12..177
        ret nc
        ld (wxu),a
        ld l,(ix+C_Y)
        ld h,(ix+C_Y+1)
        ld de,(camy)
        or a
        sbc hl,de
        ld de,26+BUF_TOP        ; w = the frame's buffer row + 32
        add hl,de               ; (frame at wy - 6, window row 0 = buffer row BUF_TOP)
        ld a,h
        or a
        ret nz
        ld a,l
        cp BUF_TOP+WIN_H+32     ; buffer rows -32..the window's last
        ret nc
        ld (dc_row0),a
        ; picture: big_tab[kind * 16 + heading]: the frame's address, its first
        ; row and how many rows it has (only the rows in use are kept: the cars
        ; turned at full size are up to 27 rows, the upright ones 20)
        ld l,(ix+C_KIND)
        ld h,0
        add hl,hl
        add hl,hl
        add hl,hl
        add hl,hl
        ld a,(ix+C_ANG)
        rrca
        rrca
        and 15
        or l
        ld l,a
        add hl,hl
        add hl,hl
        ld de,big_tab
        add hl,de
        ld e,(hl)
        inc hl
        ld d,(hl)               ; DE = the frame's rows
        inc hl
        ld b,(hl)               ; B = its first row
        inc hl
        ld a,(hl)
        ld (dc_count),a
        ld a,(dc_row0)          ; buffer row of the first row, + 32
        add a,b
        sub 32
        jr nc,dc_top
        neg                     ; above the buffer: skip that many rows
        ld b,a
        ld a,(dc_count)
        sub b
        ret c
        ret z
        ld (dc_count),a
        ld a,b                  ; DE += rows skipped * 6
        add a,a
        add a,b
        add a,a
        add a,e
        ld e,a
        jr nc,dc_sk
        inc d
dc_sk:
        xor a
dc_top:
        ld (dc_row0),a          ; now the buffer row itself
        ld b,a
        ld a,BUF_TOP+WIN_H      ; stop at the window's last line
        sub b
        ret z
        ret c
        ld b,a
        ld a,(dc_count)
        cp b
        jr c,dc_cnt
        ld a,b
        ld (dc_count),a
dc_cnt:
        ; shift table t = (15 - u) AND 7; first byte = u DIV 8
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
        ld a,(dc_row0)
        ld b,a
        call buf_addr
        ld a,(dc_tab)
        ld b,a
        ld a,(dc_count)
        push ix                 ; (the rows to go: in IXL - a register, not memory,
        ld ixl,a                ; saves 22 T a row; IX is put back at the end)
dc_loop:
        ld a,(de)               ; mask byte (0: nothing in this byte - skip it
        inc de                  ; and its ink: 14 in 100 of the big cars' bytes)
        or a
        jr z,dc_e0
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
        inc l                   ; on to the next byte
        jr dc_e0_x
dc_e0:
        inc de                  ; (its ink byte)
        inc l
dc_e0_x:
        ld a,(de)               ; mask byte (0: nothing in this byte - skip it
        inc de                  ; and its ink: 14 in 100 of the big cars' bytes)
        or a
        jr z,dc_e1
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
        inc l                   ; on to the next byte
        jr dc_e1_x
dc_e1:
        inc de                  ; (its ink byte)
        inc l
dc_e1_x:
        ld a,(de)               ; mask byte (0: nothing in this byte - skip it
        inc de                  ; and its ink: 14 in 100 of the big cars' bytes)
        or a
        jr z,dc_e2
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
        dec l                   ; back to the row's first byte
        dec l
        jr dc_e2_x
dc_e2:
        inc de                  ; (its ink byte)
        dec l
        dec l
dc_e2_x:
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
        dec ixl
        jp nz,dc_loop
        pop ix
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
        ei
        ret

; ---------------------------------------------------------------------
; LIGHTS_DRAW: the start lights into the back buffer (every picture while they are up:
; the window is copied from the buffer, so anything in it has to be drawn there). The
; rail fills its cells (row 1, columns 7-16), each lamp its 2 x 2 cells (rows 2-3): a
; ring if it is not lit, the full lamp if it is. Their colours: lights_attr (hud.asm).
; Window cell (row r, column c) is buffer row BUF_TOP + 8r - WIN_Y, buffer byte c + 1.
; ---------------------------------------------------------------------
lights_draw:
        ld b,BUF_TOP+8-WIN_Y    ; the rail: 8 lines, all in one character row (INC H)
        ld c,(LT_COL+1)*8
        call buf_addr
        ld de,lt_rail
        ld c,2                  ; lines 0-1, then 2-4, then 5-7
        call ld_rail
        ld c,3
        call ld_rail
        ld c,3
        call ld_rail
        ld c,1                  ; the lamps: C = lamp 1..3
ld_lamp:
        ld de,lt_ring
        ld a,(start_ph)
        cp c
        jr c,ld_l1
        ld de,lt_lamp           ; lit (or all green)
ld_l1:
        ld a,c                  ; its bytes: column 5 + 3C, + 1 for the buffer
        add a,a
        add a,c
        add a,LT_COL-1
        add a,a
        add a,a
        add a,a
        ld (ld_x),a
        ld b,BUF_TOP+16-WIN_Y   ; its two character rows: 8 lines each, a page apart
        call ld_half            ; (one address sum a row, then INC H - it was one a line)
        ld b,BUF_TOP+24-WIN_Y
        call ld_half
        inc c
        ld a,c
        cp 4
        jr nz,ld_lamp
        ret
ld_half:
        push bc
        ld a,(ld_x)
        ld c,a
        call buf_addr
        ld b,8
ld_h1:
        ld a,(de)
        ld (hl),a
        inc de
        inc l
        ld a,(de)
        ld (hl),a
        inc de
        dec l
        inc h
        djnz ld_h1
        pop bc
        ret
ld_x:   db 0                    ; the lamp's x in the buffer
ld_rail:                        ; C lines of the 10 bytes at DE, from HL; DE on to the next kind
        push bc
        push de
        push hl
        ld b,10
ld_r1:
        ld a,(de)
        ld (hl),a
        inc de
        inc l
        djnz ld_r1
        pop hl
        pop de
        pop bc
        inc h
        dec c
        jr nz,ld_rail
        ld a,e
        add a,10
        ld e,a
        ret nc
        inc d
        ret

; NOS_DRAW: a small canister for each one you hold (INV), in the window's bottom right
; corner, in the window's own colours: each replaces its byte of the cloth on 10 lines,
; so it stands clear of what is behind it (layout G3; the inventory slots have gone).
; Window lines 132-135 are buffer rows 140-143 (one character row), 136-141 rows 144-149.
NOS_BA  equ BUF + 0x800*2 + 4*0x100 + 1*32 + 23     ; buffer row 140 (third 2, char row 1, line 4), byte 23
NOS_BB  equ BUF + 0x800*2 + 0*0x100 + 2*32 + 23     ; buffer row 144 (third 2, char row 2, line 0)
nos_draw:
        ld hl,INV
        ld c,0                  ; C = slot 0..2: bytes 23, 22, 21
nd_1:
        ld a,(hl)
        or a
        jr z,nd_next
        push hl
        ld de,nos_can
        ld hl,NOS_BA
        ld a,l
        sub c
        ld l,a
        ld b,4
        call nd_col
        ld hl,NOS_BB
        ld a,l
        sub c
        ld l,a
        ld b,6
        call nd_col
        pop hl
nd_next:
        inc hl
        inc c
        ld a,c
        cp 3
        jr nz,nd_1
        ret
nd_col:
        ld a,(de)
        ld (hl),a
        inc de
        inc h
        djnz nd_col
        ret
        include "lights.asm"    ; the lamps, the rail, the canister

; ---------------------------------------------------------------------
; SOUND (the beeper): played in the time the loop would otherwise spend
; waiting for its next picture, so it costs no frames (the zxspectrum
; skill's sound notes, from Traverse USA). Each piece is short - at most
; ~7.5k T - so the copy still starts well ahead of the beam after the
; interrupt it was waiting for.
;   engine: one speaker flip per piece, the gap set by your speed: about
;           230 Hz rolling, 450 Hz flat out; silent before the start and
;           after the finish. The loop rarely has time to spare now (10 Nov
;           2026: 26 flips a second, measured), so the interrupt also flips
;           the speaker 9-49 times a second by speed (isr): a putter that
;           rises to a buzz, heard however busy the picture is
;   crash:  noise when your car hits another, for SND_CRASH pictures
; Port 254: bits 0-2 the border (yellow, 6), bits 3-4 the speaker.
; ---------------------------------------------------------------------
SND_CRASH equ 6
SND_CRUISE equ 84               ; (speed / 4: about three quarters of the top speed)
snd_picture:
        ld a,(snd_bump)         ; the crash fades a picture at a time
        or a
        jr z,sp_1
        dec a
        ld (snd_bump),a
sp_1:
        xor a                   ; engine pitch: 0 = quiet
        ld (snd_gap),a
        ld (snd_rate),a
        ld a,(race_on)
        or a
        ret z
        ld a,(you_done)
        or a
        ret nz
        ld a,(cars+C_CTRL)      ; only while you accelerate (Q): rolling, the
        and CT_GO               ; engine is quiet (Grant, 10 Nov 2026: too much
        ret z                   ; noise - accelerate, skid or bump only)
        ld hl,(cars+C_VX)       ; speed, roughly: |vx| + |vy|
        call abs_hl
        push hl
        ld hl,(cars+C_VY)
        call abs_hl
        pop de
        add hl,de
        srl h                   ; / 4: about 0..120
        rr l
        srl h
        rr l
        ld a,h
        or a
        jr z,sp_2
        ld l,255
sp_2:
        ld a,l
        cp 8
        ret c                   ; all but stopped: quiet
        cp SND_CRUISE           ; up to speed: quiet too - the engine is heard only while
        ret nc                  ; the car is PICKING UP speed (off the line, out of a corner,
        ld b,a                  ; after a bump): an event, not a drone (Grant, 14 Nov 2026).
        add a,a                 ; The interrupt's rate: 2 x speed + 30 flips per 256 frames
        add a,30
        ld (snd_rate),a
        ret
snd_wait:
        ld a,(snd_bump)
        or a
        jr nz,sw_crash
        ld a,(snd_gap)
        or a
        jr nz,sw_engine
        halt                    ; no sound: just wait for the interrupt
        ret
sw_engine:                      ; one flip, then the gap (51 T a count)
        ld b,a
        ld a,(snd_port)
        xor 24
        ld (snd_port),a
        out (254),a
sw_e1:
        ex (sp),hl
        ex (sp),hl
        djnz sw_e1
        ret
sw_crash:                       ; 16 random flips, random short gaps
        ld c,16
        ld a,(snd_port)         ; (the border as it is: red, if it is flashing)
        and 7
        ld e,a
sw_c1:
        call rnd
        and 24
        or e
        out (254),a
        call rnd
        and 31
        inc a
        ld b,a
sw_c2:
        djnz sw_c2
        dec c
        jr nz,sw_c1
        ld a,e
        out (254),a
        ret

; FLASH: the border as a signal (the layout review, Grant, 10 Nov 2026): green
; at GO, red on a crash, white while the NOS burns. H = TV frames, L = the
; colour; the interrupt counts it down and puts the yellow back. The border
; shares port 254 with the speaker, so it goes through snd_port like the sound.
flash:
        ld a,h
        ld (flash_t),a
        ld a,(snd_port)
        and 0xF8
        or l
        ld (snd_port),a
        ret

; ---------------------------------------------------------------------
; IM2_ON: our own interrupt routine in place of the ROM's. The game reads the
; keys from the ports itself and never calls the ROM, so all the interrupt
; has to do is count frames - and the ROM's routine (which also scans the
; keyboard) costs time every frame and pushes 10+ bytes onto whatever stack
; is in use. Ours pushes 6, which the 8-byte margin at the end of every
; buffer row soaks up, so the cloth can be filled in any order.
; Vector: I = 0x39 points at the ROM's spare bytes, all 0xFF, so whatever is
; on the bus the routine is at 0xFFFF: a JR whose offset is the ROM's first
; byte (0xF3, -13), landing at 0xFFF4: a JP to isr. (0xFFF4.. is BASIC's
; user-graphics area, unused here.)
; ---------------------------------------------------------------------
; (isr: after strip.asm, out of the gap before sq4)

; ---------------------------------------------------------------------
; CLOTH_FILL: the tablecloth. Instead of clearing the back buffer to blank,
; fill buffer rows 16..16+WIN_H-1 with the cloth the camera sees: 32-px checks, the
; dark ones 25% dots, locked to the table so they scroll with it.
; World pixel (x, y) is buffer row y-camy+16, bit x-camx+16 of that row.
;
; A buffer line repeats every 8 bytes (64 px), so 4 register pairs hold one,
; and 12 PUSHes fill its bytes 23..0 (the rest is margin, never shown).
; The lines come in kinds, by the world y: odd lines are blank; lines with
; y AND 3 = 0 and = 2 are dotted, each its own way (P0, P2), and each has two
; versions, one for each row of checks (the check row changes every 32 lines).
;
; The speed pass of 13 Nov 2026: the lines are filled KIND BY KIND, not top to
; bottom (any order is safe), so the registers are loaded a handful of times a
; picture instead of on every other line:
;   1. every blank line, 4 in each character row, with HL = 0;
;   2. the P0 lines, 2 in each character row (4 pixel rows apart), the pattern
;      in BC, DE, HL and IY - loaded again only where the check row changes
;      (every 8th line of the kind); then the P2 lines the same way.
; It was 45k T a picture, most of it loading registers; now about 26k.
; Any order is safe: the interrupt routine pushes 6 bytes, and below the
; start of every line are the 8 margin bytes of another.
; ---------------------------------------------------------------------
CL_L0   equ (BUF_TOP/8)*32+24   ; the low byte of line 0's byte 24 (buffer row BUF_TOP)
CL_PUSH macro                     ; bytes 23..0 of a line from the pairs BC, DE, HL, IY
        rept 3
        push bc
        push de
        push hl
        push iy
        endm
        endm
cloth_fill:
        call cloth_pats
        ld a,(camy)             ; (buffer row 16 is the window's first line: world
        ld (cf_y0),a            ; y = camy) - the low byte of line 0's world y
        ld (cf_sp),sp
        cpl                     ; ---- 1. the blank lines: those with y odd
        and 1
        add a,BUF_HI
        ld ixh,a                ; IX = byte 24 of the first of them
        ld ixl,CL_L0
        ld hl,0
        ld b,WIN_H/8
cb_row:
        rept 4                  ; the 4 in this character row, 2 pixel rows apart
        ld sp,ix
        rept 12
        push hl
        endm
        inc ixh
        inc ixh
        endm
        ld a,ixl                ; the next character row: 32 bytes on, and back
        add a,32                ; up its 8 pixel rows - unless that was the last
        ld ixl,a                ; row of a third of the buffer (the 8 pages on
        jr c,cb_third           ; are then the next third's)
        ld a,ixh
        sub 8
        ld ixh,a
cb_third:
        djnz cb_row
        xor a                   ; ---- 2. the dotted lines: P0, then P2
cl_kind:
        ld (cf_kk),a            ; A = 0: P0 (y AND 3 = 0), 16: P2 (y AND 3 = 2)
        exx                     ; (the counting is in the other set of registers:
        ld e,a                  ; this set holds the pattern)
        rrca
        rrca
        rrca
        ld d,a                  ; D = the kind's y AND 3
        ld hl,cf_y0
        sub (hl)
        and 3
        ld b,a                  ; B = its first line (0..3)
        add a,BUF_HI
        ld ixh,a
        ld ixl,CL_L0
        ld a,b
        add a,(hl)
        ld b,a                  ; B = that line's world y (low byte)
        and 32                  ; its check row -> which version of the pattern
        rrca
        rrca
        or e
        add a,cloth_pat AND 255
        ld l,a
        ld h,cloth_pat/256      ; HL' = the pattern's 8 bytes
        ld a,b                  ; C' = lines of this kind until the check row
        sub d                   ; changes, + 1 (8 lines of a kind to a check row)
        and 31
        rrca
        rrca
        neg
        add a,9
        ld c,a
        ld b,WIN_H/8            ; B' = character rows to go
        call cl_load            ; (SP is still the program's stack here)
cl_row:
        ld sp,ix                ; the kind's first line in this character row
        exx
        dec c
        exx
        call z,cl_flip
        CL_PUSH
        ld a,ixh                ; its second, 4 pixel rows down
        xor 4
        ld ixh,a
        ld sp,ix
        exx
        dec c
        exx
        call z,cl_flip
        CL_PUSH
        ld a,ixh
        xor 4
        ld ixh,a
        ld a,ixl                ; the next character row
        add a,32
        ld ixl,a
        jr nc,cl_1
        ld a,ixh                ; ... in the next third
        add a,8
        ld ixh,a
cl_1:
        exx
        dec b
        exx
        jp nz,cl_row
        ld sp,(cf_sp)
        ld a,(cf_kk)
        xor 16
        jp nz,cl_kind
        ret
; CL_FLIP: the check row changes at this line: the pattern's other version
; (8 bytes on or back), for the next 8 lines of the kind. The CALL's return
; address goes into the line about to be filled - which the fill then covers.
cl_flip:
        exx
        ld c,8
        ld a,l
        xor 8
        ld l,a
cl_load:                        ; HL' = 8 bytes -> IY, HL, DE, BC (bytes 0-1, 2-3,
        push hl                 ; 4-5, 6-7), and back to the pattern's registers
        exx
        pop hl
        ld e,(hl)
        inc l
        ld d,(hl)
        inc l
        push de
        pop iy
        ld e,(hl)
        inc l
        ld d,(hl)
        inc l
        push de
        ld e,(hl)
        inc l
        ld d,(hl)
        inc l
        ld c,(hl)
        inc l
        ld b,(hl)
        pop hl
        ret

; CLOTH_PATS: the 4 kinds of buffer line for this camera, 8 bytes each, into
; cloth_pat + 16 * dither phase + 8 * check row. Byte j of a line covers world
; x = camx - 16 + 8j .. +7 (and every 8th byte after it is the same).
cloth_pats:
        ld hl,(camx)
        ld a,l
        sub 16
        and 63
        ld c,a                  ; C = where in the 64-px repeat the line starts
        and 7
        ld b,a
        ld a,0xFF               ; E = 0xFF << (C AND 7): the part of a dark byte
        inc b                   ; that still shows; its CPL comes in from the
        jr cpt_1                ; next byte
cpt_0:
        add a,a
cpt_1:
        djnz cpt_0
        ld e,a
        ld a,c
        rrca
        rrca
        rrca
        and 7
        ld d,a                  ; D = which byte of the repeat
        ld hl,cloth_pat
        ld b,8
cpt_j:                          ; dark mask for check row 0: x AND 32 set = dark
        ld c,0
        ld a,d
        and 4
        jr z,cpt_a
        ld c,e
cpt_a:
        ld a,d
        inc a
        and 4
        jr z,cpt_b
        ld a,e
        cpl
        or c
        ld c,a
cpt_b:
        ld (hl),c
        inc hl
        inc d
        djnz cpt_j
        ld a,(camx)             ; the dots, 1 in 8 and staggered (Grant, option
        neg                     ; F): x AND 3 = 0 on lines y AND 3 = 0, x AND 3
        and 3                   ; = 2 on lines y AND 3 = 2, none on odd lines.
        ld b,a                  ; Bit b of byte j is x = camx - 16 + 8j + b
        ld a,0x88
        jr z,cpt_c
cpt_r:
        rrca
        djnz cpt_r
cpt_c:
        ld c,a                  ; C = the dots of lines y AND 3 = 0
        ld hl,cloth_pat
        ld b,8
cpt_k:
        ld d,(hl)               ; D = dark mask, check row 0
        ld a,d
        cpl
        ld e,a                  ; E = dark mask, check row 1
        ld a,c
        rrca
        rrca                    ; lines y AND 3 = 2
        push af
        and d
        set 4,l
        ld (hl),a               ; y AND 3 = 2, check row 0
        pop af
        and e
        set 3,l
        ld (hl),a               ; y AND 3 = 2, check row 1
        ld a,c
        and e
        res 4,l
        ld (hl),a               ; y AND 3 = 0, check row 1
        ld a,c
        and d
        res 3,l
        ld (hl),a               ; y AND 3 = 0, check row 0
        inc l
        djnz cpt_k
        ret

; lap_timed (IX = a car that just crossed the line): time its lap, and if
; it is the fastest so far by anyone, remember the time, the car, the lap
lap_timed:
        ld hl,(race_time)
        ld e,(ix+C_LST)
        ld d,(ix+C_LST+1)
        ld (ix+C_LST),l
        ld (ix+C_LST+1),h
        ld a,(ix+C_LAPS)        ; the first crossing only starts lap 1
        cp 2
        ret c
        or a
        sbc hl,de               ; HL = that lap's time
        ld de,(best_lap)
        push hl
        or a
        sbc hl,de
        pop hl
        ret nc
        ld (best_lap),hl
        ld de,(rec_lap)         ; and the lap record, kept from race to race?
        push hl
        or a
        sbc hl,de
        pop hl
        jr nc,lt_rec
        ld (rec_lap),hl
lt_rec:
        ld a,(ix+C_KIND)
        ld (best_car),a
        ld a,(ix+C_LAPS)
        dec a
        ld (best_lapno),a
        ld hl,best_seq
        inc (hl)
        ret

; ---------------------------------------------------------------------
; RACE_PROGRESS: once per picture.
;   - your car passes waypoints like the computer cars do (within 40 of
;     the next one, or of the one after it if you went wide)
;   - progress = laps * NWP + waypoints passed since the line; your
;     position = 1 + the cars with more progress than you
;   - the HUD below the window is redrawn only when something changed
; ---------------------------------------------------------------------
race_progress:
        ld a,(renders)          ; your waypoints: every other picture is
        and 1                   ; plenty (40 px circles, 5 px a picture)
        jr nz,rp_pos
        ld ix,cars
        ld b,2                  ; you may pass up to 2 waypoints a picture
rp_wp:
        push bc
        call wp_delta
        call manhattan
        ld de,40
        or a
        sbc hl,de
        jr nc,rp_try_next
        call lap_and_inc
        pop bc
        djnz rp_wp
        jr rp_pos
rp_try_next:                    ; went wide of it? the one after it counts too
        ld a,(ix+C_WP)
        push af
        call wp_inc
        call wp_delta
        call manhattan
        pop af
        ld (ix+C_WP),a
        pop bc
        ld de,40
        or a
        sbc hl,de
        jr nc,rp_pos
        call lap_and_inc        ; the missed one, then the one reached
        call lap_and_inc
rp_pos:
rp_all:
        ld a,(race_over)
        or a
        ret nz                  ; the race is over: everything stays as it ended
        ld a,(you_done)
        or a
        jr nz,rp_wait
        ld a,(cars+C_LAPS)      ; you finished?  checked every picture
        cp LAPS+1
        jr c,rp_go_on
        ld a,1
        ld (you_done),a
        ld hl,(race_time)       ; your time stays on the clock
        ld (you_time),hl
        ld a,(fin_at)           ; your place: the order you came in
        ld (position),a
        call msg_finished
        ld a,(position)         ; and on the radio
        cp 1
        ld a,M_WIN
        jr z,rp_say
        ld a,M_DONE
rp_say:
        call msg_say
rp_wait:                        ; the race is over when every car is in (or
        ld a,(fin_count)        ; 30 s after you, in case one is stuck)
        cp NCARS
        jr nc,rp_end
        ld hl,(race_time)
        ld de,(you_time)
        or a
        sbc hl,de
        ld de,1500
        or a
        sbc hl,de
        jr c,rp_go_on
rp_end:
        ld a,1
        ld (race_over),a        ; (the main loop puts up the flag and stops)
        jr rp_now               ; and the final order, straight away
rp_go_on:
        ld a,(renders)          ; the order one picture in four (4 times a
        and 3                   ; second; the tower shows it one in four)
        cp 3
        ret nz
rp_now:
        ld ix,cars              ; every car's progress (prog) and waypoints
        ld b,0                  ; passed this lap (passed)
rp_p:
        push bc
        call wp_delta           ; how far to its next waypoint: for cars level
        call manhattan          ; on waypoints, the nearer one is ahead
        srl h                   ; (HL / 2, kept to a byte)
        rr l
        ld a,h
        or a
        jr z,rp_d1
        ld l,255
rp_d1:
        pop bc
        push bc
        ld e,b
        ld d,0
        ld a,l
        ld hl,pdist
        add hl,de
        ld (hl),a
        call progress           ; A = progress, L = passed
        ld (rp_rank),a
        ld a,l
        pop bc
        ld e,b
        ld d,0
        ld hl,passed
        add hl,de
        ld (hl),a
        ld a,(rp_rank)
        ld hl,prog
        add hl,de
        ld (hl),a
        ld de,C_SIZE
        add ix,de
        inc b
        ld a,b
        cp NCARS
        jr nz,rp_p
        ; the order: car i's place = the cars with more progress, or the
        ; same progress and a lower number (so you win a tie)
        ld c,0
rp_i:
        ld hl,prog
        ld a,c
        add a,l
        ld l,a
        jr nc,rp_i1
        inc h
rp_i1:
        ld e,(hl)               ; E = progress of car i
        push de
        ld e,c
        ld d,0
        ld hl,pdist
        add hl,de
        ld a,(hl)
        ld (rp_di),a            ; and its distance to its next waypoint
        pop de
        ld d,0                  ; D = its place, counted
        ld hl,prog
        ld b,0
rp_j:
        ld a,b
        cp c
        jr z,rp_jn
        ld a,(hl)
        cp e
        jr c,rp_jn              ; j is behind
        jr nz,rp_ahead          ; j is ahead
        push hl                 ; level on waypoints: the nearer its next one
        push de                 ; is ahead
        ld e,b
        ld d,0
        ld hl,pdist
        add hl,de
        ld a,(rp_di)
        cp (hl)                 ; i's distance - j's
        pop de
        pop hl
        jr c,rp_jn              ; i nearer: j behind
        jr nz,rp_ahead          ; j nearer: ahead
        ld a,b                  ; the same: ahead only if j < i
        cp c
        jr nc,rp_jn
rp_ahead:
        inc d
rp_jn:
        inc hl
        inc b
        ld a,b
        cp NCARS
        jr nz,rp_j
        ld hl,order             ; order[place] = i
        ld a,d
        add a,l
        ld l,a
        jr nc,rp_o1
        inc h
rp_o1:
        ld (hl),c
        ld a,c
        or a
        jr nz,rp_in
        ld a,d                  ; your place, 1..5
        inc a
        ld (position),a
rp_in:
        inc c
        ld a,c
        cp NCARS
        jr nz,rp_i
        ret


; car_in (IX = a car crossing the line for the last time): its place
car_in:
        ld hl,fin_count
        inc (hl)
        ld a,(hl)
        ld e,(ix+C_KIND)
        ld d,0
        ld hl,fin_at
        add hl,de
        ld (hl),a
        ret

; progress (IX = car): A = laps * NWP + passed (stops at 255; a 3-lap race
; needs about 170), L = passed = waypoints since the line, 0..NWP-1
progress:
        ld a,(ix+C_LAPS)        ; finished: ahead of every car still racing,
        cp LAPS+1               ; in the order they came in
        jr c,pr_run
        ld e,(ix+C_KIND)
        ld d,0
        ld hl,fin_at
        add hl,de
        ld a,250
        sub (hl)
        ld l,0
        ret
pr_run:
        ld a,(ix+C_WP)          ; passed = (target - WS - 1) MOD NWP
        sub WS+1
        jr nc,pr1
        add a,NWP
pr1:
        ld l,a
        ld b,(ix+C_LAPS)
        inc b
        jr pr_go
pr_add:
        add a,NWP
        jr nc,pr_go
        ld a,255
        ret
pr_go:
        djnz pr_add
        ret

; print_at: the 0-terminated text at HL, at character row B, column C,
; using the ROM's own letters (at 0x3D00). Written straight into the
; screen, only when something changes - never every frame.
print_at:
        ld a,b                  ; screen address of the character cell
        and 0x18
        or 0x40
        ld d,a
        ld a,b
        and 7
        rrca
        rrca
        rrca
        or c
        ld e,a
pa_char:
        ld a,(hl)
        or a
        ret z
        push hl
        push de
        ld l,a                  ; font: 0x3C00 + code * 8
        ld h,0
        add hl,hl
        add hl,hl
        add hl,hl
        ld bc,0x3C00
        add hl,bc
        ld b,8
pa_line:
        ld a,(hl)
        ld (de),a
        inc hl
        inc d
        djnz pa_line
        pop de
        pop hl
        inc hl
        inc e
        jr pa_char

; ---------------------------------------------------------------------
; the starting line-up (copied into "cars" at the start)
;   x frac, x, y frac, y, vx, vy, heading, buttons, friction,
;   waypoint, offset x, offset y, mistake, kind of mistake, think,
;   PACE, REACT, ERR, picture, steering, ease off, laps, lap start
; Tuned on the real ROM (tests/tune_ai.py) to race round your pace:
; CPU A: 7 of 8, fewest mistakes  (laps ~13.9 s)
; CPU B: 7 of 8, more mistakes    (~14.2 s)
; CPU C: 7 of 8, some mistakes    (~14.2 s)
; CPU D: 6 of 8, the most mistakes (~16.0 s)
; Everyone thinks every 4 frames. Your autopilot lap: ~13.5 s.
; ---------------------------------------------------------------------
; (cars_init: kept at the top of memory - see high_src)

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
seed:     dw 0x1234
hx:       db 0
hy:       db 0
tdx:      db 0
tdy:      db 0
cross:    dw 0
dot:      dw 0
wxu:      db 0
bump_b:   dw 0
bdx:      dw 0
bdy:      dw 0
tb:       defs 9
dc_row0:  db 0
dc_count: db 0
dist_cur: dw 0
mc_y:     db 0
mc_h:     db 0
mc_n:     db 0
dt_rows:  db 0
save_sp:  dw 0
cf_sp:    dw 0
cf_y0:    db 0
cf_kk:    db 0
pace:     db PACE_FR      ; TV frames a picture: 3, or 4 for a while when busy
pace_hold: db 0
pace_skip: db 0          ; 1: this picture does not set the pace (GO's)
ph_steps: db 1
ph_dir:   db 1                  ; the way you last steered: 1 right, 0xFF left
oc_x:     dw 0                  ; o_check: car centre - 4, and its distances
oc_y:     dw 0
oc_dx:    dw 0
oc_dy:    dw 0
snd_gap:  db 0                  ; engine: counts between speaker flips (0 quiet)
snd_bump: db 0                  ; crash noise: pictures left
O_FREE   equ 6
o_hits:   db 0,0,0,0,0          ; each car's bounces off O's since its last waypoint
mu_wait:  db 1                  ; the ditty: frames until its next note
mu_ph:    db 0                  ; ... frames this note still sounds for
mu_off:   db 0                  ; ... where its burst is in mu_ptab
mu_ptr:   dw mu_tune            ; ... the next note in the tune
        include "music.asm"
SKID_FR  equ 5
snd_skt:  db 0                  ; the skid's screech: frames left
snd_skid: db 0                  ; you: 0 gripping, 1-3 sliding (the skid's step)
snd_fxt:  db 0                  ; a sound effect: frames left (0 none)
snd_fxk:  db 0                  ; ... which: 0 NOS picked up, 1 NOS fired, 2 up: a beep
snd_port: db 6                  ; what port 254 last had: border yellow
flash_t:  db 0                  ; a border flash: TV frames left
lt_on:    db 0                  ; 1: the start lights are up
lt_t:     db 0                  ; TV frames they stay after green
; the driver strip's variables (strip.asm), and the engine's - kept together, in this order:
; strip_reset clears the first 17
MSG_P:    dw 0                  ; the next letter
MSG_ST:   db 0                  ; 0 quiet (no bubble), 1-2 the bubble appears, 3 typing,
                                ; 4 shown (MSG_T), 5-6 the bubble goes
MSG_Y:    db 0                  ; pixel row of the line being typed
MSG_X:    db 0                  ; pixel x of the next letter
WAVE_T:   db 0                  ; wave updates of talking left
COOL:     db 0                  ; pictures before a nag can follow another
TRG_POS:  db 0                  ; your place, as last seen
TRG_BS:   db 0                  ; best_seq, as last seen
TRG_LAP:  db 0                  ; your lap, as last seen
HIT_O:    db 0                  ; you hit an O (set in tick)
INV:      db 0,0,0              ; the inventory: 3 slots, 0 empty, 1 NOS
INV_SH:   db 0,0,0              ; ... as shown
NOS_SHOW: db 0                  ; 0: canister A on the track, 1: B
BOOST_T:  db 0                  ; TV frames of boost left
SPACE_UP: db 0                  ; SPACE was up (so a press is new)
MSG_T:    db 0                  ; strip ticks the message stays up once typed
snd_rate: db 0                  ; engine in the interrupt: flips per 256 frames (0 quiet)
snd_acc:  db 0                  ; ... its running count
ai_s:     db 0
ph_cnt:   db 0
ph_px:    dw 0
ph_py:    dw 0
; ---- reset to zero at the start of every race ----
rec_lap:     dw 0xFFFF          ; the lap record: the best lap of any race since
                                ; loading (not cleared by a new race; 0xFFFF none)
race_vars:
yg_vf:       dw 0               ; you (grip.asm): forwards speed (8.8)
yg_vs:       dw 0               ;   sideways speed
yg_vx:       dw 0               ;   the world speed it last set
yg_vy:       dw 0
yg_ang:      db 0               ;   the heading it last saw
yg_sl:       db 0               ;   1: sliding
yg_s:        dw 0               ;   sin, cos of the heading: |x| / 128, sign
yg_c:        dw 0
yg_t1:       dw 0               ;   the turn's four products
yg_t2:       dw 0
yg_t3:       dw 0
yg_t4:       dw 0
yg_s6:       db 0               ;   sin, cos / 64 as signed bytes (the small multiplies)
yg_c6:       db 0
yg_rs:       db 0               ;   frames, for the fresh start every 32
yg_f0:       dw 0               ;   vf, vs before this frame's forces
yg_s0:       dw 0
yg_df:       db 0               ;   their changes, as bytes
yg_ds:       db 0
yg_tang:     db 0               ;   heading + 1 the sine/cosine are for (0: none)
yg_pvf:      dw 0               ;   vf, vs, heading the world speed was made from
yg_pvs:      dw 0
yg_pang:     db 0
start_go:    db 0               ; Q pressed: the lights are coming on
start_f0:    db 0               ; FRAMES when Q was pressed
start_ph:    db 0               ; the lights shown: 0 none, 1-3 red, 4 green
race_on:     db 0
race_over:   db 0
ticks:       dw 0
mistakes:    dw 0
bumps:       dw 0
position:    db 0
prog:        defs NCARS         ; each car's progress (laps * NWP + passed)
passed:      defs NCARS         ; waypoints each car has passed this lap
order:       defs NCARS         ; car in each place
shown_order: defs NCARS
shown_on:    db 0
shown_final: db 0
msg_timer:   db 0
race_time:   dw 0               ; TV frames since your first Q
best_lap:    dw 0
q_up:        db 0
rp_rank:     db 0
tr_car:      db 0
tr_row:      db 0
pb_attr:     db 0
blink:       db 0
best_car:    db 0
best_lapno:  db 0
best_seq:    db 0
shown_best_seq: db 0
md_pat:      dw 0
fin_at:      defs NCARS         ; each car's finishing place (0 = still racing)
fin_count:   db 0               ; cars in so far
you_done:    db 0
you_time:    dw 0               ; your race time, kept on the clock
tr_key:      db 0
pdist:       defs NCARS         ; each car's distance to its next waypoint / 2
rp_di:       db 0
q_free:      db 0
tr_force:    db 0               ; gap_draw: draw even if it looks unchanged
gd_place:    db 0
gd_y:        db 0               ; Q has been let go since this race was set up
bar_shown:   defs 7             ; the message bar: the 6 big letters shown (0: none),
                                ; then 1: LAP and the time are shown
bar_next:    dw 0               ; the race time when the clock's next second is due
race_vars_end:
bar_time:    db "0:00",0        ; the race time, m:ss (hud_init starts it)
shown_dot:   defs 2*NCARS       ; each car's dot on the mini-map (0xFF x: none) - not reset
last_shown: db 0
tr_base:  dw 0
dt_rowp:  dw 0
dc_tab:   db 0

        include "data.asm"
        include "clothmini.asm"   ; (fills the gap before sq4's page)
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

        ; (buf_addr and scr_addr sit here too, in the gap before sq4's page)

gap_draw:                       ; A = place: draw its car's gap, note it
        ld (gd_place),a
        ld e,a
        ld d,0
        ld hl,order
        add hl,de
        ld a,(hl)               ; its car
        add a,a
        ld e,a
        ld hl,GAPS
        add hl,de
        ld c,(hl)
        inc hl
        ld b,(hl)               ; BC = the gap
        ld a,(gd_place)
        add a,a
        ld e,a
        ld hl,SHGAP
        add hl,de
        ld a,(tr_force)         ; (tower_row: always draw)
        or a
        jr nz,gd_1
        ld a,(hl)
        cp c
        jr nz,gd_1
        inc hl
        ld a,(hl)
        cp b
        ret z                   ; as shown already
        dec hl
gd_1:
        xor a
        ld (tr_force),a
        ld (hl),c
        inc hl
        ld (hl),b
        ld a,(gd_place)         ; pixel row: the place's band + 5
        add a,a
        add a,TOWER_Y
        add a,a
        add a,a
        add a,a
        add a,5
        ld (gd_y),a
        ld a,b
        or c
        ld hl,txt_none          ; the leader (or no gap yet): nothing
        jr z,gd_2
        ld h,b
        ld l,c
        call time_fmt           ; "  1.2" -> " 1.2" at time_txt+2
        ld hl,time_txt+2
gd_2:
        ld a,(gd_y)
        ld b,a
        ld c,28
        jp st_text
        ; (gap_draw, from hud.asm, also fills the gap)
        include "sq4.asm"
        include "world.asm"
        include "hud.asm"
        include "gen_tiles.asm"
        include "gen_bumps.asm"
        include "strip.asm"     ; the driver strip: inventory, the radio, the flag
        include "waypoints.asm" ; the centre line, for the computer cars (4 bytes each)
        include "grip.asm"      ; your car: the tyre-grip model (the Skid Lab's)
        include "sqtab.asm"     ; quarter squares 0..383, for grip.asm's multiplying
        include "rowidx.asm"    ; the map: each tile row's list
        include "omap.asm"      ; the cereal O's: one bit a tile
        include "faces.asm"     ; the drivers' faces for the race order
        if OPT_TALL
        include "hudtext_gfx.asm"
        include "tdtab.asm"
txt_track_src:
        endif
isr:
        push af
        push hl
        ld hl,(FRAMES)
        inc hl
        ld (FRAMES),hl
        ld hl,flash_t           ; a border flash: its colour goes out every
        ld a,(hl)               ; frame (so it shows without any sound), then
        or a                    ; the table's yellow again
        jr z,isr_e
        dec (hl)
        ld hl,snd_port
        ld a,(hl)
        jr nz,isr_f
        or 7                    ; (yellow is 6: all three bits, less bit 0)
        dec a
        ld (hl),a
isr_f:
        out (254),a
isr_e:
        ld hl,snd_rate          ; the engine: snd_rate/256 of a speaker flip
        ld a,(hl)               ; every frame - 9 to 49 a second, so it is
        inc hl                  ; heard however busy the loop is (snd_acc
        add a,(hl)              ; follows snd_rate; a rate of 0 never carries)
        ld (hl),a
        jr nc,isr_q
        ld a,(snd_port)
        xor 24
        ld (snd_port),a
        out (254),a
isr_q:
        ; ---- the ditty (Grant, 14 Nov 2026: "a little ditty sound playing in the
        ;      background" - "please try the spilt milk"): music.asm, made by
        ;      tools/make_music.py. Only A, H and L, and no calls: see below ----
        ld hl,mu_wait           ; time for the next note (or drum)?
        dec (hl)
        jr nz,mu_ring
        ld hl,(mu_ptr)
        ld a,(hl)
        cp 255                  ; the end: round again
        jr nz,mu_1
        ld hl,mu_tune
        ld a,(hl)
mu_1:
        ld (mu_off),a           ; where its burst is in mu_ptab
        inc hl
        ld a,(hl)
        ld (mu_wait),a          ; frames until the one after
        inc hl
        ld a,(hl)               ; and the frames it sounds for (a burst on each: "buzz")
        ld (mu_ph),a
        inc hl
        ld (mu_ptr),hl
mu_ring:
        ld a,(mu_ph)
        or a
        jr z,mu_out
        dec a
        ld (mu_ph),a
        ld a,(mu_off)
        add a,mu_ptab AND 255
        ld l,a
        ld a,0
        adc a,mu_ptab/256
        ld h,a
        ld a,(snd_fxt)          ; an event is sounding (an effect, the skid, a crash):
        or a                    ; the tune keeps its place but gives way to it
        jr nz,mu_out
        ld a,(snd_skt)
        or a
        jr nz,mu_out
        ld a,(snd_bump)
        or a
        jr nz,mu_out
        ld a,(hl)               ; cycles (0: nothing this frame)
        or a
        jr z,mu_out
        inc hl
        ld a,(hl)
        ld (mu_p1+1),a
        inc hl
        ld a,(hl)
        ld (mu_p2+1),a
        dec hl
        dec hl
        ld h,(hl)
        ld a,(snd_port)
mu_c:
        xor 24                  ; a cycle: flip, 20 + 16 n T, flip, 36 + 16 m T
        out (254),a
mu_p1:  ld l,0
mu_d1:
        dec l
        jr nz,mu_d1
        xor 24
        out (254),a
mu_p2:  ld l,0
mu_d2:
        dec l
        jr nz,mu_d2
        dec h
        jr nz,mu_c
mu_out:
                                ; (only A, H and L here: the interrupt may land
        ld a,(snd_fxt)          ; while the cloth fill has SP in the buffer, which
        or a                    ; has room for just 6 bytes of pushes)
        jr z,isr_sk
        dec a                   ; an effect, a frame at a time (Grant's picks from the
        ld (snd_fxt),a          ; Sound Lab, 14 Nov 2026). L = frames left
        ld l,a
        ld a,(snd_fxk)
        or a
        jr nz,fx_fire
        ld a,l                  ; 0, NOS picked up: the coin run (P3) - four notes
        srl a                   ; climbing, two frames each: 15 + 5 x (frames left / 2)
        ld h,a                  ; counts between flips
        add a,a
        add a,a
        add a,h
        add a,15
        jr fx_go
fx_fire:
        cp 1
        jr nz,fx_bonk
        ld a,l                  ; 1, NOS fired: the whoosh up (F2) - a buzz that climbs
        srl a                   ; steeply: 12 + 2.5 x frames left
        add a,l
        add a,l
        add a,12
        jr fx_go
fx_bonk:
        cp 2                    ; (3 up: a beep, flips that many counts apart)
        jr nz,fx_go
        ld a,l                  ; 2, a bang into a cereal O: the bonk (B2) - a note
        add a,a                 ; that falls: 34 - 4 x frames left
        add a,a
        neg
        add a,34
fx_go:
        ld l,a
        ld h,6
        jr isr_burst
isr_sk:
        ld a,(snd_skt)          ; a slide has just started: a short screech - a few
        or a                    ; quick speaker flips at random short gaps, for
        jr z,isr_x              ; SKID_FR frames (you_grip sets it)
        dec a
        ld (snd_skt),a
        ld h,4
        ld l,0                  ; (gap 0: a random one each flip)
isr_burst:                      ; H flips, L counts apart (16 T a count)
        ld a,(snd_port)
        xor 24
        ld (snd_port),a
        out (254),a
        ld a,l
        or a
        jr nz,ib_1
        ld a,r
        and 7
        add a,3
ib_1:
        dec a
        jr nz,ib_1
        dec h
        jr nz,isr_burst
isr_x:
        pop hl
        pop af
        ei
        ret
code_end:

; ---------------------------------------------------------------------
; START-UP ONLY: these run once, before the first picture, so they can sit
; in the back buffer (from 0xC000), which nothing uses until then. They
; must end before the shift tables at TAB_HI*256, which they build.
; ---------------------------------------------------------------------
; START_ONCE: the data copied up out of the way, the tables, the copy routine,
; the screen, the interrupts - then the first race
start_once:                     ; (start, from the start-up area)
        ld hl,high_src          ; the data that lives at the top of memory,
        ld de,TOPMEM            ; out of the way: copied up there first,
        ld bc,high_end-high_src ; before the back buffer it loads into is used
        ldir
        ; and into the buffer's unused bottom rows: the blocks sit back to back,
        ; so HL runs on from one into the next (checked at the end)
        ld de,BUFA
        ld bc,bufa_end-bufa_src
        call so_blk
        ld de,BUFB
        ld bc,bufb_end-bufb_src
        call so_blk
        ld de,BUFD
        ld bc,bufd_end-bufd_src
        call so_blk
        ld de,BUFF
        ld bc,buff_end-buff_src
        call so_blk
        ld de,BUFH
        ld bc,bufh_end-bufh_src
        call so_blk
        ld de,BUFG
        ld bc,bufg_end-bufg_src
        call so_blk
        ld de,BUFE
        ld bc,bufe_end-bufe_src
        call so_blk
        call make_tables
        call make_copier        ; the program writes its own copy routine
        call screen_once        ; everything on the screen that never changes
        xor a                   ; the engine quiet until the first picture
        ld (snd_rate),a
        call im2_on
        jp new_race

so_blk:                         ; LDIR, unless there is nothing to copy (BC = 0 would copy 64K)
        ld a,b
        or c
        ret z
        ldir
        ret

; ---------------------------------------------------------------------
; SCREEN_ONCE: everything on the screen that never changes - the colours, the
; bezel, the logo, the track's name, the RACE heading and the driver strip.
; Drawn once at the start (from here, the start-up area); a new race only
; redraws what changes, so none of this needs a place in the program.
; ---------------------------------------------------------------------
screen_once:
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
        ld bc,0                 ; ...the window's slim frame blue on the table (its
        ld de,0x1418            ; cells: rows 0-19, columns 0-23)...
        ld a,0x31
        call set_attrs
        ld hl,0x5800+(WIN_Y/8)*32+WIN_COL   ; ...and the window blue ink on cyan paper
                                    ; (Grant, 10 Nov 2026: no white - easier on
                                    ; the eyes, and less flicker)
        ld b,WIN_H/8
win_attr:
        push bc
        push hl
        ld d,h
        ld e,l
        inc de
        ld (hl),0x29
        ld bc,WIN_W-1
        ldir
        pop hl
        ld de,32
        add hl,de
        pop bc
        djnz win_attr

        call draw_frame
        ld b,0                  ; logo, 7 x 2 cells at the top right
        ld c,25
        call draw_logo
        ld hl,txt_race
        ld b,TOWER_Y-1
        ld c,25
        call print_at
        ld b,TOWER_Y-1          ; RACE: white on blue across the panel
        ld c,25
        ld d,1
        ld e,7
        ld a,A_LAP
        call set_attrs
        ld hl,strip_img         ; the driver strip: you, your inventory, the
        ld b,160                ; crew chief's radio, the crew chief (rows
so_row:                         ; 160-191, columns 0-23)
        push bc
        push hl
        ld c,0
        call scr_addr
        ex de,hl
        pop hl
        ld bc,24
        ldir
        pop bc
        inc b
        ld a,b
        cp 192
        jr nz,so_row
        ld de,0x5800+20*32      ; and its colours
        ld b,4
so_attr:
        push bc
        ld bc,24
        ldir
        ex de,hl
        ld bc,8
        add hl,bc
        ex de,hl
        pop bc
        djnz so_attr
        ld de,minimap_src+6*7   ; the mini-map, black on yellow, under the logo (its lines
        ld b,MAP_Y+6            ; 6-42: screen lines 25-61); the cars' dots are XORed on it
so_map:
        ld c,MAP_X
        call scr_addr
        ex de,hl
        ld bc,7
        ldir
        ex de,hl
        ld a,(so_y)             ; (B is 0 after LDIR: the row is kept in so_y)
        inc a
        ld (so_y),a
        ld b,a
        cp MAP_Y+43
        jr nz,so_map
        ld hl,shown_dot         ; no dots on it yet
        ld b,2*NCARS
so_d:
        ld (hl),0xFF
        inc hl
        djnz so_d
        ret
so_y:   db MAP_Y+6

; DRAW_FRAME: the window's slim frame (layout G3 - Grant, 14 Nov 2026: "what i like in E is
; the border changes around the gameplay area"): a 2-pixel line with rounded corners, 3
; pixels of table between it and the picture. Lines 3-4 and 155-156, columns 3-4 and
; 187-188 of the screen. Drawn once; the scroller never writes outside the window.
draw_frame:
        ld b,3
        ld de,0x07E0
        call df_h
        ld b,4
        ld de,0x0FF0
        call df_h
        ld b,155
        ld de,0x0FF0
        call df_h
        ld b,156
        ld de,0x07E0
        call df_h
        ld b,5
df_v:
        ld c,0
        call scr_addr
        ld (hl),0x18
        ld a,l
        add a,23
        ld l,a
        ld (hl),0x18
        inc b
        ld a,b
        cp 155
        jr nz,df_v
        ret
df_h:                           ; line B: D at column 0, solid across, E at column 23
        ld c,0
        call scr_addr
        ld (hl),d
        ld a,22
df_h1:
        inc l
        ld (hl),0xFF
        dec a
        jr nz,df_h1
        inc l
        ld (hl),e
        ret
; draw_logo: the 56 x 24 logo at cell row B, column C, with its colours
draw_logo:
        ld a,b
        add a,a
        add a,a
        add a,a
        ld b,a                  ; B = pixel row
        ld a,c
        add a,a
        add a,a
        add a,a
        ld c,a                  ; C = pixel x
        ld de,logo_bits
        ld a,16
dl_row:
        push af
        push bc
        call scr_addr
        ld b,7
dl_byte:
        ld a,(de)
        ld (hl),a
        inc de
        inc l
        djnz dl_byte
        pop bc
        inc b
        pop af
        dec a
        jr nz,dl_row
        ld hl,logo_attr         ; 2 rows of 7 attributes
        ld de,0x5800+0*32+25
        ld b,2
dl_attr:
        push bc
        ld bc,7
        ldir
        ex de,hl
        ld bc,32-7
        add hl,bc
        ex de,hl
        pop bc
        djnz dl_attr
        ret

        include "strip_img.asm" ; the driver strip's fixed picture and colours
        include "logo.asm"      ; the logo (drawn once, from here)
        include "minimap.asm"   ; the mini-map's picture (drawn once, below)

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
; MAKE_COPIER: write the screen-copy routine into memory at COPIER.
; Code is just bytes, so a program can write code. Each 22-byte window row
; is two pieces: bytes 0-13 (POP 7 pairs off the buffer - AF, BC, DE, HL, then
; EXX and the other BC, DE, HL - and PUSH them onto the screen), then bytes
; 14-21 (4 pairs). 279 T a row; it was 295 with IX and IY as the 5th and 6th
; pairs (they cost 4 T more each way) - the speed pass, 13 Nov 2026 - and the
; routine is 36 bytes a row, not 40. Finally jp copy_done. Too big to carry on
; the tape for nothing, and every address in it is worked out here.
; ---------------------------------------------------------------------
make_copier:
        ld de,COPIER
        xor a
mc_row:
        ld (mc_y),a
        ld a,7                  ; bytes 0..13: 7 pairs
        ld (mc_n),a
        xor a
        call mc_half
        ld a,4                  ; bytes 14..21: 4 pairs - the whole row
        ld (mc_n),a
        ld a,14
        call mc_half            ; (22 bytes: no odd byte left over)
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
mc_src:                         ; HL = buffer address of this row, byte 2 + A
        add a,2
        add a,a
        add a,a
        add a,a
        ld c,a
        ld a,(mc_y)
        add a,BUF_TOP
        ld b,a
        jp buf_addr
mc_dst:                         ; HL = screen address of this row, byte WIN_COL + A
        add a,WIN_COL
        add a,a
        add a,a
        add a,a
        ld c,a
        ld a,(mc_y)
        add a,WIN_Y
        ld b,a
        jp scr_addr
mc_half:                        ; A = first byte, (mc_n) = pairs (7 or 4)
        ld (mc_h),a
        call mc_src
        call mc_ldsp            ; ld sp,<buffer row>
        call mc_cnt             ; the pops: the first 8 bytes (7 pairs) or 4
        ld hl,mc_pops
        ldir
        ld a,(mc_h)
        call mc_dst
        ld a,(mc_n)             ; + 2n: PUSH works downwards
        add a,a
        add a,l
        ld l,a
        jr nc,mc_h1
        inc h
mc_h1:
        call mc_ldsp            ; ld sp,<screen row + 2n>
        call mc_cnt             ; the pushes: the last 8 bytes, or 4
        ld hl,mc_pushes+8
        or a
        sbc hl,bc
        ldir
        ret
mc_cnt:                         ; BC = 8 for 7 pairs (with the EXX), 4 for 4
        ld bc,8
        ld a,(mc_n)
        cp 7
        ret z
        ld c,4
        ret
mc_op:                          ; write opcode A and address HL
        ld (de),a
        inc de
        ld a,l
        ld (de),a
        inc de
        ld a,h
        ld (de),a
        inc de
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
mc_pops:   db 0xF1,0xC1,0xD1,0xE1,0xD9,0xC1,0xD1,0xE1   ; pop af,bc,de,hl; exx; pop bc,de,hl
mc_pushes: db 0xE5,0xD5,0xC5,0xD9,0xE5,0xD5,0xC5,0xF5   ; push hl,de,bc; exx; push hl,de,bc,af

im2_on:
        di
        ld a,0x18               ; JR
        ld (0xFFFF),a
        ld a,0xC3               ; JP isr
        ld (0xFFF4),a
        ld hl,isr
        ld (0xFFF5),hl
        ld a,0x39
        ld i,a
        im 2
        ei
        ret
; data kept at the top of memory (TOPMEM, above the generated copy routine),
; loaded here and copied up by start; use the names below, not the _src ones
high_src:
        include "topdata.asm"   ; the breakfast things' masks, the O map, the mini-map
        include "hudtext.asm"   ; the HUD's fixed text
        include "toprows.asm"   ; some of the map's row lists
        include "strip_t.asm"   ; a message or two
        if 1-OPT_TALL           ; (with the taller window the copy routine is longer and
        include "hudtext_flag.asm"   ; there is less room up here: these four go into the
        include "hudtext_track.asm"  ; program instead - or, the track's name, nowhere)
        include "hudtext_gfx.asm"
        include "tdtab.asm"     ; the tile routine for each camy AND 7
        endif
cars_init_src:
        db 0
        dw STARTX
        db 0
        dw STARTY
        dw 0,0
        db STARTA,0,3, PLAYERWP,0,0, 0,0,0, 8,0,0, 0,0,0, 0, 0,0
        db 0
        dw CPU0X
        db 0
        dw CPU0Y
        dw 0,0
        db STARTA,0,3, CPU0WP,0,0xFC, 0,0,0, 15,0,8, 1,0,0, 0, 0,0  ; CYAN: 15/16 throttle
        db 0
        dw CPU1X
        db 0
        dw CPU1Y
        dw 0,0
        db STARTA,0,3, CPU1WP,0,4, 0,0,0, 12,0,6, 2,0,0, 0, 0,0     ; GREEN: 12/16 - the slowest (a long 3-axle truck), few mistakes
        db 0
        dw CPU2X
        db 0
        dw CPU2Y
        dw 0,0
        db STARTA,0,3, CPU2WP,0,0xFE, 0,0,0, 15,0,12, 3,0,0, 0, 0,0 ; PINK: 15/16, the most mistakes
        db 0
        dw CPU3X
        db 0
        dw CPU3Y
        dw 0,0
        db STARTA,0,3, CPU3WP,0,2, 0,0,0, 16,0,3, 4,0,0, 0, 0,0     ; WHITE: Slim Jane, the fastest - full throttle, hardly ever wrong
cars_init_src_end:
high_end:
; and two blocks kept in the back buffer's bottom rows (152..191 - never drawn
; or shown: cars reach row 151 at most), copied there by start too
bufa_src:
        include "strip_a.asm"   ; messages
bufa_end:
bufb_src:                       ; (free: the logo is drawn once, straight from the start-up area)
bufb_end:
bufd_src:
        include "thrust.asm"    ; the push for each heading
        include "consts.asm"    ; driving styles, the throttle spread, the cloth's rows
bufd_end:
buff_src:
        include "strip_f.asm"   ; the small letters, the NOS icon, messages
buff_end:
bufh_src:
        include "strip_h.asm"   ; more messages
bufh_end:
bufg_src:
        include "strip_g.asm"
bufg_end:
bufe_src:
        include "strip_e.asm"
bufe_end:
init_end:
TOPMEM      equ 0xFC50            ; the copy routine ends at 0xFC42 (144 lines of 36 bytes)
BUFA      equ BUF+0x1080        ; a table strip: 128 bytes from buffer row 160 (122 safe)
BUFB      equ BUF+0x1180        ; a table strip: 128 bytes from buffer row 160 (122 safe)
BUFD      equ BUF+0x1380        ; a table strip: 128 bytes from buffer row 160 (122 safe)
BUFG      equ BUF+0x1680        ; a table strip: 128 bytes from buffer row 160 (122 safe)
BUFF      equ BUF+0x1580        ; a table strip: 128 bytes from buffer row 160 (122 safe)
BUFH      equ BUF+0x1780        ; a table strip: 128 bytes from buffer row 160 (122 safe)
LFONT     equ BUFF + lfont_src - buff_src
NOS_ICON  equ BUFF + nos_icon_src - buff_src
MSG_INDEX equ BUFF + msg_index_src - buff_src
BB_TAIL   equ BUFG + bb_tail_src - bufg_src
BUFE      equ BUF+0x1480        ; a table strip: 128 bytes from buffer row 160 (122 safe)
row_index equ row_index_src         ; (in the program: the strips are 128 bytes now)
wp_tab    equ waypoints             ; (in the program: 46 of them outgrew BUFG)
thrust_tab equ BUFD + thrust_tab_src - bufd_src
ai_styles equ BUFD + ai_styles_src - bufd_src
rev4      equ BUFD + rev4_src - bufd_src
logo_bits equ logo_bits_src
logo_attr equ logo_attr_src
txt_race  equ TOPMEM + txt_race_src - high_src
txt_ready equ TOPMEM + txt_ready_src - high_src
txt_pressq equ TOPMEM + txt_pressq_src - high_src
txt_lamp  equ TOPMEM + txt_lamp_src - high_src
txt_go    equ TOPMEM + txt_go_src - high_src
txt_final equ TOPMEM + txt_final_src - high_src
txt_finished equ TOPMEM + txt_finished_src - high_src
txt_places equ TOPMEM + txt_places_src - high_src
        if 1-OPT_TALL
txt_flag  equ TOPMEM + txt_flag_src - high_src
        else
txt_flag equ txt_flag_src
        endif
        if 1-OPT_TALL
txt_youfin equ TOPMEM + txt_youfin_src - high_src
        else
txt_youfin equ txt_youfin_src
        endif
        if 1-OPT_TALL
txt_track equ TOPMEM + txt_track_src - high_src
        else
txt_track equ txt_track_src
        endif
txt_none  equ TOPMEM + txt_none_src - high_src
        if 1-OPT_TALL
sfont     equ TOPMEM + sfont_src - high_src
        else
sfont equ sfont_src
        endif
        if 1-OPT_TALL
flag_top  equ TOPMEM + flag_top_src - high_src
        else
flag_top equ flag_top_src
        endif
        if 1-OPT_TALL
clock_top equ TOPMEM + clock_top_src - high_src
        else
clock_top equ clock_top_src
        endif
CLOCK8    equ clock_top+4       ; the clock in one cell (8 rows straight)
        if 1-OPT_TALL
grid_order equ TOPMEM + grid_order_src - high_src
        else
grid_order equ grid_order_src
        endif
        if 1-OPT_TALL
car_colours equ TOPMEM + car_colours_src - high_src
        else
car_colours equ car_colours_src
        endif
        if 1-OPT_TALL
tdraw_table equ TOPMEM + tdraw_table_src - high_src
        else
tdraw_table equ tdraw_table_src
        endif
tmask_idx equ TOPMEM + tmask_idx_src - high_src
tmask     equ TOPMEM + tmask_src - high_src
omap      equ omap_src
cars_init equ TOPMEM + cars_init_src - high_src
faces     equ faces_src

        if WIN_W - 22
        .error make_copier is written for a 22-byte window row
        endif
        if BUF_TOP + WIN_H + 8 > 160
        .error the tiles under the window's last line run into the tables kept from buffer row 160
        endif
        if MAPW - 72
        .error surface assumes the map is 72 tiles (9 bytes of bits) wide
        endif
        if NCARS*C_SIZE - (cars_init_src_end - cars_init_src)
        .error cars_init does not hold NCARS records
        endif
        if code_end > BUF_HI*256
        .error code and data run into the back buffer
        endif
        if TOPMEM + high_end - high_src > 0xFFF4
        .error the top-of-memory data runs into the interrupt jump at 0xFFF4
        endif
        if (bufa_end - bufa_src) / 123 + (bufb_end - bufb_src) / 123 + (bufd_end - bufd_src) / 123 + (bufg_end - bufg_src) / 123 + (bufe_end - bufe_src) / 123 + (buff_end - buff_src) / 123 + (bufh_end - bufh_src) / 123
        .error a block for the buffer's bottom rows is over 122 bytes (128, less the last 6, where the interrupt's pushes can land)
        endif
        if (bufa_src - high_end) + (bufb_src - bufa_end) + (bufd_src - bufb_end) + (buff_src - bufd_end) + (bufh_src - buff_end) + (bufg_src - bufh_end) + (bufe_src - bufg_end)
        .error start_once copies the blocks back to back: keep them in this order
        endif
        if init_end > BUFA
        .error the start-up area runs into where the buffer blocks are copied
        endif
        if init_end > TAB_HI*256
        .error the start-up routines run into the shift tables they build
        endif

        end start
