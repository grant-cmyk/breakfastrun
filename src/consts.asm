; constant tables kept in the back buffer's bottom rows (BUFD: see racer.asm)
ai_styles_src:  ;  reach  line   ease fuss       (the numbers are in ai_tune.asm, with the cars' PACE, REACT and ERR)
        db AI_C_REACH, AI_C_LMASK,AI_C_LHALF, AI_C_EASE, AI_C_FUSS     ; CYAN  the racer: full throttle, a tidy
                                ;       line, eases off at 45 degrees
        db AI_G_REACH, AI_G_LMASK,AI_G_LHALF, AI_G_EASE, AI_G_FUSS     ; GREEN the smooth one (and slowest): turns in early, cuts
                                ;       corners, eases off at 45 degrees
        db AI_P_REACH, AI_P_LMASK,AI_P_LHALF, AI_P_EASE, AI_P_FUSS     ; PINK  the wild one: a wandering line, twitchy
                                ;       steering, the most mistakes
        db AI_W_REACH, AI_W_LMASK,AI_W_LHALF, AI_W_EASE, AI_W_FUSS     ; WHITE Slim Jane, the fastest: full throttle (in
                                ;       cars_init), brakes early, rarely wrong
rev4_src:   db 0,8,4,12,2,10,6,14,1,9,5,13,3,11,7,15   ; 0..15, bits reversed
