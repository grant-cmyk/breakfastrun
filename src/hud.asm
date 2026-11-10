; =====================================================================
; HUD - everything round the play window (the layout agreed on the
; Claude Design canvas "Breakfast Run Screen Design"):
;
;   cols 0-23, rows 0-2   MESSAGE BAR: start lights, GO!, FINAL LAP!,
;                         FINISHED nTH - double-size ROM letters
;   cols 1-23, rows 4-19  the play window (racer.asm), framed
;   cols 0-23, rows 21-22 LAP and TIME, BEST lap (time, car, lap)
;   cols 25-31            PANEL: logo, race order, mini-map
;
; None of it scrolls, so it can use any colours. Each part is redrawn
; only when what it shows has changed - never every frame.
; =====================================================================

A_YEL   equ 0x30                ; black ink on yellow paper (the table)
A_MSG   equ 0x57                ; bright white on red
A_GO    equ 0x67                ; bright white on green
A_LAMP  equ 0x42                ; bright red on black: a start light
A_LAP   equ 0x4F                ; bright white on blue
TOWER_Y equ 5                   ; first row of the race order (RACE above it)
A_YOU   equ 0x72                ; bright red on yellow: your marker's cell

; ---------------------------------------------------------------------
; HUD_INIT: the whole surround, once at the start of a race
; ---------------------------------------------------------------------
hud_init:
        call draw_frame
        ld b,1                  ; logo, 7 x 2 cells at the top of the panel
        ld c,25
        call draw_logo
        ld hl,txt_track         ; the track's name, along the top
        ld b,0
        ld c,1
        call print_at
        ld hl,txt_race
        ld b,TOWER_Y-1
        ld c,25
        call print_at
        ld b,TOWER_Y-1          ; RACE: white on blue across the panel
        ld c,25
        ld d,1
        ld e,7
        ld a,A_LAP
        call set_attrs
        call map_init
        ld b,0                  ; the tower in grid order, all at once
hi_tw:
        push bc
        ld e,b
        ld d,0
        ld hl,grid_order        ; the car in this place on the grid
        add hl,de
        ld c,(hl)
        ld hl,order
        add hl,de
        ld (hl),c
        ld de,shown_order-order
        add hl,de
        ld (hl),c
        ld a,c
        call tower_row
        pop bc
        inc b
        ld a,b
        cp NCARS
        jr nz,hi_tw
        ld hl,txt_lapw          ; bottom band, row BAND_Y: LAP n/3 and TIME
        ld b,BAND_Y
        ld c,1
        call print_at
        ld hl,txt_time
        ld b,BAND_Y
        ld c,12
        call print_at
        ld hl,txt_best          ; row BAND_Y+1: BEST -:--.-
        ld b,BAND_Y+1
        ld c,1
        call print_at
        ld hl,txt_nobest
        ld b,BAND_Y+1
        ld c,6
        call print_at
        jp msg_lights

; draw_logo: the 56 x 24 logo at cell row B, column C, with its colours
draw_logo:
        ld a,b
        add a,a
        add a,a
        add a,a
        ld b,a                  ; B = pixel row
        ld a,c
        add a,a
        add a,a
        add a,a
        ld c,a                  ; C = pixel x
        ld de,logo_bits
        ld a,16
dl_row:
        push af
        push bc
        call scr_addr
        ld b,7
dl_byte:
        ld a,(de)
        ld (hl),a
        inc de
        inc l
        djnz dl_byte
        pop bc
        inc b
        pop af
        dec a
        jr nz,dl_row
        ld hl,logo_attr         ; 2 rows of 7 attributes
        ld de,0x5800+1*32+25
        ld b,2
dl_attr:
        push bc
        ld bc,7
        ldir
        ex de,hl
        ld bc,32-7
        add hl,bc
        ex de,hl
        pop bc
        djnz dl_attr
        ret

; ---------------------------------------------------------------------
; set_attrs: A = attribute for D rows x E columns from cell (B, C)
; clear_cells: the same rectangle's pixels to paper
; ---------------------------------------------------------------------
set_attrs:
        push af
        call attr_addr
        pop af
sa_row:
        push hl
        ld b,e
sa_col:
        ld (hl),a
        inc hl
        djnz sa_col
        pop hl
        push de
        ld de,32
        add hl,de
        pop de
        dec d
        jr nz,sa_row
        ret

attr_addr:                      ; HL = 0x5800 + B*32 + C
        ld l,b
        ld h,0
        add hl,hl
        add hl,hl
        add hl,hl
        add hl,hl
        add hl,hl
        push de
        ld e,c
        ld d,0x58
        add hl,de
        pop de
        ret

clear_cells:
        ld a,b                  ; pixel row of the top
        add a,a
        add a,a
        add a,a
        ld b,a
        ld a,c
        add a,a
        add a,a
        add a,a
        ld c,a
        ld a,d                  ; rows * 8 pixel rows
        add a,a
        add a,a
        add a,a
cc_row:
        push af
        push bc
        call scr_addr
        ld b,e
cc_col:
        ld (hl),0
        inc l
        djnz cc_col
        pop bc
        inc b
        pop af
        dec a
        jr nz,cc_row
        ret

; ---------------------------------------------------------------------
; print_big: the 0-terminated text at HL in double-size ROM letters
; (16 x 16, 2 x 2 cells each) at cell row B, column C, cells coloured A
; ---------------------------------------------------------------------
print_big:
        ld (pb_attr),a
pb_char:
        ld a,(hl)
        or a
        ret z
        push hl
        push bc
        ld l,a                  ; DE = the letter in the ROM font
        ld h,0
        add hl,hl
        add hl,hl
        add hl,hl
        ld de,0x3C00
        add hl,de
        ex de,hl
        ld a,b                  ; pixel row and x of the top-left
        add a,a
        add a,a
        add a,a
        ld b,a
        ld a,c
        add a,a
        add a,a
        add a,a
        ld c,a
        ld a,8
pb_line:
        push af
        ld a,(de)               ; double each bit: 8 bits -> 16
        inc de
        push de
        ld e,a
        ld hl,0
        ld d,8
pb_bit:
        add hl,hl
        add hl,hl
        rl e
        jr nc,pb_b0
        inc l
        inc l
        inc l
pb_b0:
        dec d
        jr nz,pb_bit
        ex de,hl                ; DE = the doubled row
        call scr_addr           ; two pixel rows of it
        ld (hl),d
        inc l
        ld (hl),e
        inc b
        call scr_addr
        ld (hl),d
        inc l
        ld (hl),e
        inc b
        pop de
        pop af
        dec a
        jr nz,pb_line
        pop bc
        push bc                 ; colour the 2 x 2 cells
        ld d,2
        ld e,2
        ld a,(pb_attr)
        call set_attrs
        pop bc
        pop hl
        inc hl
        inc c
        inc c
        jr pb_char

; ---------------------------------------------------------------------
; THE MESSAGE BAR
; ---------------------------------------------------------------------
msg_clear:                      ; the message bar: rows 1-2 (row 0 is the
        ld b,1                  ; track's name)
        ld c,0
        ld d,2
        ld e,24
        call clear_cells
        ld b,1
        ld c,0
        ld d,2
        ld e,24
        ld a,A_YEL
        jp set_attrs

msg_lights:                     ; three red lights, GET READY, PRESS Q
        call msg_clear
        ld b,1
        ld c,2
        call ml_lamp
        ld b,1
        ld c,5
        call ml_lamp
        ld b,1
        ld c,8
        call ml_lamp
        ld hl,txt_ready
        ld b,1
        ld c,12
        call print_at
        ld hl,txt_pressq
        ld b,2
        ld c,12
        jp print_at
ml_lamp:
        ld hl,txt_lamp
        ld a,A_LAMP
        jp print_big

msg_go:
        call msg_clear
        ld hl,txt_go
        ld b,1
        ld c,9
        ld a,A_GO
        call print_big
        ld a,75                 ; 1.5 s
        ld (msg_timer),a
        ret

msg_final:
        call msg_clear
        ld hl,txt_final
        ld b,1
        ld c,2
        ld a,A_MSG
        call print_big
        ld a,150                ; 3 s
        ld (msg_timer),a
        ret

msg_finished:                   ; FINISHED nTH, which stays
        call msg_clear
        ld hl,txt_finished
        ld b,1
        ld c,0
        ld a,A_MSG
        call print_big
        ld a,(position)         ; "1ST" .. "5TH" after it
        dec a
        add a,a
        add a,a
        ld e,a
        ld d,0
        ld hl,txt_places
        add hl,de
        ld b,1
        ld c,18
        ld a,A_MSG
        call print_big
        xor a
        ld (msg_timer),a
        ret

; ---------------------------------------------------------------------
; THE GAPS TO THE LEADER (Grant, 10 Nov 2026). Every 4th waypoint of the first
; 32 is a checkpoint: 8 a lap. The first car to reach a checkpoint on a lap
; notes the time; each car after it gets its gap from that. Shown in the race
; order in a small font; the faces are only for the grid.
; Kept in the buffer's bottom rows (BUFC): nothing in low memory.
; ---------------------------------------------------------------------
CP_G    equ BUFC                ; each checkpoint: lap * 8 + n last noted
CP_T    equ BUFC+8              ; and when (2 bytes each)
GAPS    equ BUFC+24             ; each car's gap, frames (2 bytes each)
SHGAP   equ BUFC+34             ; each place's gap as shown (2 bytes each)
ST_ACC  equ BUFC+44             ; small text: the row being built (2)
ST_X    equ BUFC+46             ;   where the next character goes
ST_T    equ BUFC+47             ;   the text (2)
ST_COL  equ BUFC+49             ;   its byte column
ST_X0   equ BUFC+50             ;   where the first character goes (pixels)
gaps_reset:                     ; a new race: nothing noted, nothing shown
        ld hl,CP_G
        ld b,8
grs_1:
        ld (hl),0xF0            ; (older than any lap * 8 + n)
        inc hl
        djnz grs_1
        ld hl,GAPS
        ld b,20
grs_2:
        ld (hl),0
        inc hl
        djnz grs_2
        ret
cp_hook:                        ; IX = a car reaching its waypoint
        ld a,(race_on)
        or a
        ret z
        ld a,(ix+C_WP)
        ld c,a
        and 3
        ret nz
        ld a,c
        cp 32
        ret nc
        push bc
        push de
        push hl
        rrca
        rrca
        and 7
        ld c,a                  ; C = checkpoint 0..7
        ld a,(ix+C_LAPS)
        add a,a
        add a,a
        add a,a
        add a,c
        ld b,a                  ; B = lap * 8 + checkpoint
        ld e,c
        ld d,0
        ld hl,CP_G
        add hl,de
        sub (hl)
        jr z,cph_gap            ; someone was here first, this lap
        jp m,cph_done           ; an older lap than noted: a lapped car
        ld (hl),b               ; the first here: note the time
        ld hl,CP_T
        add hl,de
        add hl,de
        ld de,(race_time)
        ld (hl),e
        inc hl
        ld (hl),d
        ld de,0
        jr cph_store
cph_gap:
        ld hl,CP_T
        add hl,de
        add hl,de
        ld e,(hl)
        inc hl
        ld d,(hl)
        ld hl,(race_time)
        or a
        sbc hl,de
        ex de,hl
cph_store:
        ld a,(ix+C_KIND)
        add a,a
        ld l,a
        ld h,0
        ld bc,GAPS
        add hl,bc
        ld (hl),e
        inc hl
        ld (hl),d
cph_done:
        pop hl
        pop de
        pop bc
        ret
hu_go:                          ; GO: the race order redraws without the faces
        ld a,1
        ld (pace_skip),a        ; (a busy picture: it does not set the pace)
        ld hl,shown_order
        ld b,NCARS
hg_1:
        ld (hl),0xFF
        inc hl
        djnz hg_1
        jp msg_go
gap_update:                     ; one place a time: its gap, if it changed
        ld a,(race_on)
        or a
        ret z
        ld a,(renders)          ; place = (renders / 4) MOD 5
        rrca
        rrca
        and 63
gu_1:
        sub NCARS
        jr nc,gu_1
        add a,NCARS
        jp gap_draw             ; (it sits in racer.asm, in the gap before sq4's page)
best_panel:                     ; under the racers: a clock and the best lap
        ld b,TOWER_Y+2*NCARS
        ld c,25
        ld de,CLOCK8
        call tr_glyph
        ld hl,(best_lap)
        call time_fmt
        ld hl,time_txt+2
        ld b,(TOWER_Y+2*NCARS)*8+1
        ld c,26
        ld a,2                  ; 2 px clear of the clock (Grant: it read "d2.8")
        jr st_text_x
; ST_TEXT: HL = text (digits, '.', ' '), B = top pixel row, C = byte column:
; the text in the small font (3 x 5, 4 px a digit), 5 rows x 2 bytes, written
; over what was there - so more numbers fit (Grant, 10 Nov 2026)
st_text:                        ; (st_text_x: A = pixels in from the left)
        xor a
st_text_x:
        ld (ST_X0),a
        ld (ST_T),hl
        ld a,c
        ld (ST_COL),a
        ld c,0                  ; C = the font row, 0..4
st_r:
        push bc
        ld hl,0
        ld (ST_ACC),hl
        ld a,(ST_X0)
        ld (ST_X),a
        ld hl,(ST_T)
st_ch:
        ld a,(hl)
        or a
        jr z,st_put
        inc hl
        push hl
        ld e,4                  ; a digit: 3 px and a gap
        cp '.'
        jr z,st_dot
        cp '0'
        jr c,st_sp              ; a space (anything else): blank
        sub '0'
        ld l,a                  ; its row: sfont + digit * 5 + row
        add a,a
        add a,a
        add a,l
        add a,c
        ld l,a
        ld h,0
        push de
        ld de,sfont
        add hl,de
        pop de
        ld a,(hl)
        jr st_place
st_dot:
        ld e,2                  ; a point: 1 px and a gap, on the bottom row
        ld a,c
        cp 4
        ld a,0x80
        jr z,st_place
st_sp:
        xor a
st_place:                       ; row |= glyph bits >> x (16 bits), through the
        push de                 ; shift tables (page TAB_HI+2s: b >> (8-s), and
        ld e,a                  ; the next page b << s)
        ld d,0
        ld a,(ST_X)
        sub 8
        jr nc,st_low            ; x 8..15: the right byte only
        add a,8
        jr z,st_x0              ; x 0: as it is
        neg
        add a,8                 ; s = 8 - x
        add a,a
        add a,TAB_HI
        ld h,a
        ld l,e
        ld d,(hl)               ; left: g >> x
        inc h
        ld e,(hl)               ; right: g << (8 - x)
        jr st_p2
st_x0:
        ld d,e
        ld e,0
        jr st_p2
st_low:
        jr z,st_p2              ; x 8: the right byte is g
        neg
        add a,8
        add a,a
        add a,TAB_HI
        ld h,a
        ld l,e
        ld e,(hl)               ; right: g >> (x - 8)
st_p2:
        ld hl,(ST_ACC)
        ld a,h
        or d
        ld h,a
        ld a,l
        or e
        ld l,a
        ld (ST_ACC),hl
        pop de
        ld a,(ST_X)
        add a,e
        ld (ST_X),a
        pop hl
        jr st_ch
st_put:
        pop bc
        push bc
        ld a,b
        add a,c
        ld b,a
        ld a,(ST_COL)
        add a,a
        add a,a
        add a,a
        ld c,a
        call scr_addr
        ld de,(ST_ACC)
        ld (hl),d
        inc l
        ld (hl),e
        pop bc
        inc c
        ld a,c
        cp 5
        jp nz,st_r
        ret

; ---------------------------------------------------------------------
; HUD_UPDATE: once per picture, after race_progress
; ---------------------------------------------------------------------
hud_update:
        ld a,(race_on)          ; the start: lights -> GO!
        ld hl,shown_on
        cp (hl)
        jr z,hu_msg
        ld (hl),a
        or a
        jp nz,hu_go             ; (GO's picture does nothing else: a busy one)
hu_msg:
        ld a,(msg_timer)        ; a message whose time is up goes
        or a
        jr z,hu_final
        ld hl,dt
        sub (hl)
        jr nc,hu_mt
        xor a
hu_mt:
        ld (msg_timer),a
        or a
        call z,msg_clear
hu_final:
        ld a,(race_over)
        or a
        jp nz,hud_over
        ld a,(cars+C_LAPS)      ; starting the last lap: FINAL LAP!
        cp LAPS
        jr nz,hu_lap
        ld hl,shown_final
        cp (hl)
        jr z,hu_lap
        ld (hl),a
        call msg_final
hu_lap:
        ld a,(cars+C_LAPS)      ; the lap shown: 1..LAPS
        or a
        jr nz,hu_l1
        inc a
hu_l1:
        cp LAPS+1
        jr c,hu_l2
        ld a,LAPS
hu_l2:
        ld hl,shown_lap
        cp (hl)
        jr z,hu_best
        ld (hl),a
        add a,'0'
        ld (txt_digit),a
        ld hl,txt_digit
        ld b,BAND_Y
        ld c,5
        call print_at
hu_best:
        ld a,(best_seq)         ; a new best lap (by anyone)
        ld hl,shown_best_seq
        cp (hl)
        jr z,hu_order
        ld (hl),a
        call print_best
        call best_panel
hu_order:
        ld a,(renders)          ; spread the HUD out: the order on one
        and 3                   ; picture in four, the map on another, the
        jp z,tower_update       ; clock on the other two
        cp 2
        jp z,map_update
        jp time_update

; print_best: BEST m:ss.t NAME LAP n on row BAND_Y+1 (the name on the car's colour)
print_best:                     ; BEST 14.2 GREEN LAP 2 (cols 1..21)
        ld hl,(best_lap)
        call time_fmt
        ld hl,time_txt+2        ; seconds and tenths: a lap is under a minute
        ld b,BAND_Y+1
        ld c,6
        call print_at
        ld a,(best_car)         ; the name, 5 letters
        ld l,a
        add a,a
        add a,a
        add a,a
        sub l
        sub l                   ; car * 6
        ld e,a
        ld d,0
        ld hl,car_names
        add hl,de
        ld b,BAND_Y+1
        ld c,11
        call print_at
        ld a,(best_car)
        ld e,a
        ld d,0
        ld hl,car_colours
        add hl,de
        ld a,(hl)
        ld b,BAND_Y+1
        ld c,11
        ld d,1
        ld e,5
        call set_attrs
        ld hl,txt_lapword
        ld b,BAND_Y+1
        ld c,17
        call print_at
        ld a,(best_lapno)
        add a,'0'
        ld (txt_digit),a
        ld hl,txt_digit
        ld b,BAND_Y+1
        ld c,21
        jp print_at

hud_over:                       ; after the finish: the last flags, then
        call tower_update       ; wait for Q to be let go,
        ld a,0xFB               ; then pressed again - a new race
        in a,(0xFE)
        and 1
        ld hl,q_up
        jr z,ho_down
        ld (hl),1
        ret
ho_down:
        ld a,(hl)
        or a
        ret z
        pop hl                  ; leave the main loop: back to the start
        jp new_race

; ---------------------------------------------------------------------
; THE RACE ORDER (the tower): rows TOWER_Y.. of the panel, 2 rows a place:
; the place (25), the car (26-27), a gap, its driver's face (29-30), and a
; flag when it is in (31)
; ---------------------------------------------------------------------
tower_update:                   ; redraw the first place whose car changed
        ld b,0                  ; (one a picture at most: no spikes)
        ld hl,order
tu_place:
        ld a,(hl)
        call fin_key            ; + 8 if that car has finished (its flag)
        push hl
        ld de,shown_order-order
        add hl,de
        cp (hl)
        jr z,tu_same
        ld (hl),a
        pop hl
        jp tower_row            ; B = place, A = car
tu_same:
        pop hl
        inc hl
        inc b
        ld a,b
        cp NCARS
        jr nz,tu_place
        jp gap_update           ; nothing moved: bring one place's gap up to date

cell_addr:                      ; cell row B, column C -> HL = its top pixel row
        ld a,b
        and 0x18
        or 0x40
        ld h,a
        ld a,b
        and 7
        rrca
        rrca
        rrca
        or c
        ld l,a
        ret

fin_key:                        ; A = car -> A = car, + 8 if it is in, + 16 if
        push hl                 ; it has the best lap, + 32 * (its lap AND 3)
        push bc
        ld e,a                  ; E = the car
        add a,a                 ; its record: cars + car * 28
        add a,a
        add a,a
        sub e
        add a,a
        add a,a
        ld c,a
        ld b,0
        ld hl,cars+C_LAPS
        add hl,bc
        ld a,(hl)
        and 3
        rrca
        rrca
        rrca
        or e
        ld c,a                  ; C = car + lap * 32
        ld d,0
        ld hl,fin_at
        add hl,de
        ld a,(hl)
        or a
        ld a,c
        jr z,fk_1
        or 8
fk_1:
        ld c,a
        ld hl,(best_lap)        ; (0xFFFF: no best lap yet)
        inc hl
        ld a,h
        or l
        ld a,c
        jr z,fk_2
        ld a,(best_car)
        cp e
        ld a,c
        jr nz,fk_2
        or 16
fk_2:
        pop bc
        pop hl
        ret

tower_row:                      ; place B (0..4), A = car (+ 8: finished)
        ld (tr_key),a
        and 7
        ld (tr_car),a
        ld a,b
        add a,a
        add a,TOWER_Y
        ld (tr_row),a           ; its first cell row
        ld b,a                  ; clear 2 cell rows x 7 bytes, INC H per pixel row
        ld c,25
        call tr_clear
        ld a,(tr_row)
        inc a
        ld b,a
        ld c,25
        call tr_clear
        ld a,(tr_car)           ; colours: you white on red, the others black
        ld e,a                  ; on their own colour
        ld d,0
        ld hl,car_colours
        add hl,de
        ld a,(tr_row)
        ld b,a
        ld c,25
        ld a,(hl)
        ld d,2
        ld e,7
        call set_attrs
        ld a,(tr_row)           ; the place number
        sub TOWER_Y
        srl a
        add a,'1'
        ld (txt_digit),a
        ld hl,txt_digit
        ld a,(tr_row)
        ld b,a
        ld c,25
        call print_at
        ld a,(tr_car)           ; the car's own picture, facing right:
        add a,a                 ; car_data + car * 1024 + heading 4 * 64
        add a,a
        ld h,a
        ld l,0
        ld de,car_data+4*64
        add hl,de
        ex de,hl
        ld a,(tr_row)
        ld b,a
        ld c,26
        call tr_pic
        ld a,(tr_row)
        inc a
        ld b,a
        ld c,26
        call tr_pic
        ld a,(race_on)          ; racing: the gap to the leader, not the face
        or a
        jp nz,tr_race
        ld a,(tr_car)           ; the driver's face, beside the car:
        add a,a                 ; faces + car * 32
        add a,a
        add a,a
        add a,a
        add a,a
        ld e,a
        ld d,0
        ld hl,faces
        add hl,de
        ex de,hl
        ld a,(tr_row)
        ld b,a
        call tr_face
        ld a,(tr_row)
        inc a
        ld b,a
        jp tr_face
tr_race:                        ; the gap (columns 28-29), its lap or, once it is
                                ; in, a flag (30),
        ld a,1                  ; a clock if it has the best lap (31)
        ld (tr_force),a
        ld a,(tr_row)
        sub TOWER_Y
        srl a
        call gap_draw           ; A = place
        ld a,(tr_key)
        bit 3,a
        jr z,trr_lap
        ld c,30
        ld de,flag_top
        call tr_glyph16
        jr trr_1
trr_lap:                        ; still racing: the lap it is on, where its flag
        rlca                    ; will go (Grant, 10 Nov 2026)
        rlca
        rlca
        and 3
        add a,'0'
        ld (txt_digit),a
        ld hl,txt_digit
        ld a,(gd_y)
        ld b,a
        ld c,30
        ld a,2                  ; 2 px in: clear of the gap and the clock
        call st_text_x
trr_1:
        ld a,(tr_key)
        bit 4,a
        ret z
        ld c,31
        ld de,clock_top
tr_glyph16:                     ; 16 rows at DE into cells tr_row and below, column C
        ld a,(tr_row)
        ld b,a
        push bc
        call tr_glyph
        pop bc
        inc b
        jr tr_glyph
tr_face:                        ; 8 rows x 2 bytes at DE into cells B, 29-30
        ld c,29                 ; (column 28 left clear: a gap after the car)
        call cell_addr
        ld b,8
tf_row:
        ld a,(de)
        ld (hl),a
        inc de
        inc l
        ld a,(de)
        ld (hl),a
        inc de
        dec l
        inc h
        djnz tf_row
        ret
tr_glyph:                       ; 8 bytes at DE into cell B, C
        call cell_addr
        ld b,8
tg_row:
        ld a,(de)
        ld (hl),a
        inc de
        inc h
        djnz tg_row
        ret
tr_pic:                         ; 8 rows of the picture (ink only) into cell B, C
        call cell_addr
        ld b,8
tp_row:
        inc de                  ; skip the mask; ink left
        ld a,(de)
        ld (hl),a
        inc de
        inc de                  ; skip the mask; ink right
        inc l
        ld a,(de)
        ld (hl),a
        inc de
        dec l
        inc h
        djnz tp_row
        ret
tr_clear:                       ; 8 pixel rows x 7 bytes at cell B, C
        call cell_addr
        ld b,8
        xor a
tc_row:
        ld (hl),a
        inc l
        ld (hl),a
        inc l
        ld (hl),a
        inc l
        ld (hl),a
        inc l
        ld (hl),a
        inc l
        ld (hl),a
        inc l
        ld (hl),a
        ld e,a
        ld a,l
        sub 6
        ld l,a
        ld a,e
        inc h
        djnz tc_row
        ret

; ---------------------------------------------------------------------
; THE MINI-MAP: the track at 1/8 scale in the panel (rows 17-22), a dot per
; car: 2 x 2 for the computer cars, 3 x 3 and blinking for you. Each update
; puts back the map under the old dots, then draws the new ones.
; ---------------------------------------------------------------------
MAP_X   equ 25*8                ; screen pixel of the map's top-left
MAP_Y   equ 17*8
map_init:
        ld de,minimap
        ld b,MAP_Y
mi_row:
        ld c,MAP_X
        call scr_addr
        ld a,7
mi_b:
        ex af,af'
        ld a,(de)
        ld (hl),a
        inc de
        inc l
        ex af,af'
        dec a
        jr nz,mi_b
        inc b
        ld a,b
        cp MAP_Y+48
        jr nz,mi_row
        ld b,17
        ld c,25
        ld d,6
        ld e,7
        ld a,0x30               ; black on yellow, like the background (Grant: no white box)
        call set_attrs
        ld hl,shown_dot         ; no dots drawn yet
        ld b,2*NCARS
mi_d:
        ld (hl),0xFF
        inc hl
        djnz mi_d
        ret

map_update:
        ld hl,blink             ; your dot blinks: on 2 updates, off 2
        inc (hl)
        ld c,0                  ; 1. put back the map under every old dot
mu_old:
        ld a,c
        add a,a
        ld hl,shown_dot
        add a,l
        ld l,a
        jr nc,mu_o1
        inc h
mu_o1:
        ld a,(hl)
        cp 0xFF
        jr z,mu_onext
        ld e,a                  ; E = x, D = y
        inc hl
        ld d,(hl)
        push bc
        call map_restore
        pop bc
mu_onext:
        inc c
        ld a,c
        cp NCARS
        jr nz,mu_old
        ld ix,cars+(NCARS-1)*C_SIZE   ; 2. the new dots, yours last
        ld c,NCARS-1
mu_new:
        push bc
        ld a,(ix+C_X)           ; map x = (x + 8 - 64) / 8, 0..53
        add a,8-64
        ld l,a
        ld a,(ix+C_X+1)
        adc a,0xFF
        ld h,a
        call map_coord
        cp 54
        jr c,mu_x
        ld a,53
mu_x:
        ld e,a
        ld a,(ix+C_Y)           ; map y = (y + 8 - 32) / 8, 0..45
        add a,8-32
        ld l,a
        ld a,(ix+C_Y+1)
        adc a,0xFF
        ld h,a
        call map_coord
        cp 46
        jr c,mu_y
        ld a,45
mu_y:
        ld d,a
        pop bc
        push bc
        ld a,c                  ; remember where
        add a,a
        ld hl,shown_dot
        add a,l
        ld l,a
        jr nc,mu_n1
        inc h
mu_n1:
        ld (hl),e
        inc hl
        ld (hl),d
        ld a,c
        or a
        ld b,0xC0               ; 2 x 2 for a computer car
        ld c,2
        jr nz,mu_draw
        ld a,(blink)            ; you: 3 x 3, shown 2 updates in 4
        and 2
        jr z,mu_skip
        ld b,0xE0
        ld c,3
mu_draw:
        call map_dot
mu_skip:
        ld de,0x10000-C_SIZE
        add ix,de
        pop bc
        dec c
        jp p,mu_new
        ret

map_coord:                      ; HL (may be negative) / 8 -> A, 0 if negative
        bit 7,h
        ld a,0
        ret nz
        srl h
        rr l
        srl h
        rr l
        srl h
        rr l
        ld a,h
        or a
        ld a,l
        ret z
        ld a,255
        ret

; map_dot: C rows of the pattern B (0xC0 or 0xE0) at map x E, y D (OR)
map_dot:
        ld a,e
        and 7
        push bc
        ld c,b                  ; the pattern in C, shifted into C:B
        ld b,0
        or a
        jr z,md_s0
md_sh:
        srl c
        rr b
        dec a
        jr nz,md_sh
md_s0:
        ld (md_pat),bc
        pop bc
md_row:
        push bc
        push de
        ld a,d
        add a,MAP_Y
        ld b,a
        ld a,e
        add a,MAP_X
        ld c,a
        call scr_addr
        ld bc,(md_pat)
        ld a,(hl)
        or c
        ld (hl),a
        ld a,e
        and 0xF8
        cp 48                   ; the map's last byte: nothing to the right
        jr nc,md_one
        inc l
        ld a,(hl)
        or b
        ld (hl),a
md_one:
        pop de
        inc d
        pop bc
        dec c
        jr nz,md_row
        ret

; map_restore: the 3 x 3 area at map x E, y D back from the map picture
map_restore:
        ld c,3
mr_row:
        push bc
        push de
        ld a,d                  ; source: minimap + y * 7 + x / 8
        cp 48
        jr nc,mr_done
        ld l,a
        ld h,0
        ld b,h
        ld c,l
        add hl,hl
        add hl,hl
        add hl,hl
        or a
        sbc hl,bc               ; y * 7
        ld a,e
        rrca
        rrca
        rrca
        and 7
        ld c,a
        ld b,0
        add hl,bc
        ld bc,minimap
        add hl,bc
        push hl
        ld a,d
        add a,MAP_Y
        ld b,a
        ld a,e
        add a,MAP_X
        ld c,a
        call scr_addr
        pop de                  ; DE = the map picture's byte
        ld a,(de)
        ld (hl),a
        pop bc                  ; (x, y back in C/B for the edge test)
        push bc
        ld a,c
        and 0xF8
        cp 48
        jr nc,mr_done
        inc l
        inc de
        ld a,(de)
        ld (hl),a
mr_done:
        pop de
        inc d
        pop bc
        dec c
        jr nz,mr_row
        ret

; ---------------------------------------------------------------------
; THE TIME: m:ss.t on row BAND_Y, only the characters that changed
; ---------------------------------------------------------------------
time_update:
        ld hl,(race_time)
        ld a,(you_done)         ; finished: your own time stays up
        or a
        jr z,tmu_1
        ld hl,(you_time)
tmu_1:
        call time_fmt
        jr tm_print
time_fmt:                       ; HL = frames (50 a second) -> time_txt "m:ss.t"
        ld de,0
        ld bc,3000              ; minutes
tm_m:
        or a
        sbc hl,bc
        jr c,tm_m1
        inc e
        jr tm_m
tm_m1:
        add hl,bc
        ld a,e
        cp 10
        jr c,tm_m2
        ld a,9
tm_m2:
        add a,'0'
        ld (time_txt),a
        ld e,0                  ; tens of seconds (500 frames)
        ld bc,500
tm_t:
        or a
        sbc hl,bc
        jr c,tm_t1
        inc e
        jr tm_t
tm_t1:
        add hl,bc
        ld a,e
        add a,'0'
        ld (time_txt+2),a
        ld e,0                  ; seconds (50)
        ld bc,50
tm_s:
        or a
        sbc hl,bc
        jr c,tm_s1
        inc e
        jr tm_s
tm_s1:
        add hl,bc
        ld a,e
        add a,'0'
        ld (time_txt+3),a
        ld a,l                  ; tenths (5 frames)
        ld e,0
tm_d:
        sub 5
        jr c,tm_d1
        inc e
        jr tm_d
tm_d1:
        ld a,e
        add a,'0'
        ld (time_txt+5),a
        ld a,(time_txt)         ; under a minute: no "0:", and no leading 0
        cp '0'                  ; ("  14.2", "   9.8")
        ret nz
        ld a,' '
        ld (time_txt),a
        ld (time_txt+1),a
        ld a,(time_txt+2)
        cp '0'
        ret nz
        ld a,' '
        ld (time_txt+2),a
        ret
tm_print:
        ld hl,time_txt          ; print what differs from what is shown
        ld de,time_shown
        ld c,17
tm_cmp:
        ld a,(hl)
        or a
        ret z
        ex de,hl
        cp (hl)
        ex de,hl
        jr z,tm_skip
        ld (de),a
        push hl
        push de
        push bc
        ld (txt_digit),a
        ld hl,txt_digit
        ld b,BAND_Y
        call print_at
        pop bc
        pop de
        pop hl
tm_skip:
        inc hl
        inc de
        inc c
        jr tm_cmp

; ---------------------------------------------------------------------
; the finish: best lap and PRESS Q under the window
; ---------------------------------------------------------------------
show_best:
        ld b,BAND_Y
        ld c,0
        ld d,1
        ld e,24
        call clear_cells
        ld hl,txt_again
        ld b,BAND_Y
        ld c,1
        jp print_at

; (the HUD's fixed text is in hudtext.asm, kept at the top of memory)
txt_digit:    db "0",0
time_txt:     db "0:00.0",0
