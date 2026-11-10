; ---------------------------------------------------------------------
; THE DRIVER STRIP (under the window): you, your inventory, the crew chief's
; radio, the crew chief (Grant, 10 Nov 2026). Its fixed picture is drawn
; once (screen_once). Here: the inventory, the radio wave while the chief
; talks, and his message, typed out in the 3 x 5 letters a few at a time so
; no picture runs late. strip_tick runs on 2 pictures in 4: one types, the
; other moves the wave.
; ---------------------------------------------------------------------
MSG_P   equ BUFC+128            ; the next letter (2)
MSG_ST  equ BUFC+130            ; 0 quiet, 1-2 wiping the box, 3 typing, 4 shown
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
        ld a,1
        ld (MSG_ST),a           ; wipe the box,
        ld (WAVE_T),a           ; and the wave goes flat
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
        ld (MSG_ST),a
        ld a,9                  ; ~2 s of wave (4 updates a second)
        ld (WAVE_T),a
        ld a,48                 ; and ~3 s before a nag may follow
        ld (COOL),a
        ret

; STRIP_TICK: renders AND 3 = 1: wipe, then type; = 3: the wave
strip_tick:
        ld a,(renders)
        and 2
        jp nz,wave_tick
        ld a,(MSG_ST)
        cp 1
        jr z,st_wipe1
        cp 2
        jr z,st_wipe2
        cp 3
        ret nz
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
st_wipe1:                       ; the box's lines 1-2 (rows 171-181)
        ld b,171
        ld c,11
        call box_wipe
        ld a,2
        ld (MSG_ST),a
        ret
st_wipe2:                       ; line 3 (rows 182-188): then type, if any
        ld b,182
        ld c,7
        call box_wipe
        ld hl,(MSG_P)
        ld a,h
        or l
        ld a,0
        jr z,stw_1
        ld a,171
        ld (MSG_Y),a
        call line_x
        ld a,3
stw_1:
        ld (MSG_ST),a
        ret

box_wipe:                       ; B = first row, C = rows: the box's inside
        push bc                 ; (x 89-150: its left and right edge bytes
        ld c,BOX_X-1            ; keep their border pixel)
        call scr_addr
        ld a,(hl)
        and 0x80
        ld (hl),a
        inc l
        xor a
        ld b,6
bw_1:
        ld (hl),a
        inc l
        djnz bw_1
        ld a,(hl)
        and 0x01
        ld (hl),a
        pop bc
        inc b
        dec c
        jr nz,box_wipe
        ret

line_x:                         ; MSG_P at a line: MSG_X = its centred start
        ld hl,(MSG_P)
        ld b,0
lx_1:
        ld a,(hl)
        or a
        jr z,lx_2
        cp '|'
        jr z,lx_2
        inc b
        inc hl
        jr lx_1
lx_2:
        ld a,b                  ; x = BOX_X + (62 - (4n - 1)) / 2
        add a,a
        add a,a
        dec a
        neg
        add a,62
        srl a
        add a,BOX_X
        ld (MSG_X),a
        ret

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
        ld a,(WAVE_T)
        or a
        ret z
        dec a
        ld (WAVE_T),a
        ld b,WAVE_MID-3         ; wipe its 7 rows (4 bytes from x 104)
wt_1:
        push bc
        ld c,104
        call scr_addr
        xor a
        ld (hl),a
        inc l
        ld (hl),a
        inc l
        ld (hl),a
        inc l
        ld (hl),a
        pop bc
        inc b
        ld a,b
        cp WAVE_MID+4
        jr nz,wt_1
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

; INV_DRAW: each slot whose item changed: its icon (or empty)
inv_draw:
        ld hl,INV
        ld de,INV_SH
        ld c,32                 ; slot 0 at x 32 (columns 4-5), then 48, 64
id_1:
        ld a,(de)
        cp (hl)
        jr z,id_next
        ld a,(hl)
        ld (de),a
        push hl
        push de
        push bc
        ld b,170                ; the icon's rows: 170.. (centred in 169-182)
        ld e,a                  ; E = the item
        ld hl,NOS_ICON
id_row:
        push bc
        push hl
        push de
        call scr_addr           ; HL = the slot's left byte (C = its x)
        ex de,hl
        pop bc                  ; C = the item
        pop hl
        ld a,(de)               ; keep the frame: bit 7 left, bit 0 right
        and 0x80
        bit 0,c
        jr z,id_e1
        or (hl)
id_e1:
        ld (de),a
        inc hl
        inc e
        ld a,(de)
        and 0x01
        bit 0,c
        jr z,id_e2
        or (hl)
id_e2:
        ld (de),a
        inc hl
        ld e,c
        pop bc
        inc b
        ld a,b
        cp 170+NOS_ROWS
        jr nz,id_row
        pop bc
        pop de
        pop hl
id_next:
        inc hl
        inc de
        ld a,c
        add a,16
        ld c,a
        cp 32+48
        jr nz,id_1
        ret

; STRIP_TRIGGERS: what the chief says (each picture, racing)
strip_triggers:
        ld a,(race_on)
        or a
        ret z
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
        ld b,74                 ; a frame: top and bottom lines
        call rb_line
        ld b,109
        call rb_line
        ld b,75                 ; the sides
rb_side:
        push bc
        ld c,3*8
        call scr_addr
        set 5,(hl)
        ld a,l
        add a,17
        ld l,a
        set 2,(hl)
        pop bc
        inc b
        ld a,b
        cp 109
        jr nz,rb_side
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
rb_line:
        ld c,3*8
        call scr_addr
        ld (hl),0x3F
        ld b,16
rbl_1:
        inc l
        ld (hl),0xFF
        djnz rbl_1
        inc l
        ld (hl),0xFC
        ret
