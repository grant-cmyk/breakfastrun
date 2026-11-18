; RACETRACK: YOUR LAPS WHEN YOU GO OFF THE TRACK A FAIR BIT (Grant, 18 Nov 2026: "I also went off track for a bit, and I
; seemed to lose a lap"). Kept under 0x8000: it runs only when race_progress (racer.asm) has found you near neither the
; waypoint the game has you heading for nor the one it tried of the four after it.
;
; THE FAULT: your laps are counted by waypoints - points along the middle of the road, 32 pixels apart. The game keeps the
; one you are heading for; you pass it when you come within 40 of it, and the lap counts when you pass the first one after
; the start line. If you miss one (you went wide), the game also tries the next four after it (within 64). But off the
; road for longer than four waypoints - along the grass, or a spin onto the infield - and back on further round, you were
; near none of them: the game went on waiting for the one where you left the road, and found it only when you came round
; to it again, a whole lap later. That lap was lost.
;
; THE RULE NOW: when you are well away from the waypoint you are heading for (RP_FAR or more), the game looks further
; ahead for one you are near (within 64) and counts you past it and all those before it - but only as far round the road
; as you could have DRIVEN in the time since you were last near your waypoint: 2 pixels a TV frame (quicker than your top
; speed of 1.7 on the road; on the grass you do about 1.1), plus 3 for the waypoints you may already be past. So:
;   - off the track and back on further round never costs a lap: on the grass you are slower than the allowance grows;
;   - a short cut across the grass gains nothing: if you come back on the road sooner than the road would have taken you
;     there, the game waits (you are shown behind in the race order) until the allowance has caught up, and counts you
;     then - the lap line too, if the short cut crossed it. Never more than half the track at once (RP_WIN).
; The computer cars do not use this: they steer for their next waypoint and so come back to it.
RP_FAR  equ 96                  ; this far (|dx| + |dy|) from your waypoint: you are off your way to it
RP_WIN  equ NWP/2-1             ; never more waypoints than this at once (less than half the track)

rp_far:                         ; IX = your car (or player 2's)
        ld hl,(race_time)       ; H = the race clock in steps of 8 TV frames (it goes round every 41 seconds)
        add hl,hl
        add hl,hl
        add hl,hl
        add hl,hl
        add hl,hl
        push hl
        call wp_delta           ; how far is the waypoint you are heading for?
        call manhattan
        ld de,RP_FAR
        or a
        sbc hl,de
        pop hl
        jr nc,rf_far
        ld (ix+C_THINK),h       ; near your way: the clock noted (C_THINK is the computer cars' alone)
        jr rf_out
rf_far:
        ld a,(renders)          ; looked for every 8th picture (race_progress works every other one)
        and 6
        jr nz,rf_out
        ld a,h                  ; steps of 8 TV frames since you were last near your way
        sub (ix+C_THINK)
        rra                     ; halved (the AND drops the borrow)
        and 0x7F
        add a,3                 ; C = waypoints you could have driven: 3 + 16 px a step / 32 px a waypoint
        cp RP_WIN
        jr c,rf_win
        ld a,RP_WIN
rf_win:
        ld c,a
        ld a,(ix+C_WP)
        push af
        ld b,0
rf_look:                        ; the first one ahead you are near
        inc b
        ld a,c
        cp b
        jr c,rf_none
        push bc
        call wp_inc
        call wp_delta
        call manhattan
        pop bc
        ld de,64
        or a
        sbc hl,de
        jr nc,rf_look
        pop af
        ld (ix+C_WP),a          ; back to the one you were heading for, then counted past it and on to the one you
rf_count:                       ; are near (B of them; lap_and_inc counts the lap at the line, as ever)
        push bc
        call lap_and_inc
        pop bc
        djnz rf_count
        jr rf_out
rf_none:
        pop af
        ld (ix+C_WP),a
rf_out:
        if OPT_2P
        ret
        else
        jp rp_pos
        endif
