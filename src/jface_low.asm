; JFACE's part kept at TOPMEM (copied there by start: the program and the room under 0x8000 are full on the trial tape; no
; jumps inside it, so it runs where it is copied to - pa_face_h is its equ in racer.asm): PA_FACE_H (pa_face_y, A = a happy or sad list) - YOUR
; HAPPY FACE, when you have won, is shown as it is and then mirrored, in turn, each time it comes round (Grant, 22 Nov 2026:
; "If the player wins then play the happy face horizontally mirrored"); every other list as ever.
pa_face_h_src:
        cp 1                    ; (list 1: YOUR happy - only the winner's face is ever happy)
        jp nz,pa_face
        ld hl,jf_hm
        inc (hl)
        bit 0,(hl)
        jp z,pa_face
        call pa_face            ; the happy face ...
        jp pfy_m                ; ... mirrored
