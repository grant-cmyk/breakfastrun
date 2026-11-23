; =====================================================================
; PICK - CHOOSE YOUR CAR (PICK=1, the group C tape; Grant, 23 Nov 2026: "when you click 1, a popup appears asking you to
; choose your car. You press left and right to select cars"; "go ahead and build the car selector"). The title's 1 opens a
; card over the title; left and right go through the cars of tools/pick_cars.txt, round and round; accelerate (or SPACE)
; races in the one shown. "The car has default settings": nothing to adjust here.
; What the car you choose brings (each car's record, pick_data.asm, made by tools/make_data.py and make_cards.py):
;   - its picture, YOUR version of it (tools/car_art_studio.txt) - unpacked into kind 0's frames (pk_buf) and table rows
;   - its card: YOUR card row's slide, ACCEL-to-SPEED speed and two pushes (as the racer's: 45/64 of the card's slide, the
;     pushes YOU_HARD less) - su_apply reads pk_sl, pk_ka, pk_ks; the damage a piece of its armour takes; its weight class
; A computer driver keeps his own car: if you take his, there are two on the road, yours in your version.
; The choice stays for the next race. The words and numbers shown: the record's ratings (driver_cards.txt) and words.
; =====================================================================
        include "pick_cards.asm"        ; PK_n_ numbers of each car's card (tools/make_cards.py)
PK_TMP  equ BUF+0x0F62          ; the car's nose-up picture, 16 rows of 2 bytes, to draw twice the size (as the choose screen's)
PK_PAPER equ 0x78               ; black on bright white: the card
PK_BLUE equ 0x79                ; blue on bright white
pk_buf  equ bf_0_0              ; your car's frames (bigcars.asm: the racer's, then pk_pad)

pk_sel: db 0                    ; the car chosen (0: the racer)
pk_sl:  dw YOU_SL               ; YOUR card row's slide, and an eighth of it (a level of GRIP), its two pushes: su_apply
pk_s8:  dw YOU_SL/8
pk_ka:  db YOU_KA AND 255
pk_ks:  db YOU_KS AND 255
pk_col: db 0x50                 ; the car's colour, its ratings (-> 4 bytes of its record)
pk_rat: dw 0

pick:                           ; (the title: 1 is down)
        call k_up
        ld bc,3*256+3           ; the card: rows 3-22, columns 3-28, a black line round it
        ld de,20*256+26
        push bc
        push de
        call clear_cells
        pop de
        pop bc
        ld a,PK_PAPER
        call set_attrs
        call pk_frame
        ld bc,4*256+4           ; CHOOSE YOUR CAR, white on red
        ld de,1*256+24
        ld a,0x57
        call set_attrs
        ld hl,pk_t_head
        ld b,4
        call pk_ctr
        ld bc,21*256+4          ; the keys, in blue
        ld de,1*256+24
        ld a,PK_BLUE
        call set_attrs
        ld hl,pk_t_keys
        ld b,21
        call pk_ctr
pk_show:
        call pk_load            ; the car: its picture and numbers into your car
        ld bc,6*256+4           ; what changes: rows 6-19
        ld de,14*256+24
        push bc
        push de
        call clear_cells
        pop de
        pop bc
        ld a,PK_PAPER
        call set_attrs
        ld bc,11*256+4          ; (its line in blue)
        ld de,1*256+24
        ld a,PK_BLUE
        call set_attrs
        ld a,(pk_sel)           ; which of how many: 3/7
        add a,'1'
        ld hl,pk_cnt
        ld (hl),a
        ld bc,6*256+24
        ld a,PK_BLUE
        ld de,1*256+3
        push hl
        call set_attrs
        pop hl
        ld bc,6*256+24
        call print_at
        ld hl,pk_t_lr           ; < and >
        ld bc,7*256+12
        call print_at
        ld hl,pk_t_lr+2
        ld bc,7*256+19
        call print_at
        call pk_pic             ; the car, nose up, twice the size, on its colour
        xor a                   ; its name, its line
        call pk_word
        ld b,10
        call pk_ctr
        ld a,1
        call pk_word
        ld b,11
        call pk_ctr
        ld hl,(pk_rat)          ; ACCEL, SPEED, GRIP, ARMOUR: ten squares each, lit up to the rating
        ld b,13
        ld de,pk_t_rat
        ld c,0
pks_r:  push bc
        push de
        push hl
        ex de,hl                ; the label
        push bc
        ld c,5
        call print_at
        pop bc
        pop hl                  ; the rating
        push hl
        ld a,(hl)
        ld (pk_n),a
        ld a,c                  ; its colour
        ld hl,pk_t_ink
        add a,l
        ld l,a
        adc a,h
        sub l
        ld h,a
        ld a,(hl)
        ld (pk_ink),a
        ld c,12
pks_p:  ld a,(pk_n)
        add a,12
        cp c                    ; (C: the square's column; lit while column < 12 + rating)
        ld a,PK_PAPER
        ld e,0x42
        jr c,pks_q
        jr z,pks_q
        ld a,(pk_ink)
        ld e,0x7E
pks_q:  push bc
        push de
        ld de,1*256+1
        call set_attrs
        pop de
        pop bc
        push bc
        ld a,e
        call pk_pip
        pop bc
        inc c
        ld a,c
        cp 22
        jr nz,pks_p
        ld a,(pk_n)             ; the number
        ld hl,pk_num
        cp 10
        jr c,pks_1
        ld (hl),'1'
        inc hl
        sub 10
pks_1:  add a,'0'
        ld (hl),a
        inc hl
        ld (hl),0
        ld hl,pk_num
        ld c,23
        call print_at
        pop hl
        inc hl
        pop de                  ; the next label
pks_2:  ld a,(de)
        inc de
        or a
        jr nz,pks_2
        pop bc
        inc b
        inc c
        ld a,c
        cp 4
        jp nz,pks_r
        ld bc,18*256+5          ; + good, - poor
        ld de,0x0101
        ld a,0x67
        call set_attrs
        ld bc,19*256+5
        ld de,0x0101
        ld a,0x57
        call set_attrs
        ld hl,pk_t_pm
        ld bc,18*256+5
        call print_at
        ld hl,pk_t_pm+2
        ld bc,19*256+5
        call print_at
        ld a,2
        call pk_word
        ld bc,18*256+7
        call print_at
        ld a,3
        call pk_word
        ld bc,19*256+7
        call print_at
pk_up:  halt                    ; the keys let go, then a new press
        call pk_keys
        jr nz,pk_up
pk_w:   halt
        call pk_keys
        jr z,pk_w
        bit 2,a
        jp nz,k_up              ; accelerate: race in it (the key let go first; back to the title's caller)
        ld hl,pk_sel
        rra
        jr c,pk_l
        ld a,(hl)               ; right: the next, round to the first
        inc a
        cp PK_N
        jr c,pk_r1
        xor a
pk_r1:  ld (hl),a
        jp pk_show
pk_l:   ld a,(hl)               ; left: the one before, round to the last
        or a
        jr nz,pk_l1
        ld a,PK_N
pk_l1:  dec a
        ld (hl),a
        jp pk_show

; PK_LOAD: car pk_sel into your car - its frames unpacked into pk_buf and its table rows into big_tab (each address from the
; frames' start, made whole), then its card's numbers, its armour, its weight, and your card row from them (su_apply)
pk_load:
        ld a,(pk_sel)
        add a,a
        add a,a
        add a,a
        add a,a
        ld e,a
        ld d,0
        ld hl,pk_recs
        add hl,de
        ld e,(hl)
        inc hl
        ld d,(hl)
        inc hl
        push hl
        ex de,hl
        ld de,pk_buf
        call pk_dzx0
        pop hl
        ld c,(hl)               ; the frames' size: its table rows after them
        inc hl
        ld b,(hl)
        inc hl
        push hl
        ld hl,pk_buf
        add hl,bc
        ld de,big_tab
        ld b,32
pkl_1:  ld a,(hl)
        add a,pk_buf AND 255
        ld (de),a
        inc hl
        inc de
        ld a,(hl)
        adc a,pk_buf/256
        ld (de),a
        inc hl
        inc de
        ld a,(hl)
        ld (de),a
        inc hl
        inc de
        ld a,(hl)
        ld (de),a
        inc hl
        inc de
        djnz pkl_1
        pop hl
        ld e,(hl)               ; YOUR card row's slide, and an eighth of it
        inc hl
        ld d,(hl)
        inc hl
        ld (pk_sl),de
        srl d
        rr e
        srl d
        rr e
        srl d
        rr e
        ld (pk_s8),de
        ld a,(hl)               ; ACCEL to SPEED at
        inc hl
        ld (you_card+3),a
        ld a,(hl)               ; the pushes
        inc hl
        ld (pk_ka),a
        ld a,(hl)
        inc hl
        ld (pk_ks),a
        ld a,(hl)               ; the damage a piece of its armour takes
        inc hl
        ld (arm_tab),a
        ld a,(hl)               ; its weight class
        inc hl
        ld (wt_cls),a
        ld a,(hl)               ; its colour, its ratings
        inc hl
        ld (pk_col),a
        ld (pk_rat),hl
        jp su_apply

pk_word:                        ; A = which of the car's words (0 name, 1 line, 2 good, 3 poor): HL = it
        ld c,a
        ld a,(pk_sel)
        add a,a
        add a,a
        add a,c
        ld hl,pk_words
        jp str_skip

pk_ctr:                         ; the text at HL in the middle of row B
        push hl
        ld c,0xFF
pkc_1:  inc c
        ld a,(hl)
        inc hl
        or a
        jr nz,pkc_1
        srl c
        ld a,16
        sub c
        ld c,a
        pop hl
        jp print_at

pk_pic:                         ; your car (kind 0) nose up, twice the size, on the car's colour: rows 6-9, columns 14-17
        ld hl,PK_TMP
        ld b,32
pkp_0:  ld (hl),0
        inc hl
        djnz pkp_0
        ld hl,big_tab
        ld e,(hl)
        inc hl
        ld d,(hl)               ; DE = the frame: a row is mask, ink, mask, ink
        inc hl
        ld a,(hl)               ; its first row (the car's own top line is row 6)
        inc hl
        ld b,(hl)
        sub 6
        add a,a
        ld l,a
        sbc a,a
        ld h,a
        push bc
        ld bc,PK_TMP
        add hl,bc
        pop bc
pkp_1:  inc de
        ld a,(de)
        ld (hl),a
        inc de
        inc hl
        inc de
        ld a,(de)
        ld (hl),a
        inc de
        inc hl
        djnz pkp_1
        ld bc,6*256+14
        ld de,4*256+4
        ld a,(pk_col)
        call set_attrs
        ld de,PK_TMP
        ld bc,48*256+112
        ld a,2
        jp dbl

pk_pip:                         ; a square in cell B, C: A = 0x7E solid, 0x42 an outline
        push af
        call cell_addr
        pop af
        inc h
        ld (hl),0x7E
        ld b,4
pkq_1:  inc h
        ld (hl),a
        djnz pkq_1
        inc h
        ld (hl),0x7E
        ret

pk_frame:                       ; a black line round the card (rows 3-22, columns 3-28)
        ld b,24
        call pkf_row
        ld b,183
        call pkf_row
        ld b,24
pkf_1:  ld c,24
        call scr_addr
        set 7,(hl)
        ld de,25
        add hl,de
        set 0,(hl)
        inc b
        ld a,b
        cp 184
        jr nz,pkf_1
        ret
pkf_row:
        ld c,24
        call scr_addr
        ld b,26
pkf_2:  ld (hl),0xFF
        inc l
        djnz pkf_2
        ret

pk_keys:                        ; A = bit 0 left, bit 1 right, bit 2 accelerate or SPACE; Z: none down (the keys the K screen set)
        ld hl,k_left+1          ; each key: its half row, then 4 bytes on its bit; the next is 10 bytes on
        ld bc,0x0301
        ld d,0
pkk_1:  ld a,(hl)
        in a,(0xFE)
        push hl
        inc hl
        inc hl
        inc hl
        inc hl
        and (hl)
        pop hl
        jr nz,pkk_u
        ld a,d
        or c
        ld d,a
pkk_u:  sla c
        ld a,10
        add a,l
        ld l,a
        jr nc,pkk_n
        inc h
pkk_n:  djnz pkk_1
        ld a,0x7F               ; SPACE
        in a,(0xFE)
        rra
        ld a,d
        jr c,pkk_2
        or 4
pkk_2:  or a
        ret

; ZX0 "standard" decompressor by Einar Saukas & Urusergi (68 bytes; BSD 3-clause - github.com/einar-saukas/ZX0)
;   HL: source, DE: destination (as hp.asm's, for the tapes without it)
pk_dzx0:
        ld      bc, 0xffff
        push    bc
        inc     bc
        ld      a, 0x80
pkz_literals:
        call    pkz_elias
        ldir
        add     a, a
        jr      c, pkz_new_offset
        call    pkz_elias
pkz_copy:
        ex      (sp), hl
        push    hl
        add     hl, de
        ldir
        pop     hl
        ex      (sp), hl
        add     a, a
        jr      nc, pkz_literals
pkz_new_offset:
        pop     bc
        ld      c, 0xfe
        call    pkz_elias_loop
        inc     c
        ret     z
        ld      b, c
        ld      c, (hl)
        inc     hl
        rr      b
        rr      c
        push    bc
        ld      bc, 1
        call    nc, pkz_elias_backtrack
        inc     bc
        jr      pkz_copy
pkz_elias:
        inc     c
pkz_elias_loop:
        add     a, a
        jr      nz, pkz_elias_skip
        ld      a, (hl)
        inc     hl
        rla
pkz_elias_skip:
        ret     c
pkz_elias_backtrack:
        add     a, a
        rl      c
        rl      b
        jr      pkz_elias_loop

pk_cnt: db 0,"/",'0'+PK_N,0     ; which of how many
pk_num: db 0,0,0                ; a rating's number
pk_n:   db 0
pk_ink: db 0
pk_t_head: db "CHOOSE YOUR CAR",0
pk_t_keys: db "LEFT/RIGHT  FIRE TO RACE",0
pk_t_lr:   db "<",0,">",0
pk_t_pm:   db "+",0,"-",0
pk_t_rat:  db "ACCEL",0,"SPEED",0,"GRIP",0,"ARMOUR",0
pk_t_ink:  db 0x7E,0x7A,0x7C,0x79       ; the lit squares: yellow, red, green, blue on bright white
        include "pick_data2.asm"        ; the packed cars that did not go above the copy routine (tools/make_data.py)
