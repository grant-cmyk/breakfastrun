; =====================================================================
; CNOS - THE CHASERS' NOS (CNOS=1; Grant, 22 Nov 2026: "if you get ahead the other cars can speed up to catchup. But not
; a full catchup ... If you are several seconds ahead, then 2 of the cars can benefit from NOS at different times, but
; note that they also may have difficulty controlling NOS ... a deterministic rule ... that allows the chase to keep
; close but not be a cheat elastic catchup with no explanation").
; THE RULE - two drivers carry a NOS can, one a lap: SPIKE (yellow, the late braker) and JANE (white, the erratic one).
; One may light it only when ALL of these hold:
;   1. YOU are leading, and nobody has finished
;   2. that car is CN_GAP or more behind you (the gap the race order shows - its last checkpoint)
;   3. it has not used its can this lap
;   4. no NOS is burning, and CN_SPACE pictures have gone since the last one (so never both at once)
;   5. SPIKE only: the road ahead is straight (his next two waypoints bend under CN_STR) - JANE lights it at once,
;      wherever she is
; A burn lasts CN_PIC pictures: the car's pushes (and so its top speed) CN_K 64ths more - 1.75x, as yours - but its
; tyres no better: it slides through any corner it reaches at that speed. Spike still brakes for the corner; JANE DOES
; NOT LIFT (her brake speed 255 while it burns) - she flies into the corner and often into the O's.
; The crew chief says so: "NOS LIT BY | <name>". Nothing random in it.
; Kept under 0x8000 (the breakfast race tape's low room). cn_new each race (strip.asm), cn_tick each picture (racer.asm).
; =====================================================================
CN_A    equ 2                   ; SPIKE (the late braker): only on a straight, brakes as ever
CN_B    equ 4                   ; JANE (the erratic one): at once, does not lift
CN_GAP  equ 150                 ; 3 s (TV frames) behind you
CN_PIC  equ NOS_FR/OPT_STEADY   ; a burn, pictures (as long as yours)
CN_SPACE equ 60                 ; pictures after a burn before the other may light (about 5 s)
CN_K    equ 32                  ; 64ths more push: 1.5x (48, 1.75x as yours, took them to 3.3 px a frame - more than you)
M_CNOS  equ M_OTH2              ; (make_strip.py: "NOS LIT BY|@" on this tape)
CN_STR  equ 10                  ; Spike's "straight": each of the next two waypoints' bends, |x| + |y|, under this

; (cnos.asm: the part in the program - cn_tick; cnos_low.asm: cn_new, the helpers and the data, under 0x8000)

cn_tick:                        ; each picture
        ld a,(race_on)
        or a
        ret z
        ld hl,cn_burn
        ld a,(hl)
        or a
        jr z,cn_idle
        dec (hl)
        ret nz
        ld a,(cn_who)           ; the burn is over: its card row as it was
        call cn_row
        ex de,hl
        ld hl,cn_sv
        ld bc,6
        ldir
        ld a,CN_SPACE
        ld (cn_wait),a
        ret
cn_idle:
        ld hl,cn_wait
        ld a,(hl)
        or a
        jr z,cn_i1
        dec (hl)
        ret
cn_i1:  ld hl,(order-1)         ; 1. you lead (H = order's first), nobody in yet
        ld a,(fin_count)
        or h
        ret nz
        ld a,CN_A
        call cn_try
        ret c
        ld a,CN_B
cn_try:                         ; A = a carrier's kind: CY if it lit its NOS
        ld (cn_k),a
        add a,a                 ; 2. its gap to you, CN_GAP or more
        ld l,a
        ld h,0
        ld de,GAPS
        add hl,de
        ld e,(hl)
        inc hl
        ld d,(hl)
        ld hl,CN_GAP-1
        sbc hl,de               ; (carry clear: ADD HL,DE above did not overflow)
        ret nc
        ld a,(cn_k)             ; its car
        ld ix,cars-C_SIZE
        ld de,C_SIZE
cn_c:   add ix,de
        cp (ix+C_KIND)
        jr nz,cn_c
        ld l,a                  ; 3. its can, not used this lap (and still racing)
        ld h,0
        ld de,cn_used
        add hl,de
        ld a,(ix+C_LAPS)
        cp LAPS+1
        ret nc
        cp (hl)
        ret z                   ; (Z: NC as well)
        push hl
        ld a,(cn_k)             ; 5. Spike: the road ahead straight
        cp CN_A
        jr nz,cn_go
        ld a,(ix+C_WP)
        call cn_bend
        jr nc,cn_no
        ld a,(ix+C_WP)
        inc a
        call cn_bend
        jr nc,cn_no
cn_go:  pop hl
        ld a,(ix+C_LAPS)
        ld (hl),a               ; its can used, this lap
        ld a,(cn_k)
        ld (cn_who),a
        ld (ms_car),a
        call cn_row             ; its card row (grip, brake, 4/5 top, ACCEL, SPEED): kept, then NOS (cn_set)
        push hl
        ld de,cn_sv
        ld bc,6
        ldir
        pop hl
        call cn_set
        ld a,CN_PIC
        ld (cn_burn),a
        ld a,M_CNOS             ; the crew chief: NOS LIT BY <name>
        call msg_say
        scf
        ret
cn_no:  pop hl
        ret                     ; (NC from cn_bend)
cn_steer:                       ; (physics, IX = a car, D = its heading steps this go): JANE ON NOS TURNS HALF AS FAST - she
        ld a,(cn_burn)          ; does not lift and cannot get it turned: she runs wide, into the O's (Spike, tried with it
        or a                    ; too, never crashed - he brakes - and only lost time: 22 Nov 2026)
        ret z
        ld a,(cn_who)
        cp CN_B
        ret nz
        cp (ix+C_KIND)
        ret nz
        srl d
        ret
cn_ohit:                        ; (bumps_o, IX = a computer car that has just bounced off an O; HL kept): ON NOS, A CRASH - three
        ld a,(cn_burn)          ; quarters of its speed gone, its NOS over (its row put back next picture) and it flickers as a hurt
        or a                    ; car does (arm_tab byte 4: weight.asm)
        ret z
        ld a,(cn_who)
        cp (ix+C_KIND)
        ret nz
        push hl
        ld a,1
        ld (cn_burn),a
        push ix
        pop hl
        ld de,C_VX
        add hl,de
        call cno_q
        call cno_q
        ld a,(ix+C_KIND)
        add a,a
        add a,a
        add a,a
        add a,(arm_tab+4) AND 255
        ld l,a
        adc a,(arm_tab+4)/256
        sub l
        ld h,a
        ld (hl),WT_FLASH
        pop hl
        ret
cno_q:                          ; the word at HL a quarter (signed); HL on 2
        ld e,(hl)
        inc hl
        ld d,(hl)
        sra d
        rr e
        sra d
        rr e
        ld (hl),d
        dec hl
        ld (hl),e
        inc hl
        inc hl
        ret
