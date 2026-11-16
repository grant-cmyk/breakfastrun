; The place plate's code (see below), kept after the page-aligned tables: there is room here
; and none before them (racer.asm includes this after faces.asm).
; ---------------------------------------------------------------------
; THE PLACE PLATE (Grant, 14 Nov 2026: "positional information into the game area, its easier
; for the player to see" - a small solid plate with rounded corners INSIDE the window, top
; right corner; P1 2/3 - P and your place ("P1 or P2 or P3 instead of 3rd or 1st"), a space,
; the lap - and under it your lap's time so far, all in the small 3 x 5 figures; and a quick message on a second plate below it - FINAL
; LAP! for its 3 seconds: "3 is good build 3"). Into the buffer each picture, like the gauge.
; A plate is FILLED (pl_fill: its rows by how near the top or bottom they are - clear, two
; rounding rows, solid), then its letters are CUT OUT a byte-wide column at a time (pl_cut).
; Not while the start lights hang there.
; ---------------------------------------------------------------------
; SPEED (the same evening): the plate is COMPOSED once, into pl_bmp (PL_W bytes a row, PL_H rows),
; when your place or lap changes (pl_static, in the slow memory under 0x8000 with the other
; parts that run rarely); each picture only the time's figures are done again there, and the
; whole of pl_bmp is copied into the buffer. It was 12,000 T a picture built from nothing.
PL_B    equ BUF + 1*32 + 2*0x100 + 21   ; the place plate: buffer row 10 (window line 2), bytes 19-23 (the
                                ; window's last 40 pixels), 18 rows: the plate itself is 29 x 16, 6
                                ; pixels in from the window's right edge and 3 down from its top
                                ; (Grant, 14 Nov 2026: "make the P1 smaller, so that the display can be
                                ; a bit smaller ... shift it more towards the corner and have a smaller
                                ; blue border around it")
PL_M    equ BUF + 3*32 + 5*0x100 + 20   ; the message's: buffer row 29, bytes 18-23, 13 rows
PL_MT   equ BUF + 4*32 + 1*0x100 + 20   ; ... its letters' first row: buffer row 33
FL_SRC  equ 0x5000 + 6*32 + 16          ; the FINAL LAP bubble as kept: screen rows 22-23, columns 16-25
FL_DST  equ BUF + 0x1000 + 1*32 + 8     ; ... and in the window: buffer rows 136-151, bytes 8-17 (screen columns 7-16)
; (PL_W and PL_H, pl_bmp's bytes a row and rows: in racer.asm, before the first use)
pl_draw:
        call cf_blink           ; he blinks (clothmini.asm); then fl_draw: the crew chief's bubble, if he is talking (even under the start lights)
        ld a,(lt_on)
        or a
        ret nz
        inc a
        ld (pl_lin),a           ; (the letters go into pl_bmp: its rows are PL_W bytes apart)
        ld a,(position)         ; your place (1 before the race) and lap (1 behind the line)
        or a
        jr nz,pd_1
        inc a
pd_1:
        ld b,a
        ld a,(cars+C_LAPS)
        or a
        jr nz,pd_2
        inc a
pd_2:
        cp LAPS+1               ; (over the line at the end: still the last lap, not "4/3" -
        jr c,pd_2b              ; Grant, 15 Nov 2026)
        dec a
pd_2b:
        ld c,a
        ld hl,(pl_key)          ; changed? the plate afresh
        or a
        sbc hl,bc
        jr z,pd_same
        call pl_static
        jr pd_time
pd_same:                        ; the figures are cut afresh only once the time has moved on a tenth
        ld hl,(race_time)       ; of a second (5 frames) since they last were - about every other
        ld de,(cars+C_LST)      ; picture (the speed test of 15 Nov 2026: 2,000 T a picture saved)
        or a
        sbc hl,de
        ld de,(pl_tl)
        or a
        sbc hl,de
        ld a,h
        or a
        jr nz,pd_time           ; (a new lap: the time went back)
        ld a,l
        cp 5
        jr c,pd_blit
pd_time:
        ld hl,pl_bmp+10*PL_W+1  ; your lap's time so far, small: m:ss.t - its 5 rows solid again,
        ld b,5
pd_3:
        ld (hl),0xFF
        inc hl
        ld (hl),0xFF
        inc hl
        ld (hl),0xFF
        inc hl
        inc hl
        inc hl
        djnz pd_3
        ld hl,(race_time)       ; then the figures cut out
        ld de,(cars+C_LST)
        or a
        sbc hl,de
        ld (pl_tl),hl
        call time_fmt
        ld a,(time_txt)
        call pd_d
        ld c,10                 ; m and :
        ld hl,pl_bmp+10*PL_W+1
        call pl_pair
        ld a,(time_txt+3)
        call pd_d
        ld c,a
        ld a,(time_txt+2)
        call pd_d               ; s s
        ld hl,pl_bmp+10*PL_W+2
        call pl_pair
        ld a,(time_txt+5)
        call pd_d
        ld c,a
        ld a,11                 ; . and t
        ld hl,pl_bmp+10*PL_W+3
        call pl_pair
pd_blit:
        ld hl,pl_bmp            ; and the plate into the buffer
        ld de,PL_B
        ld b,PL_H
pd_4:
        ld c,255                ; (so the LDIs leave B, the row count, alone)
        ldi
        ldi
        ldi
        ldi
        ldi
        ld a,e                  ; DE: back to the row's first byte, and a line down (the buffer
        sub PL_W                ; is laid out like the screen)
        ld e,a
        inc d
        ld a,d
        and 7
        jr nz,pd_5
        ld a,e
        add a,32
        ld e,a
        ld a,d
        sub 8
        ld d,a
pd_5:
        djnz pd_4
        ret
fl_draw:
        ld a,(msg_timer)        ; a crew message - the chief and his speech bubble, at the foot of the window,
        or a                    ; while its 3 seconds run (Grant, 15 Nov 2026: "a pit crew message in the play
        ret z                   ; area ... a small pitcrew face and speech bubble"; "B small letters"; the old
        ld hl,FL_SRC            ; strip under the window went unseen - "the player is focused on the game
        ld de,FL_DST            ; area"). The picture - his face (screen_once), the message's lines (msg_say) -
        call fl_8               ; is kept on the SCREEN, under the window, in cells whose ink is
fl_8:                           ; their paper's colour, so it does not show there. Each picture its 10 x 2
        ld b,8                  ; cells are copied into the window's (rows 17-18, columns 7-16: white, set
fl_1:                           ; by msg_final).
        ld c,255
        rept 10
        ldi
        endm
        ld a,l
        sub 10
        ld l,a
        ld a,e
        sub 10
        ld e,a
        inc h
        inc d
        djnz fl_1
        ld a,l                  ; the next character row, in the screen and in the buffer alike
        add a,32
        ld l,a
        ld a,e
        add a,32
        ld e,a
        ld a,h
        sub 8
        ld h,a
        ld a,d
        sub 8
        ld d,a
        ret
pl_pair:                        ; two small figures cut out of the column at HL: number A in bits 7-5,
        push hl                 ; number C beside it in bits 3-1
        call pd_g
        ld a,c
        ld b,d
        ld c,e                  ; BC -> the left one
        call pd_g               ; DE -> the right one
        pop hl
        ld a,5
pp_1:
        push af
        ld a,(de)               ; the right one, moved over to bits 3-1
        rrca
        rrca
        rrca
        rrca
        ld (pp_2+1),a
        ld a,(bc)
pp_2:   or 0
        xor (hl)
        ld (hl),a
        inc bc
        inc de
        call pl_down
        pop af
        dec a
        jr nz,pp_1
        ret
pd_d:                           ; a character of the time -> its figure (a space is a 0)
        sub '0'
        ret nc
        xor a
        ret
pd_g:                           ; DE -> small figure A (pl_g + 5 A)
        ld e,a
        add a,a
        add a,a
        add a,e
        add a,pl_g AND 255
        ld e,a
        ld a,0
        adc a,pl_g/256
        ld d,a
        ret
pl_down:                        ; HL: the next row down - in pl_bmp (pl_lin 1: 6 bytes on) or in the
        ld a,(pl_lin)           ; buffer (0: laid out like the screen)
        or a
        jr z,pw_1
        ld a,l
        add a,PL_W
        ld l,a
        ret nc
        inc h
        ret
pw_1:
        inc h
        ld a,h
        and 7
        ret nz
        ld a,l
        add a,32
        ld l,a
        ld a,h
        sub 8
        ld h,a
        ret

; ---------------------------------------------------------------------
; THE VIEW LEADS THE CAR (Grant, 14 Nov 2026: "have the car position in the screen adjust to
; allow to see ahead more on the track"). lead_x, lead_y: how far the camera is ahead of the
; car, in pixels, signed. Each aims at the car's speed that way x 12 / 256 (21 at top speed),
; held to LEAD_X / LEAD_Y, and moves LEAD_STEP pixels a picture at most - it slides, never jumps.
; ---------------------------------------------------------------------
LEAD_X    equ 20                ; (halved, Grant 14 Nov 2026: "half on each - its a little too much")
LEAD_Y    equ 16
LEAD_STEP equ 2
cam_lead:
        ld hl,(cars+C_VX)
        ld c,LEAD_X
        ld de,lead_x
        call cl_one
        ld hl,(cars+C_VY)
        ld c,LEAD_Y
        inc de
cl_one:
        add hl,hl
        add hl,hl
        ld a,h                  ; (x 4, kept in A:B)
        ld b,l
        add hl,hl
        push de
        ld d,a
        ld e,b
        add hl,de               ; x 12: H = the lead to aim at
        pop de
        ld a,h
        or a
        jp m,cl_neg
        cp c
        jr c,cl_aim
        ld a,c
        jr cl_aim
cl_neg:
        neg
        cp c
        jr c,cl_n2
        ld a,c
cl_n2:
        neg
cl_aim:
        ld b,a                  ; B = the aim; (DE) = the lead now
        ld a,(de)
        sub b
        ret z
        jp m,cl_up
        cp LEAD_STEP+1
        jr c,cl_set
        ld a,(de)
        sub LEAD_STEP
        ld (de),a
        ret
cl_up:
        cp 256-LEAD_STEP
        jr nc,cl_set
        ld a,(de)
        add a,LEAD_STEP
        ld (de),a
        ret
cl_set:
        ld a,b
        ld (de),a
        ret
lead_x:   db 0
lead_y:   db 0

; THE TITLE'S FIVE CARS (Grant, 15 Nov 2026: "are you able to have 5 cars racing around the title
; screen"): the same lap of the edge (title3.asm, a_runs), 77 steps apart. Each has 14 bytes at
; t_blk - the title's a_x .. a_kc - copied in, moved and drawn, and copied back.
tc_init:
        ld hl,t_blk             ; all 70 bytes 0 (nothing drawn yet, no drift)
        ld de,t_blk+1
        ld bc,69
        ld (hl),b
        ldir
        ld ix,t_blk
        ld hl,tc_tab
        ld b,NCARS
tci_1:
        ld a,(hl)
        ld (ix+1),a             ; x
        inc hl
        ld a,(hl)
        ld (ix+3),a             ; y
        inc hl
        ld a,(hl)
        ld (ix+4),a             ; the way it is going
        inc hl
        ld a,(hl)
        ld (ix+6),a             ; steps left of this part of the lap
        inc hl
        ld a,(hl)               ; ... and the part after it
        inc hl
        add a,(TD + a_runs_src - td_src + 3) AND 255
        ld (ix+8),a
        ld a,0
        adc a,(TD + a_runs_src - td_src + 3) / 256
        ld (ix+9),a
        ld de,14
        add ix,de
        djnz tci_1
        ret
tc_step:
        xor a
tcs_1:
        ld (t_drv),a
        ld l,a                  ; HL = t_blk + 14 x the car
        add a,a
        add a,a
        add a,a
        add a,a
        sub l
        sub l
        add a,t_blk AND 255
        ld l,a
        ld a,0
        adc a,t_blk/256
        ld h,a
        push hl
        ld de,a_x
        ld bc,14
        ldir
        call a_step
        call ad_draw
        pop de
        ld hl,a_x
        ld bc,14
        ldir
        ld a,(t_drv)
        inc a
        cp NCARS
        jr nz,tcs_1
        ret


; YL_BEST: the best of your laps this race: its row (19-21) bright yellow
yl_best:
        ld ix,you_laps
        ld bc,0xFFFF            ; BC = the best so far, E = which lap, D = the lap looked at
        ld de,0
yb_1:
        ld l,(ix+0)
        ld h,(ix+1)
        ld a,h
        or l
        jr z,yb_2
        push hl
        or a
        sbc hl,bc
        pop hl
        jr nc,yb_2
        ld b,h
        ld c,l
        ld e,d
yb_2:
        inc ix
        inc ix
        inc d
        ld a,d
        cp LAPS
        jr nz,yb_1
        ld a,e
        add a,19
        ld b,a
        ld c,26
        ld de,0x0106
        ld a,0x70
        jp set_attrs

; ---------------------------------------------------------------------
; JIN_START: a new race - the start jingle (unless held off: jin_on 0xFF), then auto_go starts the
; lights. Kettle's On on the Spectrum's own speaker, but not as plain beeps (Grant, 15 Nov 2026:
; "add some sophistication to the sound, make it almost trancy with a background to it"): TWO
; voices at once - the tune and a bass under it - by a loop that counts both down and puts out
; either; a KICK on every beat (six flips, further and further apart: a thump) and a TICK of
; noise half way to the next. Nothing else runs while it plays; interrupts are off, for its timing.
; src/jingle.asm (tools/make_music_ay.py) has the notes and the loop's counts.
; ---------------------------------------------------------------------
jin_flag:                       ; the chequered flag's jingle (podium): "Spilt Milk" ...
        ld hl,jc_a              ; (the two changed places on 15 Nov 2026 - Grant: "switch the chequered flag music
        jr jin_go               ; with the start music"; jingle.asm's own comments still say which it was written for)
jin_start:                      ; ... and the start's, "Second Helpings": each its own tune, step and bass (src/jingle.asm)
        ld hl,jc_b
jin_go:
        ld a,(jin_on)
        inc a
        ret z
        ld de,jc
        ld bc,10
        ldir
        di
        push ix
        ld hl,(jc)
        xor a
jb_1:
        call jb_key             ; the step, counted from 0, kept (jb_n+1) - and a key skips the jingle (jb_key: at the
                                ; program's very end, so that nothing here moves - see the note there)
        ld a,(hl)
        inc hl
        cp 255
        jp z,jb_end
        push hl
        cp 254                  ; a rest: the tune's voice does not flip this step (the XOR's 16 is 0)
        ld e,a
        ld a,16
        jr nz,jb_r
        xor a
        ld e,a
jb_r:
        ld (jb_x+1),a
        ld d,0
        ld hl,(jc+2)
        add hl,de
        ld h,(hl)               ; H = the tune's period
jb_n:   ld a,0
        and 3
        ld ix,(jc+4)
        ld bc,(jc+8)            ; C = the low bass's period, B = the high one's
        ld l,c
        jr z,jb_kick            ; the beat: the kick, the low bass
        ld l,b
        rra
        jr c,jb_tone            ; steps 1 and 3: the high bass
        ld l,c                  ; step 2: the low bass again, after a tick of noise
        ld b,48
jb_hat:
        ld a,r
        and 16
        or 6
        out (254),a
        djnz jb_hat
        jr jb_tone
jb_kick:
        ld ix,(jc+6)
        ld b,6
jb_k1:
        ld a,b                  ; a flip ...
        rra
        sbc a,a
        and 16
        or 6
        out (254),a
        ld a,7                  ; ... then 1, 2, .. 6 waits of 2,500 T: the pitch falls
        sub b
        ld c,a
jb_k2:
        ld de,96
jb_k3:
        dec de
        ld a,d
        or e
        jr nz,jb_k3
        dec c
        jr nz,jb_k2
        djnz jb_k1
jb_tone:
        ld d,6                  ; D, E = each voice's speaker bit (and the border's yellow)
        ld e,0
        ld b,h                  ; B, C = each voice's count down to its next flip
        ld c,l
jb_t:
        dec b
        jr nz,jb_t1
        ld b,h
        ld a,d
jb_x:   xor 16
        ld d,a
jb_t1:
        dec c
        jr nz,jb_t2
        ld c,l
        ld a,e
        xor 16
        ld e,a
jb_t2:
        ld a,d
        or e
        out (254),a
        dec ix
        ld a,ixh
        or ixl
        jr nz,jb_t
        pop hl
        ld a,(jb_n+1)
        inc a
        jp jb_1
jb_end:
        pop ix
        jr jb_x2
jc:     defs 10                 ; the jingle being played: its tune, periods, turns a step and a beat's, bass low and high
jb_x2:
        xor a
        ld (jin_on),a
        ei
        ret
