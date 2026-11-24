; PICK: the ZX0 unpacker for the popup's cars - here, in the gap before sq4's page (racer.asm: the memory hunt, 24 Nov 2026)
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

