; =====================================================================
; THE COMPUTER CARS' SETTINGS, ALL IN ONE PLACE (17 Nov 2026; Grant, after driving the race track trial: "I also need
; the other cars to be more competitive, this drives a lot easier"). Three levels, chosen when the tape is built:
;       bash build.sh           level 0, EASY: the cars exactly as they were (not one byte of the game changes)
;       AI=1 bash build.sh      level 1, NORMAL
;       AI=2 bash build.sh      level 2, HARD
; Each car has eight numbers. What each does, and which way is quicker:
;   REACH  how near (pixels) a waypoint counts as reached. Bigger: the car turns for the next one sooner and CUTS THE
;          CORNER - the biggest single gain (24 keeps to the middle of the road; 56 is a racing line; over 60 the car
;          starts to miss waypoints, and its laps are counted too early - do not go there)
;   LINE   how far its line wanders from the middle, as mask,half: 3,2 is tidy (-2 to +1 px), 7,4 wild (-4 to +3)
;   EASE   when it lifts off: 0 only when its target is behind it (the late braker), 1 when the target is 45 degrees
;          off its nose, 2 at 27 degrees (early and careful)
;   FUSS   steering: 2 lets 14 degrees go (smooth), 3 only 7 (twitchy: it weaves, and loses a little)
;   PACE   throttle: it pushes on PACE of every 16 (16 = flat out; each 1 less costs about 6% of a lap)
;   REACT  how many of its turns to think it lets go by after each decision (0 = sharpest)
;   ERR    mistakes: chances in 256, at each waypoint, of a late turn-in, a lift or a wobble (a lap has about 47 waypoints:
;          3 is one mistake in two laps, 12 is two a lap)
; Measured on the tighter track (PROJECT-LOG, 17 Nov 2026; tests/rt_tight.py tries settings without building a tape).
; =====================================================================
; (OPT_AI is written into options.asm by build.sh)
        if OPT_AI = 0           ; ---- EASY: as they were ----
AI_C_REACH equ 24
AI_C_LMASK equ 3
AI_C_LHALF equ 2
AI_C_EASE  equ 1
AI_C_FUSS  equ 2
AI_C_PACE  equ 15
AI_C_REACT equ 0
AI_C_ERR   equ 8                ; CYAN, the racer: a tidy line, eases off at 45 degrees
AI_G_REACH equ 30
AI_G_LMASK equ 3
AI_G_LHALF equ 2
AI_G_EASE  equ 1
AI_G_FUSS  equ 2
AI_G_PACE  equ 14
AI_G_REACT equ 0
AI_G_ERR   equ 6                ; GREEN (SPIKE), the smooth one and the slowest: turns in early, few mistakes
AI_P_REACH equ 24
AI_P_LMASK equ 7
AI_P_LHALF equ 4
AI_P_EASE  equ 1
AI_P_FUSS  equ 3
AI_P_PACE  equ 15
AI_P_REACT equ 0
AI_P_ERR   equ 12               ; PINK, the wild one: a wandering line, twitchy steering, the most mistakes
AI_W_REACH equ 26
AI_W_LMASK equ 7
AI_W_LHALF equ 4
AI_W_EASE  equ 2
AI_W_FUSS  equ 2
AI_W_PACE  equ 16
AI_W_REACT equ 0
AI_W_ERR   equ 3                ; WHITE, Slim Jane, the fastest: flat out, brakes early, rarely wrong
        endif
        if OPT_AI = 1           ; ---- NORMAL: everyone flat out and cutting the corners a little ----
AI_C_REACH equ 40
AI_C_LMASK equ 3
AI_C_LHALF equ 2
AI_C_EASE  equ 0
AI_C_FUSS  equ 2
AI_C_PACE  equ 16
AI_C_REACT equ 0
AI_C_ERR   equ 6                ; CYAN
AI_G_REACH equ 30
AI_G_LMASK equ 3
AI_G_LHALF equ 2
AI_G_EASE  equ 1
AI_G_FUSS  equ 2
AI_G_PACE  equ 16
AI_G_REACT equ 0
AI_G_ERR   equ 6                ; GREEN
AI_P_REACH equ 36
AI_P_LMASK equ 7
AI_P_LHALF equ 4
AI_P_EASE  equ 1
AI_P_FUSS  equ 3
AI_P_PACE  equ 16
AI_P_REACT equ 0
AI_P_ERR   equ 12               ; PINK
AI_W_REACH equ 44
AI_W_LMASK equ 3
AI_W_LHALF equ 2
AI_W_EASE  equ 0
AI_W_FUSS  equ 2
AI_W_PACE  equ 16
AI_W_REACT equ 0
AI_W_ERR   equ 3                ; WHITE
        endif
        if OPT_AI = 2           ; ---- HARD: racing lines, late braking, fewer mistakes ----
AI_C_REACH equ 52
AI_C_LMASK equ 3
AI_C_LHALF equ 2
AI_C_EASE  equ 0
AI_C_FUSS  equ 2
AI_C_PACE  equ 16
AI_C_REACT equ 0
AI_C_ERR   equ 5                ; CYAN
AI_G_REACH equ 40
AI_G_LMASK equ 3
AI_G_LHALF equ 2
AI_G_EASE  equ 1
AI_G_FUSS  equ 2
AI_G_PACE  equ 16
AI_G_REACT equ 0
AI_G_ERR   equ 5                ; GREEN
AI_P_REACH equ 48
AI_P_LMASK equ 7
AI_P_LHALF equ 4
AI_P_EASE  equ 0
AI_P_FUSS  equ 3
AI_P_PACE  equ 16
AI_P_REACT equ 0
AI_P_ERR   equ 10               ; PINK
AI_W_REACH equ 56
AI_W_LMASK equ 3
AI_W_LHALF equ 2
AI_W_EASE  equ 0
AI_W_FUSS  equ 2
AI_W_PACE  equ 16
AI_W_REACT equ 0
AI_W_ERR   equ 2                ; WHITE
        endif
