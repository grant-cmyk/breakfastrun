; the HUD's fixed text (kept at the top of memory: see TOPMEM in racer.asm)
txt_flag_src:     db "CHEQUERED FLAG!",0   ; the race over (Grant: everything stops)
txt_youfin_src:   db "YOU FINISHED",0
txt_race_src:     db " RACE  ",0
txt_ready_src:    db "GET READY",0
txt_pressq_src:   db "PRESS Q",0
txt_lamp_src:     db "O",0
txt_go_src:       db "GO!",0
txt_final_src:    db "FINAL LAP!",0
txt_finished_src: db "FINISHED",0
txt_places_src:   db "1ST",0, "2ND",0, "3RD",0, "4TH",0, "5TH",0
txt_track_src:    db "BREAKFAST AT TIFFANY'S",0   ; track 1 (Grant, 10 Nov 2026): 22 = the window's width
txt_none_src: db 0
; the small font for numbers: 0-9, 3 x 5, the bits at the top of each byte
sfont_src:
        db %11100000,%10100000,%10100000,%10100000,%11100000   ; 0
        db %01000000,%11000000,%01000000,%01000000,%11100000   ; 1
        db %11100000,%00100000,%11100000,%10000000,%11100000   ; 2
        db %11100000,%00100000,%11100000,%00100000,%11100000   ; 3
        db %10100000,%10100000,%11100000,%00100000,%00100000   ; 4
        db %11100000,%10000000,%11100000,%00100000,%11100000   ; 5
        db %11100000,%10000000,%11100000,%10100000,%11100000   ; 6
        db %11100000,%00100000,%00100000,%00100000,%00100000   ; 7
        db %11100000,%10100000,%11100000,%10100000,%11100000   ; 8
        db %11100000,%10100000,%11100000,%00100000,%11100000   ; 9
; the race order's little pictures and tables
flag_top_src:                       ; a mini chequered flag, 6 x 6 (2 x 3 checks,
        db 0,0,0,0              ; no pole - Grant), a pixel in from each side, centred
        db %01100110,%01100110,%00011000,%00011000   ; on the place's 2 cell rows
flag_bot_src:
        db %01100110,%01100110,%00000000,%00000000
        db 0,0,0,0
clock_top_src:                      ; a little clock: the best lap is this car's
        db 0,0,0,0
        db %00111100,%01000010,%10001001,%10001001
clock_bot_src:
        db %10001101,%10000001,%01000010,%00111100
        db 0,0,0,0
grid_order_src:   db 0, 1, 4, 3, 2  ; the starting grid: YOU, CYAN, WHITE, PINK, GREEN
car_colours_src:  db A_MSG, 0x68, 0x60, 0x58, 0x78  ; you red; cyan, green, magenta, white
; the cloth fill's tables of its own routines' addresses
cf_loaders_src:                     ; by (check row * 4 + y AND 3) * 2
        dw cf_l00,cf_l10,cf_l20,cf_l30,cf_l01,cf_l11,cf_l21,cf_l31
cf_slots_src:
        dw cf_s0,cf_s1,cf_s2,cf_s3,cf_s4,cf_s5,cf_s6,cf_s7
