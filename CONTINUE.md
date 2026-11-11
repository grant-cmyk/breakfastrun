# CONTINUE - Breakfast Run

**Stamped:** 2026-11-11 15:16 SAST · machine: Claude cloud container · branch: main · commit: see `git log -1`
**Lifecycle:** Active

**Status:** Track 1, BREAKFAST AT TIFFANY'S, 1.35x (road 72 px, world 72 x 64 tiles, 46 waypoints,
lap ~19-20 s). Window 176 x 120 (blue on cyan, one colour pair - no clash) in an arcade bezel. Five of
Grant's cars at 20 x 20 (his heading-0 drawings; the 22.5 and 45 headings are Claude's drafts), race
numbers carved in; the race order still uses the 16 x 16 cars. Start lights: Q, red, red, red, then all
green - nobody moves till green. Your car handles with the Skid Lab's grip model (src/grip.asm); the
computer cars keep the old slide. Sound only when it matters: engine on Q, skid hiss, crash, NOS
pick-up chirp and fire rush, light beeps (tools/record_sound.py -> docs/design/engine_sound.wav).
NOS (start with one; SPACE; canisters A and B). Lap record kept across races, centred under the
race order. Driver strip: your face, inventory, the crew chief's radio, the crew chief.

**Speed:** lap work 211.6k T a picture (3 frames = 209.7k); 203 pictures at 3 TV frames, 64 at 4.
Biggest: cloth 45k, draw_car 31k, CPU physics 27k, tiles 27k, copy 25k, CPU thinking 16k, your
physics 14k. Measure with tests/profile_ticks.py (NOT sample_lap.py - unreliable).

**Next step:** build the layout proposals Grant approved (Layout Review,
https://claude.ai/artifact/GL5FkuruWucbShFekbkLp8): (1) your place and lap large in the message bar
while racing; (3) drop the per-row lap digit in the race order; (5-7) the strip faces at 16 x 16 in
2 x 2 cell panels, the bubble widened to columns 11-20 and fitted to rows 20-22, tail into the chief's
panel; (8) border flashes - green at GO, red on a crash, white for NOS. Mock-up built by
tools/make_layout_review.py. Then more speed before the extra window row Grant asked about (costed:
+6.5k T a picture, the copier +320 bytes into TOPMEM).

**Open:** drive_test fails 13 pictures a second off the grid with five big cars bunched (12.0);
Grant to touch up the big cars' 22.5 and 45 headings in the car editor
(https://claude.ai/artifact/2EqdSKs3fDfUqERTX9pTzL, Big cars mode).

**Tools:** car editor https://claude.ai/artifact/2EqdSKs3fDfUqERTX9pTzL (tools/make_car_editor.py:
cars, faces, big cars; left-click ink, right paper, double clear); Skid Lab
https://claude.ai/artifact/XWjkAzJ9kFKki9naPic3V8 (tools/make_skid_lab.py); tests: drive_test,
nos_test, o_test, profile_lap, profile_ticks; build: pasmo via the zxspectrum skill's build.sh, run
from src/. The retro plugin's new zx-toolkit skill (zxdev, Grant's own emulator) may suit timing and
debugging better than the zx package.

**Constraints:** memory - main area 370 bytes free (code_end 0xBE8E), 145 in the gap before sq4,
TOPMEM 15, start-up area 496; big cars 0-3 live below the program at 0x5F00 (loader CLEARs 24319).
Strip blocks: E holds the 64-row index. Code before hud.asm must not use equs defined later
(pasmo first-pass values). The interrupt may land while the cloth fill has SP in the buffer: it may
push only 6 bytes (it uses A, H, L only). Road option H is on branch trial-road-h (too slow).

**Waiting on Grant:** the layout build above is approved and ready to start; touch-ups to the big
cars' angled headings; confirm the repo should be public; push a tag for this build from his machine
(cloud sessions cannot push tags).

Track names for later tracks (verified): The Breakfast Club, Green Eggs and Ham, The Dish Ran Away
with the Spoon, Paddington's Marmalade, Goldilocks' Porridge, Breakfast in America.
Full history: PROJECT-LOG.md · Notion row: https://app.notion.com/p/41342c9abb32810d8672e5281550b1ac
