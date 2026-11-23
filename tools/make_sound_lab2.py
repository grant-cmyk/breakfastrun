"""SOUND LAB 2 (Grant, 23 Nov 2026: "Please can you work on alternative sounds to try - sounds need to be distinct, in the
background drone they all sound the same"). Each sound's alternatives, rendered as the game's own effect player would play them
- the interrupt's burst each TV frame: FLIPS speaker flips, each GAP counts apart (16 T a count, ~80 T a flip's own work; a
noise frame takes a random gap in a range) - over the engine recorded in a real race (docs/sound/race_clips/engine.wav), the two
flip streams together as the speaker has them. Each card gives what it costs: the most T-states it takes in a TV frame, as a
share of the frame (69,888 T), the time the picture loses while it plays. "Today" is the game's own sound, recorded.
Writes docs/sound/lab2/*.wav and docs/sound/sound_lab2.html. Usage: python3 tools/make_sound_lab2.py"""
import base64, html, os, random, wave
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
SR = 22050; T = 3500000; FRAME = 69888; FLIPT = 80; CT = 16
random.seed(7)
def rd(p):
    w = wave.open(p); d = w.readframes(w.getnframes()); return [v > 128 for v in d], w.getframerate()
bed, bsr = rd(os.path.join(ROOT, 'docs/sound/race_clips/engine.wav'))
bedflips = [i / bsr for i in range(len(bed) - 1) if bed[i] != bed[i + 1]]
LEN = 1.7; START = 0.45
def tone(g, n): return ('t', g, n)
def noise(lo, hi, n): return ('n', lo, hi, n)
SIL = ('s',)
def render(frames, duck=False):
    fl, worst = [], 0
    for k, fr in enumerate(frames):
        t = START + k * FRAME / T
        if fr[0] == 's': continue
        n = fr[-1]; used = 0
        for i in range(n):
            fl.append(t)
            g = fr[1] if fr[0] == 't' else random.randint(fr[1], fr[2])
            dt = FLIPT + CT * g; t += dt / T; used += dt
        worst = max(worst, used)
    end = START + len(frames) * FRAME / T
    b = [x for x in bedflips if x < LEN and not (duck and START <= x < end)]
    ev = sorted(b + fl)
    out = bytearray(); lvl = 0; j = 0
    for i in range(int(LEN * SR)):
        t = i / SR
        while j < len(ev) and ev[j] <= t: lvl ^= 1; j += 1
        out.append(228 if lvl else 28)
    return bytes(out), worst / FRAME
def ramp(a, b, n): return [round(a + (b - a) * i / max(1, n - 1)) for i in range(n)]
S = {}
S['crash'] = ('Car crash', 'today', [
    ('B', 'Thud', 'Low and heavy: a few widely spaced clicks that die away.', [noise(60, 140, f) for f in (5, 4, 4, 3, 3, 2, 2, 1, 1, 1)]),
    ('C', 'Crunch', 'A dense burst of noise that thins out.', [noise(3, 20, f) for f in (16, 14, 12, 10, 8, 6, 5, 4)]),
    ('D', 'Bang and rattle', 'One loud bang, then three short rattles.', [noise(3, 12, 22), SIL, noise(20, 60, 6), SIL, noise(20, 60, 5), SIL, noise(20, 60, 4)]),
])
S['skid'] = ('Skid screech', 'today', [
    ('B', 'Squeal', 'A high tyre squeal that wavers between two notes.', [tone(9 if i % 2 else 11, 12) for i in range(14)]),
    ('C', 'Chirp', 'Pulsed: chirp, gap, chirp - like tyres juddering.', [tone(7, 12) if i % 2 == 0 else SIL for i in range(14)]),
    ('D', 'Grind', 'A hiss with a low grind under it.', [noise(3, 8, 8) if i % 3 else noise(80, 120, 3) for i in range(14)]),
])
S['oil'] = ('Oil spin', 'today', [
    ('B', 'Whoosh down', 'A tone that falls all through the spin.', [tone(g, 8) for g in ramp(10, 60, 14)]),
    ('C', 'Wobble', 'Two notes swapping as the car turns round.', [tone(15 if (i // 2) % 2 == 0 else 45, 8) for i in range(14)]),
    ('D', 'Splash and slide', 'A splash of noise, then a falling slide.', [noise(3, 12, 16)] * 3 + [tone(g, 6) for g in ramp(20, 70, 11)]),
])
S['nos_pickup'] = ('NOS pickup', 'today', [
    ('B', 'Power-up', 'A quick climbing arpeggio, twice.', [tone(g, 8) for g in (40, 40, 30, 30, 22, 22, 16, 16) * 2]),
    ('C', 'Ding-ding', 'Two clear high notes.', [tone(12, 10)] * 6 + [SIL] * 2 + [tone(12, 10)] * 6),
])
S['nos_fire'] = ('NOS fired', 'today', [
    ('B', 'Roar', 'A low rough roar for most of a second.', [noise(20, 50, 6)] * 20),
    ('C', 'Jet', 'Noise that rises like a jet spooling up.', [noise(max(3, a), max(10, a + 20), 8) for a in ramp(40, 3, 18)]),
])
S['bonk'] = ('Hitting a cereal O', 'today', [
    ('B', 'Boing', 'A springy note that bounces down.', [tone(g, 6) for g in (20, 30, 40, 30, 40, 50, 40, 50, 60, 70)]),
    ('C', 'Knock knock', 'Two low knocks.', [tone(150, 2), SIL, SIL, tone(150, 2)]),
])
S['lap'] = ('Lap complete', 'today', [
    ('B', 'Fanfare', 'Three rising notes, the last held.', [tone(30, 14)] * 4 + [tone(22, 14)] * 4 + [tone(14, 14)] * 8),
    ('C', 'Triple bell', 'The same high note three times.', ([tone(12, 14)] * 4 + [SIL] * 2) * 3),
])
S['overtake'] = ('Overtaking (new)', None, [
    ('A', 'You pass: blip up', 'A short rising blip as you take a place.', [tone(g, 8) for g in ramp(30, 12, 6)]),
    ('B', 'You are passed: blip down', 'A short falling blip as you lose one.', [tone(g, 8) for g in ramp(12, 30, 6)]),
])
os.makedirs(os.path.join(ROOT, 'docs/sound/lab2'), exist_ok=True)
def wav(path, data):
    o = wave.open(path, 'wb'); o.setnchannels(1); o.setsampwidth(1); o.setframerate(SR); o.writeframes(data); o.close()
    return base64.b64encode(open(path, 'rb').read()).decode()
def card(key, letter, name, desc, b64, cost):
    c = '' if cost is None else '<span class="cost">%d%% of a frame</span>' % round(100 * cost)
    return ('<article class="alt%s"><div class="top"><span class="letter">%s</span><h3>%s</h3>%s</div><p>%s</p>'
            '<audio id="a-%s-%s" controls preload="none" src="data:audio/wav;base64,%s"></audio></article>') % (
            ' today' if letter == 'A' and cost is None else '', letter, html.escape(name), c, html.escape(desc), key, letter, b64)
secs = []
for key, (title, today, alts) in S.items():
    cards = []
    if today:
        p = os.path.join(ROOT, 'docs/sound/race_clips/%s.wav' % key)
        cards.append(card(key, 'A', 'Today', 'The game as it is, recorded in a race.', base64.b64encode(open(p, 'rb').read()).decode(), None))
    for letter, name, desc, frames in alts:
        data, cost = render(frames)
        cards.append(card(key, letter, name, desc, wav(os.path.join(ROOT, 'docs/sound/lab2/%s_%s.wav' % (key, letter)), data), cost))
    secs.append('<section><h2>%s</h2><div class="grid">%s</div></section>' % (html.escape(title), ''.join(cards)))
duck_data, _ = render(S['crash'][2][0][3], duck=True)
duck = card('duck', 'B', 'Thud, engine hushed', 'Crash B with the engine silent while it plays, so the crash stands clear of the drone.', wav(os.path.join(ROOT, 'docs/sound/lab2/duck_crash_B.wav'), duck_data), render(S['crash'][2][0][3])[1])
page = '''<title>Breakfast Run Sound Lab</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;600&display=swap">
<style>
/* Layout: one band per sound, its alternatives side by side as lettered cards; "Today" first in each. */
:root {
  --bg: #f4f6f8; --panel: #ffffff; --fg: #141a2b; --muted: #5a6378; --line: #d8dde6; --accent: #d70000; --today: #00a0a0;
  --display: "Space Grotesk", "Segoe UI", system-ui, sans-serif; --text: "Inter", "Segoe UI", system-ui, sans-serif;
  --mono: "JetBrains Mono", ui-monospace, Menlo, Consolas, monospace;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg: #10141d; --panel: #181d29; --fg: #e8ebf3; --muted: #9aa3b8; --line: #2b3244; --accent: #ff6a6a; --today: #3cc9c9; color-scheme: dark } }
:root[data-theme="dark"] {
  --bg: #10141d; --panel: #181d29; --fg: #e8ebf3; --muted: #9aa3b8; --line: #2b3244; --accent: #ff6a6a; --today: #3cc9c9; color-scheme: dark }
body { background: var(--bg); color: var(--fg); font-family: var(--text); line-height: 1.5;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); padding-block: 24px 48px; }
.wrap { max-width: 980px; margin: 0 auto; display: grid; gap: 22px; }
h1 { font-family: var(--display); font-size: 1.7rem; margin: 0; text-wrap: balance; }
h2 { font-family: var(--display); font-size: 1.1rem; margin: 0 0 8px; }
.lede { color: var(--muted); margin: 4px 0 0; max-width: 68ch; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 10px; }
.alt { background: var(--panel); border: 1px solid var(--line); border-radius: 10px; padding: 12px; display: grid; gap: 6px; min-width: 0; }
.alt.today { border-color: var(--today); }
.top { display: flex; align-items: baseline; gap: 8px; }
.letter { font-family: var(--display); font-weight: 700; color: var(--accent); font-size: 1.1rem; }
.alt.today .letter { color: var(--today); }
h3 { margin: 0; font-family: var(--display); font-size: 0.98rem; flex: 1; }
.cost { font-family: var(--mono); font-size: 0.72rem; color: var(--muted); white-space: nowrap; }
.alt p { margin: 0; color: var(--muted); font-size: 0.85rem; }
audio { width: 100%; }
.note { font-size: 0.82rem; color: var(--muted); margin: 0; max-width: 70ch; }
</style>
<div class="wrap">
  <header>
    <h1>Breakfast Run Sound Lab</h1>
    <p class="lede">Alternatives for each sound, so each one is clearly its own. A is the game today. B, C and D are played over the engine as it runs in a race, as the Spectrum’s effect player would play them. The figure on each is how much of a TV frame it takes while it sounds. Pick a letter for each.</p>
  </header>
  @@SECS@@
  <section><h2>Making room under the sounds</h2><div class="grid">@@DUCK@@</div>
  <p class="note">The engine could go quiet while any sound plays. That alone makes every sound stand out from the drone.</p></section>
</div>
<script>
for (const a of document.querySelectorAll('audio')) a.addEventListener('play', () => { for (const b of document.querySelectorAll('audio')) if (b !== a) b.pause(); });
</script>
'''.replace('@@SECS@@', '\n'.join(secs)).replace('@@DUCK@@', duck)
open(os.path.join(ROOT, 'docs/sound/sound_lab2.html'), 'w').write(page)
print('docs/sound/sound_lab2.html: %d KB' % (len(page) // 1024))
for key, (title, today, alts) in S.items():
    print(' ', title, ', '.join('%s %d%%' % (l, round(100 * render(fr)[1])) for l, n, d, fr in alts))
