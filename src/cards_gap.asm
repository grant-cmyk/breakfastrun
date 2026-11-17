; THE DRIVER CARDS (CARDS=1): the pieces that fit the gap in front of the multiplying table's page (71 bytes of nothing
; on the tight track's build; these are 42). The rest, and what all this is: src/cards_code.asm. If these outgrow the gap the tables
; move a page on and the build loses 256 bytes - tools/build_cards.sh prints the bytes free.
cd_v:   db 0                    ; the car's speed / 4
cd_k:   db 0                    ; its push's number
cd_near:                        ; NEAR, PULL for CYAN, GREEN, PINK, WHITE (ai_tune.asm)
        db AI_C_NEAR,AI_C_PULL, AI_G_NEAR,AI_G_PULL, AI_P_NEAR,AI_P_PULL, AI_W_NEAR,AI_W_PULL
        include "cards.asm"     ; the cards' numbers (tools/make_cards.py)
