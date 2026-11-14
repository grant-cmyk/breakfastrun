#!/usr/bin/env bash
# Build Breakfast Run: build/racer.tap (with its BASIC loader), racer.bin and racer.sym.
# Usage: build.sh [small|big]     the cars (default small; the big cars need a memory plan first)
# Run from anywhere. Needs pasmo and the retro plugin's zxspectrum skill (its build.sh).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
CARSOPT="${1:-small}"
CARS="$CARSOPT" python3 "$ROOT/tools/make_data.py" | grep -i "cars:"
cd "$ROOT/src"
B=$(ls /root/.claude/plugins/synced/*/retro/skills/zxspectrum/scripts/build.sh 2>/dev/null | head -1)
B=${ZX_BUILD:-$B}
bash "$B" asm racer.asm ../build/racer.tap racer
pasmo racer.asm ../build/racer.bin ../build/racer.sym
grep -i -E "^(code_end|init_end)\s" ../build/racer.sym
