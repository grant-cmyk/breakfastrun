; HP.ASM - MULTI (several tracks in one load): what lives above the looped screen-copy routine, at HP.
; Assembled BY ITSELF for HP by tools/make_multi.py (pasmo has no PHASE), then loaded with the game after
; the start-up area and copied up by start_once. hp_syms.asm (the game's own addresses) and hp_data.asm (the
; tracks) are written by the tool.
;
; A TRACK, WAITING: everything in memory that is not the same for every track - its tiles, row lists,
; surface, O map, waypoints, masks, arrows' table, mini-map, grid, and the numbers built into the code
; (MAPH, NWP, the start, the cans...) - found by comparing the tracks' builds byte for byte. The long
; stretches are packed (ZX0), the short ones kept as they are.
; TRK_SET unpacks one track straight onto its working places. The title calls TRK_HOOK for its keys.
        include "hp_syms.asm"
        org HP
        jp trk_hook             ; HP + 0: the title's key scan (title.asm, t_keys)
trk_cur: db 0                   ; HP + 3: the track in its working places now (0 = the first)
        jp trk_set              ; HP + 4: A = track -> unpacked (for tests and for a menu)
trk_hook:
        call K_SCAN
        ret z
        ld a,l
        cp 14                   ; T: the next track
        jr z,th_t
        or 1                    ; (any other key: back to the title with it, NZ)
        ret
th_t:
        ld a,(trk_cur)
        inc a
        cp NTRK
        jr c,th_1
        xor a
th_1:
        call trk_set
        ld a,(trk_cur)          ; its name, on the title's message line
        ld l,a
        ld h,0
        ld d,h
        ld e,l
        add hl,hl
        add hl,hl
        add hl,de               ; x 5
        add hl,hl
        add hl,hl               ; x 20
        add hl,de               ; x 21
        ld de,trk_names
        add hl,de
        call T_PROMPT
        call K_UP               ; (the key let go)
        xor a                   ; Z: no key for the title
        ret

; TRK_SET (A = track): its data onto the working places. A list of packed stretches (where to, then the ZX0
; stream - the unpacker leaves HL after it), a zero, then the short ones (where to, how many, the bytes), a zero.
trk_set:
        di
        ld (trk_cur),a
        add a,a
        ld l,a
        ld h,0
        ld de,trk_tab
        add hl,de
        ld a,(hl)
        inc hl
        ld h,(hl)
        ld l,a
ts_1:
        ld e,(hl)
        inc hl
        ld d,(hl)
        inc hl
        ld a,d
        or e
        jr z,ts_raw
        call dzx0_standard
        jr ts_1
ts_raw:
        ld e,(hl)
        inc hl
        ld d,(hl)
        inc hl
        ld a,d
        or e
        jr z,ts_x
        ld c,(hl)
        inc hl
        ld b,0
        ldir
        jr ts_raw
ts_x:
        ei
        ret

; ZX0 "standard" decompressor by Einar Saukas & Urusergi (68 bytes; BSD 3-clause - github.com/einar-saukas/ZX0)
;   HL: source, DE: destination
dzx0_standard:
        ld      bc, 0xffff              ; preserve default offset 1
        push    bc
        inc     bc
        ld      a, 0x80
dzx0s_literals:
        call    dzx0s_elias             ; obtain length
        ldir                            ; copy literals
        add     a, a                    ; copy from last offset or new offset?
        jr      c, dzx0s_new_offset
        call    dzx0s_elias             ; obtain length
dzx0s_copy:
        ex      (sp), hl                ; preserve source, restore offset
        push    hl                      ; preserve offset
        add     hl, de                  ; calculate destination - offset
        ldir                            ; copy from offset
        pop     hl                      ; restore offset
        ex      (sp), hl                ; preserve offset, restore source
        add     a, a                    ; copy from literals or new offset?
        jr      nc, dzx0s_literals
dzx0s_new_offset:
        pop     bc                      ; discard last offset
        ld      c, 0xfe                 ; prepare negative offset
        call    dzx0s_elias_loop        ; obtain offset MSB
        inc     c
        ret     z                       ; check end marker
        ld      b, c
        ld      c, (hl)                 ; obtain offset LSB
        inc     hl
        rr      b                       ; last offset bit becomes first length bit
        rr      c
        push    bc                      ; preserve new offset
        ld      bc, 1                   ; obtain length
        call    nc, dzx0s_elias_backtrack
        inc     bc
        jr      dzx0s_copy
dzx0s_elias:
        inc     c                       ; interlaced Elias gamma coding
dzx0s_elias_loop:
        add     a, a
        jr      nz, dzx0s_elias_skip
        ld      a, (hl)                 ; load another group of 8 bits
        inc     hl
        rla
dzx0s_elias_skip:
        ret     c
dzx0s_elias_backtrack:
        add     a, a
        rl      c
        rl      b
        jr      dzx0s_elias_loop
hp_code_end:
        include "hp_data.asm"   ; NTRK, trk_names (21 bytes a track), trk_tab and the tracks
hp_end:
