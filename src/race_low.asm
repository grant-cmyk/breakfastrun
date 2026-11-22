; =====================================================================
; RACE MODE (RACEMODE=1): its table kept under 0x8000. Every computer car's card row in a race (cards_code.asm's
; card_push reads it in place of cd_tab: race.asm's rm_setup points it here) - all four on MAX's card (CD_R_..., made by
; tools/make_cards.py) with each car's own small differences (ai_tune.asm, AI_Rx_GRIP, _KA, _KS: since 19 Nov
; 2026). Each its own row as the game writes in it as the car drives (the seventh byte: braking), and ELASTIC changes its
; two pushes (the fifth and sixth bytes) as the race goes - adding its rubber band, which it keeps in the eighth byte.
; =====================================================================
RROW    macro grip, ka, ks
        dw CD_R_SLIDE*grip/64                 ; where it slides (its grip)
        db CD_R_BRAKE*AI_R_BRAKEG/64, CD_R_VSW, (CD_R_KA+ka) AND 255, (CD_R_KS+ks) AND 255, 0, 0
        endm
        if OPT_RACEONLY * (1 - OPT_RT)  ; (the breakfast race tapes: every car on its own card - rm_setup points card_push at
cd_race equ cd_tab              ;  cd_tab - so these rows were never read: 32 bytes, 22 Nov 2026)
        else
cd_race:
        RROW AI_RC_GRIP, AI_RC_KA, AI_RC_KS     ; CYAN    the smooth one
        RROW AI_RY_GRIP, AI_RY_KA, AI_RY_KS     ; YELLOW  the late braker
        RROW AI_RM_GRIP, AI_RM_KA, AI_RM_KS     ; MAGENTA the wide one
        RROW AI_RW_GRIP, AI_RW_KA, AI_RW_KS     ; WHITE   the erratic one
        endif
        if OPT_RACEONLY * OPT_MIRROR    ; (RACEONLY with MIRROR, 22 Nov 2026: rl_line's helpers down here - three times a second a car, so the slower
        include "race_lines.asm" ; memory costs little; the program's room went to the tighter tracks)
        endif
