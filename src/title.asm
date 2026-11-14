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
t_drv   equ TS+13               ; the driver on the stage, 0..4
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
        ld hl,BUF+25            ; the logo is in the kept picture: 32 bytes a line
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
        ld hl,TD + t_script_src - td_src
        call ds_run
t_logo: ld de,0                 ; the logo twice the size: 14 x 4 cells from column 1
t_lsk:  ld a,0
        ld (db_skip+1),a
        ld bc,0x0008
        ld a,7
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
        ld bc,0x0112
        ld a,T_TABLE
        call print_big
        call st_frame
        xor a
        ld (t_msg),a
        call a_new
t_loop:
        halt
        call a_show             ; the car, straight after the interrupt
        call a_step
        halt
        ld hl,t_msg             ; the 2UP message: the choice again after 1.5 s
        ld a,(hl)
        or a
        jr z,t_keys
        dec (hl)
        ld hl,TD + t_press_src - td_src
        call z,t_prompt
t_keys:
        call k_scan
        jr z,t_loop
        ld a,l
        cp 15                   ; 1: play
        jp z,k_up
        cp 16                   ; 2: not yet
        jr nz,t_k
        ld a,40
        ld (t_msg),a
        ld hl,TD + t_soon_src - td_src
        call t_prompt
        jr t_loop
t_k:
        cp 32                   ; K: the keys
        jr nz,t_loop
        call keys_screen
        jr t_redraw
t_prompt:
        ld bc,0x1705
        jp print_at

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

; ST_FRAME: the stage's slim frame, as the play window's: a 2-pixel line with
; rounded corners, 3 pixels of table inside it (lines 35-36 and 139-140, x 11-12
; and 131-132, round the cloth at x 16-127, lines 40-135)
st_frame:
        ld b,35
        ld de,0x07E0
        call st_h
        ld de,0x0FF0
        call st_h
st_v:
        ld c,8
        call scr_addr
        ld (hl),0x18
        ld a,l
        add a,15
        ld l,a
        ld (hl),0x18
        inc b
        ld a,b
        cp 139
        jr nz,st_v
        ld de,0x0FF0
        call st_h
        ld de,0x07E0
st_h:                           ; line B: D, 14 bytes solid, E; then B + 1
        ld c,8
        call scr_addr
        ld (hl),d
        ld a,14
st_h1:
        inc l
        ld (hl),0xFF
        dec a
        jr nz,st_h1
        inc l
        ld (hl),e
        inc b
        ret

; CL_FILL: the cloth, clean: 32-pixel checks, the dark ones dotted (as the race's)
tcl_fill:
        ld b,0                  ; B = the cloth's line, 0..95
tcl_row:
        push bc
        ld a,b
        add a,40
        ld b,a
        ld c,16
        call scr_addr
        pop bc
        ld a,b                  ; D = a dark check's byte on this line
        and 3
        ld d,0x22
        jr z,tcl_p
        cp 2
        ld d,0x88
        jr z,tcl_p
        ld d,0
tcl_p:
        ld c,0                  ; C = the byte, 0..13
tcl_col:
        ld a,b                  ; dark if (line / 32 + byte / 4) is odd
        rlca
        rlca
        rlca
        ld e,a
        ld a,c
        rrca
        rrca
        add a,e
        rrca
        ld a,d
        jr c,tcl_d
        xor a
tcl_d:
        ld (hl),a
        inc l
        inc c
        ld a,c
        cp 14
        jr nz,tcl_col
        inc b
        ld a,b
        cp 96
        jr nz,tcl_row
        ret

; A_NEW: the driver t_drv comes on: a clean cloth, the card (number, face on the
; car's colour, name, two lines about them), and the run from its start
a_new:
        call tcl_fill
        ld a,(t_drv)
        add a,'1'
        ld hl,t_tmp
        ld (hl),a
        inc hl
        ld (hl),0
        dec hl
        ld bc,0x0519
        call print_at
        ld a,(t_drv)
        ld e,a
        ld d,0
        ld hl,car_colours_src
        add hl,de
        ld a,(hl)
        ld bc,0x0612
        ld de,0x0404
        call set_attrs
        ld a,(t_drv)
        rrca
        rrca
        rrca
        ld e,a
        ld d,0
        ld hl,faces_src
        add hl,de
        ex de,hl
        xor a
        ld (db_skip+1),a
        ld bc,0x3090
        ld a,2
        call dbl
        ld a,(t_drv)            ; the car, facing right, twice the size: the race order's
        ld h,a                  ; picture of it (tower_cars: 16 rows of mask, ink, mask,
        ld l,0                  ; ink, 64 bytes a car) - its ink put together first
        srl h
        rr l
        srl h
        rr l
        ld de,tower_cars+1
        add hl,de
        ld de,a_sav
        ld b,32
an_car:
        ld a,(hl)
        ld (de),a
        inc de
        inc hl
        inc hl
        djnz an_car
        ld de,a_sav
        ld bc,0x68B0            ; (line 104, x 176: rows 13-16, columns 22-25)
        ld a,2
        call dbl
        ld bc,0x0717
        ld de,0x0208
        call clear_cells
        ld bc,0x0A12
        ld de,0x020D
        call clear_cells
        ld a,(t_drv)
        add a,a
        add a,a
        ld hl,TD + t_cast_src - td_src
        call str_skip
        ld bc,0x0717
        call print_at
        inc hl
        ld bc,0x0817
        call print_at
        inc hl
        ld bc,0x0A12
        call print_at
        inc hl
        ld bc,0x0B12
        call print_at
        ld a,(t_drv)            ; the run: 12 bytes a driver
        add a,a
        add a,a
        ld e,a
        add a,a
        add a,e
        ld e,a
        ld d,0
        ld hl,TD + a_runs_src - td_src
        add hl,de
        ld de,a_x+1
        ldi
        inc de
        ldi
        ldi
        ld (a_scr),hl
        xor a
        ld (a_n),a
        ld (a_dr),a
        ld (a_on),a
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
        ld a,(k_go+1)           ; the accelerate key also ends the wait after a race (hud_over)
        ld (ho_key+1),a
        ld a,(k_go+5)
        ld (ho_key+5),a
        ld a,(TD + key_ch_src - td_src + 2)         ; the race screen's PRESS Q names the new key
        ld (txt_strip+7),a
        ld (TOPMEM + txt_pressq_src - high_src + 6),a
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

; A_MARKS: while it drifts, its skid marks - two dots a step, 4 pixels either side
; of its middle across the way the nose points. (Here, not with the car's drawing
; in title2.asm: the program has less room, and this is quick.) Put down before the car is drawn
; (so they are kept with what is under it), and left behind as it moves on.
a_marks:
        ld a,(a_dr)
        add a,16
        cp 33
        ret c                   ; (the nose within 22 degrees of the way it goes: gripping)
        ld a,(a_h)
        add a,a
        add a,a
        call heading_push       ; E = 64 sin, C = -64 cos of the nose's heading
        ld a,c
        call am_q
        neg
        ld d,a                  ; D, E = 4 pixels across the car
        ld a,e
        call am_q
        ld e,a
        ld a,(a_x+1)            ; H, L = its middle on the cloth
        sub 24
        ld h,a
        ld a,(a_y+1)
        sub 18
        ld l,a
        push hl
        push de
        ld a,h
        add a,d
        ld d,a
        ld a,l
        add a,e
        ld e,a
        call am_plot
        pop de
        pop hl
        ld a,h
        sub d
        ld d,a
        ld a,l
        sub e
        ld e,a
am_plot:                        ; a dot at D, E on the cloth (112 x 96), if it is on it
        ld a,d
        cp 112
        ret nc
        ld a,e
        cp 96
        ret nc
        add a,40
        ld b,a
        ld a,d
        add a,16
        ld c,a
        call scr_addr
        ld a,c
        and 7
        inc a
        ld b,a
        xor a
        scf
am_1:
        rra
        djnz am_1
        or (hl)
        ld (hl),a
        ret
am_q:                           ; A / 16, signed
        sra a
        sra a
        sra a
        sra a
        ret
