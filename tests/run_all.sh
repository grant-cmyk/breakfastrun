#!/bin/bash
# Every suite on every built track, against a build made with the options given - in a scratch copy, so the
# tapes in build/ are not touched.   Usage: tests/run_all.sh <name> [VAR=value ...]     e.g.  tests/run_all.sh looped LOOP=1
#   TRACKS="1 2 3 5" (default)   FULL=1: the long track tests (default QUICK=1)   JOBS=n
# Output: one line a suite; the logs are in $SCR/<name>/logs.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCR="${SCR:-${TMPDIR:-/tmp}/br_runs}"
NAME="$1"; shift
D="$SCR/$NAME"; rm -rf "$D"; mkdir -p "$D/build" "$D/logs"
cp -r "$ROOT/src" "$ROOT/tools" "$ROOT/tests" "$ROOT/build.sh" "$D/"
mkdir -p "$D/docs/design"; cp -r "$ROOT/docs/design/tracks" "$D/docs/design/" 2>/dev/null
find "$ROOT/build" -maxdepth 1 -type f \( -name '*.txt' -o -name '*.json' \) -exec cp {} "$D/build/" \;
cd "$D"
for T in ${TRACKS:-1 2 3 5}; do
  env "$@" TRACK=$T bash build.sh > logs/build$T.log 2>&1 || echo "BUILD FAILED track $T: $(grep -i error logs/build$T.log | head -2)"
done
Q=1; [ -n "$FULL" ] && Q=
{
for T in ${TRACKS:-1 2 3 5}; do
  if [ "$T" = 1 ]; then
    for s in arrow crew damage drift drive finish lapcount lead nos o objects plate setup stuck title skip copy; do
      f=${s}_test.py; [ "$s" = copy ] && f=copy_check.py
      echo "t1_$s python3 tests/$f"
    done
  else
    tt=track2_test.py; [ "$T" = 5 ] && tt=track5_test.py
    echo "t${T}_track env TRACK=$T QUICK=$Q python3 tests/$tt"
    echo "t${T}_arrow env TRACK=$T python3 tests/arrow_test.py"
    echo "t${T}_skip env TRACK=$T python3 tests/skip_test.py"
    echo "t${T}_copy env ZTAP=build/racer_track$T.tap ZSYM=build/racer_track$T.sym python3 tests/copy_check.py"
  fi
done
} | xargs -P "${JOBS:-4}" -L 1 bash -c 'n=$0; "$@" > logs/$n.log 2>&1; echo "$n: $(grep -c "^PASS" logs/$n.log) pass, $(grep -c "^FAIL" logs/$n.log) fail - $(grep -E "^RESULT|Traceback|Error" logs/$n.log | tail -1)"' | sort
echo "FAILS:"; grep -h "^FAIL" logs/*.log | cut -c1-200 | head -20
