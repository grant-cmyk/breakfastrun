; =====================================================================
; RACE MODE (RACEMODE=1): its parts that run once a race or once a picture and are not in a hurry - kept in the table
; block at TD (copied there by start_once, like title3.asm: so a call into this file names TD + label_src - td_src, and
; the jumps inside it are relative). The rest: race.asm (the top says what RACE is).
; =====================================================================
; RM_SETUP: a new race (new_race, once the cars' records are copied): the chosen game's parts put in place - by changing a
; few numbers and first bytes in the code, so that nothing extra runs in the race
rm_setup_src:
        ld a,(rmode)
        dec a                   ; RACE 0, COMBAT 0xFF
        ld (dc_kmask+1),a       ; the cars' pictures: RACE, kind AND 0 - every car the racer
        ld (tw_kmask+1),a       ; ... in the race order too
        ld bc,0xDDCD            ; COMBAT: card_near's and arm_bump's first byte (DD), arm_tick's (CD), as assembled
        ld hl,cd_tab-8
        ld de,ai_styles-5
        inc a
        jr z,rms_p
        ld bc,0xC9C9            ; RACE: they return at once (no steering at other cars, no armour lost, no weapons)
        ld hl,cars+C_SIZE+C_PACE
        ld a,4
rms_1:  ld (hl),AI_R_PACE       ; the race drivers' throttle, thinking and mistakes
        inc hl
        ld (hl),AI_R_REACT+OPT_REACT1
        inc hl
        ld (hl),AI_R_ERR
        ld de,C_SIZE-2
        add hl,de
        dec a
        jr nz,rms_1
        ld hl,cd_race-8
        ld de,ai_race-5
rms_p:  ld (cdp_tab+1),hl       ; the cars' card rows
        ld (ais_tab+1),de       ; the drivers' styles
        ld a,b
        ld (card_near),a
        ld (arm_bump),a
        ld a,c
        ld (arm_tick),a
        ret

; RG_UPDATE (tower_update, a picture when no row of the race order needed drawing): RACE - one place's gap brought up to
; date (place = renders MOD 5). RG_FORCE (arm_flag, RACE: the row has just been drawn): its gap drawn, A = its place.
; RG_DRAW: A = a place - its car's GAP TO THE CAR AHEAD (each car's gap to the leader at the last checkpoint it passed,
; hud.asm's cp_hook, less the gap of the car ahead), in small letters in columns 29-31; the leader's row: nothing.
rg_force_src:
        ld hl,tr_force
        ld (hl),1
        jr rg_draw
rg_update_src:
        ld a,(rmode)
        or a
        ret z
        ld a,(renders)
rgu_1:  sub NCARS
        jr nc,rgu_1
        add a,NCARS
rg_draw:
        ld (gd_place),a
        ld bc,0
        or a
        jr z,rgd_0              ; the leader
        ld e,a
        ld d,0
        ld hl,order
        add hl,de
        ld a,(hl)               ; this place's car
        dec hl
        ld c,(hl)               ; C = the car ahead
        call rg_gap
        push de
        ld a,c
        call rg_gap
        pop hl
        or a
        sbc hl,de
        jr nc,rgd_1
        ld hl,0                 ; (ahead of it by the last checkpoints: nothing shown)
rgd_1:  ld b,h
        ld c,l
rgd_0:  ld a,(gd_place)
        add a,a
        ld e,a
        ld d,0
        ld hl,SHGAP
        add hl,de
        ld a,(tr_force)
        or a
        jr nz,rgd_2
        ld a,(hl)
        cp c
        jr nz,rgd_2
        inc hl
        ld a,(hl)
        cp b
        ret z                   ; as shown already
        dec hl
rgd_2:  xor a
        ld (tr_force),a
        ld (hl),c
        inc hl
        ld (hl),b
        ld a,b
        or c
        ld hl,txt_none
        jr z,rgd_3
        ld h,b
        ld l,c
        call time_fmt           ; " 1.2" at time_txt+2
        ld hl,time_txt+2
rgd_3:  ld a,(gd_place)         ; pixel row: the place's band + 5
        add a,a
        add a,TOWER_Y
        add a,a
        add a,a
        add a,a
        add a,5
        ld b,a
        ld c,29
        jp st_text
rg_gap_src:                         ; A = a car -> DE = its gap to the leader (GAPS, frames); C kept
        add a,a
        ld e,a
        ld d,0
        ld hl,GAPS
        add hl,de
        ld e,(hl)
        inc hl
        ld d,(hl)
        ret

