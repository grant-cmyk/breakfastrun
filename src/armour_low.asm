; ARMOUR AND WEAPONS (ARMOUR=1; src/armour.asm has the account of it and every number): the parts that run only now and
; then - the race order's armour bars, a new race, the moment a shell is fired. They live under 0x8000, where code runs
; slower while the TV picture is being drawn, to leave the program's room for the parts that run every picture.
; ---- THE HUD (the race order, hud.asm) ----
; ARM_GAP_PUT (from st_put, when the race order's gap time is being written: B = the pixel row, ST_ACC its 16 pixels):
; the gap ARM_TXT_SH pixels further left than it was - from 3 pixels before column 29 - leaving the car's picture to
; its left and the flag to its right as they are.
arm_gap_put:
        ld c,28*8
        call scr_addr
        ex de,hl
        ld hl,(ST_ACC)
        xor a
        rept ARM_TXT_SH
        add hl,hl
        rla
        endm
        ex de,hl
        ld c,a
        ld a,(hl)
        and 0xFF AND (0xFF << ARM_TXT_SH)
        or c
        ld (hl),a
        inc l
        ld (hl),d
        inc l
        ld a,(hl)
        and (1 << ARM_GLY_SH)-1
        or e
        ld (hl),a
        jp st_nx
; ARM_FLAG (from tower_row, in a race): the flag (it is in), the clock (it has the best lap) or both, ARM_GLY_SH pixels
; left of where they were; then this row's bar.
arm_flag:
        ld a,(tr_row)
        ld b,a
        ld a,(tr_key)
        and 0x18
        jr z,afl_bar
        ld de,clock_top
        cp 0x10
        jr z,afl_2
        ld de,flag_top
        cp 0x08
        jr z,afl_2
        ld de,FLAG8
        call arm_glyph
        ld de,CLOCK8
        call arm_glyph
        jr afl_bar
afl_2:
        call arm_glyph
        call arm_glyph
afl_bar:
        ld a,(tr_row)
        sub TOWER_Y
        srl a
; ARM_BAR (A = a place, 0 to 4): the armour bar of the car in that place - in the row's last column, pixels 4 to 6 of
; its 8 (3 wide), lines 2 to 13 of the row's 16: six pieces of 2 lines, the first at the foot. A piece that is gone
; leaves one dot. While its FLASH runs the piece just lost is shown and not shown, two pictures each.
arm_bar:
        ld e,a
        ld d,0
        ld hl,shown_order       ; (a row not yet drawn for the race - the drivers' faces are still there, in the first
        add hl,de               ; second after the lights: its bar comes with the row)
        ld a,(hl)
        inc a
        ret z
        ld hl,order
        add hl,de
        ld a,(hl)
        call arm_row_a
        ld d,(hl)               ; D = its pieces
        inc hl
        inc hl
        bit 1,(hl)
        jr z,abr_0
        inc d
abr_0:
        ld a,e
        add a,a
        add a,TOWER_Y
        ld b,a
        ld c,31
        call cell_addr
        inc h
        inc h
        ld b,ARM_PIECES
abr_1:
        ld a,b
        dec a
        cp d                    ; piece B - 1: is it there?
        ld a,0x0E
        ld e,a
        jr c,abr_2
        xor a
        ld e,0x04
abr_2:
        call abr_put
        ld a,e
        call abr_put
        djnz abr_1
        ret
abr_put:                        ; A = the bar's 3 pixels for this line; HL to the line below
        ld c,a
        ld a,(hl)
        and 0xF1
        or c
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
arm_glyph:                      ; 8 rows at DE into cell row B, ARM_GLY_SH pixels left of column 31; B to the next row, DE on 8
        ld c,30
        call cell_addr
        push bc
        ld b,8
agl_1:
        ld a,(de)
        inc de
        push de
        ld e,a
        ld d,0
        ex de,hl
        rept ARM_GLY_SH
        add hl,hl
        endm
        ex de,hl
        ld a,(hl)
        and 0xFF AND (0xFF << ARM_GLY_SH)
        or d
        ld (hl),a
        inc l
        ld a,(hl)
        and (1 << ARM_GLY_SH)-1
        or e
        ld (hl),a
        dec l
        inc h
        pop de
        djnz agl_1
        pop bc
        inc b
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
arm_fire:
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
