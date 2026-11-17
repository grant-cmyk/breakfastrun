; TWO PLAYERS (twoplayer.asm): the parts that run rarely, kept under 0x8000
; p2_new: a new race
p2_new:
        ld hl,p2_vars
        ld de,p2_vars+1
        ld bc,P2_NVARS-1
        ld (hl),0
        ldir
        ld hl,p2_yg
        ld de,p2_yg+1
        ld c,P2_YGN-1
        ld (hl),b
        ldir
        ld a,(two_p)
        or a
        ret z
        ld h,b                  ; (BC is 0) player 2's car aims at the waypoints themselves, as yours does - not to one side
        ld l,b
        ld (P2+C_OFFX),hl
        ld bc,0x001A            ; the panel's colours: player 1's two rows white on red, player 2's three black on cyan
        ld de,0x0206
        ld a,0x57
        call set_attrs
        ld bc,0x021A
        ld de,0x0306
        ld a,0x68
        jp set_attrs
p2p_t0:  db "P1 1ST",0
p2p_t1:  db "LAP1/",'0'+LAPS,0
        if OPT_2PPTS
p2p_t4:  db "0 - 0 ",0
        else
p2p_t4:  db "NOS 0 ",0
        endif
