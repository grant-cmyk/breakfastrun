; Build options (written by build.sh)
OPT_TALL equ 1                  ; (always: the tables that sit in the program rather than at the top of memory)
CAR_U    equ 15                 ; draw_car: the car frame's x - 12 for the big cars, 15 for the small
OPT_OBJ  equ 0                 ; 1: the coloured objects (obj_paint, objects.asm)
OPT_MUSIC equ 0                ; 1: the ditty in the race
OPT_PIT  equ 0                 ; 1: the crew chief talks under the window (off: the logo is there)
OPT_AY   equ 0                 ; 1: the race tune on the AY sound chip (AY=1 bash build.sh; off since 15 Nov 2026: Grant, "Lets not use the AY chip for now please - old spectrum sounds")
