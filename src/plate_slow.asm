; The place plate's parts that run rarely (see plateco.asm), in the slower memory under 0x8000.
pl_static:                      ; B = your place, C = your lap: the plate composed in pl_bmp
        ld (pl_key),bc
        push bc
        ld hl,pl_bmp            ; the plate: a clear line, a rounding row, 14 solid, a rounding
        ld c,PL_W               ; row, a clear line - 29 pixels of the 40 across
        ld de,0x0000
        call pf_row
        ld de,0x0380
        call pf_row
        ld b,14
ps_1:
        ld de,0x07C0
        call pf_row
        djnz ps_1
        ld de,0x0380
        call pf_row
        ld de,0x0000
        call pf_row
        pop bc
        push bc
        ld a,14                 ; P and your place
        ld c,b
        ld hl,pl_bmp+3*PL_W+1
        call pl_pair
        pop bc                  ; a space, the lap
        ld a,13
        ld hl,pl_bmp+3*PL_W+2
        call pl_pair
        ld a,12                 ; /3
        ld c,3
        ld hl,pl_bmp+3*PL_W+3
        jp pl_pair
; (pl_cols, pl_cut and pl_fill, which nothing called any more, went on 15 Nov 2026: 63 bytes)
; PA_STEP: the faces' step, 0-3 in A and E - a new one every 32 TV frames; Z if it is the one last given.
pa_step:
        ld a,(FRAMES)
        rlca
        rlca
        rlca
        and 3
        ld e,a
        ld hl,pa_last
        cp (hl)
        ld (hl),a
        ret
pa_last: db 0
; T_ANIM: the title's row of faces moves: everyday, eyes, in turn (at first with happy as well) (Grant, 15 Nov 2026: "in the
; title screen you can run the rotation of eyes and the happy face").
t_anim:
        call pa_step
        ret z
        res 1,e                 ; (just the two looks, no smile: Grant, 15 Nov 2026 - steps 0 and 1 in turn)
        xor a
ta_1:
        push af
        add a,a
        add a,a
        add a,7
        ld c,a
        ld b,16
        pop af
        push af
        call pa_car
        pop af
        inc a
        cp NCARS
        jr nz,ta_1
        ret
pf_row:                         ; a row: D its left byte, E its right, solid between (clear if D is 0)
        push hl
        push bc
        ld (hl),d
        inc hl
        ld a,d
        or a
        jr z,pf_2
        ld a,0xFF
pf_2:
        ld b,c
        dec b
        dec b
pf_3:
        ld (hl),a
        inc hl
        djnz pf_3
        ld (hl),e
        pop bc
        pop hl
        jp pl_down
; HUD_PRE, each picture before the canisters and the gauge are drawn (Grant, 14 Nov 2026: "make
; the NOS bottles in the bottom right red ink and the health lightning bolt magenta. So these
; would need a decent mask to prevent colour clash"). They do not scroll, so their colour cells
; can have an ink of their own - as long as nothing else is in those cells: the gauge's 3 x 2
; cells are written whole by dmg_draw; a canister's 1 x 2 are cleared here when you hold it
; (and are the window's own colour again when you do not).
HP_AT   equ 0x5800 + (WIN_Y/8 + WIN_H/8 - 2)*32 + WIN_COL   ; the window's last two cell rows on the screen
HP_NB   equ BUF + 0x800*2 + 2*32 + 2 + WIN_W - 1            ; the first canister's upper cell in the buffer (its last byte)
hud_pre:
        ld a,0x2B               ; the gauge: magenta on the table's cyan
        ld hl,HP_AT + WIN_W - 3 ; (at the window's right edge since 15 Nov 2026; the canisters at its left)
        ld (hl),a
        inc l
        ld (hl),a
        inc l
        ld (hl),a
        ld l,(HP_AT + 32 + WIN_W - 3) AND 255
        ld (hl),a
        inc l
        ld (hl),a
        inc l
        ld (hl),a
        ld a,(INV)              ; the canisters: red
        ld hl,HP_AT
        ld de,HP_NB - (WIN_W - 1)
        call hp_slot
        ld a,(INV+1)
        ld hl,HP_AT + 1
        ld de,HP_NB - (WIN_W - 1) + 1
        call hp_slot
        ld a,(INV+2)
        ld hl,HP_AT + 2
        ld de,HP_NB - (WIN_W - 1) + 2
hp_slot:                        ; A = the slot (0: empty), HL = its upper cell on the screen, DE = in the buffer
        or a
        ld a,WIN_ATTR2
        jr z,hp_2
        ex de,hl                ; held: its two cells cleared (16 lines of the one byte)
        xor a
        ld b,8
hp_0:
        ld (hl),a
        inc h
        djnz hp_0
        ld a,h
        sub 8
        ld h,a
        ld a,l
        add a,32
        ld l,a
        xor a
        ld b,8
hp_1:
        ld (hl),a
        inc h
        djnz hp_1
        ex de,hl
        ld a,0x2A
hp_2:
        ld (hl),a
        ld bc,32
        add hl,bc
        ld (hl),a
        ret
WIN_ATTR2 equ 0x29              ; the window's own colours: blue on cyan
pl_key:  dw 0                   ; the place and lap pl_bmp was composed for
pl_lin:  db 0                   ; pl_down's rows: 1 in pl_bmp, 0 in the buffer
pl_bmp:  defs PL_W*PL_H          ; the plate, composed

; DMG_MAKE: the health gauge composed for damage A (HL = dmg_sh) into dmg_bmp: DMG_ROWS rows of 3
; bytes - the outline, and the fill in every row but the first C (dmg_emp: it empties from the top).
dmg_make:
        ld (hl),a
        add a,5                 ; the mug: a clear row, 3 of steam, the rim, then a row of coffee a hit
        ld c,a
        ld hl,dmg_heart         ; for each byte: the outline, the fill
        ld de,dmg_bmp
        ld b,DMG_ROWS
dk_1:
        push bc
        ld b,3
dk_2:
        ld a,(hl)
        inc hl
        inc c
        dec c
        jr nz,dk_3
        or (hl)
dk_3:
        inc hl
        ld (de),a
        inc de
        djnz dk_2
        pop bc
        ld a,c
        or a
        jr z,dk_4
        dec c
dk_4:
        djnz dk_1
        ret
; DMG_ANIM: the gauge with its steam moving - every 8th picture the two wisps (pixels 9 and 13 of the
; rows 1 and 3, 8 and 12 of row 2: all in the middle byte) swap places with each other's. (Grant, 15 Nov
; 2026: "animate it so that the steam out of the top looks like steam coming out of the cup ... just
; those top bits".)
dmg_anim:
        ld a,(renders)
        and 7
        jr nz,da_2
        ld hl,dmg_bmp+4
        ld b,3
da_1:
        ld a,(hl)
        xor 0xCC
        ld (hl),a
        inc hl
        inc hl
        inc hl
        djnz da_1
da_2:
        jp dmg_draw
dmg_sh:  db 0xFF                 ; the damage dmg_bmp shows (0xFF: none yet)
dmg_bmp: defs 3*DMG_ROWS
        include "dmgicon.asm"   ; dmg_heart: the icon's art (tools/make_damage_icons.py)
pl_tl:   dw 0xFFFF               ; the lap time (frames) the plate's figures were last cut for

; ---------------------------------------------------------------------
; THE RACE'S START AND END (Grant, 15 Nov 2026): "once you click 1 or 2, then a ditty plays and
; the countdown after the ditty automatically begins"; "once all players are finished, there is
; a winner display in the centre of the gameplay area ... a podium with their faces, 1st, 2nd,
; 3rd, then also show fastest lap. Winner must have a graphic showing them smiling"; "on game
; over, it should go back to the title screen" (hud_over: any key). Layout A4 of
; docs/design/podium_inside.png: a yellow card, each driver on a step of their own colour.
; ---------------------------------------------------------------------
auto_go:                        ; each TV frame: the ditty over and no lights yet? they come on
        ld a,(jin_on)
        or a
        ret nz
        ld a,(race_on)
        ld hl,start_go
        or (hl)
        ret nz
        inc (hl)
        ld a,(FRAMES)
        ld (start_f0),a
        ret

podium:
        ld bc,0x0505            ; the card: rows 5-18, columns 5-20, black on bright yellow -
        ld de,0x0E10            ; a colour no driver has, so nobody blends into it
        call clear_cells
        ld bc,0x0505
        ld de,0x0E10
        ld a,0x70
        call set_attrs
        ld bc,0x0505            ; its head and foot: white on blue
        call pd_bar
        ld bc,0x1205            ; (a row of yellow between the fastest lap and this: Grant, 15 Nov 2026)
        call pd_bar
        ld a,208                ; under YOUR RACE: FINISHED and your place ...
        ld (MSG_X),a
        ld a,146
        ld (MSG_Y),a
        ld hl,pd_t6
        call sm_text
        ld a,(position)
        dec a
        add a,a
        add a,a
        ld e,a
        ld d,0
        ld hl,txt_places
        add hl,de
        call sm_text
        call yl_all             ; your laps (each was shown as it was done: again, to be sure)
        call yl_best            ; ... and your best lap picked out in yellow
        ld a,(order)            ; the steps, each its driver's colour: 1st in the middle, the tallest
        ld bc,0x070B
        ld de,0x0704
        call pd_col
        ld a,(order+1)
        ld bc,0x0807
        ld de,0x0604
        call pd_col
        ld a,(order+2)
        ld bc,0x090F
        ld de,0x0504
        call pd_col
        ld hl,pd_t1
        ld bc,41*256+104
        call sm_ctr
        ld hl,pd_t2
        ld bc,50*256+104
        call sm_ctr
        ld hl,pd_t3
        ld bc,121*256+104       ; (a row of card between the podium and this: Grant, 15 Nov 2026)
        call sm_ctr
        ld hl,pd_t4
        ld bc,145*256+104
        call sm_ctr
        ld a,(order)            ; their names
        ld bc,91*256+104
        call pd_name
        ld a,(order+1)
        ld bc,99*256+72
        call pd_name
        ld a,(order+2)
        ld bc,106*256+136
        call pd_name
        ld hl,(best_lap)        ; the fastest lap: whose, and the time
        ld a,h
        and l
        inc a
        jr z,pd_nb
        ld bc,0x1008            ; under FASTEST LAP (Grant, 15 Nov 2026: "B but also show which lap they did
        ld de,CLOCK8            ; it in"): the clock, the time, whose, and the lap
        call tr_glyph
        ld hl,(best_lap)
        call time_fmt
        ld hl,time_txt+2
        ld b,130
        ld c,9
        ld a,2
        call st_text_x
        ld a,(best_car)
        ld bc,130*256+108
        call pd_name
        ld hl,pd_t5
        ld bc,130*256+138
        call sm_ctr
        ld a,(best_lapno)
        add a,'0'
        call glyph
pd_nb:
        ld hl,pd_d1             ; the places, large
        ld bc,0x090C
        ld a,(order)
        call pd_big
        ld hl,pd_d2
        ld bc,0x0A08
        ld a,(order+1)
        call pd_big
        ld hl,pd_d3
        ld bc,0x0B10
        ld a,(order+2)
        call pd_big
        ld a,(order+1)          ; the faces: 2nd and 3rd as every day ...
        ld bc,0x0808
        call pd_face
        ld a,(order+2)
        ld bc,0x0910
        call pd_face
        ld a,(order)            ; ... the winner smiling - the same size as the others (Grant, 15 Nov
        ld bc,0x070C            ; 2026: "the faces can all be the same size")
        call pd_face            ; (pod_anim has it smile, once the jingle is over)
        jp jin_flag             ; and its jingle (Grant, 15 Nov 2026: "Also play it when the chequered flag is shown")
pd_bar:
        ld de,0x0110
        ld a,0x4F
        jp set_attrs
pd_cc:                          ; A = a car -> A = its colour
        push hl
        ld hl,car_colours
        add a,l
        ld l,a
        jr nc,pd_c1
        inc h
pd_c1:
        ld a,(hl)
        pop hl
        ret
pd_col:
        call pd_cc
        jp set_attrs
pd_big:
        call pd_cc
        jp print_big
pd_face:                        ; car A's everyday face into cells B, C (2 x 2)
        ld hl,faces
pd_f2:                          ; (... or its face from the set at HL)
        push bc
        rrca
        rrca
        rrca
        ld e,a
        ld d,0
        add hl,de
        ex de,hl
        pop bc
        push bc
        call tr_face_c
        pop bc
        inc b
        jp tr_face_c
pd_name:                        ; car A's name, small, centred on x C at line B
        push bc
        ld hl,pd_names
        call str_skip
        pop bc
sm_ctr:                         ; the text at HL in the small letters (4 pixels each), centred on x C at line B
        ld a,(hl)               ; (@: the name of the driver the crew chief is talking about - ms_car)
        cp '@'
        jr nz,sc_0
        push bc
        ld a,(ms_car)
        ld hl,pd_names
        call str_skip
        pop bc
sc_0:
        push hl
sc_1:
        ld a,(hl)
        or a
        jr z,sc_2
        cp '|'                  ; (a line of a crew message ends at | too)
        jr z,sc_2
        inc hl
        dec c
        dec c
        jr sc_1
sc_2:
        pop hl
        ld a,c
        ld (MSG_X),a
        ld a,b
        ld (MSG_Y),a
sm_text:
        ld a,(hl)
        or a
        ret z
        cp '|'
        ret z
        push hl
        call glyph
        ld hl,MSG_X
        ld a,(hl)
        add a,4
        ld (hl),a
        pop hl
        inc hl
        jr sm_text

; the title's five cars: where each starts (tc_init, plateco.asm)
tc_tab:                         ; x, y + 18, heading, steps left, the next part (2 bytes a part)
        db 32,30,64,96,2,  186,30,64,19,2,  244,134,128,22,6,  148,198,192,58,10,  12,172,0,61,14
t_blk   equ BUF+0x1700          ; (in the back buffer, past what the title keeps of the race screen there: free while no race runs)



; THE CREW CHIEF ON THE OTHER DRIVERS (Grant, 15 Nov 2026: "Include some random events for other
; riders too, Great driving Butch or something like that").
trg_best:                       ; the race's best lap has just been set: by you, or by one of them
        ld a,(best_car)
        ld (ms_car),a
        or a
        ld a,M_BEST
        jp z,msg_say
        ld a,(COOL)             ; (theirs is not said over a message just put up)
        or a
        ret nz
        ld a,M_FAST
        jp msg_say
trg_rand:                       ; when he has nothing else to say: one picture in 256 (about every 20 s), a
        call rnd                ; remark about one of the four, picked at random. Z: he spoke
        or a
        ret nz
        call rnd
        and 3
        inc a
        ld (ms_car),a
        call rnd
        and 3
        add a,M_OTH0
        call msg_say
        xor a
        ret
ms_car: db 0                    ; the driver a message with @ names

; The start jingle plays AFTER the race's first picture is shown (it was before: nothing runs while
; it plays, so the window stood empty - Grant, 15 Nov 2026: "at the start of the game while the
; jingle plays, the game does not show properly"). jin_on 2: due.
win_cells:                      ; a new race, before anything is put up: the window's cells its own colours again
        ld bc,0x0101            ; (the title keeps the screen's colours from when the last race ended - the
        ld de,0x1318            ; podium's, which then came back over the next race: Grant's screenshots,
        ld a,0x29               ; 15 Nov 2026)
        jp set_attrs
jin_arm:                        ; a new race (unless the jingle is held off: 0xFF)
        ld a,(jin_on)
        inc a
        ret z
        ld a,2
        ld (jin_on),a
        ret
jin_due:                        ; after each picture
        ld a,(jin_on)
        cp 2
        ret nz
        jp jin_start
