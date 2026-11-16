"""Today's memory map, measured from a build's .sym and .bin: bytes used and free in each area.
    python3 tools/memmap.py build/racer.sym [more .sym ...]
A gap's free bytes are counted from the .bin (pasmo fills what nothing was assembled into with zeros: the zeros at the
end of an area are its free bytes - a table that really ends in zeros would be counted too, so 'about')."""
import sys, os
def load(p):
    d = {}
    for l in open(p):
        q = l.split()
        if len(q) >= 3 and q[1] == 'EQU': d[q[0].lower()] = int(q[2].rstrip('H'), 16)
    return d
rows = {}
order = []
for p in sys.argv[1:]:
    s = load(p); b = open(p[:-4] + '.bin', 'rb').read(); org = 0x5F00
    def tail0(end):                      # zeros just below address `end` in the image
        n = 0
        while end - 1 - n >= org and b[end - 1 - n - org] == 0: n += 1
        return n
    top_used = s['high_end'] - s['high_src']
    r = [
        ('Title variables and tables 5B00-5DFF', 0x300, 0x5E00 - (s['td'] + s['td_end2'] - s['td_src']) if 'td_end2' in s else None),
        ('Stack page 5E00-5EFF (deepest seen 56)', 0x100, None),
        ('Car frames 5F00- (80 frames)', s['title'] - 0x5F00 if 'title' in s else None, 0),
        ('Title, plate, podium code, to TOPMEM', s['topmem'] - s.get('title', 0x7200), tail0(s['topmem'])),
        ('TOPMEM data (masks, HUD text, row lists, grid)', s['lowtab'] - s['topmem'], s['lowtab'] - s['topmem'] - top_used),
        ('LOWTAB 5 x 128 + 64 (messages, constants)', 704, sum(128 - (s[k + '_end'] - s[k + '_src']) for k in ('bufd', 'buff', 'bufh', 'bufg', 'bufe') if k + '_end' in s)),
        ('Program 8000-BFFF', 0x4000, 0xC000 - s['code_end']),
        ('Start-up area C000- (used once; limit %04X)' % s['mapdat'], s['mapdat'] - 0xC000, s['mapdat'] - s['init_end']),
        ('Strip D0: mini-map ink (90)', 90, 90 - s['map_h'] * 3),
        ('Strip D1: arrows table + row lists (90)', 90, 90 - (s['s1_end'] - s['s1_src'])),
        ('Strip D2: row lists (32)', 32, 32 - (s['s2_end'] - s['s2_src'])),
        ('Strips D3-D7: arrow pictures (5 x 90)', 450, 0),
        ('5B16 (title a_sav): row lists (54)', 54, 54 - (s['s3_end'] - s['s3_src'])),
        ('Stack page 5E46: row lists (90, track 5 only)', 90, 90 - (s['tk_end'] - s['tk_src']) if 'tk_end' in s else None),
        ('Shift tables D800-E7FF', 4096, 0),
        ('Screen copy routine from E800', (s['himem'] - 0xE800) if not s.get('opt_loop') else 0x200, 0),
        ('Freed above a looped copy routine', (s['himem'] - 0xEA00) if s.get('opt_loop') else 0, (s['himem'] - 0xEA00 - (s.get('hp_end', 0) - s.get('hp_src', 0))) if s.get('opt_loop') else 0),
        ('HIMEM %04X-FFF3: row lists' % s['himem'], 0xFFF4 - s['himem'], 0xFFF4 - s['himem'] - (s['hi_end'] - s['hi_src'])),
    ]
    for name, size, free in r:
        key = name.split(' (limit')[0] if 'Start-up' in name else name
        if key not in rows: rows[key] = []; order.append(key)
        rows[key].append((size, free))
names = [os.path.basename(p)[:-4] for p in sys.argv[1:]]
print('| Area | ' + ' | '.join('%s size / free' % n for n in names) + ' |'); print('|---|' + '---|' * len(names))
for k in order:
    print('| %s | ' % k + ' | '.join('%s / %s' % ('-' if a is None else a, '-' if f is None else f) for a, f in rows[k]) + ' |')
tot = [sum(f for k in order for (a, f) in [rows[k][i]] if f and 'Start-up' not in k) for i in range(len(names))]
print('| **Free while racing (start-up area not counted)** | ' + ' | '.join('**%d**' % t for t in tot) + ' |')
