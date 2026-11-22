; =====================================================================
; JFACE - THE FACES MOVE WITH THE MUSIC (JFACE=1, breakfast race tapes; Grant, 22 Nov 2026: "During the music - animate
; the faces - at the start and end of a race", and "at the chequered flag use the mirrored picture of the player racer
; looking left and right and then the big smile - not the picture facing the front").
;   - The jingle player (plateco.asm jb_1) calls jin_key each step in place of jb_key. Every JF_STEPS steps (two beats)
;     the faces take a step, as they do after the music: at the start the race order's (tw_anim, plate_slow.asm - on with
;     RT_EYES), at the chequered flag the podium's (pod_anim's three, title3.asm). The step is the music's own count, as
;     nothing else runs while it plays (the TV frame count does not move: interrupts are off).
;   - YOUR face's other look is your everyday face MIRRORED - looking the other way - not the face from the front (the
;     "eyes" list), and so for every driver whose face changes when mirrored (JF_MIRROR): pa_face_y, from pa_car
;     (title3.asm). Everywhere pa_car draws: the podium (left, right, left, the big smile - or sad), the race order before
;     the start, the title's row.
; =====================================================================
JF_STEPS equ 8
JF_MIRROR equ 0x19               ; the cars whose look is their face mirrored: YOU, PINK (Bruno), WHITE (Jane) - bits 0, 3, 4

jin_key:                        ; (jb_1, A = the step; HL the tune - kept) then jb_key as ever
        push af
        and JF_STEPS-1
        jr nz,jk_1
        pop af
        push af
        push hl
        rrca
        rrca
        rrca
        and 0x1F
        ld e,a                  ; E = the faces' step
        ld a,(race_over)
        or a
        jr nz,jk_pod
        ld a,(race_on)          ; (the start: before the lights go green)
        or a
        call z,twa_go
        jr jk_0
jk_pod: ld d,1                  ; (the podium: as pod_anim does - the winner happy, second and third sad)
        ld hl,order
        ld bc,0x070C
        call pa_one
        ld bc,0x0808
        call pa_one
        ld bc,0x0910
        call pa_one
jk_0:   pop hl
jk_1:   pop af
        jp jb_key

pa_face_y:                      ; (pa_car, A = a list of faces_mood: car x 3 + 0 look, 1 happy, 2 sad; B, C the face's cells):
        ld e,a                  ; a car in JF_MIRROR takes its look as its everyday face (just drawn there) MIRRORED (Grant,
        ld d,0xFF               ; 22 Nov 2026: "Each players image can basically have a horizontal mirror, a happy and a sad
pfy_1:  inc d                   ; face"); the two whose faces are near alike both ways round keep their own eyes - mirrored,
        sub 3                   ; the shades face changes 14 pixels and the asleep one none)
        jr nc,pfy_1             ; (D = the car, A = its mood - 3)
        cp 0xFD
        ld a,e
        jp nz,pa_face
        ld a,JF_MIRROR
pfy_2:  rrca
        dec d
        jp p,pfy_2              ; (CY: the car's bit)
        ld a,e
        jp nc,pa_face
        push bc
        call fm_cell
        pop bc
        push bc
        inc b
        call fm_cell
        pop bc
        ret
fm_cell:                        ; the 2 x 8 bytes at cell B, C mirrored: each byte's bits the other way round (rev_tab), the
        call cell_addr          ; two bytes changed over
        ld d,8
fm_1:   ld b,rev_tab/256
        ld c,(hl)
        ld a,(bc)
        ld e,a
        inc l
        ld c,(hl)
        ld a,(bc)
        ld (hl),e
        dec l
        ld (hl),a
        inc h
        dec d
        jr nz,fm_1
        ret
