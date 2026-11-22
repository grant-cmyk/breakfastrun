; ARMOUR AND WEAPONS (ARMOUR=1; src/armour.asm has the account of it and every number): the parts that run only now and
; then - the race order's health blocks, a new race, the moment a shell is fired. They live under 0x8000, where code
; runs slower while the TV picture is being drawn, to leave the program's room for the parts that run every picture.
; ---- THE HUD (the race order, hud.asm) ----
; ARM_FLAG (from tower_row, in a race): the flag (it is in), the clock (it has the best lap) or both, in column 28 - where
; the gap time was (it has gone: the health blocks have its room); then this row's health blocks.
arm_flag:
        ld a,(tr_key)
        and 0x18
        jr z,afl_bar
        ld c,28
        if OPT_RACEONLY         ; (the race-only tapes, Grant 22 Nov 2026: "at the end of the game the chequered flag cuts off half
        ld c,29                 ; the car in the HUD" - the car's picture is in columns 27-28: the flag and the clock go in column
        endif                   ; 29, where the gap was, and no gap is drawn for that row - a car in has its place; the best
                                ; lap's time is under the race order as well. The old RACE / COMBAT tapes have no room for it.)
        ld de,clock_top
        cp 0x10
        jr z,afl_2
        ld de,flag_top
        cp 0x08
        jr z,afl_2
        ld a,(tr_row)           ; both: the flag above the small clock
        ld b,a
        ld de,FLAG8
        push bc
        call tr_glyph
        pop bc
        inc b
        ld de,CLOCK8
        call tr_glyph
        jr afl_done
afl_2:
        call tr_glyph16
afl_done:
        if OPT_RACEONLY         ; (race-only: flag or clock, nothing more for this row)
        ret
        endif
afl_bar:
        ld a,(tr_row)
        sub TOWER_Y
        srl a
        if OPT_RACE             ; (RACE mode: no health blocks - the gap to the car ahead in their place: race.asm)
        ld e,a
        ld a,(rmode)
        or a
        ld a,e
        jp nz,rg_force
        endif
; ARM_BAR (A = a place, 0 to 4): THE HEALTH BLOCKS of the car that row shows (Grant, 18 Nov 2026, option C: "when health
; is good all bars are green, when 2 bars the 2 bars are yellow and 1 bar the 1 bar is red, when 0 - all three bars
; flash red"). The row's last three squares (columns 29-31, both its character rows) black, a block in each: 6 pixels
; wide (pixels 1-6), 12 lines tall (lines 2-13 of the row's 16). A block is two of the car's six pieces of armour; an odd
; one left shows as the lower half of its block. The ink by the blocks left (pieces / 2, rounded up): 3 green, 2 yellow,
; 1 red. While a FLASH runs (ARM_FLASH pictures after a piece is lost) the half just lost is shown and not shown, two
; pictures each. With none left: three red outlines, two pictures on and two off, for as long as it lasts (the FLASH
; kept going round here - atk_1 in armour.asm counts it down every picture and calls this).
arm_bar:
        ld e,a
        ld d,0
        ld hl,shown_order       ; (a row not yet drawn for the race - the drivers' faces are still there, in the first
        add hl,de               ; second after the lights: its blocks come with the row)
        ld a,(hl)
        inc a
        ret z
        dec a                   ; the car the row SHOWS (not the one the race order has there now: two cars that swapped
        and 7                   ; and swapped back before the row was drawn again left a row with the other's bar - 18 Nov 2026)
        call arm_row_a
        ld d,(hl)               ; D = its pieces
        inc hl
        inc hl                  ; HL at its FLASH
        ld a,d
        ld c,0x44               ; the colour (bright, on black): green,
        cp 5
        jr nc,abr_c
        ld c,0x46               ; yellow,
        cp 3
        jr nc,abr_c
        ld c,0x42               ; red
abr_c:
        or a
        jr nz,abr_s
        ld a,(hl)               ; none left: keep the FLASH going round (4, 3, 2, 1, 0: two shown, two not)
        or a
        jr nz,abr_o
        ld (hl),4
abr_o:
        and 2
        jr z,abr_d              ; (D = 0: nothing shown this picture)
        ld a,0x80               ; (D = 0x80: the outlines)
        jr abr_d
abr_s:
        bit 1,(hl)
        jr z,abr_d
        inc a                   ; the piece just lost, shown this picture
abr_d:
        ld d,a                  ; D = halves of a block shown
        ld a,e
        add a,a
        add a,TOWER_Y
        ld b,a                  ; B = the row's first character row
        rrca                    ; its colours: 0x5800 + 32 x B + 29, and the row below
        rrca
        rrca
        ld l,a
        and 3
        or 0x58
        ld h,a
        ld a,l
        and 0xE0
        or 29
        ld l,a
        ld a,c
        ld (hl),a
        inc l
        ld (hl),a
        inc l
        ld (hl),a
        push de
        ld de,30
        add hl,de
        pop de
        ld (hl),a
        inc l
        ld (hl),a
        inc l
        ld (hl),a
        ld c,29                 ; the three blocks, columns 29-31
abr_b:
        push bc
        push de
        ld a,c                  ; E = 2 x the block (0, 2, 4): the halves before it
        sub 29
        add a,a
        ld e,a
        call cell_addr          ; HL = its top line
        ld a,d
        rla
        ld c,0x42               ; the outline: its sides
        ld a,2
        jr c,abr_e
        ld c,0x7E               ; a block: solid
        ld a,d
        sub e                   ; halves in this block
        ld e,16                 ; (none: no line drawn)
        jr c,abr_t
        jr z,abr_t
        ld e,8                  ; one: the lower half, lines 8-13
        dec a
        jr z,abr_t
        ld a,2                  ; two: lines 2-13
abr_e:
        ld e,a
abr_t:                          ; lines E to 13: the first and the last whole, the rest C; the others clear
        ld b,0
abr_l:
        ld a,b
        cp e
        jr c,abr_0
        cp 14
        jr nc,abr_0
        cp 13
        jr z,abr_7
        cp e
        ld a,c
        jr nz,abr_w
abr_7:
        ld a,0x7E
        jr abr_w
abr_0:
        xor a
abr_w:
        call abr_put
        inc b
        bit 4,b
        jr z,abr_l
        pop de
        pop bc
        inc c
        ld a,c
        cp 32
        jr nz,abr_b
        ret
arm_bar_t:                      ; (from arm_tick: HL at the car's FLASH, just counted down; A = the place) drawn again only when
        bit 0,(hl)              ; it changes - at an odd count, as the shown and not shown go by twos (a drawing is about 8,000
        jp nz,arm_bar           ; T: this halves it) ...
        inc (hl)
        dec (hl)
        ret nz
        dec hl                  ; ... and at 0: drawn as it now is - or, with no pieces left, the outlines' flash set going
        dec hl                  ; round again (they are not shown at 1, 0 or 4)
        ld c,(hl)
        inc hl
        inc hl
        inc c
        dec c
        jp nz,arm_bar
        ld (hl),4
        ret
abr_put:                        ; A into the line at HL; HL to the line below
        ld (hl),a
        inc h
        ld a,h
        and 7
        ret nz
        ld a,l
        add a,32
        ld l,a
        ret c
        ld a,h
        sub 8
        ld h,a
        ret

; ARM_NEW: a new race - every car's armour whole, nothing flashing, nobody spinning; the weapons wait ARM_START pictures.
; ARM_MEND: your armour whole again (the oil can).
arm_new:
        ld hl,arm_tab+1
        ld b,NCARS
anw_1:
        call anw_row
        inc hl
        inc hl
        djnz anw_1
        ld a,ARM_START
        ld (sh_cool),a
        ld (wh_cool),a
        ld a,TANK_SHOTS         ; a race's shells and wheel-outs, as the NOS canisters (18 Nov 2026)
        ld (sh_ammo),a
        ld a,WH_USES
        ld (wh_ammo),a
        ret
arm_mend:
        ld hl,arm_tab+1
        call anw_row
        ld a,1                  ; (and its bar drawn afresh: arm_tick)
        ld (arm_tab+1+A_FL),a
        ret
anw_row:                        ; the row at HL (its PIECES): whole, and its other six bytes 0; HL to its last byte
        ld (hl),ARM_PIECES
        ld c,6
        xor a
anw_2:
        inc hl
        ld (hl),a
        dec c
        jr nz,anw_2
        ret
; ARM_FIRE (IX = the car that fires): a shell leaves it, straight along its heading.
        if OPT_RACEONLY = 0     ; (RACEONLY: no shells)
arm_fire:
        ld hl,sh_ammo           ; (one shell fewer)
        dec (hl)
        ld a,TANK_COOL
        ld (sh_cool),a
        ld a,(ix+C_KIND)
        ld (sh_own),a
        ld hl,sh_fired
        inc (hl)
        ld hl,2*256+8           ; the falling note
        ld (snd_fxt),hl
        push ix                 ; it starts where the car is
        pop hl
        ld de,sh_rec
        ld bc,6
        ldir
        ld a,(ix+C_ANG)
        call heading_push       ; DE across, BC down: 64 the way it points
        ex de,hl
        rept SHELL_SHIFT
        add hl,hl
        endm
        ld (sh_vx),hl
        ld h,b
        ld l,c
        rept SHELL_SHIFT
        add hl,hl
        endm
        ld (sh_vy),hl
        ld a,SHELL_LIFE
        ld (sh_life),a
        ret
        endif
