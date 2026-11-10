; constant tables kept in the back buffer's bottom rows (BUFD: see racer.asm)
ai_styles_src:  ;  reach  line   ease fuss
        db 24, 3,2,  1,   2     ; CYAN  the racer: full throttle, a tidy
                                ;       line, eases off at 45 degrees
        db 30, 3,2,  1,   2     ; GREEN the smooth one (and slowest): turns in early, cuts
                                ;       corners, eases off at 45 degrees
        db 24, 7,4,  1,   3     ; PINK  the wild one: a wandering line, twitchy
                                ;       steering, the most mistakes
        db 26, 7,4,  2,   2     ; WHITE Slim Jane, the fastest: full throttle (in
                                ;       cars_init), brakes early, rarely wrong
rev4_src:   db 0,8,4,12,2,10,6,14,1,9,5,13,3,11,7,15   ; 0..15, bits reversed
cf_tab_src:                         ; each character row: IX for line 0, buffer row
                                ; (WIN_H/8 of them: buffer rows 16..135)
        dw 0xD018
        db 128
        dw 0xC8F8
        db 120
        dw 0xC8D8
        db 112
        dw 0xC8B8
        db 104
        dw 0xC898
        db 96
        dw 0xC878
        db 88
        dw 0xC858
        db 80
        dw 0xC838
        db 72
        dw 0xC818
        db 64
        dw 0xC0F8
        db 56
        dw 0xC0D8
        db 48
        dw 0xC0B8
        db 40
        dw 0xC098
        db 32
        dw 0xC078
        db 24
        dw 0xC058
        db 16

