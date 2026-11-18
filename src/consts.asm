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
        if OPT_RACE             ; RACE mode: the four drivers' styles (ai_tune.asm, AI_Rx_...; race.asm points ai_style here)
ai_race_src:
        db AI_RC_REACH, AI_RC_LMASK,AI_RC_LHALF, AI_RC_EASE, AI_RC_FUSS    ; CYAN    the smooth one
        db AI_RY_REACH, AI_RY_LMASK,AI_RY_LHALF, AI_RY_EASE, AI_RY_FUSS    ; YELLOW  the late braker
        db AI_RM_REACH, AI_RM_LMASK,AI_RM_LHALF, AI_RM_EASE, AI_RM_FUSS    ; MAGENTA the wide one
        db AI_RW_REACH, AI_RW_LMASK,AI_RW_LHALF, AI_RW_EASE, AI_RW_FUSS    ; WHITE   the erratic one
        endif
