"""SEVERAL TRACKS IN ONE LOAD - the proof build (docs/design/OPTIMISATION-PLAN.md).
    python3 tools/make_multi.py [tracks]        default "1 2"  ->  build/racer_2tracks.tap (.bin, .sym)
                                                T at the title picks the next track; 1 starts the race

How: each track is built by itself with the same options (MULTI=1: the looped screen copy, the race order's
cars from their frames) and with every block of track data padded to the longest, so that every routine and
every table sits at the same address whichever track it is. Each build is run to its title screen in the
emulator and its memory read twice, some seconds apart. A byte that stays put in each build and is not the
same in all of them belongs to a track: its tiles, row lists, surface, O map, waypoints, masks, arrows' table,
mini-map, grid - and the numbers the assembler built into the code (MAPH, NWP, the start, the cans' places).
Long stretches of such bytes are packed with ZX0, short ones kept as they are; the lot, with the unpacker
(src/hp.asm), loads with the first track's game and is copied above the looped copy routine.
ZX0: needs the `zx0` program (github.com/einar-saukas/ZX0, built with gcc) - ZX0=path, or on the PATH."""
import os, sys, subprocess, shutil, re
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
TRACKS = [int(v) for v in (sys.argv[1] if len(sys.argv) > 1 else '1 2').split()]
NAMES = {1: "TRACK 1  TIFFANY'S  ", 2: 'TRACK 2  THE CLUB   ', 3: 'TRACK 3  GREEN EGGS ', 5: 'TRACK 5  THE FRIDGE '}
OUTN = os.environ.get('OUT', 'racer_%dtracks' % len(TRACKS))
ZX0 = os.environ.get('ZX0') or shutil.which('zx0') or '/tmp/claude-0/-home-user/fffe8284-32d1-5fde-8a48-51a919ed51ce/scratchpad/ext/ZX0/zx0'
M = os.path.join(ROOT, 'build', 'multi'); os.makedirs(M, exist_ok=True)
BLOCKS = ['world', 'wp', 'ridx', 'omap', 'top', 'trow']
EXTRA = [v for v in os.environ.get('MULTI_ENV', '').split() if '=' in v]      # more build options, e.g. "FLIP=1"

def syms(path):
    d = {}
    for l in open(path):
        q = l.split()
        if len(q) >= 3 and q[1] == 'EQU': d[q[0]] = int(q[2].rstrip('H'), 16)
    return d
def build(t, tag, pre):
    env = dict(os.environ, MULTI='1', LOOP='1', TRACK=str(t), BDIR='multi/t%d' % t, OUT='multi/%s_t%d' % (tag, t), PREASM=pre)
    env.update(dict(v.split('=', 1) for v in EXTRA))
    r = subprocess.run(['bash', os.path.join(ROOT, 'build.sh')], env=env, capture_output=True, text=True)
    if 'ERROR' in r.stdout + r.stderr or r.returncode:
        raise SystemExit('track %d (%s) did not build:\n%s' % (t, tag, (r.stdout + r.stderr)[-1500:]))
    return syms(os.path.join(M, '%s_t%d.sym' % (tag, t)))
def put(name, text, mode='w'):
    with open(os.path.join(M, name), mode) as f: f.write(text)
def hp(data_asm, sy, name):
    """assemble src/hp.asm for HP with this data; -> its bytes"""
    d = os.path.join(M, 'hp'); os.makedirs(d, exist_ok=True)
    shutil.copy(os.path.join(ROOT, 'src', 'hp.asm'), d)
    open(os.path.join(d, 'hp_syms.asm'), 'w').write(''.join('%s equ 0x%04X\n' % (k, sy[v]) for k, v in (('HP', 'HP'), ('K_SCAN', 'k_scan'), ('K_UP', 'k_up'), ('T_PROMPT', 't_prompt'))))
    open(os.path.join(d, 'hp_data.asm'), 'w').write(data_asm)
    r = subprocess.run(['pasmo', 'hp.asm', name, name + '.sym'], cwd=d, capture_output=True, text=True)
    if 'ERROR' in r.stdout + r.stderr: raise SystemExit('hp.asm: ' + r.stdout + r.stderr)
    return open(os.path.join(d, name), 'rb').read(), syms(os.path.join(d, name + '.sym'))

# ---- 1. each track by itself, no padding: how long is each block? ----
put('multi_pads.asm', 'MP_ON   equ 0\n'); put('hp.bin', '', 'w')
pre = 'cp %s/multi_pads.asm %s/hp.bin .' % (M, M)
size = {b: 0 for b in BLOCKS}; first = {}
for t in TRACKS:
    sy = build(t, 'measure', pre); first[t] = sy
    for b in BLOCKS: size[b] = max(size[b], sy['me_' + b] - sy['mb_' + b])
    print('track %d alone: program ends %04X, blocks %s' % (t, sy['code_end'], {b: sy['me_' + b] - sy['mb_' + b] for b in BLOCKS}))
put('multi_pads.asm', 'MP_ON   equ 1\n' + ''.join('MP_%s equ %d\n' % (b.upper(), size[b]) for b in BLOCKS))
# ---- 2. padded, with a stand-in at HP (JP k_scan): the same layout for every track? ----
stub, _ = hp('NTRK equ 1\ntrk_names:\ntrk_tab:\n', first[TRACKS[0]], 'stub.bin')
stub = bytes([0xC3, first[TRACKS[0]]['k_scan'] & 255, first[TRACKS[0]]['k_scan'] >> 8])
open(os.path.join(M, 'hp.bin'), 'wb').write(stub)
S = {t: build(t, 'pad', pre) for t in TRACKS}
base = S[TRACKS[0]]
ok_move = re.compile(r'^(row_\d+|NOS_\w+|surface_map|tmask_src|tmask|s\d_end|s\d_src|hi_src|hi_end|tk_\w+|MAP_BUF|minimap_end|arrow_tab_end|me_\w+)$', re.I)
for t in TRACKS[1:]:
    moved = [k for k in base if k in S[t] and S[t][k] != base[k] and 0x5B00 <= base[k] <= 0xFFFF and not ok_move.match(k)]
    code_moved = [k for k in moved if base[k] < base['init_end'] and not (base['code_end'] <= base[k])]
    print('track %d padded: program ends %04X (track %d: %04X); labels at another address: %d in the program %s' % (t, S[t]['code_end'], TRACKS[0], base['code_end'], len(code_moved), sorted(code_moved)[:12]))
    assert S[t]['code_end'] == base['code_end'], 'the padded builds are not the same length'

# ---- 3. run each to its title, read the memory twice ----
from zx._spectrum import Spectrum
def dumps(t):
    out = []
    with Spectrum(headless=True) as sp:
        sp.load_tape(os.path.join(M, 'pad_t%d.tap' % t)); n = 0
        while sp.read8(0x5800 + 8 * 32 + 10) != 0x7A and n < 600: sp.run(duration=0.1, fast_forward=True); n += 1
        assert n < 600, 'track %d: no title screen' % t
        for wait in (1.0, 3.3, 4.9):
            sp.run(duration=wait, fast_forward=True); out.append(bytes(sp.read(0, 65536)))
    return out
DU = {t: dumps(t) for t in TRACKS}
def stable(a): return all(DU[t][0][a] == DU[t][1][a] == DU[t][2][a] for t in TRACKS)
AREAS = [(0x5B00, 0x5E00), (0x5F00, 0xC000)] + [(0xD0A0 + 256 * k, 0xD0FA + 256 * k) for k in range(8)] + [(base['HIMEM'], 0xFFF4)]
if any(t == 5 for t in TRACKS): AREAS.append((0x5E46, 0x5E46 + 90))
D = [a for lo, hi in AREAS for a in range(lo, hi) if len({DU[t][0][a] for t in TRACKS}) > 1]
unst = [a for a in D if not stable(a)]
D = [a for a in D if stable(a)]
print('bytes that belong to a track: %d (and %d that differ but change by themselves - variables: left alone)' % (len(D), len(unst)))
# stretches: join over gaps of up to 3 bytes that are the same on every track (never over a variable)
runs = []
for a in D:
    if runs and a - runs[-1][1] <= 4 and all(stable(x) for x in range(runs[-1][1], a)): runs[-1][1] = a + 1
    else: runs.append([a, a + 1])
# long stretches near each other pack better as one: join over gaps of up to 48 stable bytes, each side 24 or more
big = []
for lo, hi in runs:
    if big and lo - big[-1][1] <= 48 and all(stable(x) for x in range(big[-1][1], lo)) and (hi - lo >= 24 or big[-1][1] - big[-1][0] >= 24): big[-1][1] = hi
    else: big.append([lo, hi])
packed = [r for r in big if r[1] - r[0] >= 20]; raw = [r for r in big if r[1] - r[0] < 20]
lab = sorted((v, k) for k, v in base.items() if 0x5B00 <= v <= 0xFFFF)
def near(a):
    import bisect
    i = bisect.bisect_right(lab, (a, '~')) - 1
    return '%s+%d' % (lab[i][1], a - lab[i][0]) if i >= 0 else '?'
print('%d packed stretches (%d bytes), %d short ones (%d bytes):' % (len(packed), sum(h - l for l, h in packed), len(raw), sum(h - l for l, h in raw)))
for lo, hi in packed: print('   %04X-%04X %5d  %s' % (lo, hi - 1, hi - lo, near(lo)))
print('   short ones at: ' + ', '.join(sorted({near(lo).split('+')[0] for lo, hi in raw}))[:1500])
# ---- 4. pack ----
data = 'NTRK equ %d\ntrk_names:\n' % len(TRACKS) + ''.join('        db "%s",0\n' % NAMES[t].replace('"', "'")[:20].ljust(20) for t in TRACKS)
data += 'trk_tab:\n' + ''.join('        dw trk_%d\n' % t for t in TRACKS)
report = []
for t in TRACKS:
    img = DU[t][0]; tot = 0; data += 'trk_%d:\n' % t
    for i, (lo, hi) in enumerate(packed):
        f = os.path.join(M, 'hp', 't%d_%d' % (t, i)); open(f, 'wb').write(img[lo:hi])
        if os.path.exists(f + '.zx0'): os.remove(f + '.zx0')
        subprocess.run([ZX0, '-q', f, f + '.zx0'] if False else [ZX0, f, f + '.zx0'], capture_output=True, check=True)
        z = open(f + '.zx0', 'rb').read(); tot += len(z) + 2
        data += '        dw 0x%04X\n        incbin "t%d_%d.zx0"\n' % (lo, t, i)
    data += '        dw 0\n'
    for lo, hi in raw:
        data += '        dw 0x%04X\n        db %d,%s\n' % (lo, hi - lo, ','.join(str(b) for b in img[lo:hi])); tot += 3 + hi - lo
    data += '        dw 0\n'; tot += 4
    report.append((t, sum(h - l for l, h in packed) + sum(h - l for l, h in raw), tot))
blob, hs = hp(data, base, 'hp.bin')
shutil.copy(os.path.join(M, 'hp', 'hp.bin'), os.path.join(M, 'hp.bin'))
code = hs['hp_code_end'] - base['HP']
print('above the copy routine, from %04X: %d bytes of code and unpacker, then the tracks:' % (base['HP'], code))
for t, rawn, pk in report: print('   track %d: %d bytes of its own -> %d packed' % (t, rawn, pk))
room = base['HIMEM'] - base['HP']
print('   in all %d of %d bytes: %d free up there' % (len(blob), room, room - len(blob)))
# ---- 5. the tape: the first track's game with the lot ----
fin = build(TRACKS[0], 'final', pre)
bad = [k for k in base if k not in ('hp_end',) and fin.get(k) != base[k]]
assert not bad, 'the final build moved %s' % bad[:8]
for ext in ('tap', 'bin', 'sym'): shutil.copy(os.path.join(M, 'final_t%d.%s' % (TRACKS[0], ext)), os.path.join(ROOT, 'build', OUTN + '.' + ext))
import json
json.dump(dict(tracks=TRACKS, packed=packed, raw=raw, report=report, code=code, free=room - len(blob), program_free=0xC000 - base['code_end']), open(os.path.join(M, 'multi.json'), 'w'))
print('build/%s.tap: program %d bytes free; the tracks\' own folders: build/multi/t<n>/src' % (OUTN, 0xC000 - base['code_end']))
