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
; driver's SKILL: L below is that number, and a higher level turns in sooner (REACH), makes fewer mistakes (ERR) and
; carries more speed into a corner (SLIP).
; Three numbers more than above:
;   SLIP   how much faster than its tyres will hold the driver goes into a corner (in quarter-pixels a frame over 64:
;          4 is 0.06 px a frame). 0: brakes down to exactly what the car can take - no slide, tidy. More: goes in too
;          fast, and the car slides wide (the less grip on its card, the lower the speed it must come down to)
;   NEAR   0: minds its own business. Otherwise: when another car is within this many pixels (across plus down) ...
;   PULL   ... its line is moved up to this many pixels towards that car. Add 128 and it LUNGES too: one time in four
;          it steers straight at the other car for AI_LUNGE of its turns (a turn is two TV frames)
; =====================================================================
        if OPT_CARDS
AI_L equ OPT_AI
AI_SK equ 6*AI_L-6               ; (the driver's skill in the corners: EASY brakes 0.09 px a frame lower than NORMAL, HARD carries 0.09 more)
AI_LUNGE equ 3
; CYAN - FRANK in the coupe: "Keeps a tidy line and brakes late ... very similar to Max"
AI_C_REACH equ 32+8*AI_L
AI_C_LMASK equ 3
AI_C_LHALF equ 2
AI_C_EASE  equ 2
AI_C_FUSS  equ 2
AI_C_PACE  equ 16
AI_C_REACT equ 0
AI_C_ERR   equ 8-2*AI_L
AI_C_SLIP  equ 4+AI_SK
AI_C_NEAR  equ 0
AI_C_PULL  equ 0
; GREEN band (yellow on the track) - SPIKE in the clown car: "Erratic. A real clown. unpredictable. Almost seems to
; want to hit other cars": the widest wandering line, twitchy steering, by far the most mistakes (a late turn-in, a
; lift, a wobble: about four a lap), into corners too fast, and it steers for any car that comes near
AI_G_REACH equ 40+6*AI_L
AI_G_LMASK equ 7
AI_G_LHALF equ 4
AI_G_EASE  equ 2
AI_G_FUSS  equ 2
AI_G_PACE  equ 16
AI_G_REACT equ 0
AI_G_ERR   equ 14-2*AI_L
AI_G_SLIP  equ 24+AI_SK
AI_G_NEAR  equ 56
AI_G_PULL  equ 128+14
; PINK - BRUNO in the tank: "Heavy and slow, likes to get in the way. Cuts corners": holds the very middle of the road,
; turns in the earliest (the corner cut), brakes to exactly what the tank will hold, and moves his line over on a car that
; comes within 40 pixels
AI_P_REACH equ 44+6*AI_L
AI_P_LMASK equ 1
AI_P_LHALF equ 1
AI_P_EASE  equ 2
AI_P_FUSS  equ 2
AI_P_PACE  equ 16
AI_P_REACT equ 0
AI_P_ERR   equ 5-AI_L
AI_P_SLIP  equ 0+AI_SK
AI_P_NEAR  equ 40
AI_P_PULL  equ 10
; WHITE - JANE in the dragster: "should shoot ahead of Max on the straights but really battle on the corners ...
; Brakes early because she has to ... skids wide if pushed": flat out, eases off the earliest (27 degrees), and still
; goes in faster than the long car will hold
AI_W_REACH equ 40+6*AI_L
AI_W_LMASK equ 3
AI_W_LHALF equ 2
AI_W_EASE  equ 3
AI_W_FUSS  equ 2
AI_W_PACE  equ 16
AI_W_REACT equ 0
AI_W_ERR   equ 8-2*AI_L
AI_W_SLIP  equ 16+AI_SK
AI_W_NEAR  equ 0
AI_W_PULL  equ 0
        endif
; =====================================================================
; RACE MODE (RACEMODE=1; Grant, 18 Nov 2026: "I would like to try a traditional race ... the idea is to make it competitive
; so you don't run away with it"): the four computer drivers on the title's RACE. Every car is the racer on MAX's card
; (CD_R_... in cards.asm: his top speed and acceleration), so the race is decided by driving - these numbers are how they
; drive it - until 19 Nov 2026 the same for all four (now each its own: below). The numbers mean what they do
; above. Tuned with tests/race_measure.py (18 Nov 2026, 70% speed, 10 races of 3 laps, you from the back of the grid):
;   - their best driving alone (REACH 60 - the most that still counts every waypoint - flat out, EASE 0, few mistakes)
;     lapped in 24.7 s at best against the good driver's 23.7: on MAX's card a computer car must slow to 0.82 px a frame
;     for every bend (70% of its top speed) where your car's tyres hold far more. So:
;   AI_R_GRIP  their GRIP in RACE, in 64ths of what MAX's card gives a computer car: 107 (x1.67) - on this track they then
;              neither slide nor brake for a bend at their top speed (it is 1.18 px a frame; they slide above 1.37). Their
;              top speed and acceleration stay MAX's. With it: the good driver won 6 of 10, mean place 1.9, 2.0 s behind
;              the winner when beaten, the four of them within 2% of each other a lap, the order changing 32 times a race.
;              (80/64: won 8 of 10; 64/64, MAX's card as it is: won 10 of 10 by 5 to 10 s.)
;              Then 88 (Grant, 18 Nov 2026: "the computer cars need to skid a bit more": in a slide about 10% of the time).
;              Since 19 Nov 2026 each car has its own (AI_Rx_GRIP, below).
        if OPT_CARDS
AI_R_SLIP  equ 12                ; (all four: added to the card's corner speed before AI_R_BRAKEG)
AI_R_BRAKEG equ 107               ; the speed they brake down to for a bend, in 64ths of the card's: at 107 over their top
                                  ; speed, so they never brake - they lift instead (EASE). Braking even just under the top
                                  ; speed (19 Nov 2026: at 76, 74, 72 quarter-pixels) cost every car about 0.7 s a lap -
                                  ; they brake whenever they steer - so it is the same for all four
; EACH DRIVER ITS OWN STYLE, EACH CAR A LITTLE DIFFERENT (Grant, 19 Nov 2026, after driving it: "the racers race too
; similarly - we need to mix it up a bit - so driving is different and maybe cars are slightly different - at the moment
; it looks like a procession"). Until then all four drove as one (REACH 60, line 3,2, EASE 0, FUSS 2, PACE 16, REACT 0,
; ERR 2, grip 88, MAX's top speed and acceleration). Now each colour has its own numbers: the drivers' eight as above,
; and three for the car itself:
;   GRIP where it starts to slide when it steers, in 64ths of MAX's card (88 was the four's: smaller slides sooner)
;   KS   its SPEED push, 64ths more or less than MAX's card: its top speed on the straights (at 70% speed one 64th is
;        about 2.3% of the top speed; a lap about 0.5 s quicker on its own)
;   KA   its ACCEL push, the same way: how quickly it gets back up to speed after a slow corner, a slide or a bump (only
;        under about 0.94 px a frame at 70%, so it is worth much less than KS)
; Measured (tests/race_measure.py, 20 races of 3 laps, the good driver from the back, 70%): what mixes them most is the
; LINE - two cars on lines a few pixels either side of the others' (yellow's 7,7: -7 to 0; magenta's 7,0: 0 to +7) can
; run side by side and pass, where on one line they queue. With these the computer cars changed places with EACH OTHER
; about 15 times a race (3 with the four the same), and ran nose-to-tail behind another car about a third of the time
; (nearly half). Their laps within 1.5% of each other; the good driver won 19 of 40, 1.8 s behind when beaten.
; AT 75% SPEED (Grant, 19 Nov 2026: "Any chance of speed 75%?" - the racer_race75 tapes, tools/build_race.sh): the same
; drivers, but each car one or two 64ths slower on the straights than at 70% (AI_R75, in each KS below). At 75% your car's
; tyres give a little less in the bends than the speed gains (the good driver's best lap 22.8 s, 3.5% quicker than at 70%)
; while the computer cars, which hardly brake, gained 8% (22.2 s): with the 70% numbers the good driver won 0 of 20. With
; these: 20 of 40, 1.8 s behind when beaten (each 64th off the straight is about 0.6 s a lap at 75%).
        if GAME_SPEED > 70
AI_R75     equ 1
        else
AI_R75     equ 0
        endif
; CYAN - THE SMOOTH ONE: a tight, tidy line (0 to +1 px off it), lifts early for a bend (EASE 2), almost never wrong;
;        its car grips best (it never slides) but has MAX's top speed - the others are quicker on the straights
AI_RC_REACH equ 56
AI_RC_LMASK equ 1
AI_RC_LHALF equ 0
AI_RC_EASE  equ 2
AI_RC_FUSS  equ 2
AI_RC_PACE  equ 16
AI_RC_REACT equ 0
AI_RC_ERR   equ 1
AI_R_GRIPCUT equ 20               ; (all four cars' grip less this many 64ths: Grant, 19 Nov 2026, "with new drivers still too
                                  ; tough. Make them skid more". tests/race_measure.py, good driver, 10 races each: cut 0 -
                                  ; 20 of 40 wins at 75%; cut 12 - 5 of 10; cut 20 - 9 of 10 at 70% and 75%, 7 of 10 with the
                                  ; catch-up; time in a slide C 11-13% G 25-32% P 7-13% W 28-37%)
AI_RC_GRIP  equ 104-AI_R_GRIPCUT
AI_RC_KA    equ 0
AI_RC_KS    equ 0-2*AI_R75
; YELLOW - THE LATE BRAKER: cuts every corner as hard as it may (REACH 60), never lifts, twitchy hands (FUSS 3) - in a
;        slide more than a quarter of the time - and more small mistakes; its own line, a few pixels to one side; its car
;        the fastest on the straights (+4.6%) and the least grip
AI_RY_REACH equ 60
AI_RY_LMASK equ 7
AI_RY_LHALF equ 7
AI_RY_EASE  equ 0
AI_RY_FUSS  equ 3
AI_RY_PACE  equ 16
AI_RY_REACT equ 0
AI_RY_ERR   equ 5
AI_RY_GRIP  equ 76-AI_R_GRIPCUT
AI_RY_KA    equ 0
AI_RY_KS    equ 2-AI_R75
; MAGENTA - THE WIDE ONE: keeps a little nearer the middle of the road (REACH 54), on its own line a few pixels to the
;        other side, lifts for the bends (EASE 1), steady hands; its car is the quickest away from a slow corner (+9%
;        acceleration), a touch quicker on the straights (+2.3%), grips a little better than MAX's computer car did
AI_RM_REACH equ 54
AI_RM_LMASK equ 7
AI_RM_LHALF equ 0
AI_RM_EASE  equ 1
AI_RM_FUSS  equ 2
AI_RM_PACE  equ 16
AI_RM_REACT equ 0
AI_RM_ERR   equ 2
AI_RM_GRIP  equ 92-AI_R_GRIPCUT
AI_RM_KA    equ 6
AI_RM_KS    equ 1-2*AI_R75
; WHITE - THE ERRATIC ONE: its line wanders the most (-8 to +7 px), twitchy hands, never lifts, the most mistakes (about
;        one a lap) - and quick when it gets it right: its car +2.3% on the straights, a little less grip
AI_RW_REACH equ 60
AI_RW_LMASK equ 15
AI_RW_LHALF equ 8
AI_RW_EASE  equ 0
AI_RW_FUSS  equ 3
AI_RW_PACE  equ 16
AI_RW_REACT equ 0
AI_RW_ERR   equ 10
AI_RW_GRIP  equ 80-AI_R_GRIPCUT
AI_RW_KA    equ 0
AI_RW_KS    equ 1-AI_R75
; ELASTIC (ELASTIC=1: the second race tape, tools/build_race.sh) - the rubber band, in race.asm's el_tick. A computer car
; behind the leader gets one 64th more push (at 70% speed a 64th is 2.3% of its top speed) for every 2^EL_SH waypoints it
; is behind (waypoints are 32 pixels apart, about half a second at speed), up to EL_MAX 64ths; and one more than EL_AHEAD
; waypoints ahead of YOU eases off EL_EASE 64ths. Nothing pushes once any car has finished. As built: +2.3% a waypoint
; behind the leader, up to +7% from 3 waypoints (about 1.6 s) behind; -2.3% for a car more than 4 waypoints (about 2 s)
; ahead of you. Tried (tests/race_measure.py, 10 races each, the good driver): pushing every 2 waypoints and easing for any
; car ahead of you - you won 8 of 10; easing only 2 s ahead - 5 of 10; this - 3 of 10, beaten by 0.9 s on average.
EL_SH      equ 0                ; (every 2 to the power EL_SH waypoints: 1 = every 2, about a second)
EL_MAX     equ 3
EL_EASE    equ 1
EL_AHEAD   equ 4                ; (more than this many waypoints ahead of you - about 2 seconds - before it eases off)
        endif
