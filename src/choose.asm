; =====================================================================
; THE CHOOSE SCREEN (Grant, 16 Nov 2026: "when you click 1 or 2, you get a screen that asks you which track
; and which player ... The race track is selected by clicking left and right to choose the track, then click
; forward to select. Then click person and then car ... You select them in the same way. Then on the car you
; choose one extra of acceleration, grip and speed (you have one of each by default)").
;
; Only in the CHOOSE build (tools/build_choose.sh -> build/racer_choose.tap), which is the several-tracks build.
; Four steps, each a card like the title's menu: TRACK, then for each player DRIVER, CAR and EXTRA. Steer left
; and right to go through the choices, accelerate to pick - player 1 with the keys the K screen gave, player 2
; with 6 (left), 7 (right) and 9 (accelerate): the keys a Sinclair joystick presses.
;
; How a choice reaches the race:
;   TRACK   hp.asm unpacks it onto its working places each time the choice moves (trk_set)
;   DRIVER  pwho: the driver in each car, 0-6 (who_a looks it up wherever a face or a name is shown). The first
;           five are in the race; player 1's is the first, player 2's the second, the computer has the rest
;   CAR     the cars' table (big_tab, 16 headings a car) holds the five cars in the race; up to five more are kept
;           with the packed tracks (tools/choose_cars.txt lists them: a new car is a drawing and a line there).
;           Choosing swaps two cars' places in the table, so the race draws as before
;   EXTRA   su_lv, which su_apply (hud.asm) turns into your car's top speed, push and grip
; The choices stay as they are for the next race. Two players: the second's driver and car are in the race
; (the cyan car), but the computer drives it - there is no two-player race yet.
; =====================================================================
CH_TMP  equ BUF+0x0F62          ; a car's picture, 16 rows of 2 bytes, to draw twice the size (the back buffer's rows that
                                ; scr_save does not use; 2 bytes before it and 4 after may be written)
ch_np:  db 1                    ; how many are playing
ch_p:   db 0                    ; the player choosing: 0, 1
ch_j:   db 0                    ; the choice shown ...
ch_min: db 0                    ; ... the first that can be chosen (player 2 cannot have player 1's driver or car) ...
ch_n:   db 0                    ; ... and one past the last
ch_ex:  db 0,0                  ; each player's extra: 0 ACCELERATION, 1 GRIP, 2 SPEED
pwho:   db 0,1,2,3,4,5,6        ; the driver in each car (the last two: not in this race)
cwho:   db 0,1,2,3,4,5,6,7,8,9  ; the car in each place of the cars' table (for its name): ten at most

choose:
        ld hl,ch_r_trk          ; THE TRACK
        ld a,(HP+3)             ; (the one in its working places now)
        ld e,a
        ld d,0
        call ch_run
        xor a
ch_pl:
        ld (ch_p),a
        ld d,a
        ld e,a
        push de
        ld hl,ch_r_who          ; THE DRIVER
        call ch_run
        ld hl,pwho
        call ch_swap
        pop de
        ld a,(HP_NCAR)          ; (as many cars as tools/choose_cars.txt lists)
        ld (ch_r_car+3),a
        ld hl,ch_r_car          ; THE CAR
        call ch_run
        ld hl,cwho
        call ch_swap
        ld a,(ch_p)             ; ... and the two cars' 16 headings change places in the cars' table
        call ch_ent
        ex de,hl
        ld a,(ch_j)
        call ch_ent
        ld b,64
        call ch_xch
        call ch_exp             ; THE EXTRA
        ld e,(hl)
        ld d,0
        ld hl,ch_r_ex
        call ch_run
        call ch_exp
        ld a,(ch_j)
        ld (hl),a
        ld a,(ch_p)             ; the next player
        inc a
        ld hl,ch_np
        cp (hl)
        jr c,ch_pl
        ld hl,0x0101            ; player 1's extra: every part at level 1 ...
        ld (su_lv),hl
        ld hl,0x0001
        ld (su_lv+2),hl
        ld a,(ch_ex)            ; ... and one of them at 2 (su_lv: GRIP, SPEED, ACCEL)
        ld hl,su_lv+2
        or a
        jr z,ch_a1
        ld hl,su_lv
        dec a
        jr z,ch_a1
        inc hl
ch_a1:
        inc (hl)
        jp k_up                 ; (the keys let go: the race reads them too)

ch_exp:                         ; HL -> the choosing player's extra
        ld hl,ch_ex
        ld a,(ch_p)
        or a
        ret z
        inc hl
        ret

; CH_SWAP: in the list at HL, entries ch_p and ch_j change places
ch_swap:
        ld d,0
        ld a,(ch_p)
        ld e,a
        push hl
        add hl,de
        ex (sp),hl
        ld a,(ch_j)
        ld e,a
        add hl,de
        pop de
        ld b,1
ch_xch:                         ; the B bytes at HL and at DE change places
        ld a,(de)
        ld c,(hl)
        ld (hl),a
        ld a,c
        ld (de),a
        inc hl
        inc de
        djnz ch_xch
        ret

; CH_ENT: A = a place in the cars' table, 0-6 -> HL = its 64 bytes (DE kept)
ch_ent:
        ld hl,big_tab
        cp 5
        jr c,ce_1
        sub 5
        ld hl,(HP_CARS)
ce_1:
        push de
        ld d,a
        ld e,0
        srl d
        rr e
        srl d
        rr e
        add hl,de
        pop de
        ret

; WHO_A: A = a car -> A = its driver (HL kept)
who_a:
        push hl
        ld hl,pwho
        call ch_at
        pop hl
        ret
ch_at:                          ; A = entry A of the list at HL
        add a,l
        ld l,a
        jr nc,ct_1
        inc h
ct_1:
        ld a,(hl)
        ret

; CH_RUN: one step. HL = its record: the heading's text, its column, the number of choices, the routine that
; shows choice ch_j. E = the choice to start on, D = the first that can be chosen. Comes back when accelerate
; is pressed, the choice in ch_j.
ch_run:
        ld (ch_j),de
        ld e,(hl)
        inc hl
        ld d,(hl)
        inc hl
        ld c,(hl)
        inc hl
        ld a,(hl)
        ld (ch_n),a
        inc hl
        ld a,(hl)
        inc hl
        ld h,(hl)
        ld l,a
        ld (cr_draw+1),hl
        push de
        push bc
        call t_cls
        call t_ging
        ld hl,ch_script
        call ds_run
        pop bc
        pop hl
        ld b,2
        ld a,0x67
        call print_big
cr_draw:
        call 0
cr_up:
        call ch_keys            ; the keys let go, then a new press
        jr nz,cr_up
cr_w:
        halt
        call ch_keys
        jr z,cr_w
        ld hl,ch_j
        bit 2,a
        ret nz                  ; accelerate: this one
        rra
        jr c,cr_l
        inc (hl)                ; right: the next, round to the first
        ld a,(ch_n)
        cp (hl)
        jr nz,cr_draw
        ld a,(ch_min)
        ld (hl),a
        jr cr_draw
cr_l:
        ld a,(ch_min)           ; left: the one before, round to the last
        cp (hl)
        jr nz,cr_l1
        ld a,(ch_n)
        ld (hl),a
cr_l1:
        dec (hl)
        jr cr_draw

; CH_KEYS: the choosing player's keys - A = bit 0 left, bit 1 right, bit 2 accelerate; Z: none down.
; Player 1: the keys read_keys reads (the K screen writes them there). Player 2: 6, 7 and 9.
ch_keys:
        ld a,(ch_p)
        or a
        jr nz,ck_2
        ld hl,k_left+1          ; each key: its half row, then 4 bytes on its bit; the next is 10 bytes on
        ld bc,0x0301
        ld d,a
ck_1:
        ld a,(hl)
        in a,(0xFE)
        push hl
        inc hl
        inc hl
        inc hl
        inc hl
        and (hl)
        pop hl
        jr nz,ck_u
        ld a,d
        or c
        ld d,a
ck_u:
        sla c
        ld a,10
        add a,l
        ld l,a
        jr nc,ck_n
        inc h
ck_n:
        djnz ck_1
        ld a,d
        or a
        ret
ck_2:
        ld a,0xEF               ; the half row 6 7 8 9 0: bits 4 3 2 1 0
        in a,(0xFE)
        cpl
        ld b,a
        xor a
        bit 4,b
        jr z,ck_3
        inc a
ck_3:
        bit 3,b
        jr z,ck_4
        or 2
ck_4:
        bit 1,b
        jr z,ck_5
        or 4
ck_5:
        or a
        ret

; ---- what each step shows ----
ch_tag:                         ; PLAYER 1 / PLAYER 2 on the player's own colour, under the heading
        ld a,(ch_p)
        add a,'1'
        ld (ch_t_pl+7),a
        call ch_col
        ld bc,0x060C
        ld de,0x0108
        call set_attrs
        ld hl,ch_t_pl
        ld bc,0x060C
        jp print_at
ch_band:                        ; the picture's 4 x 4 cells in the player's colour, as the race order shows a car
        call ch_col
        ld bc,0x0A0E
        ld de,0x0404
        jp set_attrs
ch_col:
        ld a,(ch_p)
        jp pd_cc

; The track: unpacked, then its road drawn from the track's own SURFACE MAP - a bit a tile, 9 bytes a row, 0 = road -
; a pixel a tile, so the picture is 72 across and as many lines as the track has tile rows (64 to 84). Its name above.
ch_d_trk:
        ld a,(ch_j)
        call HP+4               ; (trk_set, hp.asm)
        ld bc,0x080C
        ld de,0x0B09
        call clear_cells
        ld de,surface_map
        ld a,(oc_try+3)         ; (the track's tile rows: MAPH, as this track's code has it)
        ld b,64
ct_row:
        push af
        ld c,96
        call scr_addr
        push bc
        ld b,9
ct_byte:
        ld a,(de)
        cpl
        ld (hl),a
        inc de
        inc l
        djnz ct_byte
        pop bc
        inc b
        pop af
        dec a
        jr nz,ct_row
        ld a,(ch_j)
        ld hl,(HP_NAMES)
        ld b,6
        jp ch_nam2

ch_d_who:                       ; a driver: the face twice the size, the name
        call ch_tag
        call ch_band
        ld a,(ch_j)
        ld hl,pwho
        call ch_at
        push af
        rrca
        rrca
        rrca
        ld e,a
        ld d,0
        ld hl,faces
        add hl,de
        ex de,hl
        call ch_pic
        pop af
        ld hl,pd_names
ch_name:                        ; text A of the list at HL, in the middle of row 16 (ch_nam2: of row B)
        ld b,16
ch_nam2:
        push bc
        call str_skip
        pop bc
        push bc
        push hl
        ld c,4
        ld de,0x0118
        call clear_cells
        pop hl
        push hl
        ld b,0xFF
cn_1:
        inc b
        ld a,(hl)
        inc hl
        or a
        jr nz,cn_1
        srl b
        ld a,16
        sub b
        ld c,a
        pop hl
        pop af
        ld b,a
        jp print_at
ch_pic:                         ; 16 rows of 2 bytes at DE, twice the size, in the picture's cells
        ld bc,80*256+112
        ld a,2
        jp dbl

ch_d_car:                       ; a car: its heading 0 (nose up) twice the size, its name
        call ch_tag
        call ch_band
        ld hl,CH_TMP
        ld b,32
cd_0:
        ld (hl),0
        inc hl
        djnz cd_0
        ld a,(ch_j)
        call ch_ent
        ld e,(hl)
        inc hl
        ld d,(hl)               ; DE = the frame: a row is mask, ink, mask, ink
        inc hl
        ld a,(hl)               ; its first row (the car's own top line is row 6)
        inc hl
        ld b,(hl)               ; its rows
        sub 6
        add a,a
        ld l,a
        sbc a,a
        ld h,a
        push bc
        ld bc,CH_TMP
        add hl,bc
        pop bc
cd_1:
        inc de
        ld a,(de)
        ld (hl),a
        inc de
        inc hl
        inc de
        ld a,(de)
        ld (hl),a
        inc de
        inc hl
        djnz cd_1
        ld de,CH_TMP
        call ch_pic
        ld a,(ch_j)
        ld hl,cwho
        call ch_at
        ld hl,(HP_CNAMES)
        jp ch_name

ch_d_ex:                        ; the extra: three parts, a filled pip each; the one chosen is lit and has a second
        call ch_tag
        xor a
cx_1:
        ld (cx_i+1),a
        add a,a
        add a,10
        ld (cx_r+1),a
        ld b,a
        ld c,7
        ld de,0x0112
        ld hl,ch_j
        ld a,(cx_i+1)
        cp (hl)
        ld a,T_CARD
        ld l,0x42
        jr nz,cx_2
        ld a,0x70
        ld l,0x7E
cx_2:
        push hl
        call set_attrs
cx_i:   ld a,0
        ld hl,ch_t_ex
        call str_skip
        call cx_row
        ld c,8
        call print_at
        call cx_row
        ld a,0x7E
        call ch_pip
        call cx_row
        inc c
        inc c
        pop hl
        ld a,l
        call ch_pip
        ld a,(cx_i+1)
        inc a
        cp 3
        jr nz,cx_1
        ret
cx_row:
cx_r:   ld b,0
        ld c,21
        ret
ch_pip:                         ; a pip in cell B, C: A = 0x7E filled, 0x42 an empty box
        push af
        call cell_addr
        pop af
        inc h
        ld (hl),0x7E
        ld b,4
cp_1:
        inc h
        ld (hl),a
        djnz cp_1
        inc h
        ld (hl),0x7E
        ret

; (the steps' records, the card and the texts: src/choose_td.asm, in the table block at TD; their equs: racer.asm, after the block)
