; VARS_D0 (the breakfast fast tapes: MAPW40 with MAPHUD): the 90 bytes of the back buffer's D0 strip (rows 168-191,
; D0A0-D0F9 - nothing is drawn there) held the 24-wide map's ink; with the 40-wide map's ink under 0x8000 they are free,
; and these live there - no bytes in the program (22 Nov 2026, for the finish line's judge: the tape was full). Each is
; set when a race starts (lj_new, spill_new, cn_new), nothing is kept from loading.
VD0     equ BUF+0x10A0
line_at   equ VD0                ; each car (by kind): its place over the line at the end of its last lap (0: not yet)
line_cnt  equ VD0+5              ; cars over so far
line_px   equ VD0+6              ; each car's x at the last picture (2 bytes each)
spill_on  equ VD0+16             ; OIL: which of the 8 spots has the spill
spill_lap equ VD0+17             ;   your lap when it was picked
spill_spin equ VD0+18            ;   each car: pictures of spin (and then immunity) left
spill_rec equ VD0+23             ;   the record draw_car draws a spill from (C_SIZE: 28)
cn_burn   equ VD0+51             ; CNOS: pictures of NOS left
cn_wait   equ VD0+52             ;   pictures before the next may light
cn_who    equ VD0+53
cn_k      equ VD0+54
cn_sv     equ VD0+55             ;   6 bytes
cn_used   equ VD0+61             ;   5 bytes
cn_end    equ VD0+66
wk_ka     equ VD0+66             ; WEIGHT (weight.asm): the bump's working values
wk_kb     equ VD0+67
wk_ax     equ VD0+68
wk_ca     equ VD0+69
wk_cb     equ VD0+70
wk_kav    equ VD0+71             ;   (2 bytes each from here)
wk_kbv    equ VD0+73
wk_va     equ VD0+75
wk_vb     equ VD0+77
wk_ta     equ VD0+79
wk_tb     equ VD0+81
wk_big    equ VD0+83
wk_sm     equ VD0+85
wk_who    equ VD0+87
jf_hm     equ VD0+88             ; JFACE: your happy face this time mirrored or not (bit 0)
; (VD0+89 is the last of the 90)
; (spill_rec is laid out for 28-byte car records: racer.asm's C_SIZE - checked at the end of racer.asm)
