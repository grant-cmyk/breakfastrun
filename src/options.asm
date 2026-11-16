; Build options (written by build.sh)
OPT_TALL equ 1                  ; (always: the tables that sit in the program rather than at the top of memory)
CAR_U    equ 15                 ; draw_car: the car frame's x - 12 for the big cars, 15 for the small
OPT_OBJ  equ 0                 ; 1: the coloured objects (obj_paint, objects.asm)
OPT_MUSIC equ 0                ; 1: the ditty in the race
OPT_PIT  equ 0                 ; 1: the crew chief talks under the window (off: the logo is there)
OPT_AY   equ 0                 ; 1: the race tune on the AY sound chip (AY=1 bash build.sh; off since 15 Nov 2026: Grant, "Lets not use the AY chip for now please - old spectrum sounds")
OPT_BRIDGE equ 0               ; 1: the track has a bridge (TRACK=5 bash build.sh: levels, walls, ramps - bridge.asm)
OPT_LOOP equ 0                 ; 1: the screen copy as a loop of one character row (LOOP=1 bash build.sh)
OPT_TOWERF equ 0               ; 1: the race order draws its cars from their frames (TOWER=1 bash build.sh)
OPT_MULTI equ 0                ; 1: several tracks in one load (tools/make_multi.py sets it: not for build.sh alone)
OPT_FLIP equ 0                 ; 1: draw_car and the title car read such a frame last row first (FLIP=1 bash build.sh)
OPT_TILE1 equ 0                ; 1: one tile routine (TILE1=1 bash build.sh)
OPT_PACEFIX equ 0              ; 1: pace_gate counts pictures (PACEFIX=1 bash build.sh)
OPT_ROADCOL equ 7              ; the trial road paper: 7 white, 6 yellow (ROADCOL=6 ROADW=1 bash build.sh)
OPT_ROADW equ 0                ; 1: the road white (ROADW=1 bash build.sh); 2: and plain, no dots (ROADW=2) - a trial
