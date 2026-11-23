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
LOGO_ROW equ 21                 ; the logo: under the window, centred on it (columns 9-15)
LOGO_COL equ 9
TOWER_Y equ 6                   ; (just under the map since 15 Nov 2026: it was 10) ;                 ; first row of the race order (RACE above it)
A_YOU   equ 0x72                ; bright red on yellow: your marker's cell

; ---------------------------------------------------------------------
; HUD_INIT: the whole surround, once at the start of a race
; ---------------------------------------------------------------------
hud_init:                       ; a new race: what changes (the rest: screen_once)
        ld bc,0x121A            ; YOUR RACE, under the cars (Grant, 15 Nov 2026: panel C, "fill it in as the game
        ld de,0x0406            ; commences, showing lap times"): the last race's result and laps off,
        call clear_cells
        ld bc,0x121A
        ld de,0x0406
        ld a,A_YEL
        call set_attrs
        ld bc,0x111A            ; its heading, white on blue
        ld de,0x0106
        ld a,A_LAP
        call set_attrs
        ld hl,pd_t7
        ld bc,137*256+232
        call sm_ctr
        ld b,TOWER_Y+2*NCARS    ; the lap record under the order: cleared,
        ld c,26                 ; then shown if there is one from an earlier race
        ld d,1
        ld e,6
        call clear_cells
        ld hl,(rec_lap)
        inc hl
        ld a,h
        or l
        call nz,best_panel
        call strip_reset        ; the driver strip: inventory, the radio
        ld a,M_SETUP            ; the crew chief: pick your upgrades (CHOOSE: the extra is picked on the choose screen - he says
        call msg_say            ; ON THE GRID / WAIT FOR GREEN instead)
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
aa_hi:  ld d,0x58               ; (RACETRACK switches this page to its copy of the colour squares: rt_hud)
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
        if OPT_RT
        ld a,0x05               ; (RACETRACK: cyan on black)
        else
        ld a,0x28
        endif
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
        if OPT_RT
        ret                     ; (RACETRACK: every square is decided afresh each picture)
        endif
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
        if OPT_RREC             ; (RREC: the race clock at green - your race time runs from here)
        ld hl,(race_time)
        ld (rr_t0),hl
        endif
        ld a,1                  ; and away
        ld (race_on),a
        if OPT_AY
        ld (mu_wait),a          ; the race tune from its first note
        ld hl,mu_tune
        ld (mu_ptr),hl
        endif
        jp lights_attr

msg_go:                         ; green: the lights stay 1.5 s more
        ld a,75
        ld (lt_t),a
        ret
msg_final:                      ; FINAL LAP: the crew chief's bubble in the window for 3 s (plateco.asm copies it
        ld a,150                ; in each picture): its cells white
        ld (msg_timer),a
        if OPT_RT
        ret                     ; (RACETRACK: rt_hud colours the bubble's squares each picture)
        endif
        ld a,0x78
msg_cells:
        ld bc,0x1107
        ld de,0x020A
        jp set_attrs
msg_finished:                   ; at the flag: your place, whole, and FINISHED! on the
        xor a                   ; strip - drawn here and now, as the pictures stop
        ld (msg_timer),a
        ret                     ; (FINISHED! went with the strip: the window says CHEQUERED FLAG!)
; (place_txt went with the old banner: 15 Nov 2026)

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
PNUM    equ BUF+0x12E0          ; the place number, 16 rows (tower_row): in the buffer's bottom rows
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
        ld hl,25*256+4          ; the border green for half a second
        call flash
        ld a,M_LUCK             ; the crew chief: good luck (after the flash: writing his words takes a while)
        call msg_say
        ld hl,shown_order
        ld b,NCARS
hg_1:
        ld (hl),0xFF
        inc hl
        djnz hg_1
        jp msg_go
        if OPT_ARMOUR = 0
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
        endif
best_panel:                     ; under the racers: a clock and the lap RECORD - the
        ld b,TOWER_Y+2*NCARS    ; best lap of any race since the game was loaded (a
        ld c,28                 ; hi-score, Grant 10 Nov 2026), centred under the
        ld de,CLOCK8            ; order (the clock in column 27, the time 2 px into
        call tr_glyph           ; 28: x 216-238 against the panel's 200-255)
        ld hl,(rec_lap)
        call time_fmt
        ld hl,time_txt+2
        ld b,(TOWER_Y+2*NCARS)*8+1
        ld c,29
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
st_nx:
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
        ld a,(race_on)          ; until green: keys 1, 2, 3 set your car up (the lights' 2.6 s, now that the
                                ; jingle and the countdown come by themselves)
        or a
        if 1-OPT_CHOOSE         ; (CHOOSE: the extra is picked on the choose screen instead)
        call z,su_keys
        endif
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
        or a                    ; its time up: the bubble's cells the window's colours again
        ld a,0x29               ; (blue on cyan)
        if OPT_RT = 0
        call z,msg_cells
        endif
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
        ld (hl),a               ; (the crew chief says so: strip_triggers, M_LAST)
hu_lap:
hu_best:
        ld a,(best_seq)         ; a new best lap (by anyone)
        ld hl,shown_best_seq
        cp (hl)
        jr z,hu_order
        ld (hl),a
        call best_panel
hu_order:
        call strip_triggers     ; the canisters, the oil can - and what the crew chief says
        ; (no scoreboard under the window any more: your place and lap are on the plate in it - Grant, 14 Nov 2026)
        if OPT_ARMOUR           ; ARMOUR: the race order a row EVERY picture (the rows were drawn again one in four pictures,
        call tower_update       ; the first that changed first: early in a race, with places changing at the top, the rows
        endif                   ; below could show the car that had left them for seconds - four rows of the red car were
        ld a,(renders)          ; seen, 18 Nov 2026). Spread the HUD out: the order on one
        and 3                   ; picture in four, the map on another, the
        if OPT_ARMOUR
        ret z
        else
        jp z,tower_update       ; clock on the other two
        endif
        cp 2
        jp z,map_update
        if OPT_PIT
        jp strip_tick           ; the radio on the other two
        else
        ret                     ; (no pit talk for now: Grant, 14 Nov 2026)
        endif

hud_over:                       ; after the finish: the last flags, then
        call tower_update       ; wait for Q (the accelerate key) to be let go,
        call k_scan             ; ANY key (Grant, 15 Nov 2026: "on game over, it should go back to the
        ld hl,q_up              ; title screen"): let go, then pressed
        jr nz,ho_down
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
        if OPT_CHOOSE
; CHOOSE (Grant, 16 Nov 2026: "on the car you choose one extra of acceleration, grip and speed (you have one of each by
; default)"): each part is at level 1 or 2 - choose.asm sets su_lv - and one step is worth about a tenth:
;   SPEED:  top speed 448 -> 492 (1.75 -> 1.92 px a frame, +9.8%; CH_TOP), with the extra push that speed needs
;           (CH_SPUSH), given only above 1.5 px a frame so that it does not also get the car away quicker (grip.asm)
;   ACCEL:  push 64 -> 71 (+10.9%; CH_PUSH)
;   GRIP:   the tyres hold 18, 9, 9, 6 where they held 16, 8, 8, 5 (+12.5%, the last +20%: whole numbers; su_gtab's row 2)
CH_TOP  equ 44
CH_SPUSH equ 7
CH_PUSH equ 7
su_apply:
        ld hl,G_TOP
        ld b,0
        ld a,(su_lv+1)
        dec a
        jr z,sa_c1
        ld hl,G_TOP+CH_TOP
        ld b,CH_SPUSH
sa_c1:
        ld (yg_topv),hl
        ld a,b
        ld (yg_spush+1),a
        ld hl,G_PUSH
        ld a,(su_lv+2)
        dec a
        jr z,sa_c2
        ld l,G_PUSH+CH_PUSH
sa_c2:
        ld (yg_pushv),hl
        else
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
        if OPT_SIMPLE           ; SIMPLE (C1): the levels into your card row (you_card, cards_code.asm) - SPEED s: its SPEED push
        ld a,(su_lv+1)          ; 4 (s - 1) 64ths more (as the grip model's top speed: +6% a level); ACCEL a: its ACCEL push
        dec a                   ; 10 (a - 1) more as well; GRIP g: where it slides, an eighth more a level
        add a,a
        add a,a
        ld c,a
        if OPT_PICK             ; (PICK: from the car you chose - pick.asm)
        ld hl,pk_ks
        add a,(hl)
        else
        add a,YOU_KS AND 255
        endif
        ld (you_card+5),a
        ld a,(su_lv+2)
        dec a
        ld e,a
        add a,a
        add a,a
        add a,e
        add a,a
        add a,c
        if OPT_PICK
        ld hl,pk_ka
        add a,(hl)
        else
        add a,YOU_KA AND 255
        endif
        ld (you_card+4),a
        ld a,(su_lv)
        dec a
        ld e,a
        ld d,0
        if OPT_PICK
        ld hl,(pk_sl)
        ld bc,(pk_s8)
        else
        ld hl,YOU_SL
        ld bc,YOU_SL/8
        endif
        jr z,sua_g
sua_1:
        add hl,bc
        dec e
        jr nz,sua_1
sua_g:  ld (you_card),hl
        ret
        endif
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
        endif                   ; (CHOOSE)
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
        if OPT_ARMOUR           ; (ARMOUR: no gap times in the race order - the health blocks have their room)
        if OPT_RACE
        jp rg_update            ; (RACE mode: one place's gap to the car ahead - race.asm)
        else
        ret
        endif
        else
        jp gap_update           ; nothing moved: bring one place's gap up to date
        endif

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
        ld c,26
        call tr_clear
        ld a,(tr_row)
        inc a
        ld b,a
        ld c,26
        call tr_clear
        ld a,(tr_car)           ; colours: you white on red, the others black
        ld e,a                  ; on their own colour
        ld d,0
        ld hl,car_colours
        add hl,de
        ld a,(tr_row)
        ld b,a
        ld c,26
        ld a,(hl)
        ld d,2
        ld e,6
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
        ld c,26
        ld de,PNUM
        call tr_glyph16
        if OPT_TOWERF           ; BRIDGE: (memory) the car's picture comes from its frame, not from a second copy (tower_cars)
        call tower_b
        else
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
        ld c,27
        call tr_pic
        ld a,(tr_row)
        inc a
        ld b,a
        ld c,27
        call tr_pic
        endif                   ; (BRIDGE)
        ld a,(race_on)          ; racing: the gap to the leader, not the face
        or a
        jp nz,tr_race
        ld a,(tr_car)           ; the driver's face, beside the car:
        if OPT_CHOOSE
        call who_a              ; CHOOSE: the driver in this car today
        endif
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
        if OPT_ARMOUR           ; (ARMOUR: no gap - the health blocks have its room; the flag and the clock in column 28,
        jp arm_flag             ; then the blocks: armour_low.asm)
        else
        ld a,1                  ; (30); a clock if it has the best lap (31). (Each
        ld (tr_force),a         ; row had its lap too: yours is large in the
        ld a,(tr_row)           ; message bar now - the layout review, Grant,
        sub TOWER_Y             ; 10 Nov 2026)
        srl a
        call gap_draw           ; A = place
        ld a,(tr_key)           ; column 31: the flag once it is in, the clock if it has the best
        and 0x18                ; lap; both: the flag above the small clock (Grant, 14 Nov 2026:
        ret z                   ; "the flag and the fastest time icons are in the same column")
        ld c,31
        ld de,clock_top
        cp 0x10
        jr z,tr_glyph16
        ld de,flag_top
        cp 0x08
        jr z,tr_glyph16
        ld a,(tr_row)
        ld b,a
        ld de,FLAG8
        push bc
        call tr_glyph
        pop bc
        inc b
        ld de,CLOCK8
        jr tr_glyph
        endif                   ; (ARMOUR)
tr_glyph16:                     ; 16 rows at DE into cells tr_row and below, column C
        ld a,(tr_row)
        ld b,a
        push bc
        call tr_glyph
        pop bc
        inc b
        jr tr_glyph
tr_face:                        ; 8 rows x 2 bytes at DE into cells B, 29-30
        ld c,30                 ; (column 29 left clear: a gap after the car)
tr_face_c:                      ; (... into cells B, C and C + 1: the title's row of faces)
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
        if OPT_TOWERF
; TOWER_B: the race order's car picture, 16 x 16 at cell row tr_row, column 27, from the car's own frame
; facing right (heading 4: big_tab's address, first row, rows; a frame's row 6 is the car's top line) -
; the lines above and below the frame's rows are cleared. Uses the other BC (the count of each).
tower_b:
        ld a,(tr_car)
        if OPT_RACE
tw_kmask: and 0xFF              ; (RACE mode: every car the racer - race.asm makes this AND 0)
        endif
        if OPT_HEAD32 = 2       ; (HEAD32=all: every car 32 headings - its heading 8 faces right: big_tab + car * 128 + 32)
        ld h,a
        ld l,0
        srl h
        rr l
        ld de,big_tab+32
        add hl,de
        jr tw_have
        endif
        if OPT_HEAD32           ; (HEAD32: YOUR car's 32 headings first - its heading 8 faces right; then the others')
        ld hl,big_tab+32
        or a
        jr z,tw_have
        endif
        rrca
        rrca
        ld l,a
        and 0x3F
        ld h,a
        xor l
        ld l,a
        if OPT_HEAD32
        ld de,big_tab+80
        else
        ld de,big_tab+16
        endif
        add hl,de
        if OPT_HEAD32
tw_have:
        endif
        ld e,(hl)
        inc hl
        ld d,(hl)               ; DE = the frame
        inc hl
        ld a,(hl)
        sub 6
        inc hl
        ld h,(hl)
        ld l,a
        push hl
        exx
        pop bc                  ; C' = clear lines first, B' = the frame's rows
        exx
        ld a,(tr_row)
        ld b,a
        call tw_8
        ld a,(tr_row)
        inc a
        ld b,a
tw_8:
        ld c,27
        call cell_addr
        ld b,8
tw_1:
        exx
        ld a,c
        or a
        jr z,tw_2
        dec c
tw_clr:
        exx
        xor a
        ld (hl),a
        inc l
        ld (hl),a
        jr tw_4
tw_2:
        ld a,b
        or a
        jr z,tw_clr
        dec b
        exx
        inc de                  ; skip the mask; ink left
        ld a,(de)
        ld (hl),a
        inc de
        inc de                  ; skip the mask; ink right
        inc l
        ld a,(de)
        ld (hl),a
        inc de
tw_4:
        dec l
        inc h
        djnz tw_1
        ret
        else
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
        endif                   ; (BRIDGE)
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
        ld e,a
        ld a,l
        sub 5
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
; In the WINDOW's bottom left corner since 15 Nov 2026 (Grant: "have the track map on the bottom left inside of
; play"; "c (2)4 is good, and the inside parts could be blue - so no masking inside required"): 24 pixels wide,
; MAP_H lines, the road a solid ribbon of ink. Its ink is kept at MAPDAT, 3 bytes a line, and map_blit ORs it
; into the back buffer each picture. The dots are XORed into MAPDAT itself: on the ribbon a dot is a HOLE the
; picture shows through (yours 2 x 2 and blinking, the others a single pixel); off the road it is ink.
; MAPW40=1 (a build option, 16 Nov 2026 - Grant: "C wide please"): 40 pixels wide, 5 bytes a line, the ribbon 4 to 5 across,
; at 19/256 - the same corner and the same dots. Its ink is then in the program itself (racer.asm, at MAPDAT).
map_init:                       ; a new race: the last race's dots out of the map
        jp map_off
; MAP_BLIT: the mini-map over the picture, each picture after the cars and the arrow (about 130 T a line)
map_blit:
        ld hl,MAPDAT
        if OPT_MAPHUD           ; MAPHUD (Grant, 22 Nov 2026: "move the map out of the in game display and back to the HUD
        ld de,MAP_SCR           ; please. You can place it at the top of the HUD on the right"): copied to the screen, over
        else                    ; the race order, whenever its dots move (map_update) - not ORed into the window
        ld de,MAP_BUF
        endif
        ld b,MAP_H
mb_1:
        if OPT_MAP40            ; MAPW40: 5 bytes a line (about 200 T a line), the ink anywhere in the program (so INC HL)
        if OPT_MAPHUD           ; (MAPHUD: to the screen - a copy)
        ld c,e
        ld a,(hl)
        ld (de),a
        inc hl
        inc e
        ld a,(hl)
        ld (de),a
        inc hl
        inc e
        ld a,(hl)
        ld (de),a
        inc hl
        inc e
        ld a,(hl)
        ld (de),a
        inc hl
        inc e
        ld a,(hl)
        ld (de),a
        inc hl
        ld e,c
        else
        ld c,e
        ld a,(de)
        or (hl)
        ld (de),a
        inc hl
        inc e
        ld a,(de)
        or (hl)
        ld (de),a
        inc hl
        inc e
        ld a,(de)
        or (hl)
        ld (de),a
        inc hl
        inc e
        ld a,(de)
        or (hl)
        ld (de),a
        inc hl
        inc e
        ld a,(de)
        or (hl)
        ld (de),a
        inc hl
        ld e,c
        endif
        else
        if OPT_MAPHUD           ; (the screen: a copy - the dots are in MAPDAT already)
        ld a,(hl)
        ld (de),a
        inc l
        inc e
        ld a,(hl)
        ld (de),a
        inc l
        inc e
        ld a,(hl)
        ld (de),a
        else
        ld a,(de)
        or (hl)
        ld (de),a
        inc l
        inc e
        ld a,(de)
        or (hl)
        ld (de),a
        inc l
        inc e
        ld a,(de)
        or (hl)
        ld (de),a
        endif
        inc l
        dec e
        dec e
        endif
        inc d                   ; the next line down (the buffer is laid out like the screen)
        ld a,d
        and 7
        jr nz,mb_2
        ld a,e
        add a,32
        ld e,a
        jr c,mb_2
        ld a,d
        sub 8
        ld d,a
mb_2:
        djnz mb_1
        if OPT_MAPHUD           ; (and its squares' colours: blue on the panel's yellow)
        ld hl,0x5800+(MAP_SY/8)*32+MAP_SC
        ld de,32-MAP_W/8
        ld b,(MAP_SY+MAP_H+7)/8-MAP_SY/8
mb_a:   ld c,MAP_W/8
mb_a2:  ld (hl),MAP_ATTR
        inc l
        dec c
        jr nz,mb_a2
        add hl,de
        djnz mb_a
        endif
        ret

map_update:
        if OPT_RT               ; (RACETRACK: the map has changed - it goes to the screen afresh. rt_hud, racetrack.asm)
        ld hl,rt_fx
        set 0,(hl)
        endif
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
        cp MAP_W-1
        jr c,mu_x
        ld a,MAP_W-2
mu_x:
        push af                 ; (x kept: map_c3 uses DE)
        ld l,(ix+C_Y)           ; map y = (y + 8 - MMY0) * 3 / 32, 0..45
        ld h,(ix+C_Y+1)
        ld de,8-MMY0
        add hl,de
        call map_c3
        cp MAP_H-1
        jr c,mu_y
        ld a,MAP_H-2
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
        ld b,0x80               ; a single pixel for a computer car
        ld c,1
        jr nz,mu_draw
        ld a,(blink)            ; you: 3 x 3, shown 2 updates in 4
        and 2
        jr nz,mu_you
        dec hl
        ld (hl),0xFF            ; (blinked off: nothing to take off next time)
        jr mu_skip
mu_you:
        ld b,0xC0
        ld c,2
mu_draw:
        call map_dot
mu_skip:
        ld de,0x10000-C_SIZE
        add ix,de
        pop bc
        dec c
        jp p,mu_new
        if OPT_MAPHUD
        jp map_blit             ; MAPHUD: to the screen now
        else
        ret
        endif

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
        ld b,0x80               ; a computer car's pixel, your 2 x 2
        ld c,1
        jr nz,mo_4
        ld b,0xC0
        ld c,2
mo_4:
        call map_dot
        pop bc
mo_3:
        inc c
        ld a,c
        cp NCARS
        jr nz,mo_1
        ret

map_c3:                         ; HL (0..~700) * 11 / 256 -> A (every track: the map is 24 wide)
        ld d,h
        ld e,l
        if OPT_MAP40            ; MAPW40: * 19 / 256 (the map is 40 wide)
        add hl,hl
        add hl,hl
        add hl,hl
        add hl,de               ; * 9
        add hl,hl
        add hl,de               ; * 19
        ld a,h
        ret
        endif
        add hl,hl
        add hl,hl
        add hl,de               ; * 5
        add hl,hl
        add hl,de               ; * 11
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
        if OPT_MAP40            ; MAPW40: MAPDAT + 5 * the line + the byte across (under 256 in all: racer.asm checks)
        ld a,d
        add a,a
        add a,a
        add a,d
        ld l,a
        ld a,e
        rrca
        rrca
        rrca
        and 7
        add a,l
        ld l,a
        ld h,0
        ld bc,MAPDAT
        add hl,bc
        else
        ld a,d                  ; MAPDAT + 3 * the line + the byte across
        add a,a
        add a,d
        ld l,a
        ld a,e
        rrca
        rrca
        rrca
        and 3
        add a,l
        add a,MAPDAT AND 255
        ld l,a
        ld h,MAPDAT/256
        endif
        ld bc,(md_pat)
        ld a,(hl)
        xor c
        ld (hl),a
        ld a,e
        and 0xF8
        cp MAP_W-8              ; the map's last byte: nothing to the right
        jr nc,md_one
        if OPT_MAP40
        inc hl
        else
        inc l
        endif
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
; (the old message bar's words went on 15 Nov 2026: nothing showed them)
time_txt:     db "0:00.0",0
