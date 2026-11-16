#!/bin/bash
# The tape with the choose screen (bash tools/build_choose.sh -> build/racer_choose.tap): its own test, then the game's
# suites on each of its three tracks, chosen on the choose screen (TSEL = steps right on the track step; the test
# harness in tests/drive_test.py walks the screen). Logs: build/multi/logs/ch_*.log.
# Usage: bash tests/choose_suites.sh        JOBS=n (default 8)   FULL=1: the long track tests
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
L=build/multi/logs; mkdir -p $L; rm -f $L/ch_*.log
export ZTAP="$ROOT/build/racer_choose.tap"
T1="ZSYM=$ROOT/build/racer_choose.sym TSRC=$ROOT/build/multi/t1/src TRACK=1"
T2="ZSYM=$ROOT/build/multi/pad_t2.sym TSRC=$ROOT/build/multi/t2/src TRACK=2 TSEL=1"
T3="ZSYM=$ROOT/build/multi/pad_t3.sym TSRC=$ROOT/build/multi/t3/src TRACK=3 TSEL=2"
Q=1; [ -n "$FULL" ] && Q=
{
for p in title track mem who extra two; do echo "ch_choose_$p python3 tests/choose_test.py $p"; done
# (not run here: setup_test - the set-up keys are gone on this tape, choose_test's extra part stands in for it; skip_test and
# objects_test - they load build/racer.tap by name)
for s in arrow crew damage drift drive finish lapcount lead nos o plate stuck title copy; do
  f=${s}_test.py; [ "$s" = copy ] && f=copy_check.py
  echo "ch_t1_$s env $T1 python3 tests/$f"
done
echo "ch_t1_again_drive env $T1 TSEL=3 python3 tests/drive_test.py"
echo "ch_unpack python3 tests/unpack_time.py $ROOT/build/racer_choose.tap $ROOT/build/racer_choose.sym"
echo "ch_t2_track env $T2 QUICK=$Q python3 tests/track2_test.py"
echo "ch_t2_arrow env $T2 python3 tests/arrow_test.py"
echo "ch_t3_track env $T3 QUICK=$Q python3 tests/track2_test.py"
echo "ch_t3_arrow env $T3 python3 tests/arrow_test.py"
} | xargs -P "${JOBS:-8}" -L 1 bash -c 'n=$0; "$@" > build/multi/logs/$n.log 2>&1; echo "$n: $(grep -c "^PASS" build/multi/logs/$n.log) pass, $(grep -c "^FAIL" build/multi/logs/$n.log) fail - $(grep -E "^RESULT|Traceback|Error" build/multi/logs/$n.log | tail -1)"' | sort
echo "FAILS:"; grep -H "^FAIL" $L/ch_*.log | sed 's|.*/logs/||' | cut -c1-260
