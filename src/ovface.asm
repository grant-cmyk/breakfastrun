; =====================================================================
; OVF - THE FACE OF WHO YOU PASSED, OR WHO PASSED YOU (OVF=1, the group C tape; Grant, 23 Nov 2026: "if you overtake or are
; overtaken by a player, then their face shows up top right in the gameplay as either happy or sad a short animation between
; frames and then it disappears").
;   - Each picture (ov_draw, from draw_all after the place plate): your place against the last picture's. Better: the
;     driver now just behind you - you passed him - shows SAD; worse: the driver now just ahead - he passed you - HAPPY.
;   - His face in a framed box just under the place plate, top right of the window: his everyday face and the sad (or
;     happy) one by turns, every OV_FR pictures, for OV_T pictures (about 1.6 seconds); then it is gone. The window is drawn
;     afresh each picture, so nothing need be put back. A new pass starts it again with the new face.
;   - The faces: faces (16 rows of 2 bytes a driver) and faces_mood's happy and sad rows (tools/make_faces.py).
; =====================================================================
OV_T    equ 20                  ; pictures it shows (12.5 a second)
OV_FR   equ 4                   ; pictures a look lasts (a power of two)
        if OPT_BIGPL
OV_B    equ BUF + 5*32 + 0*0x100 + 23   ; (BIGPL: buffer row 40, under the plate's 28 rows)
        else
OV_B    equ BUF + 3*32 + 6*0x100 + 23   ; buffer row 30 (window line 22, under the plate's 18 rows), bytes 23-25
        endif

ov_draw:
        ld a,(race_on)
        or a
        jr z,ov_rst
        ld a,(you_done)         ; (over the line: nothing new)
        or a
        jr nz,ov_tick
        ld a,(position)
        ld hl,ov_last
        cp (hl)
        jr z,ov_tick
        ld b,(hl)               ; B = the place you had
        ld (hl),a
        ld e,a
        ld d,0
        ld hl,order-1
        add hl,de               ; (HL: you, in the order)
        ld c,2                  ; better: the one just behind you, sad
        cp b
        jr c,ov_g
        dec hl                  ; worse: the one just ahead of you, happy
        ld c,1
        jr ov_s
ov_g:   inc hl
ov_s:   ld a,(hl)
        ld (ov_kind),a
        ld a,c
        ld (ov_mood),a
        ld a,OV_T
        ld (ov_t),a
        ld a,0xFF
        ld (ov_ph),a            ; (its picture made afresh)
ov_tick:
        ld hl,ov_t
        ld a,(hl)
        or a
        ret z
        dec (hl)
        and OV_FR               ; which look: everyday or the mood
        ld hl,ov_ph
        cp (hl)
        jr z,ov_blit
        ld (hl),a
        or a
        ld a,(ov_mood)
        jr nz,ov_mk
        xor a
ov_mk:  call ov_make
ov_blit:
        ld hl,ov_bmp            ; the box into the buffer (laid out like the screen)
        ld de,OV_B
        ld b,18
ovl_1:  ld c,255                ; (so the LDIs leave B alone)
        ldi
        ldi
        ldi
        dec de
        dec de
        dec de
        inc d
        ld a,d
        and 7
        jr nz,ovl_2
        ld a,e
        add a,32
        ld e,a
        ld a,d
        jr c,ovl_2
        sub 8
        ld d,a
ovl_2:  djnz ovl_1
        ret
ov_rst: ld a,(position)         ; before the green light: where you are, and nothing showing
        ld (ov_last),a
        xor a
        ld (ov_t),a
        ret

ov_make:                        ; A = the look (0 everyday, 1 happy, 2 sad): the driver ov_kind's face, in its box, in ov_bmp
        ld (ov_m),a
        ld a,(ov_kind)
        add a,a
        add a,a
        add a,a
        add a,a
        add a,a
        ld e,a
        ld d,0
        ld hl,faces
        add hl,de
        ld de,ov_face
        ld bc,32
        ldir
        ld a,(ov_m)
        or a
        jr z,ovm_x
        ld a,(ov_kind)          ; the look's rows: list kind x 3 + look of faces_mood
        ld b,a
        add a,a
        add a,b
        ld hl,ov_m
        add a,(hl)
        ld b,a
        ld hl,faces_mood
ovm_s:  ld a,b
        or a
        jr z,ovm_ap
ovm_k:  ld a,(hl)
        inc hl
        cp 0xFF
        jr z,ovm_n
        inc hl
        inc hl
        jr ovm_k
ovm_n:  dec b
        jr ovm_s
ovm_ap: ld a,(hl)               ; each: its row, its 2 bytes
        cp 0xFF
        jr z,ovm_x
        inc hl
        add a,a
        ld e,a
        ld d,0
        push hl
        ld hl,ov_face
        add hl,de
        ex de,hl
        pop hl
        ldi
        ldi
        jr ovm_ap
ovm_x:  ld hl,ov_bmp            ; the box: a line round it, the face 4 px in
        call ov_line
        ld de,ov_face
        ld b,16
ovb_1:  ld a,(de)
        ld c,a                  ; C = the face's left byte
        inc de
        ld a,(de)
        inc de
        push de
        ld e,a                  ; E = its right byte
        ld a,c
        rrca
        rrca
        rrca
        rrca
        and 0x0F
        or 0x80
        ld (hl),a
        inc hl
        ld a,c
        rlca
        rlca
        rlca
        rlca
        and 0xF0
        ld d,a
        ld a,e
        rrca
        rrca
        rrca
        rrca
        and 0x0F
        or d
        ld (hl),a
        inc hl
        ld a,e
        rlca
        rlca
        rlca
        rlca
        and 0xF0
        or 0x01
        ld (hl),a
        inc hl
        pop de
        djnz ovb_1
ov_line:
        ld (hl),0xFF
        inc hl
        ld (hl),0xFF
        inc hl
        ld (hl),0xFF
        inc hl
        ret

ov_last: db 0                   ; your place, the last picture
ov_t:    db 0                   ; pictures left to show
ov_ph:   db 0                   ; the look showing (its bit of ov_t)
ov_kind: db 0                   ; whose face
ov_mood: db 0                   ; 1 happy, 2 sad
ov_m:    db 0
ov_face: defs 32
ov_bmp:  defs 3*18              ; (in the program: at TS, 0x5B00, it ran into STRIP3's row lists at 0x5B16 - the O's of two
                                ; map rows went from the second race on: Grant, 23 Nov 2026, "many of the inside loops ... are not showing")
