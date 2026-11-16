"""Each built track's own data, measured from a build of it: python3 tools/track_sizes.py [tracks, default "1 2 3 5"]
(builds each in build/meas<n> with build.sh, reads the .sym and the generated world.asm)."""
import sys, re, os, subprocess
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
rows = []
for t in (sys.argv[1] if len(sys.argv) > 1 else '1 2 3 5').split():
    subprocess.run(['bash', os.path.join(ROOT, 'build.sh')], env=dict(os.environ, TRACK=t, BDIR='meas' + t, OUT='meas' + t), capture_output=True)
    d = {}
    for l in open(os.path.join(ROOT, 'build', 'meas%s.sym' % t)):
        q = l.split()
        if len(q) >= 3 and q[1] == 'EQU': d[q[0]] = int(q[2].rstrip('H'), 16)
    src = open(os.path.join(ROOT, 'build', 'meas%s' % t, 'src', 'world.asm')).read()
    ntiles = len(re.findall(r'defb.*; \d+\n', src[src.index('tiles:'):src.index('surface_map:')]))
    B = {b: d.get('me_' + b, 0) - d.get('mb_' + b, 0) for b in ('world', 'wp', 'ridx', 'omap', 'top', 'trow')}
    MAPH, NWP = d['MAPH'], d['NWP']
    rows_prog = d['surface_map'] - d['tiles'] - ntiles * 8
    out = (d['s1_end'] - d['s1_src'] - NWP) + (d['hi_end'] - d['hi_src']) + (d['s2_end'] - d['s2_src']) + (d['s3_end'] - d['s3_src']) + (d.get('tk_end', 0) - d.get('tk_src', 0))
    r = dict(track=t, MAPH=MAPH, NWP=NWP, tiles=ntiles * 8, ntiles=ntiles, rowlists=rows_prog + B['trow'] + out, rowidx=B['ridx'], surface=MAPH * 9, omap=B['omap'], waypoints=NWP * 4,
             masks=B['top'], arrows=NWP, minimap=d['MAP_H'] * 3, grid=140)
    r['total'] = sum(v for k, v in r.items() if k not in ('track', 'MAPH', 'NWP', 'ntiles'))
    rows.append(r)
keys = ['MAPH', 'NWP', 'ntiles', 'tiles', 'rowlists', 'rowidx', 'surface', 'omap', 'waypoints', 'masks', 'arrows', 'minimap', 'grid', 'total']
print('| | ' + ' | '.join('track %s' % r['track'] for r in rows) + ' |'); print('|---|' + '---|' * len(rows))
for k in keys: print('| %s | ' % k + ' | '.join(str(r[k]) for r in rows) + ' |')
