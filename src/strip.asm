; ---------------------------------------------------------------------
; THE DRIVER STRIP (under the window): you, your inventory, the crew chief's
; radio, the crew chief (Grant, 10 Nov 2026). Its fixed picture is drawn
; once (screen_once). Here: the inventory, the radio wave while the chief
; talks, and his message, typed out in the 3 x 5 letters a few at a time so
; no picture runs late. strip_tick runs on 2 pictures in 4: one types, the
; other moves the wave.
; ---------------------------------------------------------------------
MSG_P   equ BUFC+128            ; the next letter (2)
MSG_ST  equ BUFC+130            ; 0 quiet (no bubble), 1-2 the bubble appears, 3 typing,
                                ; 4 shown (MSG_T), 5-6 the bubble goes
MSG_Y   equ BUFC+131            ; pixel row of the line being typed
MSG_X   equ BUFC+132            ; pixel x of the next letter
WAVE_T  equ BUFC+133            ; wave updates of talking left
COOL    equ BUFC+134            ; pictures before a nag can follow another
TRG_POS equ BUFC+135            ; your place, as last seen
TRG_BS  equ BUFC+136            ; best_seq, as last seen
TRG_LAP equ BUFC+137            ; your lap, as last seen
HIT_O   equ BUFC+138            ; you hit an O (set in tick)
INV     equ BUFC+139            ; the inventory: 3 slots, 0 empty, 1 NOS
INV_SH  equ BUFC+142            ; ... as shown (3)
MSG_T   equ BUFC+148            ; strip ticks the message stays up once typed
BOX_X   equ 89                  ; the box's inside: x 89-150
WAVE_X  equ 107                 ; the wave: 13 lines, 2 px apart, rows 161-167
WAVE_MID equ 164

strip_reset:                    ; a new race
        ld hl,MSG_P
        ld b,17
srs_1:
        ld (hl),0
        inc hl
        djnz srs_1
        ld a,0xFF               ; (nothing shown, so all redrawn)
        ld (INV_SH),a
        ld (INV_SH+1),a
        ld (INV_SH+2),a
        ld (TRG_LAP),a
        ld a,1                  ; your place on the grid
        ld (TRG_POS),a
        ld a,1                  ; you start with one NOS canister
        ld (INV),a
        ld (SPACE_UP),a
        xor a                   ; canister A on the track, no boost
        ld (NOS_SHOW),a
        ld (BOOST_T),a
        call nos_place
        ld a,5
        ld (MSG_ST),a           ; no bubble (it goes, if one was up)
        jp inv_draw

msg_say:                        ; A = message: the chief starts talking
        add a,a
        ld l,a
        ld h,0
        ld de,MSG_INDEX
        add hl,de
        ld e,(hl)
        inc hl
        ld d,(hl)
        ld (MSG_P),de
        ld a,1
        ld (MSG_ST),a           ; the bubble (drawn afresh: the old words go)
        ld a,9                  ; ~2 s of wave (4 updates a second)
        ld (WAVE_T),a
        ld a,12                 ; up ~3 s once typed
        ld (MSG_T),a
        ld a,48                 ; and ~3 s before a nag may follow
        ld (COOL),a
        ret

; STRIP_TICK: renders AND 3 = 1: wipe, then type; = 3: the wave
strip_tick:
        ld a,(renders)
        and 2
        jp nz,wave_tick
        ld a,(MSG_ST)
        or a
        ret z
        cp 3
        jr z,st_type
        jr c,st_show
        cp 4
        jr z,st_up
        cp 5                    ; 5-6: the bubble goes, half a tick
        ld b,20
        jr z,st_hide
        ld b,22
st_hide:
        xor a
        call bubble2
        ld a,(MSG_ST)
        cp 6
        jr nz,st_next
        ld a,0x30               ; gone: the strip's yellow again
        call bb_attr
        xor a
        ld (MSG_ST),a
        ret
st_up:                          ; shown: the bubble stays a while, then goes
        ld hl,MSG_T
        dec (hl)
        ret nz
st_next:
        ld hl,MSG_ST
        inc (hl)
        ret
st_show:                        ; 1-2: the bubble appears, half a tick
        ld b,20
        cp 1
        jr z,st_sh1
        ld b,22
st_sh1:
        ld a,1
        call bubble2
        ld a,(MSG_ST)
        cp 2
        jr nz,st_next
        ld a,0x78               ; drawn: white, then the words
        call bb_attr
        ld a,171
        ld (MSG_Y),a
        call line_x
        ld a,3
        ld (MSG_ST),a
        ret
st_type:
        ld b,4                  ; typing: 4 letters a time
stt_1:
        push bc
        ld hl,(MSG_P)
        ld a,(hl)
        or a
        jr z,stt_end
        cp '|'
        jr nz,stt_ch
        inc hl                  ; the next line
        ld (MSG_P),hl
        ld a,(MSG_Y)
        add a,6
        ld (MSG_Y),a
        call line_x
        jr stt_2
stt_ch:
        inc hl
        ld (MSG_P),hl
        call glyph
        ld a,(MSG_X)
        add a,4
        ld (MSG_X),a
stt_2:
        pop bc
        djnz stt_1
        ret
stt_end:
        pop bc
        ld a,4
        ld (MSG_ST),a
        ret
; BUBBLE: A = 1 draws, 0 clears the crew chief's speech bubble in
; char row B (20-23) - its 8 lines, columns 11-19: the box (x 88-151, rounded) and
; its tail out to the chief (column 19, rows 172-179). Drawn while he talks.
bubble:
        ld (bb_on+1),a
        ld a,b
        and 7
        rrca
        rrca
        rrca
        or 11
        ld l,a
        ld h,0x50               ; (rows 160-191: the screen's third third)
        ld a,b
        sub 20
        add a,a
        add a,a
        add a,a
        add a,160
        ld c,a                  ; C = y
        ld b,8
bb_ln:
        push bc
        push hl
        ld d,0x80               ; D: column 11 (the left edge), E: 18 (the right),
        ld e,0x01               ; B: 19 (the tail); the middle: blank
        ld b,0
        ld a,c
        cp 160
        jr z,bb_lin
        cp 191
        jr z,bb_lin
        cp 161
        jr z,bb_crn
        cp 190
        jr z,bb_crn
        sub 172                 ; the tail: rows 172-179
        cp 8
        jr nc,bb_mid
        push hl
        ld hl,bb_tail
        add a,l
        ld l,a
        jr nc,bb_t1
        inc h
bb_t1:
        ld b,(hl)
        pop hl
        ld a,c
        cp 173                  ; its mouth, rows 173-178: no right edge
        jr c,bb_mid
        cp 179
        jr nc,bb_mid
        ld e,0
        jr bb_mid
bb_crn:
        ld d,0x40               ; the rounded corners
        ld e,0x02
        jr bb_mid
bb_lin:
        ld d,0x3F               ; the top and bottom lines
        ld e,0xFC
        ld a,0xFF
        jr bb_w
bb_mid:
        xor a
bb_w:
bb_on:
        ld c,0                  ; (patched) 1 draw, 0 clear
        inc c
        dec c
        jr nz,bb_w1
        xor a
        ld d,a
        ld e,a
        ld b,a
bb_w1:
        ld (hl),d
        inc l
        ld c,6
bb_w2:
        ld (hl),a
        inc l
        dec c
        jr nz,bb_w2
        ld (hl),e
        inc l
        ld (hl),b
        pop hl
        pop bc
        inc h
        inc c
        djnz bb_ln
        ret
bb_tail: db 0x80,0x40,0x20,0x18,0x18,0x20,0x40,0x80

bubble2:                        ; A = 1 draw, 0 clear: char rows B and B+1
        push af
        push bc
        call bubble
        pop bc
        pop af
        inc b
        jp bubble
bb_attr:                        ; A = the bubble's colour: columns 11-18, rows 20-23
        ld b,20
        ld c,11
        ld d,4
        ld e,8
        jp set_attrs

        ; (line_x: in clothmini.asm, the gap before sq4's page)

; GLYPH: A = a letter (A-Z ! . - '; anything else is a gap), drawn at
; MSG_X, MSG_Y in the 3 x 5 letters: 15 bits, top row first
glyph:
        cp 'A'
        jr c,gl_sym
        cp 'Z'+1
        ret nc
        sub 'A'
        jr gl_go
gl_sym:
        ld hl,gl_syms
        ld b,4
gl_s1:
        cp (hl)
        jr z,gl_s2
        inc hl
        djnz gl_s1
        ret                     ; (a space)
gl_s2:
        ld a,30
        sub b                   ; ! . - ' -> 26..29
gl_go:
        add a,a
        ld l,a
        ld h,0
        ld de,LFONT
        add hl,de
        ld d,(hl)
        inc hl
        ld e,(hl)               ; DE = the 15 bits
        ld a,(MSG_X)            ; the shift table page for this x
        and 7
        ld (gl_s+1),a
        ld a,(MSG_Y)
        ld b,a
        ld c,5
gl_row:
        push bc
        ld a,d                  ; this row: the top 3 bits
        and 0xE0
        ld c,a
        ld b,3
gl_sh:
        sla e
        rl d
        djnz gl_sh
        or a
        jr z,gl_next            ; an empty row
        pop hl
        push hl                 ; H = the pixel row
        push de
        ld e,c                  ; E = the row's bits (at the top)
        ld b,h
        ld a,(MSG_X)
        ld c,a
        call scr_addr           ; HL = the byte at MSG_X
gl_s:
        ld a,0                  ; (patched) x AND 7
        or a
        jr z,gl_0
        neg
        add a,8
        add a,a
        add a,TAB_HI            ; page TAB_HI + 2(8 - s): A = b >> s, then
        ld d,a                  ; the next page B = b << (8 - s)
        ld a,e
        ex de,hl                ; (DE = screen)
        ld l,a
        ld a,(de)
        or (hl)
        ld (de),a
        inc e
        inc h
        ld a,(de)
        or (hl)
        ld (de),a
        jr gl_d
gl_0:
        ld a,e
        or (hl)
        ld (hl),a
gl_d:
        pop de
gl_next:
        pop bc
        inc b
        dec c
        jr nz,gl_row
        ret
gl_syms: db "!.-'"              ; in the font's order: 26..29 (B counts down)

; WAVE_TICK: the radio wave - 13 lines about a mid line, a new shape while
; the chief talks, flat when he stops
wave_tick:
        ld a,(MSG_ST)           ; only in the bubble (3 typing, 4 shown)
        sub 3
        cp 2
        ret nc
        ld a,(WAVE_T)
        or a
        ret z
        dec a
        ld (WAVE_T),a
        ld b,WAVE_MID-3         ; wipe its 7 rows (4 bytes from x 104): one
        ld c,104                ; character row, so the next row is INC H
        call scr_addr
        ld b,7
wt_1:
        xor a
        ld (hl),a
        inc l
        ld (hl),a
        inc l
        ld (hl),a
        inc l
        ld (hl),a
        dec l
        dec l
        dec l
        inc h
        djnz wt_1
        ld c,0                  ; C = line 0..12
wt_line:
        ld a,(WAVE_T)
        or a
        ld a,0
        jr z,wt_h               ; stopped talking: flat
        ld a,r                  ; a height 0-3, lower towards the ends
        and 3
        ld b,a
        ld a,c
        cp 7
        jr c,wt_e
        ld a,12
        sub c
wt_e:
        inc a
        cp b
        jr c,wt_h
        ld a,b
wt_h:
        ld e,a                  ; E = height: rows MID-E .. MID+E
        push bc
        ld a,c
        add a,a
        add a,WAVE_X
        ld c,a
        and 7
        ld b,a
        ld a,0x80
        jr z,wt_m
wt_m1:
        rrca
        djnz wt_m1
wt_m:
        ld d,a                  ; D = its bit
        ld a,WAVE_MID
        sub e
        ld b,a
        call scr_addr           ; (the 7 rows are one character row: INC H)
        ld a,e
        add a,a
        inc a
        ld b,a
wt_px:
        ld a,(hl)
        or d
        ld (hl),a
        inc h
        djnz wt_px
        pop bc
        inc c
        ld a,c
        cp 13
        jr nz,wt_line
        ret

; STRIP_TRIGGERS: what the chief says (each picture, racing)
strip_triggers:
        ld a,(race_on)
        or a
        ret z
        call nos_take           ; over a canister?
        ld hl,COOL
        ld a,(hl)
        or a
        jr z,trg_0
        dec (hl)
trg_0:
        ld a,(best_seq)         ; your lap, the best yet
        ld hl,TRG_BS
        cp (hl)
        jr z,trg_1
        ld (hl),a
        ld a,(best_car)
        or a
        ld a,M_BEST
        jp z,msg_say
trg_1:
        ld a,(cars+C_LAPS)      ; the last lap
        ld hl,TRG_LAP
        cp (hl)
        jr z,trg_2
        ld (hl),a
        cp LAPS
        ld a,M_LAST
        jp z,msg_say
trg_2:
        ld a,(position)         ; places
        ld hl,TRG_POS
        cp (hl)
        jr z,trg_3
        ld b,(hl)
        ld (hl),a
        cp 1
        ld a,M_P1
        jp z,msg_say            ; the lead: always
        ld a,(COOL)
        or a
        ret nz
        ld a,(hl)
        cp b
        ld a,M_PASS
        jp c,msg_say
        ld a,M_LOST
        jp msg_say
trg_3:
        ld hl,HIT_O             ; the nags: only after a quiet while
        ld b,(hl)
        ld (hl),0
        ld a,(COOL)
        or a
        ret nz
        or b
        ld a,M_HIT
        jp nz,msg_say
        ld a,(position)         ; second, and within 0.5 s of the leader
        cp 2
        ret nz
        ld hl,(GAPS)            ; (GAPS: each car's gap; you are car 0)
        ld a,h
        or a
        ret nz
        ld a,l
        or a
        ret z
        cp 25
        ret nc
        ld a,M_PUSH
        jp msg_say

; RACE_BOX: the race is over - the chequered flag in the middle of the
; window, over the last picture, which stays (Grant: everything stops)
race_box:
        ld b,9                  ; cells rows 9-13, columns 3-20, wiped
        ld c,3
        ld d,5
        ld e,18
        call clear_cells
        ld b,74                 ; lines above and below (a banner)
        call rb_line
        ld b,109
        call rb_line
        ld hl,txt_flag          ; CHEQUERED FLAG!
        ld b,10
        ld c,4
        call print_at
        ld hl,txt_youfin        ; YOU FINISHED 3RD
        ld b,11
        ld c,4
        call print_at
        ld a,(position)
        dec a
        add a,a
        add a,a
        ld e,a
        ld d,0
        ld hl,txt_places
        add hl,de
        ld b,11
        ld c,17
        call print_at
        ld hl,txt_pressq        ; PRESS Q
        ld b,12
        ld c,8
        jp print_at
        ; (rb_line: in clothmini.asm, the gap before sq4's page)

; ---------------------------------------------------------------------
; NOS (Grant, 10 Nov 2026): you start with one canister; SPACE fires one -
; 1 second (50 TV frames) of twice the push, so twice the top speed, then
; it fades as usual. Canisters on the track: A just behind the grid, then B
; in the middle of the top area, one at a time; driving over one puts it in
; your first empty slot (none taken if all 3 are full).
; ---------------------------------------------------------------------
NOS_SHOW equ BUFC+145           ; 0: canister A on the track, 1: B
BOOST_T  equ BUFC+146           ; TV frames of boost left
SPACE_UP equ BUFC+147           ; SPACE was up (so a press is new)
BOOST_FR equ 50

nos_place:                      ; show the canister NOS_SHOW names, hide the other
        ld a,(NOS_SHOW)
        or a
        ld a,NOS_A_V0
        ld b,NOS_A_V1
        ld c,0
        ld d,c
        jr z,np_1
        ld c,NOS_B_V0
        ld d,NOS_B_V1
        ld a,0
        ld b,a
np_1:
        ld (NOS_A_T0),a
        ld a,b
        ld (NOS_A_T1),a
        ld a,c
        ld (NOS_B_T0),a
        ld a,d
        ld (NOS_B_T1),a
        ret

nos_take:                       ; each picture: are you over the canister?
        ld a,(NOS_SHOW)
        or a
        ld de,8+10-NOS_A_X
        ld bc,8+10-NOS_A_Y
        jr z,nt_1
        ld de,8+10-NOS_B_X
        ld bc,8+10-NOS_B_Y
nt_1:
        ld hl,(cars+C_X)        ; within 10 pixels of its centre, both ways
        add hl,de
        ld a,h
        or a
        ret nz
        ld a,l
        cp 21
        ret nc
        ld hl,(cars+C_Y)
        add hl,bc
        ld a,h
        or a
        ret nz
        ld a,l
        cp 21
        ret nc
        ld hl,INV               ; your first empty slot
        ld b,3
nt_2:
        ld a,(hl)
        or a
        jr z,nt_3
        inc hl
        djnz nt_2
        ret                     ; all full: it stays
nt_3:
        inc (hl)
        ld a,(NOS_SHOW)         ; the other canister comes out
        xor 1
        ld (NOS_SHOW),a
        call nos_place
        call inv_draw
        ld a,M_NOS
        jp msg_say

nos_fire:                       ; SPACE: one canister, if racing and you have one
        ld a,(race_on)
        or a
        ret z
        ld a,(you_done)
        or a
        ret nz
        ld a,(BOOST_T)
        or a
        ret nz
        ld hl,INV+2             ; your last full slot
        ld b,3
nf_1:
        ld a,(hl)
        or a
        jr nz,nf_2
        dec hl
        djnz nf_1
        ret                     ; none
nf_2:
        ld (hl),0
        ld a,BOOST_FR
        ld (BOOST_T),a
        call inv_draw
        ld a,M_BOOST
        jp msg_say
