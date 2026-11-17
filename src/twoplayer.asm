; =====================================================================
; TWO PLAYERS IN ONE VIEW - A TRIAL (TWOP=1 with RACETRACK=1 bash build.sh; Grant, 17 Nov 2026: "two players would
; exist in the same screen" - layout A of docs/design/racetrack/two_player_options.png, "one shared view").
; The title's 2 sets two_p; 1 leaves it 0 and the game is the one-player game.
;   - PLAYER 2 drives the car in the second grid place (cyan) with 6 left, 7 right, 0 accelerate, 5 brake, 8 NOS.
;     (Not 9: with 0 and 9 both in use, O + P + 0 held together would read as 9 as well - the Spectrum's keyboard
;     is a grid of wires, and three corners of a square of it held down look like the fourth.)
;   - THE SAME SUMS AS YOUR CAR: the grip model (grip.asm) keeps one car's speeds in the bytes from yg_vf. Player 2's
;     (the 18 of them that last from one TV frame to the next) are kept in p2_yg, and the two sets change places
;     (p2_swap, about 1,300 T) around player 2's turn; so do the two NOS timers. To change places only twice a picture,
;     player 2's car has all of a picture's TV frames one after the other, after everything else's (p2_ticked).
;   - THE VIEW (camera2) is centred between the two cars. THE LEASH: the car further round the lap (the leader) is
;     never nearer the window's edge than P2_MX / P2_MY pixels; when that pushes the other car's box over the
;     window's edge it is put back (leash): on the middle of the road at the waypoint behind the one the leader
;     last passed, facing the next one, standing still, held and flashing for LEASH_HOLD TV frames, with a beep.
;     Its lap count becomes the lap the leader is on there. Once one player has finished, the view is the other's.
;   - THE POINTS RULE (TWOP_PTS=N with it): each time the leash goes the leader scores a point; N points end the race.
; =====================================================================
P2         equ cars+C_SIZE      ; player 2's car: the second on the grid
P2_MX      equ 40               ; the leader is kept this far inside the window's left and right edges,
P2_MY      equ 32               ; ... and its top and bottom
LEASH_BACK equ 40               ; a car is put back at the first waypoint behind the leader that is this far from it or more (pixels across + down)
LEASH_HOLD equ 12               ; TV frames a car put back is held still, flashing (the time it costs, with starting from rest)
P2_YGN     equ 18               ; the grip model's bytes that are kept for each car (p2_swap)

two_p:     db 0                 ; 1: two players (the title's 2); kept from race to race
; Its other variables are not in the program (there is no room): they use memory that is free once the race is on -
; the title's own variables (TS: its moving car's 14 bytes) and the page under the stack that only track 5 uses.
p2_vars    equ TS               ; ---- zero at the start of every race ----
p2_boost   equ TS               ; player 2's NOS: TV frames of boost left (player 1's, while their own is in BOOST_T's place)
p2_inv     equ TS+1             ; player 2's canisters, 0..3
p2_up      equ TS+2             ; player 2's NOS key was up (so a press is new)
lsh_t      equ TS+5             ; the leash: TV frames the car put back is still held
lsh_car    equ TS+6             ; ... which: 1 player 1's, 2 player 2's (0: none) - the byte after lsh_t
p2_pts     equ TS+7             ; POINTS: player 1's, player 2's (2 bytes)
P2_NVARS   equ 9
p2_yg      equ 0x5E00           ; player 2's grip sums, P2_YGN bytes (player 1's, during player 2's turn); zero at the start of every race
c2_lr      equ TS+9             ; camera2: the leader's car record, the other's
c2_tr      equ TS+11
P2_LOWC    equ 0x5E22           ; and two routines that run from there (twoplayer_pic.asm; start_once copies them down)
p2p_shown  equ 0x5E12           ; the panel: what each of its 5 rows shows (0: nothing yet); zero at the start of every race
        if (yg_t1-yg_vf-14) OR (yg_c6-yg_s6-1) OR (yg_rs-yg_c6-1)
        .error twoplayer.asm: the grip model's variables have moved - see p2_swap
        endif
c2_l:      dw 0                 ; camera2: the leader's place and the other's, one way at a time
c2_t:      dw 0
c2_lim:    dw 0

; p2_swap: the two players' grip sums change places, and their NOS timers
p2_swap:
        ld hl,yg_vf             ; what the grip model keeps from one TV frame to the next: its speeds, heading and sliding
        ld de,p2_yg             ; flag, the heading's sine and cosine (14 bytes from yg_vf),
        ld b,yg_t1-yg_vf
        call p2_x
        ld hl,yg_s6             ; ... their small copies and the count to its fresh start (3),
        ld b,3
        call p2_x
        ld hl,yg_tang           ; ... and which heading the sine and cosine are for. (The other 16 bytes are sums it
        inc b                   ; makes and uses within one call.)
        call p2_x
        ld hl,BOOST_T
        ld de,p2_boost
        ld b,1
p2_x:
        ld a,(de)
        ld c,(hl)
        ld (hl),a
        ld a,c
        ld (de),a
        inc hl
        inc de
        djnz p2_x
        ret

; p2_top: the start of every TV frame (tick)
p2_top:
        ld hl,lsh_t             ; the leash's hold runs down
        ld a,(hl)
        or a
        jr z,p2o_1
        dec (hl)
        jr nz,p2o_1
        inc hl
        ld (hl),0               ; (time: it is let go)
p2o_1:
        ret

; p2_ticked: after a picture's TV frames of everything else (main) - player 2's. Their sums and NOS timer change places
; with yours once, their car has all the picture's TV frames one after the other (the buttons are read in a burst at the
; start of a picture anyway), and yours come back. The frame count that says when to look at the ground is stepped as if
; the frames had been taken in turn.
p2_ticked:
        ld a,(two_p)
        or a
        ret z
        call p2_swap
        ld a,(dt)
        ld b,a
        ld hl,ticks
        ld a,(hl)
        sub b
        ld (hl),a
p2b_1:
        push bc
        ld hl,ticks
        inc (hl)
        call p2_tick
        pop bc
        djnz p2b_1
        if OPT_GRIP1            ; (GRIP1: it has only steered - now it is moved, once, as yours is)
        ld a,(dt)
        ld (ph_steps),a
        call p2_phys
        endif
        jp p2_swap

; p2_tick: player 2's TV frame - the buttons, and the car moved (their NOS timer is in BOOST_T's place here)
p2_tick:
        ld hl,BOOST_T
        ld a,(hl)
        or a
        jr z,p2k_1
        dec (hl)
p2k_1:
        ld a,0xEF               ; the half row 6 7 8 9 0
        in a,(0xFE)
        cpl
        ld b,a
        ld c,0
        bit 4,b                 ; 6: left
        jr z,p2k_2
        set 0,c
p2k_2:
        bit 3,b                 ; 7: right
        jr z,p2k_3
        set 1,c
p2k_3:
        bit 0,b                 ; 0: accelerate
        jr z,p2k_4
        set 2,c
p2k_4:
        ld a,0xF7               ; 5: brake
        in a,(0xFE)
        and 0x10
        jr nz,p2k_5
        set 3,c
p2k_5:
        ld hl,p2_up             ; 8: a NOS canister (a new press)
        bit 2,b
        jr z,p2k_6
        ld a,(hl)
        ld (hl),0
        or a
        jr z,p2k_7
        ld a,(race_on)          ; ... if racing, not already burning, and they hold one
        or a
        jr z,p2k_7
        ld a,(BOOST_T)
        or a
        jr nz,p2k_7
        ld hl,p2_inv
        ld a,(hl)
        or a
        jr z,p2k_7
        dec (hl)
        ld a,BOOST_FR
        ld (BOOST_T),a
        ld hl,1*256+18          ; (the whoosh)
        ld (snd_fxt),hl
        jr p2k_7
p2k_6:
        ld (hl),1
p2k_7:
        ld a,(race_on)          ; before green, once finished, or just put back by the leash: no buttons
        or a
        jr z,p2k_8
        ld a,(lsh_car)
        cp 2
        jr z,p2k_8
        ld a,(P2+C_LAPS)
        cp LAPS+1
        jr c,p2k_9
p2k_8:
        ld c,0
p2k_9:
        ld a,c
        ld (P2+C_CTRL),a
        if OPT_GRIP1            ; GRIP1: each TV frame the car only steers (as yours: tick)
        ld hl,P2+C_ANG
        rra
        jr nc,p2k_a
        dec (hl)
p2k_a:
        rra
        jr nc,p2k_b
        inc (hl)
p2k_b:
        res 6,(hl)
        res 7,(hl)
        ret
        else
        ld a,1
        ld (ph_steps),a
        endif                   ; ... on into p2_phys
; p2_phys: player 2's car moved as yours is - for as long as physics runs, it is car "0, you" (C_KIND)
p2_phys:
        ld ix,P2
        ld (ix+C_KIND),0
        call physics
        ld (ix+C_KIND),1
        ret

; p2_move (main's cpu_move; B = NCARS-1 for the second car): Z - player 2's car, and it is seen to
p2_move:
        ld a,b
        cp NCARS-1
        ret nz
        ld a,(two_p)
        dec a
        ret nz
        ret

; ---------------------------------------------------------------------
; CAMERA2: the view between the two cars, and the leash
; ---------------------------------------------------------------------
camera2:
        ld hl,order             ; who leads: the first of the two in the race order
c2_o:
        ld a,(hl)
        inc hl
        cp 2
        jr nc,c2_o
        ld hl,cars
        ld de,P2
        or a
        jr z,c2_1
        ex de,hl
c2_1:
        ld a,(cars+C_LAPS)      ; a player who has finished is left out of it: the view is the other's
        cp LAPS+1
        jr c,c2_2
        ld hl,P2
        ld d,h
        ld e,l
c2_2:
        ld a,(P2+C_LAPS)
        cp LAPS+1
        jr c,c2_3
        ld hl,cars
        ld d,h
        ld e,l
c2_3:
        ld (c2_lr),hl
        ld (c2_tr),de
        push hl
        pop ix                  ; IX = the leader
        ld l,(ix+C_X)           ; across
        ld h,(ix+C_X+1)
        ld (c2_l),hl
        ld hl,(c2_tr)
        inc hl
        ld e,(hl)
        inc hl
        ld d,(hl)
        ld (c2_t),de
        push hl
        ld bc,256*(WIN_W*4-8)+P2_MX
        ld de,MAPW*8-WIN_W*8-24
        call c2_axis
        ld (camx),de
        pop hl
        push af                 ; (CY: the other car is over the edge)
        inc hl
        inc hl
        ld e,(hl)               ; down
        inc hl
        ld d,(hl)
        ld (c2_t),de
        ld l,(ix+C_Y)
        ld h,(ix+C_Y+1)
        ld (c2_l),hl
        ld bc,256*(OPT_RTROWS*4-8)+P2_MY
        ld de,MAPH*8-OPT_RTROWS*8-8
        call c2_axis
        ld (camy),de
        pop bc
        jr c,leash
        bit 0,c
        ret z
; LEASH: the other car has been left behind - put it back on the road behind the leader
leash:
        ld a,(lsh_t)            ; (not again while the last one is still held)
        or a
        ret nz
        ld a,(race_on)
        or a
        ret z
        ld hl,(c2_lr)
        ld de,(c2_tr)
        or a
        sbc hl,de
        ret z                   ; (there is only one car in it)
        ld c,(ix+C_LAPS)        ; the leader's lap, and the waypoint it is heading for
        ld b,(ix+C_WP)
        jr lsh_3
lsh_1:
        ld a,(ix+C_WP)          ; (one waypoint further back: if it is the first past the start line, the line is still in
        cp WS                   ; front of the car that will aim at it - it is on the lap before the leader's)
        jr nz,lsh_3
        dec c
lsh_3:
        ld a,(ix+C_WP)          ; back along the road from there, to the first waypoint LEASH_BACK or more from the leader
        or a
        jr nz,lsh_2
        ld a,NWP
lsh_2:
        dec a
        ld (ix+C_WP),a
        push bc
        call wp_delta
        call manhattan
        pop bc
        ld a,h
        or a
        jr nz,lsh_4
        ld a,l
        cp LEASH_BACK
        jr c,lsh_1
lsh_4:
        ; ONE FURTHER BACK when that is the very waypoint the leader last passed (17 Nov 2026): a car put there aims at the
        ; same waypoint as the leader, 30-odd pixels behind it - not "behind the leader" by the race order's count. So the
        ; one before it is taken instead, if it is LEASH_BACK or more from the leader and both cars then fit in the window
        ; (across and down, each no more than the window less a car and the leader's margin); if not, the choice stands.
        ld a,(ix+C_WP)
        inc a
        cp NWP
        jr nz,lsh_a
        xor a
lsh_a:
        cp b
        jr nz,lsh_5             ; (the search had already gone further back)
        ld a,(ix+C_WP)
        push af                 ; the choice as it stands,
        push bc                 ; ... and its lap
        cp WS                   ; (back over the start line: the lap before, as above)
        jr nz,lsh_b
        dec c
lsh_b:
        or a
        jr nz,lsh_c
        ld a,NWP
lsh_c:
        dec a
        ld (ix+C_WP),a
        push bc
        call wp_delta
        call manhattan
        ld a,h
        or a
        jr nz,lsh_d
        ld a,l
        cp LEASH_BACK
        jr c,lsh_no
lsh_d:
        call wp_delta           ; DE across, BC down: from the leader to it
        push bc
        ex de,hl
        call abs_hl
        ld de,WIN_W*8-16-P2_MX+1
        or a
        sbc hl,de
        pop hl
        jr nc,lsh_no
        call abs_hl
        ld de,OPT_RTROWS*8-16-P2_MY+1
        or a
        sbc hl,de
        jr nc,lsh_no
        pop bc                  ; taken: its lap,
        pop hl                  ; (the first choice forgotten)
        pop hl
        jr lsh_5
lsh_no:
        pop bc
        pop bc                  ; not taken: the first choice and its lap again
        pop af
        ld (ix+C_WP),a
lsh_5:
        ld a,(ix+C_WP)
        ld (ix+C_WP),b          ; (the leader's own waypoint back as it was)
        ld ix,(c2_tr)           ; IX = the car left behind:
        ld (ix+C_LAPS),c
        ld (ix+C_WP),a          ; put down at that waypoint,
        call wp_delta           ; DE, BC = from the car's middle to it
        ld l,(ix+C_X)
        ld h,(ix+C_X+1)
        add hl,de
        ld (ix+C_X),l
        ld (ix+C_X+1),h
        ld l,(ix+C_Y)
        ld h,(ix+C_Y+1)
        add hl,bc
        ld (ix+C_Y),l
        ld (ix+C_Y+1),h
        call wp_inc             ; aiming at the next
        call wp_delta           ; facing the way the road goes: the nearest of 8 ways
        call p2_dir
        ld (ix+C_ANG),a
        xor a                   ; standing still
        ld (ix+C_VX),a
        ld (ix+C_VX+1),a
        ld (ix+C_VY),a
        ld (ix+C_VY+1),a
        ld hl,lsh_t             ; held and flashing for a moment
        ld (hl),LEASH_HOLD
        inc hl
        ld (hl),1
        ld a,(ix+C_KIND)
        or a
        jr z,lsh_6
        inc (hl)
lsh_6:
        ld hl,2*256+12          ; a beep
        ld (snd_fxt),hl
        if OPT_2PPTS            ; POINTS: one to the leader; enough of them end the race
        ld hl,p2_pts+1
        or a
        jr z,lsh_7
        dec hl
lsh_7:
        inc (hl)
        ld a,(hl)
        cp OPT_2PPTS
        jr c,lsh_8
        ld b,4                  ; (the last point on the panel: nothing more is drawn there once the race is over)
        call p2p_nos
        ld a,1
        ld (race_over),a
lsh_8:
        endif
        jp camera2              ; and the view again, with the car where it now is

; c2_axis: (c2_l), (c2_t) = the leader's and the other car's place one way; B = half the window
; less the car, C = the margin; DE = the furthest the view goes. Gives DE = the view; CY = the other car is over an edge
c2_axis:
        ld (c2_lim),de
        ld hl,(c2_l)
        ld de,(c2_t)
        add hl,de
        srl h
        rr l                    ; half way between them (the view does not lead the cars, as it does one car: which one?)
        ld e,b
        ld d,0
        or a
        sbc hl,de               ; in the window's middle
        ex de,hl
        ld hl,(c2_l)            ; but the leader no nearer the far edge than the margin ...
        push bc
        ld b,0
        or a
        sbc hl,bc
        pop bc
        push hl
        call c2_min
        ex de,hl
        pop hl
        ld a,b                  ; ... nor the near edge
        sub c
        add a,a
        push bc
        ld c,a
        ld b,0
        or a
        sbc hl,bc
        pop bc
        call c2_max
        ld de,0                 ; and inside the world
        call c2_max
        ld de,(c2_lim)
        call c2_min
        ex de,hl
        ld hl,(c2_t)            ; the other car in the window: 0 to (the window less the car), or it is over the edge
        or a
        sbc hl,de
        ld a,h
        or a
        scf
        ret nz
        ld a,b
        add a,a
        cp l
        ret
c2_min:                         ; HL = the smaller of HL and DE (signed; small numbers)
        push hl
        or a
        sbc hl,de
        ld a,h
        pop hl
        rla
        ret c
        ex de,hl
        ret
c2_max:                         ; HL = the larger
        push hl
        or a
        sbc hl,de
        ld a,h
        pop hl
        rla
        ret nc
        ex de,hl
        ret

; ---------------------------------------------------------------------
; P2_PANEL, each picture: one row of the panel top right - P1 and its place, its lap; P2 and its place, its lap,
; its NOS canisters (yours are in the window)
; ---------------------------------------------------------------------
p2_panel:
        ld a,(two_p)
        or a
        ret z
        ld a,(renders)
        and 7
        cp 5
        ret nc
        ld b,a                  ; B = the row
        cp 4
        jr z,p2p_nos
        srl a
        ld e,a                  ; E = which player's car, 0 or 1; CY: the lap's row
        jr c,p2p_lap
        add a,'1'
        ld (p2p_t0+1),a
        ld hl,order             ; its place: where it is in the race order
        ld c,'1'
        ld d,NCARS-1
p2p_1:
        ld a,(hl)
        cp e
        jr z,p2p_2
        inc hl
        inc c
        dec d
        jr nz,p2p_1
p2p_2:
        ld a,c
        ld (p2p_t0+3),a
        sub '1'
        add a,a
        add a,p2p_suf AND 255
        ld l,a
        ld a,0
        adc a,p2p_suf/256
        ld h,a
        ld a,(hl)
        ld (p2p_t0+4),a
        inc hl
        ld a,(hl)
        ld (p2p_t0+5),a
        ld a,c
        add a,e                 ; (what the row shows: the place - and whose, since two rows share the text)
        ld hl,p2p_t0
        jr p2p_put
p2p_lap:
        ld hl,cars+C_LAPS
        dec e
        jr nz,p2p_3
        ld hl,P2+C_LAPS
p2p_3:
        ld a,(hl)               ; the lap it is on: 1 until the line is crossed, the last one once it is in
        or a
        jr nz,p2p_4
        inc a
p2p_4:
        cp LAPS+1
        jr c,p2p_5
        ld a,LAPS
p2p_5:
        add a,'0'
        ld (p2p_t1+3),a
        ld hl,p2p_t1
        jr p2p_put
p2p_nos:
        if OPT_2PPTS            ; (POINTS: the score there instead)
        ld hl,(p2_pts)
        ld a,l
        add a,'0'
        ld (p2p_t4),a
        ld a,h
        add a,'0'
        ld (p2p_t4+4),a
        add a,l
        add a,l
        add a,l
        add a,l
        else
        ld a,(p2_inv)
        add a,'0'
        ld (p2p_t4+4),a
        endif
        ld hl,p2p_t4
p2p_put:                        ; A = what the row shows now, HL = its text, B = the row: printed only when it has changed
        ex de,hl
        ld hl,p2p_shown
        ld c,b
        ld b,0
        add hl,bc
        ld b,c
        cp (hl)
        ret z
        ld (hl),a
        ex de,hl
        ld c,26
        jp print_at
