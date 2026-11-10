; ---------------------------------------------------------------------
; ROAD_CLEAR: the road (out to its O's) shows the tablecloth much lighter
; (Grant, 10 Nov 2026, option H): on the dark checks the road's tiles lose
; the cloth's dots but one in 64 (each tile's top-left pixel). Runs after
; cloth_fill, before the tiles. Reads the surface map (a bit a tile, 0 = road).
;
; Window tile i (i = 0 at column camx DIV 8) starts at bit i*8 + 16 - s of
; its buffer row (s = camx AND 7): byte i + FB, bit o (o = -s AND 7; FB = 2
; when s = 0, else 1). A run of tiles a..b is cleared on the tile row's even
; lines (the dots are only on even lines): its first byte ANDed to keep the
; o bits before it, b - a bytes zeroed, the last ANDed to keep the bits after.
; Dark checks: (tx DIV 4 + ty DIV 4) odd - in a surface byte, the low nibble
; when ty DIV 4 is even, else the high one. A run never crosses a nibble.
; (its set-up, rc_run, rc_addr and rc_div8 sit in the gap before sq4's page:
; roadclear2.asm)
; ---------------------------------------------------------------------
RC_TX0  equ BUFC+56             ; first tile column in view
RC_TY   equ BUFC+57             ; this tile row
RC_R0   equ BUFC+58             ; its first buffer row
RC_N    equ BUFC+59             ; tile rows left
RC_L    equ BUFC+68             ; the row's lines 0, 2, 4, 6: buffer addresses (8)

rc_row:
        ld a,(RC_R0)            ; this tile row's even lines
        ld hl,RC_L
        ld b,4
rcl_1:
        push af
        call rc_addr            ; -> DE
        ld (hl),e
        inc l
        ld (hl),d
        inc l
        pop af
        add a,2
        djnz rcl_1
        ld a,(RC_TY)            ; surface_map + ty * 9 + tx0 DIV 8
        ld l,a
        ld h,0
        ld e,l
        ld d,h
        add hl,hl
        add hl,hl
        add hl,hl
        add hl,de
        ld a,(RC_TX0)
        ld c,a
        rrca
        rrca
        rrca
        and 31
        ld e,a
        add hl,de
        ld de,surface_map
        add hl,de
        ld a,(RC_TY)            ; D = the dark nibble
        and 4
        ld d,0x0F
        jr z,rc_m
        ld d,0xF0
rc_m:
        ld a,c                  ; E = (window tile of this byte's first) + 8
        and 7
        neg
        add a,8
        ld e,a
rc_byte:
        ld a,(hl)
        inc hl
        cpl                     ; 1 = road
        and d                   ; ... on a dark check
        jr z,rc_skip
        push hl
        push de
        ld c,a
        ld b,8
        ld h,0                  ; H = a run's first tile + 8 (0: none)
rc_bit:
        sla c
        jr nc,rc_end
        inc h
        dec h
        jr nz,rc_nx
        ld h,e
        jr rc_nx
rc_end:
        inc h
        dec h
        jr z,rc_nx
        call rc_run             ; tiles H-8 .. E-9
        ld h,0
rc_nx:
        inc e
        djnz rc_bit
        inc h
        dec h
        call nz,rc_run
        pop de
        pop hl
rc_skip:
        ld a,e
        add a,8
        ld e,a
        cp 31                   ; tiles past 22 are out of view
        jr c,rc_byte
        ld hl,RC_TY
        inc (hl)
        ld hl,RC_R0
        ld a,(hl)
        add a,8
        ld (hl),a
        ld hl,RC_N
        dec (hl)
        jp nz,rc_row
        ret
