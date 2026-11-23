; =====================================================================
; THE TITLE / ATTRACT SCREEN (Grant, 14 Nov 2026: "want the person to see they
; choose 1UP or 2UP to play, K to customize keys, have the title screen have
; some kind of attract sequence showing the different drivers, maybe a face
; and have that car skid around"). Layout A of docs/design/TITLE-SCREEN.md:
; the logo twice its size, the lap record, a cloth "stage" in a slim frame, a
; driver's card beside it, 1 = 1UP, 2 = 2UP, K = KEYS.
;
; This file sits BELOW the program, in the 1.1 KB the small cars leave free
; under 0x8000 (it loads in the same block), so it is still there after a race.
; The stage's car (drawn every other TV frame) is in title2.asm, in the program
; itself: memory below 0x8000 runs slower while the picture is being shown.
;
; It only uses the cars, faces, font and routines the game already has:
;   print_at, print_big, set_attrs, clear_cells, scr_addr, time_fmt, trig.
; Its variables are in the printer buffer (0x5B00), which nothing else uses.
; =====================================================================
TS      equ 0x5B00              ; the title's variables (not kept on the tape)
a_x     equ TS                  ; the stage's car: x, 8.8 (whole part = cloth x + 32)
a_y     equ TS+2                ;   y, 8.8 (whole part = the frame's top row + 32)
a_phi   equ TS+4                ;   the way it is going, 256 to the turn (0 = up, clockwise)
a_om    equ TS+5                ;   its turn a step (signed)
a_n     equ TS+6                ;   steps left of this part of the run
a_dr    equ TS+7                ;   the drift: how far the nose is turned into the bend
a_scr   equ TS+8                ;   the next part of the run
a_h     equ TS+10               ;   the heading pictured, 0..15
a_oy    equ TS+11               ;   as drawn: its first row (+ 32) ...
a_on    equ TS+12               ;   ... and its rows (0: not drawn)
a_kc    equ TS+13               ;   ... and its first column (the 14 bytes from a_x are a car's: t_blk)
t_drv   equ TS+21               ; the car being moved, 0..4
t_tmp   equ TS+14               ; a one-letter text (2 bytes)
k_i     equ TS+16               ; KEYS: the key being asked for, 0..4
k_tmp   equ TS+17               ; KEYS: a key cap's text (3 bytes)
t_msg   equ TS+20               ; steps the 2UP message stays
a_sav   equ TS+22               ; what was under the car: 3 bytes a row, 18 rows at most
TD      equ TS+76               ; the title's tables kept in memory but not in the program: the
                                ; start-up copies title3.asm here (to 0x5C77: the printer buffer
                                ; and the ROM's own variables below FRAMES, idle once the game's
                                ; interrupt is on - the game calls nothing in the ROM)

T_TABLE equ 0x30                ; black on yellow: the table
T_HEAD  equ 0x4F                ; bright white on blue
T_CARD  equ 0x78                ; black on bright white
T_KEY   equ 0x47                ; bright white on black: a key cap
T_P1    equ 0x57                ; bright white on red: 1UP

; ---------------------------------------------------------------------
; TITLE_AGAIN: after a race (hud_over jumps here on the accelerate key). The race
; screen's fixed parts are drawn once, by start-up code that is gone by now, so
; everything outside the play window is kept in the back buffer (free while no
; race is running) and put back before the next race.
; ---------------------------------------------------------------------
title_again:
        call k_up               ; (the key let go first: it may be one the title answers to)
        xor a
        ld (snd_rate),a         ; the engine quiet
        ld a,6                  ; (and the border the table's yellow, if the NOS left it white)
        ld (snd_port),a
        out (254),a
        call scr_save
        ld hl,BUF+2384+LOGO_COL ; the logo is in the kept picture (line 168 of it: 16 whole lines, 136 of 10 bytes, 16 whole), 32 bytes a line
        ld a,25
        call title
        call scr_rest
        jp new_race

; SCR_SAVE / SCR_REST: the screen outside the play window to the back buffer, or
; back: lines 0-15 and 152-191 whole, lines 16-151 byte 0 and bytes 23-31 (the
; logo's lines whole, so the title can read it there), then the colours. 3,920 bytes.
scr_rest:
        ld a,0xEB               ; (EX DE,HL round the copy: buffer -> screen)
        defb 0x01               ; (LD BC,nn: skips the next two bytes)
scr_save:
        xor a                   ; (NOP: screen -> buffer)
        nop
        ld (xf_a),a
        ld (xf_b),a
        ld de,BUF
        ld b,0
xs_row:
        ld c,0
        call scr_addr
        push bc
        ld a,b
        sub 16
        cp 136
        ld bc,32
        jr nc,xs_full
        ld c,1
        call xf
        ld c,22
        add hl,bc
        ld c,9
xs_full:
        call xf
        pop bc
        inc b
        ld a,b
        cp 192
        jr nz,xs_row
        ld hl,0x5800
        ld bc,768
xf:
xf_a:   nop
        ldir
xf_b:   nop
        ret

; ---------------------------------------------------------------------
; TITLE: HL = the logo's 16 rows of 7 bytes, A = the bytes between one row and
; the next (0, or 25 for rows kept 32 apart). Comes back when 1 is pressed (and
; let go: the race's set-up reads the same key).
; ---------------------------------------------------------------------
title:
        ld (t_logo+1),hl
        ld (t_lsk+1),a
t_redraw:
        call t_cls
        call t_ging
        ld hl,t_script
        call ds_run
        if OPT_RACE * (1 - OPT_RACEONLY)
        call t_mode             ; RACE or COMBAT, after "M  MODE:"
        endif
t_logo: ld de,0                 ; the logo twice the size: 14 x 4 cells, centred on the card
t_lsk:  ld a,0
        ld (db_skip+1),a
        ld bc,0x1858            ; (from column 11: the big egg is on their left)
        ld a,7
        call dbl
        ld bc,0x050B            ; the logo's own RUN and small egg off: the title has its own
        ld de,0x020E
        call clear_cells
        call t_run              ; RUN, cut through the middle, and its speed lines (clothmini.asm)
        xor a
        ld (db_skip+1),a
        ld de,t_egg             ; the egg, twice the size: 4 x 4 cells from row 3, column 5
        ld bc,0x1828
        ld a,2
        call dbl
        ld hl,(rec_lap)         ; the lap record: the best lap since loading
        ld a,h
        and l
        inc a
        ld hl,TD + t_norec_src - td_src
        jr z,t_rec
        ld hl,(rec_lap)
        call time_fmt
        ld hl,time_txt
t_rec:
        ld bc,162*256+148       ; small, and a row lower (Grant, 15 Nov 2026: "the lap record should be the
        call sm_ctr             ; smaller text and one row down")
        ld hl,t_lrec
        ld bc,162*256+100
        call sm_ctr
        xor a                   ; the five drivers' faces in a row, each on its car's colour
t_face:
        ld (t_tmp),a
        ld e,a
        ld d,0
        ld hl,car_colours_src
        add hl,de
        add a,a
        add a,a
        add a,7
        ld c,a
        ld (t_tmp+1),a
        ld b,16
        ld a,(hl)
        cp 0x78                 ; the white driver's band: plain white, so it shows on the card's bright white
        jr nz,t_f1              ; (Grant, 15 Nov 2026: "put the lady in bright zero area, so she also has a colour border")
        ld a,0x38
t_f1:
        ld de,0x0202
        call set_attrs
        ld a,(t_tmp)
        if OPT_CHOOSE
        call who_a              ; CHOOSE: the driver in this car today
        endif
        rrca
        rrca
        rrca
        ld e,a
        ld d,0
        ld hl,faces_src
        add hl,de
        ex de,hl
        ld a,(t_tmp+1)
        ld c,a
        ld b,16
        push bc
        call tr_face_c
        pop bc
        inc b
        call tr_face_c
        call t_name             ; the driver's name under the face (racer.asm, in the table block)
        ld a,(t_tmp)
        inc a
        cp NCARS
        jr nz,t_face
        xor a
        ld (t_msg),a
        call tc_init            ; the five cars, round the cloth's edge (plateco.asm)
t_loop:
        halt
        call t_anim             ; the faces (plate_slow.asm)
        call tc_step            ; the cars, straight after the interrupt (five masked cars take more than
                                ; one TV frame, so there is no second HALT: a step every other frame, 25 a second)
        if OPT_CHOOSE           ; CHOOSE: 1 or 2 -> the choose screen (choose.asm), and from there the race
        call k_scan
        jr z,t_loop
        ld a,l
        sub 15                  ; (1 is key 15, 2 is key 16)
        cp 2
        jr nc,t_k0
        inc a
        ld (ch_np),a            ; how many are playing
        jp choose
t_k0:
        ld a,l
        else
        if OPT_2P = 0           ; (TWOP: 2 plays, so there is no message)
        ld hl,t_msg             ; the 2UP message: the choice again after 1.5 s
        ld a,(hl)
        or a
        jr z,t_keys
        dec (hl)
        ld hl,t_press
        call z,t_prompt
        endif
t_keys:
        if OPT_MULTI
        call HP                 ; MULTI: k_scan, and T picks the next track (src/hp.asm)
        else
        call k_scan
        endif
        jr z,t_loop
        ld a,l
        cp 15                   ; 1: play
        if OPT_PICK             ; (PICK: first the CHOOSE YOUR CAR card - pick.asm)
        jp z,pick
        else
        jp z,k_up
        endif
        cp 16                   ; 2: not yet
        jr nz,t_k
        if OPT_2P               ; TWOP: 2 - a two-player race (twoplayer.asm)
        ld a,1
        ld (two_p),a
        jp k_up
        else
        ld a,40
        ld (t_msg),a
        ld hl,t_soon
        call t_prompt
        jr t_loop
        endif
        endif                   ; (CHOOSE)
t_k:
        if OPT_RACE * (1 - OPT_RACEONLY)  ; (RACEONLY: no COMBAT, no M)
        cp 37                   ; M: RACE or COMBAT
        jr nz,t_k1
        ld hl,rmode
        ld a,(hl)
        xor 1
        ld (hl),a
        call t_mode
        call k_up
        jr t_loop
t_k1:
        endif
        cp 32                   ; K: the keys
        jr nz,t_loop
        call keys_screen
        jp t_redraw
        if OPT_2P = 0
t_prompt:
        ld bc,0x0E06            ; (row 14, under the choices: the lap record has row 20 now)
        jp print_at
        endif

t_cls:                          ; the whole screen: the bare table
        ld hl,0x4000
        ld de,0x4001
        ld bc,6144
        ld (hl),l
        ldir
        ld (hl),T_TABLE
        ld bc,767
        ldir
        ret

; T_GING: the tablecloth - every cell bright red or bright white paper in turn, ink black, and not
; a pixel set: the cars that lap the edge are black line on whichever they are over, the checks
; showing through them (Grant, 15 Nov 2026, after trying them masked in red line: "lets go back
; to A - black line see through"). Black with a white mask as well would be three colours a cell.
t_ging:
        ld hl,0x5800
tgg_1:
        ld a,l                  ; (column + row) odd? the column's low bit is L's, the row's is L's bit 5
        rlca
        rlca
        rlca
        xor l
        rra
        ld (hl),0x50
        jr nc,tgg_2
        ld (hl),T_CARD
tgg_2:
        inc hl
        ld a,h
        cp 0x5B
        jr nz,tgg_1
        ret
; A_START: the car's run, from its start (title3.asm, a_runs)
a_start:
        ld hl,TD + a_runs_src - td_src
        ld de,a_x+1
        ldi
        inc de
        ldi
        ldi
        ld (a_scr),hl
        xor a
        ld (a_n),a
        ld (a_dr),a
        ret

; DS_RUN: draw what the list at HL says. Each entry starts row + kind, column:
;   row         text ...,0             the ROM's letters
;   row + 0x40  colour, text ...,0     letters twice the size, in that colour
;   row + 0x80  rows, columns, colour  those cells' colour
;   0xFF        the end
ds_run:
        ld a,(hl)
        cp 0xFF
        ret z
        inc hl
        ld c,(hl)
        inc hl
        ld b,a
        res 7,b
        res 6,b
        add a,a
        jr c,ds_rect
        jp m,ds_big
        call print_at
        jr ds_nx
ds_big:
        ld a,(hl)
        inc hl
        call print_big
ds_nx:
        inc hl
        jr ds_run
ds_rect:
        ld d,(hl)
        inc hl
        ld e,(hl)
        inc hl
        ld a,(hl)
        push hl
        call set_attrs
        pop hl
        jr ds_nx

; DBL: a picture twice the size. DE = 16 rows of A bytes (db_skip bytes between
; rows), B = the top pixel line, C = the pixel x (a whole byte).
dbl:
        ld (db_w+1),a
        ld a,16
db_row:
        push af
        push de
        call db_line
        pop de
        call db_line
db_skip: ld hl,0
        add hl,de
        ex de,hl
        pop af
        dec a
        jr nz,db_row
        ret
db_line:
        call scr_addr
        push bc
db_w:   ld c,0
db_b:
        ld a,(de)
        inc de
        push hl
        ld b,8
db_1:
        add a,a                 ; each bit twice
        push af
        adc hl,hl
        pop af
        adc hl,hl
        djnz db_1
        ld a,l
        ld b,h
        pop hl
        ld (hl),b
        inc l
        ld (hl),a
        inc l
        dec c
        jr nz,db_b
        pop bc
        inc b
        ret

str_skip:                       ; HL = texts, one after another: on past A of them
        or a
        ret z
        ld b,a
ss_1:
        ld a,(hl)
        inc hl
        or a
        jr nz,ss_1
        djnz ss_1
        ret

; ---------------------------------------------------------------------
; K_SCAN: the keyboard. NZ: a key is down - L = which (0..39: the 8 half rows,
; 5 keys each, from CAPS SHIFT), E = its half row's port byte, D = its bit.
; K_UP: wait until no key is down.
; ---------------------------------------------------------------------
k_up:
        call k_scan
        jr nz,k_up
        ret
k_scan:
        ld bc,0xFEFE
        ld l,0
ks_row:
        in a,(c)
        cpl
        and 0x1F
        jr nz,ks_hit
        ld a,l
        add a,5
        ld l,a
        rlc b
        jr c,ks_row
        xor a
        ret
ks_hit:
        ld d,1
ks_bit:
        rrca
        jr c,ks_done
        inc l
        sla d
        jr ks_bit
ks_done:
        ld e,b
        or 1
        ret

; ---------------------------------------------------------------------
; KEYS_SCREEN (K): 1UP's five keys, asked for in turn - the row lights and its
; key cap flashes, the big line names the key wanted. Refused: a key already
; taken, the shifts and ENTER, 0-3 (the set-up's keys), SPACE to accelerate (the
; race screen's PRESS ? has to name the key). read_keys is told each choice.
; ---------------------------------------------------------------------
keys_screen:
        call t_cls
        ld hl,TD + k_script_src - td_src
        call ds_run
        ld hl,0x0020
        ld (k_tmp+1),hl
        xor a
kd_1:
        ld (k_i),a
        call k_name
        call k_rowb
        ld c,10
        call print_at
        call k_cap
        ld a,(k_i)
        inc a
        cp 5
        jr nz,kd_1
        xor a
ka_1:
        ld (k_i),a
        ld a,0x70               ; the row lit: bright yellow
        call k_rattr
        call k_rowb             ; its cap flashing
        ld c,21
        ld de,0x0101
        ld a,0xC7
        call set_attrs
        ld bc,0x1300            ; the big line: the key wanted
        ld de,0x0220
        call clear_cells
        ld bc,0x1300
        ld de,0x0220
        ld a,T_TABLE
        call set_attrs
        call k_name
        ld bc,0x1306
        ld a,T_P1
        call print_big
        call k_up
ka_w:
        call k_scan
        jr z,ka_w
        ld h,0
        ld bc,TD + k_chars_src - td_src
        add hl,bc
        ld c,(hl)               ; C = the key's letter
        ld a,(k_i)
        ld b,a
        ld a,c
        cp ' '
        jr nz,ka_2
        ld a,b
        cp 2
        jr z,ka_w
        jr ka_3
ka_2:
        cp '4'
        jr c,ka_w
ka_3:
        ld hl,TD + key_ch_src - td_src            ; taken by one before it?
        inc b
        jr ka_5
ka_4:
        ld a,(hl)
        cp c
        jr z,ka_w
        inc hl
ka_5:
        djnz ka_4
        ld (hl),c               ; (HL = key_ch + k_i)
        ld a,(k_i)
        add a,a
        ld c,a
        ld hl,TD + k_patch_src - td_src
        add hl,bc               ; (B = 0)
        ld a,(hl)
        inc hl
        ld h,(hl)
        ld l,a                  ; where read_keys has this key's half row ...
        ld (hl),e
        inc hl
        inc hl
        inc hl
        inc hl
        ld (hl),d               ; ... and its bit
        ld a,T_CARD
        call k_rattr
        call k_cap
        ld a,(k_i)
        inc a
        cp 5
        jp nz,ka_1
        ; (any key ends the wait after a race now: hud_over)
        jp k_up
k_rowb:                         ; B = the cell row of key k_i
        ld a,(k_i)
        add a,a
        add a,6
        ld b,a
        ret
k_name:                         ; HL = the name of key k_i
        ld a,(k_i)
        ld hl,TD + k_names_src - td_src
        jp str_skip
k_rattr:                        ; key k_i's row in colour A
        push af
        call k_rowb
        ld c,9
        ld de,0x010E
        pop af
        jp set_attrs
k_cap:                          ; key k_i's cap: its letter, or SP
        call k_rowb
        ld c,21
        push bc
        ld hl,TD + key_ch_src - td_src
        ld a,(k_i)
        ld e,a
        ld d,0
        add hl,de
        ld a,(hl)
        ld hl,TD + k_sp_src - td_src
        ld e,2
        cp ' '
        jr z,kc_1
        ld hl,k_tmp
        ld (hl),a
        dec e
kc_1:
        ld d,1
        push hl
        ld a,T_KEY
        call set_attrs
        pop hl
        pop bc
        jp print_at
; the title's own layout and messages (here, under 0x8000: the tables at TD are full)
t_script:                       ; layout B, the menu card (Grant, 15 Nov 2026: "I like title screen B")
        db 0x83,3,18,26,T_CARD  ; the card: rows 3-20, columns 3-28
        db 0x83,3,5,26,0x60     ; its head GREEN, bright, rows 3-7 (Grant, 15 Nov 2026: "share a colour between character
                                ; blocks, but switch a colour to create its outside ... make the breakfast run area green";
                                ; "the run should not touch the bottom white area, it should be surround by green")
        db 0x85,11,1,13,0x66    ; RUN: yellow above its cut ...
        db 0x86,11,1,13,0x62    ; ... red below ("s4 is perfect")
        db 0x83,5,4,4,0x67      ; the egg: white on the green ...
        db 0x84,6,2,2,0x7E      ; ... its yolk yellow on white, in the middle four cells, in the middle four cells (so it is 15 pixels of yellow, not a 6-pixel hole)
        db 0x88,10,1,12,0x7A
        db 8,10,"TODAY'S MENU",0
        db 9,6,"--------------------",0
        if OPT_CHOOSE           ; CHOOSE: three choices; 1 or 2 goes on to the choose screen (Grant, 16 Nov 2026: "you can remove
        db 10,6,"1  ONE PLAYER",0   ; option 3 from the title screen")
        db 11,6,"2  TWO PLAYERS",0
        db 12,6,"K  CHOOSE KEYS",0
        db 13,6,"--------------------",0
        else
        db 10,6,"1  ONE PLAYER",0   ; the four choices on four rows (Grant, 15 Nov 2026: "condense the menu, add a menu
        db 11,6,"2  TWO PLAYERS",0  ; option 'choose your player' ... we will build that later but you can show the
        if OPT_RACE             ; RACE or COMBAT (Grant, 18 Nov 2026: "I need a game option - combat or race"): M changes
        if OPT_RACEONLY = 0     ; (RACEONLY, 22 Nov 2026: the race only - nothing on this row)
        db 12,6,"M  MODE:",0    ; it - t_mode writes which after it (the row "3 CHOOSE YOUR PLAYER", which did nothing, is gone)
        endif
        else
        db 12,6,"3  CHOOSE YOUR PLAYER",0   ; menu option for now": 3 does nothing yet)
        endif
        db 13,6,"K  CHOOSE KEYS",0
        db 15,6,"--------------------",0
        endif
        db 0x94,6,1,20,0x79
        db 0xFF
t_lrec: db "LAP RECORD",0
        if OPT_RACE
rmode:  db 1                    ; THE GAME: 1 RACE, 0 COMBAT (the title's M; kept from race to race - race.asm)
t_mode:                         ; the title's row 12: which game
        ld hl,t_race
        ld a,(rmode)
        or a
        jr nz,tmo_1
        ld hl,t_combat
tmo_1:  ld bc,0x0C0F
        jp print_at
t_race: db "RACE  ",0
t_combat: db "COMBAT",0
        endif
        if 1-OPT_CHOOSE
        if OPT_2P = 0
t_press: db "                    ",0
        endif
        if OPT_2P = 0
t_soon: db "  2UP COMING SOON   ",0
        endif
        endif
; the title's egg (logo C of docs/design/logo_options.png), 16 x 16, drawn twice the size: the white, and in its
; middle 8 x 8 (the four cells with colours of their own) the yolk - small and round (Grant, 15 Nov 2026):
; 12 pixels across on the screen, white all round it
t_egg:
        defb %00000000,%00000000
        defb %00000000,%00110000
        defb %00001111,%11111100
        defb %00011111,%11111110
        defb %00110000,%00001110
        defb %01110001,%10001111
        defb %01110011,%11001111
        defb %11110111,%11101111
        defb %11110111,%11101111
        defb %11110011,%11001110
        defb %11110001,%10001110
        defb %01110000,%00001100
        defb %01111111,%11111000
        defb %00111111,%11110000
        defb %00011111,%00000000
        defb %00000000,%00000000
