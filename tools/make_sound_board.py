"""docs/sound/sound_board.html: the game's key sounds to listen to in Claude (Grant, 23 Nov 2026: "lets work on sound. I would
like there to be more significant sounds. Can you play in Claude the key sounds played during the gameplay"). The clips are cut
from one race on the group C tape recorded in the emulator (zxdev wav_start / wav_save; the cut frames from the events logged
each TV frame) - docs/sound/race_clips/*.wav, 22,050 Hz. Usage: python3 tools/make_sound_board.py"""
import base64, html, os, wave
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
D = os.path.join(ROOT, 'docs', 'sound', 'race_clips')
CLIPS = [('start_music', 'Start music', 'Plays while the drivers’ faces animate, before the lights.', 'music'),
         ('start_lights', 'Start lights', 'Three beeps on red, a higher one on green, then your engine.', 'event'),
         ('engine', 'Engine, flat out', 'Your engine while you hold accelerate. It goes quiet when you lift.', 'loop'),
         ('crash', 'Car crash', 'You and another car bump.', 'event'),
         ('bonk', 'Hitting a cereal O', 'A falling note when you bounce off an O.', 'event'),
         ('oil', 'Oil spin', 'Today the same crash noise as a bump, then quiet while you spin.', 'event'),
         ('nos_pickup', 'NOS pickup', 'Driving over a NOS canister: a run of four notes.', 'event'),
         ('nos_fire', 'NOS fired', 'SPACE: a buzz that climbs steeply as the boost starts. (Until today the crew chief\u2019s blip cut it off at once.)', 'event'),
         ('lap', 'Lap complete', 'NEW: its own chime, a low note then a high one (ding-DING), louder than the other beeps.', 'event'),
         ('crew', 'Crew chief message', 'A short blip as his speech bubble opens.', 'event'),
         ('finish', 'Finish music', 'The chequered flag, then the podium.', 'music')]
IDEAS = [('Skid screech', 'There is none on this tape: the screech belongs to the old handling model. A screech while a car slides, harsher the further over its grip.'),
         ('Heavier crash', 'Twice as long, denser noise, and longer still for a hard hit than a rub.'),
         ('Engine with more body', 'More clicks a second, rising in pitch with speed, so you hear yourself accelerate.'),
         ('Oil spin sound', 'Its own sound: a whooshing fall in pitch through the spin, not the crash.'),
         ('NOS roar', 'A rough roar for the whole burn, not only the moment it fires.'),
         ('Overtaking', 'A short rising blip when you pass a car and a falling one when you are passed, with the faces.'),
         ('Final lap', 'A bigger fanfare as you start the last lap.')]
# (done 23 Nov 2026: the lap's own chime - "lap complete needs a unique beep"; the NOS whoosh no longer cut off)
def clicks(path):
    w = wave.open(path); d = w.readframes(w.getnframes()); sr = w.getframerate()
    win = sr // 50; hi = [v > 128 for v in d]
    return [sum(1 for j in range(i, min(i + win, len(hi) - 1)) if hi[j] != hi[j + 1]) for i in range(0, len(hi) - 1, win)], len(d) / sr
cards = []
for key, name, desc, kind in CLIPS:
    p = os.path.join(D, key + '.wav'); dens, secs = clicks(p)
    b64 = base64.b64encode(open(p, 'rb').read()).decode()
    cards.append('''<article class="clip %s">
  <div class="top"><h3>%s</h3><span class="len">%.1f s</span></div>
  <p>%s</p>
  <canvas class="strip" data-d="%s" width="300" height="40" aria-hidden="true"></canvas>
  <audio id="a-%s" controls preload="none" src="data:audio/wav;base64,%s"></audio>
</article>''' % (kind, html.escape(name), secs, html.escape(desc), ','.join(str(v) for v in dens), key, b64))
ideas = ''.join('<li><strong>%s.</strong> %s</li>' % (html.escape(a), html.escape(b)) for a, b in IDEAS)
page = '''<title>Breakfast Run Sound Board</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;600&display=swap">
<style>
/* Layout: a column of clip cards, each with the sound's click density drawn as a strip (a fiftieth of a second a bar), then the ideas. */
:root {
  --bg: #f4f6f8; --panel: #ffffff; --fg: #141a2b; --muted: #5a6378; --line: #d8dde6;
  --ink: #0000d7; --music: #00a0a0; --event: #d70000; --loop: #b88a00;
  --display: "Space Grotesk", "Segoe UI", system-ui, sans-serif; --text: "Inter", "Segoe UI", system-ui, sans-serif;
  --mono: "JetBrains Mono", ui-monospace, Menlo, Consolas, monospace;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg: #10141d; --panel: #181d29; --fg: #e8ebf3; --muted: #9aa3b8; --line: #2b3244; --ink: #6f8bff; --music: #3cc9c9; --event: #ff6a6a; --loop: #e0b440; color-scheme: dark } }
:root[data-theme="dark"] {
  --bg: #10141d; --panel: #181d29; --fg: #e8ebf3; --muted: #9aa3b8; --line: #2b3244; --ink: #6f8bff; --music: #3cc9c9; --event: #ff6a6a; --loop: #e0b440; color-scheme: dark }
body { background: var(--bg); color: var(--fg); font-family: var(--text); line-height: 1.5;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); padding-block: 24px 48px; }
.wrap { max-width: 880px; margin: 0 auto; display: grid; gap: 20px; }
h1 { font-family: var(--display); font-size: 1.7rem; margin: 0; text-wrap: balance; }
h2 { font-family: var(--display); font-size: 1.15rem; margin: 8px 0 0; }
.lede { color: var(--muted); margin: 4px 0 0; max-width: 65ch; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 12px; }
.clip { background: var(--panel); border: 1px solid var(--line); border-radius: 10px; padding: 14px; display: grid; gap: 8px; min-width: 0; border-top: 4px solid var(--event); }
.clip.music { border-top-color: var(--music); } .clip.loop { border-top-color: var(--loop); }
.top { display: flex; justify-content: space-between; align-items: baseline; gap: 8px; }
h3 { margin: 0; font-family: var(--display); font-size: 1rem; }
.len { font-family: var(--mono); font-size: 0.8rem; color: var(--muted); font-variant-numeric: tabular-nums; }
.clip p { margin: 0; color: var(--muted); font-size: 0.88rem; }
.strip { width: 100%; height: 40px; display: block; }
audio { width: 100%; }
.key { display: flex; flex-wrap: wrap; gap: 14px; font-size: 0.82rem; color: var(--muted); }
.key span::before { content: ""; display: inline-block; width: 10px; height: 10px; border-radius: 2px; margin-right: 6px; vertical-align: -1px; background: var(--c); }
.ideas { background: var(--panel); border: 1px solid var(--line); border-radius: 10px; padding: 16px 18px; }
.ideas ol { margin: 8px 0 0; padding-left: 1.3em; display: grid; gap: 6px; }
.note { font-size: 0.82rem; color: var(--muted); margin: 0; }
</style>
<div class="wrap">
  <header>
    <h1>Breakfast Run Sound Board</h1>
    <p class="lede">The sounds of one race on the group C tape, recorded from the emulator as the Spectrum’s beeper plays them. The strip under each shows how busy the sound is: one bar a fiftieth of a second, taller for more speaker clicks.</p>
  </header>
  <div class="key"><span style="--c: var(--music)">Music</span><span style="--c: var(--event)">A moment in the race</span><span style="--c: var(--loop)">Plays all the time</span></div>
  <div class="grid">@@CARDS@@</div>
  <section class="ideas">
    <h2>To make the sounds count for more</h2>
    <ol>@@IDEAS@@</ol>
    <p class="note">Every sound shares the processor with the picture, so each one is tried on the tape and measured for smoothness before it stays.</p>
  </section>
</div>
<script>
for (const c of document.querySelectorAll('canvas.strip')) {
  const d = c.dataset.d.split(',').map(Number), ctx = c.getContext('2d'), W = c.width = c.clientWidth * 2 || 600, H = c.height = 80;
  const col = getComputedStyle(c.closest('.clip')).borderTopColor, max = 40, w = W / d.length;
  ctx.fillStyle = col;
  d.forEach((v, i) => { const h = Math.max(v ? 4 : 1, Math.min(1, v / max) * (H - 4)); ctx.fillRect(i * w, H - h, Math.max(1, w - 1), h); });
}
for (const a of document.querySelectorAll('audio')) a.addEventListener('play', () => { for (const b of document.querySelectorAll('audio')) if (b !== a) b.pause(); });
</script>
'''.replace('@@CARDS@@', '\n'.join(cards)).replace('@@IDEAS@@', ideas)
open(os.path.join(ROOT, 'docs', 'sound', 'sound_board.html'), 'w').write(page)
print('docs/sound/sound_board.html: %d clips, %d KB' % (len(cards), len(page) // 1024))
