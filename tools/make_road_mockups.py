"""Mock-ups: a plain road, the tablecloth's checks only off the track (Grant,
10 Nov 2026: "so the track does not have the table chequered markings, only the
outside area - this makes the track easier to see"; "the chequered area hugs
around the map, like the corners"). Renders the real map (world.asm and
topdata.asm as built) through the 176 x 120 window, blue ink on cyan.
Writes docs/design/road_options.png, and (Grant: "the dotted effect ... less
visible in the road area") docs/design/road_dots_options.png, and (Grant: "the dots on the road area
specifically ... much lighter") docs/design/road_light_options.png."""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
src = open(os.path.join(ROOT, 'tests', 'drive_test.py')).read()
src = src[:src.index('with Racer(headless=True)')].replace("os.path.dirname(os.path.abspath(__file__))", repr(os.path.join(ROOT, 'tests')))
ns = {}; exec(src, ns)                                   # world (tile ink) and wmask (breakfast things)
world, wmask = ns['world'], ns['wmask']
wsrc = open(os.path.join(HERE, 'make_world.py')).read()
wns = {'__file__': os.path.join(HERE, 'make_world.py')}
exec(wsrc[:wsrc.index('road = road_mask(ROAD)')], wns)   # the track's path and road_mask()
ROAD, road_mask = wns['ROAD'], wns['road_mask']
H, W = world.shape
yy, xx = np.mgrid[0:H, 0:W]
dots = ((((xx >> 5) + (yy >> 5)) & 1) == 1) & (xx % 2 == 0) & (yy % 2 == 0)
def plain(width):
    return np.array(road_mask(width), dtype=bool)[:H, :W]
OPTS = [('NOW', 'checks everywhere', np.zeros((H, W), bool)),
        ('A', 'plain road, checks up to its edge', plain(ROAD)),
        ('B', 'plain out past the O\'s', plain(ROAD + 24)),
        ('C', 'checks only in the corners and infield', plain(ROAD + 72))]
INK, PAPER = (0, 0, 215), (0, 215, 215)
VIEWS = [(248 - 88 + 8, 352 - 60), (360, 250)]          # window top-left: the start straight, the bottom-right bend
S = 2
def render(clear):
    ink = world.astype(bool) | (dots & ~wmask & ~clear)
    return ink
fnt = ImageFont.load_default()
cw, ch = 176 * S, 120 * S
sheet = Image.new('RGB', (len(OPTS) * (cw + 16) + 16, 40 + len(VIEWS) * (ch + 12) + 12 + H // 2 + 20), (17, 18, 22))
d = ImageDraw.Draw(sheet)
for i, (tag, what, clear) in enumerate(OPTS):
    ink = render(clear)
    ox = 16 + i * (cw + 16)
    d.text((ox, 10), tag + ': ' + what, fill=(236, 235, 230), font=fnt)
    for j, (vx, vy) in enumerate(VIEWS):
        win = ink[vy:vy + 120, vx:vx + 176]
        rgb = np.where(win[..., None], np.array(INK, np.uint8), np.array(PAPER, np.uint8)).astype(np.uint8)
        sheet.paste(Image.fromarray(rgb).resize((cw, ch), Image.NEAREST), (ox, 32 + j * (ch + 12)))
    full = np.where(ink[..., None], np.array(INK, np.uint8), np.array(PAPER, np.uint8)).astype(np.uint8)
    small = Image.fromarray(full).resize((W // 2, H // 2), Image.BOX)      # (averaged: the dots read as a tint)
    sheet.paste(small, (ox, 32 + len(VIEWS) * (ch + 12) + 8))
    sd = ImageDraw.Draw(sheet)
    for vx, vy in VIEWS: sd.rectangle([ox + vx // 2, 32 + len(VIEWS) * (ch + 12) + 8 + vy // 2, ox + (vx + 176) // 2, 32 + len(VIEWS) * (ch + 12) + 8 + (vy + 120) // 2], outline=(255, 212, 0))
out = os.path.join(ROOT, 'docs', 'design', 'road_options.png')
sheet.save(out); print('wrote', os.path.normpath(out))

# ---- lighter dots on the road, rather than none
dark = (((xx >> 5) + (yy >> 5)) & 1) == 1
d25 = dark & (xx % 2 == 0) & (yy % 2 == 0)                              # today: 1 pixel in 4
d12 = dark & (((xx % 4 == 0) & (yy % 4 == 0)) | ((xx % 4 == 2) & (yy % 4 == 2)))   # 1 in 8, staggered
d06 = dark & (xx % 4 == 0) & (yy % 4 == 0)                              # 1 in 16
ROADA = plain(ROAD + 24)                                                 # the road and its O's
OPTS2 = [('NOW', 'dots 1 in 4 everywhere', d25),
         ('D', 'road dots 1 in 8, cloth as now', np.where(ROADA, d12, d25)),
         ('E', 'road dots 1 in 16, cloth as now', np.where(ROADA, d06, d25)),
         ('F', 'dots 1 in 8 everywhere (no cost)', d12)]
sheet = Image.new('RGB', (len(OPTS2) * (cw + 16) + 16, 40 + len(VIEWS) * (ch + 12) + 12 + H // 2 + 20), (17, 18, 22))
d = ImageDraw.Draw(sheet)
for i, (tag, what, dd) in enumerate(OPTS2):
    ink = world.astype(bool) | (dd & ~wmask)
    ox = 16 + i * (cw + 16)
    d.text((ox, 10), tag + ': ' + what, fill=(236, 235, 230), font=fnt)
    for j, (vx, vy) in enumerate(VIEWS):
        win = ink[vy:vy + 120, vx:vx + 176]
        rgb = np.where(win[..., None], np.array(INK, np.uint8), np.array(PAPER, np.uint8)).astype(np.uint8)
        sheet.paste(Image.fromarray(rgb).resize((cw, ch), Image.NEAREST), (ox, 32 + j * (ch + 12)))
    full = np.where(ink[..., None], np.array(INK, np.uint8), np.array(PAPER, np.uint8)).astype(np.uint8)
    sheet.paste(Image.fromarray(full).resize((W // 2, H // 2), Image.BOX), (ox, 32 + len(VIEWS) * (ch + 12) + 8))
out = os.path.join(ROOT, 'docs', 'design', 'road_dots_options.png')
sheet.save(out); print('wrote', os.path.normpath(out))

# ---- much lighter dots on the road only
d32 = dark & (((xx % 8 == 0) & (yy % 8 == 0)) | ((xx % 8 == 4) & (yy % 8 == 4)))  # 1 in 32, staggered
d64 = dark & (xx % 8 == 0) & (yy % 8 == 0)                                         # 1 in 64
edge = dark & (((xx % 32 == 0) | (yy % 32 == 0)) & (xx % 4 == 0) & (yy % 4 == 0))  # each check's outline, dotted
edge = edge | (dark & (((xx % 32 == 30) | (yy % 32 == 30)) & (xx % 4 == 2) & (yy % 4 == 2)))
OPTS3 = [('E', 'road 1 in 16 (from before)', np.where(ROADA, d06, d25)),
         ('G', 'road 1 in 32', np.where(ROADA, d32, d25)),
         ('H', 'road 1 in 64', np.where(ROADA, d64, d25)),
         ('I', 'road: only the checks\' outlines', np.where(ROADA, edge, d25))]
sheet = Image.new('RGB', (len(OPTS3) * (cw + 16) + 16, 40 + len(VIEWS) * (ch + 12) + 12 + H // 2 + 20), (17, 18, 22))
d = ImageDraw.Draw(sheet)
for i, (tag, what, dd) in enumerate(OPTS3):
    ink = world.astype(bool) | (dd & ~wmask)
    ox = 16 + i * (cw + 16)
    d.text((ox, 10), tag + ': ' + what, fill=(236, 235, 230), font=fnt)
    for j, (vx, vy) in enumerate(VIEWS):
        win = ink[vy:vy + 120, vx:vx + 176]
        rgb = np.where(win[..., None], np.array(INK, np.uint8), np.array(PAPER, np.uint8)).astype(np.uint8)
        sheet.paste(Image.fromarray(rgb).resize((cw, ch), Image.NEAREST), (ox, 32 + j * (ch + 12)))
    full = np.where(ink[..., None], np.array(INK, np.uint8), np.array(PAPER, np.uint8)).astype(np.uint8)
    sheet.paste(Image.fromarray(full).resize((W // 2, H // 2), Image.BOX), (ox, 32 + len(VIEWS) * (ch + 12) + 8))
out = os.path.join(ROOT, 'docs', 'design', 'road_light_options.png')
sheet.save(out); print('wrote', os.path.normpath(out))

# ---- H as the game can build it cheaply: the road map it already keeps (whole 8 x 8
# tiles, the road itself) decides where the dots thin out
surf = np.array(ns['surf'], dtype=np.uint8).reshape(H // 8, W // 8)
RT = np.repeat(np.repeat(surf == 0, 8, 0), 8, 1)
_t = ROADA.reshape(H // 8, 8, W // 8, 8).sum(axis=(1, 3)) >= 32           # road + the O's, whole tiles
RT3 = np.repeat(np.repeat(_t, 8, 0), 8, 1)
OPTS4 = [('H', 'road 1 in 64 (as approved)', np.where(ROADA, d64, d25)),
         ('H2', 'on the road map as it is', np.where(RT, d64, d25)),
         ('H3', 'road map out to the O\'s (to build)', np.where(RT3, d64, d25))]
sheet = Image.new('RGB', (len(OPTS4) * (cw + 16) + 16, 40 + len(VIEWS) * (ch + 12) + 12 + H // 2 + 20), (17, 18, 22))
d = ImageDraw.Draw(sheet)
for i, (tag, what, dd) in enumerate(OPTS4):
    ink = world.astype(bool) | (dd & ~wmask)
    ox = 16 + i * (cw + 16)
    d.text((ox, 10), tag + ': ' + what, fill=(236, 235, 230), font=fnt)
    for j, (vx, vy) in enumerate(VIEWS):
        win = ink[vy:vy + 120, vx:vx + 176]
        rgb = np.where(win[..., None], np.array(INK, np.uint8), np.array(PAPER, np.uint8)).astype(np.uint8)
        sheet.paste(Image.fromarray(rgb).resize((cw, ch), Image.NEAREST), (ox, 32 + j * (ch + 12)))
    full = np.where(ink[..., None], np.array(INK, np.uint8), np.array(PAPER, np.uint8)).astype(np.uint8)
    sheet.paste(Image.fromarray(full).resize((W // 2, H // 2), Image.BOX), (ox, 32 + len(VIEWS) * (ch + 12) + 8))
out = os.path.join(ROOT, 'docs', 'design', 'road_h_build.png')
sheet.save(out); print('wrote', os.path.normpath(out))
