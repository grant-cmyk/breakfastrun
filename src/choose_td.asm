; THE CHOOSE SCREEN's records, card and texts (src/choose.asm). They sit at the end of the table block that start_once
; copies to TD (0x5B4C), where the seven drivers' mood lists would be if they had not gone above the copy routine: use
; them as TD + name_src - td_src (choose.asm has the equs).
ch_r_trk_src: dw ch_t_trk
        db 11,3
        dw ch_d_trk
ch_r_who_src: dw ch_t_who
        db 10,7
        dw ch_d_who
ch_r_car_src: dw ch_t_car
        db 13,7
        dw ch_d_car
ch_r_ex_src: dw ch_t_x
        db 11,3
        dw ch_d_ex
ch_script_src:                      ; the card, as the title's menu: a green head, white under it
        db 0x81,3,22,26,T_CARD  ; rows 1-22, columns 3-28
        db 0x81,3,4,26,0x60
        db 12,10,"<",0
        db 12,22,">",0
        db 20,5,"LEFT / RIGHT TO CHOOSE",0
        db 21,6,"ACCELERATE TO SELECT",0
        db 0xFF
ch_t_trk_src: db "TRACK",0
ch_t_who_src: db "DRIVER",0
ch_t_car_src: db "CAR",0
ch_t_x_src: db "EXTRA",0
ch_t_pl_src: db "PLAYER 1",0
ch_t_ex_src: db "ACCELERATION",0,"GRIP           ",0,"SPEED",0   ; (GRIP's row is the arrows' row: its spaces cover them)
pd_names_src:                       ; the seven drivers (the first was YOU: now that a player can be any of them, he has a name)
        db "MAX",0,"FRANK",0,"SPIKE",0,"BRUNO",0,"JANE",0,"SPECS",0,"DOT",0
