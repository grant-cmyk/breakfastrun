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
        if 1-OPT_CARDS          ; (CARDS=1: the drivers' numbers are the personalities at the end of this file)
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
        endif                   ; (not CARDS)
; =====================================================================
; CARDS=1 (Grant, 17 Nov 2026: "Each car has a personality ..."): THE DRIVERS, ON TOP OF THEIR CARS' CARDS. The car's
; acceleration, top speed and grip come from tools/driver_cards.txt (tools/make_cards.py -> src/cards.asm); the numbers
; here are how each driver DRIVES it, in Grant's words on the cards. The level (AI=0, 1, 2: EASY, NORMAL, HARD) is the
; driver's SKILL: L below is that number, and a higher level turns in sooner (REACH) and makes fewer mistakes (ERR).
; Three numbers more than above:
;   SLIP   how much faster than its tyres will hold the driver goes into a corner (in quarter-pixels a frame over 64:
;          4 is 0.06 px a frame). 0: brakes down to exactly what the car can take - no slide, tidy. More: goes in too
;          fast, and the car slides wide (the less grip on its card, the lower the speed it must come down to)
;   NEAR   0: minds its own business. Otherwise: when another car is within this many pixels (across plus down) ...
;   PULL   ... its line is moved up to this many pixels towards that car
; =====================================================================
        if OPT_CARDS
AI_L equ OPT_AI
; CYAN - FRANK in the coupe: "Keeps a tidy line and brakes late ... very similar to Max"
AI_C_REACH equ 32+8*AI_L
AI_C_LMASK equ 3
AI_C_LHALF equ 2
AI_C_EASE  equ 2
AI_C_FUSS  equ 2
AI_C_PACE  equ 16
AI_C_REACT equ 0
AI_C_ERR   equ 8-2*AI_L
AI_C_SLIP  equ 4
AI_C_NEAR  equ 0
AI_C_PULL  equ 0
; GREEN band (yellow on the track) - SPIKE in the clown car: "Erratic. A real clown. unpredictable. Almost seems to
; want to hit other cars": the widest wandering line, twitchy steering, by far the most mistakes (a late turn-in, a
; lift, a wobble: about four a lap), into corners too fast, and it steers for any car that comes near
AI_G_REACH equ 28+6*AI_L
AI_G_LMASK equ 7
AI_G_LHALF equ 4
AI_G_EASE  equ 2
AI_G_FUSS  equ 2
AI_G_PACE  equ 16
AI_G_REACT equ 0
AI_G_ERR   equ 22-2*AI_L
AI_G_SLIP  equ 24
AI_G_NEAR  equ 56
AI_G_PULL  equ 16
; PINK - BRUNO in the tank: "Heavy and slow, likes to get in the way. Cuts corners": holds the very middle of the road,
; turns in the earliest (the corner cut), no slide at all, and moves over on a car that comes alongside
AI_P_REACH equ 44+6*AI_L
AI_P_LMASK equ 1
AI_P_LHALF equ 1
AI_P_EASE  equ 2
AI_P_FUSS  equ 2
AI_P_PACE  equ 16
AI_P_REACT equ 0
AI_P_ERR   equ 5-AI_L
AI_P_SLIP  equ 0
AI_P_NEAR  equ 40
AI_P_PULL  equ 10
; WHITE - JANE in the dragster: "should shoot ahead of Max on the straights but really battle on the corners ...
; Brakes early because she has to ... skids wide if pushed": flat out, eases off the earliest (27 degrees), and still
; goes in faster than the long car will hold
AI_W_REACH equ 30+6*AI_L
AI_W_LMASK equ 7
AI_W_LHALF equ 4
AI_W_EASE  equ 3
AI_W_FUSS  equ 2
AI_W_PACE  equ 16
AI_W_REACT equ 0
AI_W_ERR   equ 8-2*AI_L
AI_W_SLIP  equ 10
AI_W_NEAR  equ 0
AI_W_PULL  equ 0
        endif
