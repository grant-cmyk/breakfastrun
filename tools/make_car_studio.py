"""Build docs/tools/car_studio.html: the car studio (Grant, 23 Nov 2026: "give me an editor to make a tweak to each
graphic") - every car's three drawn headings (0, 22.5, 45; 16 x 16: X ink, o the white body, . empty) as the game has
them today, from tools/car_art.txt and tools/pool_art.txt, painted in the page and kept in its database (cars/<key>) so
Claude reads them back. The page: docs/tools/car_studio.template.html."""
import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
text = open(os.path.join(HERE, 'car_art.txt')).read() + open(os.path.join(HERE, 'pool_art.txt')).read()
def art(name, h):
    m = re.search(r'== %s heading %s ==\n((?:[Xo.]{16}\n){16})' % (name, h), text)
    return m.group(1).split()
CARS = [('YOU', 'racer', 'Racer', 'Max - you'), ('TRUCK', 'sixwheeler', 'Six-wheeler', 'Frank'),
        ('GREEN', 'clown', 'Clown car', 'Spike'), ('PINK', 'tank', 'Tank', 'Bruno'), ('WHITE', 'dragster', 'Dragster', 'Jane'),
        ('CYAN', 'coupe', 'Coupe', 'spare'), ('SPECS', 'saloon', 'Saloon', 'spare')]
data = [dict(art=n, key=k, name=t, who=w, h0=art(n, '0'), h22=art(n, '22.5'), h45=art(n, '45')) for n, k, t, w in CARS]
page = open(os.path.join(ROOT, 'docs/tools/car_studio.template.html')).read().replace('__CARS__', json.dumps(data, separators=(',', ':')))
open(os.path.join(ROOT, 'docs/tools/car_studio.html'), 'w').write(page); print('docs/tools/car_studio.html: %d cars' % len(data))
