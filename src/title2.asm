; =====================================================================
; THE TITLE SCREEN'S CAR (see title.asm): one of the game's own cars driven
; round the cloth "stage" - on, a circle or a figure of eight with its nose
; turned into the bend, and off. In the program (above 0x8000) because it is
; drawn against the clock: put back what was under the old picture, then draw
; the new one, before the TV's beam gets down to the stage.
; The car's frames are the race's (big_tab: 16 headings a car; a row is three
; (mask, ink) pairs, the third empty for the small cars), shifted with the
; race's shift tables (TAB_HI). Cut off at the cloth's edges, byte by byte.
; =====================================================================

; A_SHOW: the old picture off (what was under it back), the new one on
a_show:
        ld ix,a_sav
        ld a,(a_on)
        or a
        jr z,ad_draw
        ld b,a
        ld a,(a_oy)
ar_row:
        push bc
        push af
        call a_radr
        jr nc,ar_next
        ld b,3
ar_b:
        ld a,c
        cp 14
        jr nc,ar_s
        ld a,(ix+0)
        ld (hl),a
        inc ix
ar_s:
        inc l
        inc c
        djnz ar_b
ar_next:
        pop af
        inc a
        pop bc
        djnz ar_row
ad_draw:
        call a_marks
        ld ix,a_sav
        ld a,(t_drv)            ; the frame: big_tab[car * 16 + heading]
        add a,a
        add a,a
        add a,a
        add a,a
        ld l,a
        ld a,(a_h)
        or l
        ld l,a
        ld h,0
        add hl,hl
        add hl,hl
        ld de,big_tab
        add hl,de
        ld e,(hl)
        inc hl
        ld d,(hl)
        inc hl
        ld a,(a_y+1)
        add a,(hl)
        ld (a_oy),a             ; its first row
        inc hl
        ld a,(hl)
        ld (a_on),a             ; its rows
        ld a,(a_x+1)
        push de
        exx
        pop de                  ; DE' = the frame's rows
        neg                     ; the shift: (-x) AND 7 to the left, from the byte before
        and 7
        add a,a
        add a,TAB_HI
        ld h,a                  ; H' = that shift's tables
        exx
        ld a,(a_x+1)            ; the first byte's column on the cloth: (x + 7) / 8 - 1 - 4
        add a,7
        rrca
        rrca
        rrca
        and 31
        sub 5
        ld (a_k0+1),a
        ld a,(a_on)
        ld b,a
        ld a,(a_oy)
ad_row:
        push bc
        push af
        call a_radr
        exx
        jr c,ad_vis
        ld a,e                  ; a row off the cloth: past its 6 bytes
        add a,6
        ld e,a
        jr nc,ad_o
        inc d
ad_o:
        exx
        jr ad_next
ad_vis:
        ld bc,0                 ; B', C' = the mask's and the ink's bits carried on
        exx                     ; from the byte before
        ld b,3
ad_b:
        exx
        ld a,(de)
        inc de
        ld l,a
        ld a,(hl)               ; the mask here: this byte's left part ...
        or b                    ; ... and the last one's right part
        inc h
        ld b,(hl)
        dec h
        cpl
        ex af,af'
        ld a,(de)
        inc de
        ld l,a
        ld a,(hl)               ; the ink, the same way
        or c
        inc h
        ld c,(hl)
        dec h
        exx
        ld e,a
        ld a,c
        cp 14                   ; on the cloth (bytes 0..13)?
        jr nc,ad_s
        ld a,(hl)
        ld (ix+0),a             ; keep what is there
        inc ix
        ex af,af'
        and (hl)                ; a hole the car's shape, then the car
        or e
        ld (hl),a
ad_s:
        inc l
        inc c
        djnz ad_b
ad_next:
        pop af
        inc a
        pop bc
        djnz ad_row
        ret

; A_RADR: A = a row (+ 32). Carry: it is on the cloth - HL = the screen address
; of the car's first byte in it, C = that byte's column on the cloth (signed)
a_radr:
        sub 32
        cp 96
        ret nc
        add a,40
        ld b,a
        ld c,16
        call scr_addr
a_k0:   ld c,0
        ld a,c
        add a,l
        ld l,a
        scf
        ret

; A_STEP: the car's next place. A run is parts: so many steps at a turn a step.
; It moves 2 pixels a step the way it is going; the picture's nose is turned
; further into the bend (the drift), up to 56 degrees, eased in and out.
a_step:
        ld hl,a_n
        ld a,(hl)
        or a
        jr nz,as_1
        ld hl,(a_scr)
        ld a,(hl)
        or a
        jr z,as_end
        inc hl
        ld (a_n),a
        ld a,(hl)
        inc hl
        ld (a_om),a
        ld (a_scr),hl
        ld hl,a_n
as_1:
        dec (hl)
        ld a,(a_om)
        ld e,a
        ld hl,a_phi
        add a,(hl)
        ld (hl),a
        ld hl,a_dr
        ld a,e
        or a
        jr z,as_dec
        add a,(hl)              ; turning: the drift grows, to 40 (of 256) at most
        ld d,a
        add a,40
        cp 81
        jr nc,as_d1
        ld (hl),d
        jr as_d1
as_dec:
        ld a,(hl)               ; straight: it dies away
        sra a
        sra a
        neg
        add a,(hl)
        ld (hl),a
as_d1:
        ld a,(a_phi)
        add a,(hl)
        add a,8
        rrca
        rrca
        rrca
        rrca
        and 15
        ld (a_h),a
        ld a,(a_phi)
        rrca
        rrca
        push af
        call a_vel
        ex de,hl
        ld hl,(a_x)
        add hl,de
        ld (a_x),hl
        pop af
        add a,48                ; (- cos)
        call a_vel
        ex de,hl
        ld hl,(a_y)
        add hl,de
        ld (a_y),hl
        ret
as_end:                         ; the run is over: the next driver
        ld hl,t_drv
        ld a,(hl)
        inc a
        cp NCARS
        jr c,as_e1
        xor a
as_e1:
        ld (hl),a
        jp a_new
a_vel:                          ; A = heading 0..63 -> HL = 2 x its sine, 8.8
        call trig
        ld l,c
        ld h,0
        add hl,hl
        add hl,hl
        dec b
        ret nz
        xor a
        sub l
        ld l,a
        sbc a,a
        sub h
        ld h,a
        ret
