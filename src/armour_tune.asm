; =====================================================================
; ARMOUR AND WEAPONS - A TRIAL (ARMOUR=1 on top of CARDS=1; Grant, 17 Nov 2026: "I would like to organise that the cars
; have some weapons. The tank can shoot, and the clown extends its wheels on the sides - if they hit you your car spins
; where it is. We need to add 'armour' to the cars as a gauge item. Tank is very strong. The fast dragster does not take
; much hit. So for example a tactic therefore is to hit the dragster - which will get more damage than you. I would love
; a way to show damage on each car in the HUD somewhere.")
; Only in builds made with ARMOUR=1 (tools/build_armour.sh -> build/racer_armour.tap): with OPT_ARMOUR 0 not a byte of
; any other tape changes.
;
; WHAT THERE IS
;   ARMOUR   every car has ARM_PIECES pieces of armour (6). A car's ARMOUR RATING on its driver card
;            (tools/driver_cards.txt) says how much punishment ONE PIECE takes (tools/make_cards.py: ARMOUR_PIECE; the
;            numbers arrive here as cd_arm, in src/cards.asm). When two cars bump, BOTH lose armour: the damage is
;            how fast they were closing on each other (ARM_DIV) plus a little (ARM_MIN), the same for both - so the car
;            with the poorer rating loses pieces sooner. Grass and walls do no damage.
;   LIMP     a car with no armour left stays in the race, at half its top speed (ARM_LIMP_SHIFT). Nobody is knocked out.
;   THE BAR  (the HUD, Grant's option V) at the right edge of each car's row in the race order: 3 pixels wide, six pieces
;            of 2 pixels; a piece just lost FLASHES for about a second (ARM_FLASH) and then leaves a single dot.
;   THE MUG  in the window's corner is YOUR armour now (it empties as your pieces go): one system, not two. The oil can
;            on the road mends your armour, as it mended your damage.
;   THE TANK SHOOTS (BRUNO, the computer's): a shell straight ahead when a car is in line ahead of him.
;   THE CLOWN'S WHEELS (SPIKE, the computer's): out to both sides for a moment when a car is alongside.
;   A car a shell or a wheel hits SPINS WHERE IT IS (SPIN_T: no speed, no steering, a full turn) and loses armour.
;
; THE NUMBERS TO TUNE - all of them are here. A PICTURE is one drawing of the screen (about 12 a second); a TV FRAME is a
; fiftieth of a second.
;   name            now   what it is
;   ARM_PIECES        6   pieces of armour on every car (the bar has room for six)
;   ARM_DIV           4   a bump's damage = the closing speed halved this many times (4: a sixteenth - cars closing at
;                         half a pixel a TV frame do 8 points of damage to each other; at a whole pixel, 16)
;   ARM_MIN           2   ... plus this much, so that even a rub costs something
;   ARM_COOL         12   pictures before a car that has just been bumped can be bumped again (one crash is many touches)
;   ARM_FLASH        12   pictures a lost piece flashes on the bar (about a second)
;   ARM_LIMP_SHIFT    1   a car with no armour: its top speed halved this many times (1: half; 2: a quarter)
;   ARM_START        60   pictures after a new race is set up before either weapon may be used (about 5 seconds - it
;                         covers the wait on the grid and the first moments after the lights)
;   SPIN_T           32   TV frames a car that is hit spins for ...
;   SPIN_RATE         2   ... turning this many of the 64 headings each TV frame (32 x 2 = 64: one full turn, so it ends
;                         facing the way it was going. Keep SPIN_T x SPIN_RATE a multiple of 64)
;   WPN_SAFE         40   pictures after a hit before the clown's wheels can hit that car again (about 3 seconds)
;   ARM_TANK          3   which car has the gun: 3 is the pink car, BRUNO
;   TANK_RANGE       80   pixels: he fires at a car this near or nearer, ahead of him ...
;   TANK_AIM          6   ... and no more than this many pixels to either side of the line his nose points along
;   TANK_COOL        48   pictures between shots (about 4 seconds)
;   SHELL_SHIFT       4   the shell's speed: 4 is 4 pixels a TV frame (3: 2 pixels; 5: 8). A car does about 1.7
;   SHELL_LIFE       30   TV frames the shell flies if it meets nothing (30 x 4 = 120 pixels)
;   SHELL_HIT         9   pixels: the shell hits a car whose middle is nearer than this, across and down
;   SHELL_DMG        20   the damage a shell does (a firm bump is 8)
;   SHELL_INK         7   its colour on the black road: white
;   ARM_CLOWN         2   which car has the wheels: 2 is the yellow car with the green band, SPIKE
;   WH_SEE_LEN       16   pixels: the wheels come out when a car's middle is within this far ahead of or behind his ...
;   WH_SEE           30   ... and within this far to either side
;   WH_LEN           12   pixels: while they are out they hit a car within this far ahead or behind ...
;   WH_REACH         26   ... and this far to the side (the wheel's tip is 14 from his middle, a car is 8 either way)
;   WH_TIME          10   pictures the wheels stay out (under a second)
;   WH_COOL          60   pictures from when they come out until they can come out again (about 5 seconds)
;   WHEEL_DMG        14   the damage a wheel does
;   WH_DRAW          12   pixels from his middle to the wheel's outer end, as drawn
;
; A PLAYER'S FIRE KEY is not built (Grant has not asked yet; only the computer's two cars have weapons). The weapons are
; written for "a car": arm_fire fires a shell from the car in IX, and arm_wheels pushes the wheels out. A key would need:
; a key read in read_keys (racer.asm) that calls arm_fire with IX = cars when the cool-down is 0; a second shell record
; if your tank and the computer's may both have one in the air (today there is one shell: sh_rec); and the choose screen
; to say which car you drive (today you are always MAX, who has no weapon).
; =====================================================================
ARM_PIECES     equ 6
ARM_DIV        equ 5
ARM_MIN        equ 2
ARM_COOL       equ 30
ARM_FLASH      equ 12
ARM_LIMP_SHIFT equ 1
ARM_START      equ 60
SPIN_T         equ 32
SPIN_RATE      equ 2
WPN_SAFE       equ 40
ARM_TANK       equ 3
TANK_RANGE     equ 80
TANK_AIM       equ 6
TANK_COOL      equ 96
SHELL_SHIFT    equ 4
SHELL_LIFE     equ 30
SHELL_HIT      equ 9
SHELL_DMG      equ 16
SHELL_INK      equ 7
ARM_CLOWN      equ 2
WH_SEE_LEN     equ 16
WH_SEE         equ 30
WH_LEN         equ 12
WH_REACH       equ 26
WH_TIME        equ 10
WH_COOL        equ 60
WHEEL_DMG      equ 12
WH_DRAW        equ 12
ARM_TXT_SH     equ 3            ; the HUD: the gap time sits this many pixels further left, to make room for the bar ...
ARM_GLY_SH     equ 5            ; ... and the flag and the best-lap clock this many
; a car's row of arm_tab (8 bytes; arm_row gives HL at its PIECES):
;   -1 what a piece takes (from the card)   0 PIECES left   1 damage taken in the piece it is on   2 FLASH, pictures left
;   3 SPIN, TV frames left   4 pictures until a bump counts again   5 pictures until a wheel can hit it again
;   6 how many times it has been spun this race (the tests and the race reports read it)
A_FL    equ 2
A_SPIN  equ 3
A_SAFE  equ 4
A_WSAFE equ 5
A_CNT   equ 6
