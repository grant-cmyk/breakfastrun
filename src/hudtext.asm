; the HUD's fixed text (kept at the top of memory: see TOPMEM in racer.asm)
txt_race_src:     db " RACE  ",0
txt_lapw_src:     db "LAP  /",'0'+LAPS,0
txt_of_src:       db "/",'0'+LAPS,0
txt_time_src:     db "TIME",0
txt_ready_src:    db "GET READY",0
txt_pressq_src:   db "PRESS Q",0
txt_lamp_src:     db "O",0
txt_go_src:       db "GO!",0
txt_final_src:    db "FINAL LAP!",0
txt_finished_src: db "FINISHED",0
txt_places_src:   db "1ST",0, "2ND",0, "3RD",0, "4TH",0, "5TH",0
txt_track_src:    db "BREAKFAST AT TIFFANY'S",0   ; track 1 (Grant, 10 Nov 2026): 22 = the window's width
txt_best_src:     db "BEST",0
txt_nobest_src:   db "--.-",0
txt_lapword_src:  db "LAP",0
car_names_src:    db "YOU  ",0, "CYAN ",0, "GREEN",0, "PINK ",0, "WHITE",0
txt_again_src:    db "RACE FINISHED  PRESS Q",0
