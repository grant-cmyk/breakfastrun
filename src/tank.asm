; =====================================================================
; TANKUP - THE TANK GETS STRONGER (TANKUP=1, the group C tape; Grant, 23 Nov 2026: "The fastest car appears to be the tank -
; so the tank needs a slight slowdown - it should be the slowest car initially but as it takes little damage it gets
; stronger towards the end").
; Bruno's two pushes (his card row's ACCEL and SPEED: cards.asm) are TK_L1 64ths less on lap 1, TK_L2 on lap 2, TK_L3 on
; lap 3 - written to his row whenever his lap changes (tk_cur: what is in the row now; the row is his card's plus tk_cur,
; so a new race needs nothing put back). On the grid, lap 1's.
; =====================================================================
TK_KIND equ 3                   ; Bruno (PINK, the tank)
TK_L1   equ -5
TK_L2   equ 0
TK_L3   equ 3

tk_tick:                        ; each picture
        ld hl,cars+C_KIND       ; his car
        ld de,C_SIZE
        ld a,TK_KIND
tk_1:   cp (hl)
        jr z,tk_2
        add hl,de
        jr tk_1
tk_2:   ld de,C_LAPS-C_KIND
        add hl,de
        ld a,(hl)               ; his lap (0 on the grid; LAPS+1 home): what his row takes
        cp LAPS
        jr c,tk_3
        ld a,LAPS
tk_3:   ld e,a
        ld d,0
        ld hl,tk_tab
        add hl,de
        ld a,(hl)
        ld hl,tk_cur
        ld b,(hl)
        ld (hl),a
        sub b                   ; the change
        ret z
        ld b,a
        ld hl,(cdp_tab+1)       ; his card row (the rows card_push reads), its two pushes
        ld de,8*TK_KIND+4
        add hl,de
        ld a,(hl)
        add a,b
        ld (hl),a
        inc hl
        ld a,(hl)
        add a,b
        ld (hl),a
        ret
tk_tab: db TK_L1 AND 255, TK_L1 AND 255, TK_L2 AND 255, TK_L3 AND 255
tk_cur: db 0
