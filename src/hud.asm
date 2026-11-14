; =====================================================================
; HUD - everything round the play window (the layout agreed on the
; Claude Design canvas "Breakfast Run Screen Design"):
;
;   cols 0-23, rows 0-1   the track's name, then the MESSAGE BAR (one row): start
;                         lights, GO!, FINAL LAP!, FINISHED nTH; while you race
;                         and it has no message: your place, lap and the race
;                         time (bar_tick)
;   cols 1-23, rows 3-19  the play window (racer.asm), framed
;   cols 0-23, rows 21-22 LAP and TIME, BEST lap (time, car, lap)
;   cols 25-31            PANEL: logo, race order, mini-map
;
; None of it scrolls, so it can use any colours. Each part is redrawn
; only when what it shows has changed - never every frame.
; =====================================================================

A_YEL   equ 0x30                ; black ink on yellow paper (the table)
A_MSG   equ 0x57                ; bright white on red
A_GO    equ 0x67                ; bright white on green
A_LAMP  equ 0x42                ; bright red on black: a start light, lit
A_LOFF  equ 0x01                ; blue on black: a start light, not lit yet
A_LGRN  equ 0x44                ; bright green on black: all three - go
A_LAP   equ 0x4F                ; bright white on blue
TOWER_Y equ 10                  ; first row of the race order (RACE above it)
A_YOU   equ 0x72                ; bright red on yellow: your marker's cell

; ---------------------------------------------------------------------
; HUD_INIT: the whole surround, once at the start of a race
; ---------------------------------------------------------------------
hud_init:                       ; a new race: what changes (the rest: screen_once)
        ld b,TOWER_Y+2*NCARS    ; the lap record under the order: cleared,
        ld c,25                 ; then shown if there is one from an earlier race
        ld d,1
        ld e,7
        call clear_cells
        ld hl,(rec_lap)
        inc hl
        ld a,h
        or l
        call nz,best_panel
        ld hl,0x3030            ; the race time: 0:00
        ld (bar_time+2),hl
        ld a,l
        ld (bar_time),a
        call strip_reset        ; the driver strip: inventory, the radio
        ld a,M_SETUP            ; the crew chief: pick your upgrades
        call msg_say
        call su_apply           ; your car's set-up, and its row on the HUD
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
        jp msg_lights

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
; THE SCOREBOARD AND THE START LIGHTS (layout G3 - Grant, 14 Nov 2026). The play window
; has the whole height above the driver strip, so nothing is written above it any more:
;   bottom left (columns 1-9): your face and your place, large, in one red block (rows
;     20-21); a white strip under it (row 22) - PRESS Q before the start, then LAP n/3,
;     FINAL LAP for 3 s, FINISHED! at the flag; the race time under that (row 23): bar_tick;
;   in the window: three start lights hanging from a rail under its top edge (design L2):
;     empty white rings, then red, red, red, then all green; gone 1.5 s after green.
;     Their pixels are drawn into the back buffer every picture while they are up
;     (lights_draw, racer.asm); their colours are set here when they change.
; ---------------------------------------------------------------------
A_CARD  equ 0x78                ; black on bright white
LT_COL  equ 7                   ; the rail: row 1, columns 7-16; the lamps: rows 2-3,
                                ; columns 8-9, 11-12, 14-15
msg_lights:                     ; a new race: everything on the scoreboard afresh,
        ld hl,bar_shown         ; the lights up and not lit
        ld b,7
mc_1:
        ld (hl),0
        inc hl
        djnz mc_1
        ld a,1
        ld (lt_on),a
; LIGHTS_ATTR: the lights' colours for start_ph (0 none lit, 1-3 red, 4 all green)
lights_attr:
        ld bc,0x0100+LT_COL     ; the rail: black on the window's cyan
        ld de,0x010A
        ld a,0x28
        call set_attrs
        ld c,LT_COL+1
        ld l,1                  ; L = lamp 1..3
la_1:
        ld a,(start_ph)
        ld h,0x44               ; all green
        cp 4
        jr z,la_2
        ld h,0x42               ; red, if this lamp's turn has come
        cp l
        jr nc,la_2
        ld h,0x47               ; not lit: a white ring in its black box
la_2:
        push hl
        push bc
        ld a,h
        ld b,2
        ld de,0x0202
        call set_attrs
        pop bc
        pop hl
        inc c
        inc c
        inc c
        inc l
        ld a,l
        cp 4
        jr nz,la_1
        ret
lights_off:                     ; the lights go: their cells the window's colours again
        xor a
        ld (lt_on),a
        ld bc,0x0100+LT_COL
        ld de,0x030A
        ld a,0x29
        jp set_attrs

; START_LIGHTS (once a picture, before the race): Q pressed, the lights come on
; one at a time - red, red, red - then all three green, and only then does anyone
; go (Grant, 10 Nov 2026). Each light: a beep; green: a higher one.
SL_RED  equ 40                  ; TV frames between the lights (0.8 s)
SL_GRN  equ 130                 ; green this long after Q (2.6 s)
start_lights:
        ld a,(race_on)
        or a
        ret nz
        ld a,(start_go)
        or a
        ret z
        ld a,(start_f0)
        ld b,a
        ld a,(FRAMES)
        sub b                   ; frames since Q
        ld c,1
        cp SL_RED
        jr c,sl_ph
        inc c
        cp 2*SL_RED
        jr c,sl_ph
        inc c
        cp SL_GRN
        jr c,sl_ph
        inc c
sl_ph:
        ld a,(start_ph)         ; a new light?
        cp c
        ret z
        ld a,c
        ld (start_ph),a
        cp 4
        jr z,sl_green
        ld hl,0x3000+6          ; a red light: a beep - 6 frames, flips 48 counts apart
        ld (snd_fxt),hl
        jp lights_attr
sl_green:
        ld hl,0x1800+10         ; green: a higher beep, longer
        ld (snd_fxt),hl
        ld a,1                  ; and away
        ld (race_on),a
        jp lights_attr

msg_go:                         ; green: the lights stay 1.5 s more
        ld a,75
        ld (lt_t),a
        ret
msg_final:                      ; FINAL LAP on the strip for 3 s (bar_tick shows it)
        ld a,150
        ld (msg_timer),a
        ret
msg_finished:                   ; at the flag: your place, whole, and FINISHED! on the
        xor a                   ; strip - drawn here and now, as the pictures stop
        ld (msg_timer),a
        ld a,(position)
        call place_txt
        ld bc,20*256+4
        ld a,0x57
        call print_big
        ld hl,txt_strip+20
        ld bc,22*256+1
        jp print_at
place_txt:                      ; A = a place 1..5 (0 before the race: 1) -> HL = its text
        or a
        jr nz,pt_1
        inc a
pt_1:
        dec a
        add a,a
        add a,a
        ld e,a
        ld d,0
        ld hl,txt_places
        add hl,de
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
PNUM    equ BUFC+96             ; the place number, 16 rows (tower_row)
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
        ld a,M_LUCK             ; the crew chief: good luck
        call msg_say
        ld a,1
        ld (pace_skip),a        ; (a busy picture: it does not set the pace)
        ld hl,25*256+4          ; the border green for half a second
        call flash
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
best_panel:                     ; under the racers: a clock and the lap RECORD - the
        ld b,TOWER_Y+2*NCARS    ; best lap of any race since the game was loaded (a
        ld c,27                 ; hi-score, Grant 10 Nov 2026), centred under the
        ld de,CLOCK8            ; order (the clock in column 27, the time 2 px into
        call tr_glyph           ; 28: x 216-238 against the panel's 200-255)
        ld hl,(rec_lap)
        call time_fmt
        ld hl,time_txt+2
        ld b,(TOWER_Y+2*NCARS)*8+1
        ld c,28
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
        ld a,(start_go)         ; before Q: keys 1, 2, 3 set your car up
        or a
        call z,su_keys
        call start_lights       ; Q pressed: the lights, red, red, red, green
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
hu_final:
        ld a,(lt_t)             ; the lights' last 1.5 s
        or a
        jr z,hu_f1
        ld hl,dt
        sub (hl)
        jr nc,hu_lt
        xor a
hu_lt:
        ld (lt_t),a
        call z,lights_off
hu_f1:
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
hu_best:
        ld a,(best_seq)         ; a new best lap (by anyone)
        ld hl,shown_best_seq
        cp (hl)
        jr z,hu_order
        ld (hl),a
        call best_panel
hu_order:
        call strip_triggers     ; what the crew chief says
        call bar_tick           ; the scoreboard: your place, the strip, the time
        ld a,(renders)          ; spread the HUD out: the order on one
        and 3                   ; picture in four, the map on another, the
        jp z,tower_update       ; clock on the other two
        cp 2
        jp z,map_update
        jp strip_tick           ; the radio on the other two

hud_over:                       ; after the finish: the last flags, then
        call tower_update       ; wait for Q (the accelerate key) to be let go,
        call key_go             ; then pressed again - the title screen, then a new race
        ld hl,q_up
        jr z,ho_down
        ld (hl),1
        ret
ho_down:
        ld a,(hl)
        or a
        ret z
        pop hl                  ; leave the main loop: back to the start
        jp title_again          ; (title.asm; it ends at new_race)

; ---------------------------------------------------------------------
; BAR_TICK (each picture, racing): the message bar is empty after GO, so it
; shows what you most want to know, large (the layout review, Grant, 10 Nov
; 2026): your place - bright white on red, your colour - in columns 1-6, and
; LAP n/3 - black on bright yellow - in 12-17, with the race time after it.
; One big letter a picture at most, and only one that changed, so no picture
; runs late; the time a digit a second. A message (GO!, FINAL LAP!) takes
; the bar: msg_clear, when it goes, has everything drawn afresh.
; ---------------------------------------------------------------------
        ; (bar_tick and bar_3: in clothmini.asm, the gap before sq4's page)

; ---------------------------------------------------------------------
; YOUR CAR'S SET-UP (Grant, 13 Nov 2026): every car has three parts, each at a
; level 1..5 - GRIP (traction), SPEED (top speed), ACCEL (acceleration). Every
; car starts at 1, 1, 1; you have 2 points to add, anywhere, before the start:
; keys 1, 2, 3 add one to GRIP, SPEED, ACCEL; 0 takes both back. The computer
; cars stay at 1, 1, 1. The choice is kept from race to race.
;   GRIP:  the tyres' grip (yg_gtab), 15% more a level
;   SPEED: the top speed, 1/16 more a level (1.75 px a frame at level 1)
;   ACCEL: more push, so the top speed comes sooner (the top speed holds it)
; The HUD's bottom row (row 23) shows it: for each part its key (before the
; start), its letter and 5 pips, a filled one for each level.
; ---------------------------------------------------------------------
su_keys:
        ld a,0xEF               ; 0: start again (keys 6-0: 0 is bit 0)
        in a,(0xFE)
        rra
        jr nc,su_reset
        ld a,0xF7               ; 1, 2, 3 (keys 1-5: bits 0, 1, 2)
        in a,(0xFE)
        cpl
        and 7
        ld hl,su_up
        jr nz,su_k1
        ld (hl),1               ; none down: the next press is a new one
        ret
su_k1:
        ld b,(hl)
        ld (hl),0
        dec b
        ret nz                  ; still held from last time
        ld hl,su_lv-1
su_k2:
        inc hl                  ; HL -> the part's level
        rra
        jr nc,su_k2
        ld a,(su_pts)           ; a point left, and not at 5 yet?
        or a
        ret z
        ld a,(hl)
        cp 5
        ret nc
        inc (hl)
        ld hl,su_pts
        dec (hl)
        jr su_apply
su_reset:
        ld hl,su_lv
        ld (hl),1
        inc hl
        ld (hl),1
        inc hl
        ld (hl),1
        inc hl
        ld (hl),2
; SU_APPLY: the levels -> the numbers grip.asm drives your car by, then the row
su_apply:
        ld a,(su_lv+1)          ; SPEED s: top = 448 + 28 (s - 1) (8.8: 1.75 + 0.11)
        dec a
        add a,a
        add a,a
        ld c,a                  ; C = 4 (s - 1): the push that top speed needs
        add a,a
        add a,a
        add a,a
        sub c
        ld l,a
        ld h,0
        ld de,G_TOP
        add hl,de
        ld (yg_topv),hl
        ld a,(su_lv+2)          ; ACCEL a: push = 64 + 4 (s - 1) + 10 (a - 1)
        dec a
        ld e,a
        add a,a
        add a,a
        add a,e
        add a,a
        add a,c
        add a,G_PUSH
        ld l,a
        ld h,0
        ld (yg_pushv),hl
        ld a,(su_lv)            ; GRIP g: its row of the grip table
        dec a
        add a,a
        add a,a
        ld e,a
        ld d,0
        ld hl,su_gtab
        add hl,de
        ld de,yg_gtab
        ld bc,4
        ldir
        ret                     ; (the set-up is not shown on the race screen: Grant, 14 Nov
                                ; 2026, "don't worry about displaying the car strengths")

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
        push hl                 ; it has the best lap
        push bc
        ld e,a                  ; E = the car
        ld c,a
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
        ld a,(tr_row)           ; the place number, centred against the car:
        sub TOWER_Y             ; its ROM letter 4 px down the 16-px row
        srl a                   ; (Grant, 10 Nov 2026)
        add a,'1'
        ld l,a
        ld h,0
        add hl,hl
        add hl,hl
        add hl,hl
        ld de,0x3C00
        add hl,de
        ld de,PNUM
        xor a
        ld b,4
trp_1:
        ld (de),a
        inc de
        djnz trp_1
        ld bc,8
        ldir
        ld b,4
trp_2:
        ld (de),a
        inc de
        djnz trp_2
        ld c,25
        ld de,PNUM
        call tr_glyph16
        ld a,(tr_car)           ; the car's own picture, facing right, at
        rrca                    ; 16 x 16: tower_cars + car * 64
        rrca
        ld l,a
        and 0x3F
        ld h,a
        xor l
        ld l,a
        ld de,tower_cars
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
tr_race:                        ; the gap (columns 28-29); once it is in, a flag
        ld a,1                  ; (30); a clock if it has the best lap (31). (Each
        ld (tr_force),a         ; row had its lap too: yours is large in the
        ld a,(tr_row)           ; message bar now - the layout review, Grant,
        sub TOWER_Y             ; 10 Nov 2026)
        srl a
        call gap_draw           ; A = place
        ld a,(tr_key)
        bit 3,a
        jr z,trr_1
        ld c,30
        ld de,flag_top
        call tr_glyph16
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
MAP_Y   equ 19                  ; (the map's own picture starts 6 lines down: it shows on lines 25-61)
map_init:                       ; a new race: the last race's dots off the map (the
        jp map_off              ; map itself is drawn once, by screen_once)

map_update:
        ld hl,blink             ; your dot blinks: on 2 updates, off 2
        inc (hl)
        call map_off            ; 1. every old dot off (XOR it again)
        ld ix,cars+(NCARS-1)*C_SIZE   ; 2. the new dots, yours last
        ld c,NCARS-1
mu_new:
        push bc
        ld l,(ix+C_X)           ; map x = (x + 8 - MMX0) * 3 / 32, 0..53
        ld h,(ix+C_X+1)         ; (3/32 for the bigger track; it was 1/8)
        ld de,8-MMX0
        add hl,de
        call map_c3
        cp 54
        jr c,mu_x
        ld a,53
mu_x:
        push af                 ; (x kept: map_c3 uses DE)
        ld l,(ix+C_Y)           ; map y = (y + 8 - MMY0) * 3 / 32, 0..45
        ld h,(ix+C_Y+1)
        ld de,8-MMY0
        add hl,de
        call map_c3
        cp 46
        jr c,mu_y
        ld a,45
mu_y:
        ld d,a
        pop af
        ld e,a
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
        jr nz,mu_you
        dec hl
        ld (hl),0xFF            ; (blinked off: nothing to take off next time)
        jr mu_skip
mu_you:
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

; MAP_OFF: every dot shown, off again - drawn with XOR, so drawing it again
; puts the map back (no copy of the map needed: Grant's sweep, 10 Nov 2026)
map_off:
        ld c,0
mo_1:
        ld a,c
        add a,a
        ld hl,shown_dot
        add a,l
        ld l,a
        jr nc,mo_2
        inc h
mo_2:
        ld a,(hl)
        cp 0xFF
        jr z,mo_3
        ld (hl),0xFF
        ld e,a                  ; E = x, D = y
        inc hl
        ld d,(hl)
        push bc
        ld a,c
        or a
        ld b,0xC0               ; a computer car's 2 x 2, your 3 x 3
        ld c,2
        jr nz,mo_4
        ld b,0xE0
        ld c,3
mo_4:
        call map_dot
        pop bc
mo_3:
        inc c
        ld a,c
        cp NCARS
        jr nz,mo_1
        ret

map_c3:                         ; HL (0..~700) * 3 / 32 -> A
        ld d,h
        ld e,l
        add hl,hl
        add hl,de
        add hl,hl               ; * 8: H = HL * 3 / 32
        add hl,hl
        add hl,hl
        ld a,h
        ret

; map_dot: C rows of the pattern B (0xC0 or 0xE0) at map x E, y D (XOR)
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
        xor c
        ld (hl),a
        ld a,e
        and 0xF8
        cp 48                   ; the map's last byte: nothing to the right
        jr nc,md_one
        inc l
        ld a,(hl)
        xor b
        ld (hl),a
md_one:
        pop de
        inc d
        pop bc
        dec c
        jr nz,md_row
        ret

; ---------------------------------------------------------------------
; TIME_FMT: frames -> m:ss.t (the gaps and the best lap use it)
; ---------------------------------------------------------------------
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
; (the HUD's fixed text is in hudtext.asm, kept at the top of memory)
txt_digit:    db "0",0
bar_lap:      db " LAP 1/",'0'+LAPS," ",0  ; the strip while racing
txt_strip:    db " PRESS Q ",0,"FINAL LAP",0,"FINISHED!",0   ; ... and its other three (10 bytes each)
txt_time:     db "TIME",0
time_txt:     db "0:00.0",0
