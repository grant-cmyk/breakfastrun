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
