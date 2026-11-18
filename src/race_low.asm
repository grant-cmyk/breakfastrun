; =====================================================================
; RACE MODE (RACEMODE=1): its table kept under 0x8000. Every computer car's card row in a race (cards_code.asm's
; card_push reads it in place of cd_tab: race.asm's rm_setup points it here) - all four on MAX's card (CD_R_..., made by
; tools/make_cards.py), each its own row because the game writes in it as the car drives (the seventh byte: braking), and
; ELASTIC changes its two pushes (the fifth and sixth bytes) as the race goes.
; =====================================================================
cd_race:
        rept 4
        dw CD_R_SLIDE
        db CD_R_BRAKE, CD_R_VSW, CD_R_KA AND 255, CD_R_KS AND 255, 0, 0
        endm
