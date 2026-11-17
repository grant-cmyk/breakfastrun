; TWO PLAYERS (twoplayer.asm): two routines that run from the free page under the stack (P2_LOWC). They are loaded in the
; start-up area and copied down by start_once, so they are written to run anywhere: no jumps but relative ones, and nothing
; of their own named by its address. The names the game calls them by are worked out below.
p2c_src:
; p2_take, each picture: is player 2 over the canister?  (as nos_take, strip.asm)
p2c_take:
        ld a,(two_p)
        or a
        ret z
        ld a,(p2_inv)
        cp 3
        ret nc
        ld a,(NOS_SHOW)
        or a
        ld de,8+10-NOS_A_X
        ld bc,8+10-NOS_A_Y
        jr z,p2t_1
        ld de,8+10-NOS_B_X
        ld bc,8+10-NOS_B_Y
p2t_1:
        ld hl,(P2+C_X)
        add hl,de
        ld a,h
        or a
        ret nz
        ld a,l
        cp 21
        ret nc
        ld hl,(P2+C_Y)
        add hl,bc
        ld a,h
        or a
        ret nz
        ld a,l
        cp 21
        ret nc
        ld hl,p2_inv
        jp nt_3                 ; (one more for them; the other canister comes out)

; p2c_dir: DE, BC = a step across and down (small) - A = the heading nearest it, of 8 (0 up, 16 right, 32 down, 48 left)
p2c_dir:
        ld a,e
        bit 7,d
        jr z,p2d_1
        neg
p2d_1:
        ld l,a                  ; L = how far across,
        ld a,c
        bit 7,b
        jr z,p2d_2
        neg
p2d_2:
        ld h,a                  ; H = how far down, signs apart
        add a,a
        cp l
        jr nc,p2d_3
        ld a,16                 ; across, mostly: right or left
        bit 7,d
        ret z
        ld a,48
        ret
p2d_3:
        ld a,l
        add a,a
        cp h
        jr nc,p2d_4
        xor a                   ; up or down
        bit 7,b
        ret nz
        ld a,32
        ret
p2d_4:
        ld a,8                  ; a diagonal
        bit 7,b
        jr nz,p2d_5
        ld a,24
p2d_5:
        bit 7,d
        ret z
        neg
        and 63
        ret

p2c_suf: db "STNDRDTHTH"           ; the panel's 1ST .. 5TH
p2c_end:
p2_take equ P2_LOWC+p2c_take-p2c_src
p2_dir  equ P2_LOWC+p2c_dir-p2c_src
p2p_suf equ P2_LOWC+p2c_suf-p2c_src
        if P2_LOWC+p2c_end-p2c_src > 0x5EA0
        .error twoplayer_pic.asm runs into the stack's room (0x5EA0 up)
        endif
