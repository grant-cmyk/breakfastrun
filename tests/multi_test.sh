#!/bin/bash
# The tape with several tracks (tools/make_multi.py -> build/racer_2tracks.tap): the suites that take a tape
# from ZTAP/ZSYM, on each track chosen with T at the title (TSEL = presses of T), and on track 1 again after
# going round all the tracks. Logs: build/multi/logs.   Usage: bash tests/multi_test.sh [tape name, default racer_2tracks]
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
N="${1:-racer_2tracks}"; L=build/multi/logs; mkdir -p $L
export ZTAP="$ROOT/build/$N.tap"
T1="ZSYM=$ROOT/build/$N.sym TSRC=$ROOT/build/multi/t1/src"
T2="ZSYM=$ROOT/build/multi/pad_t2.sym TSRC=$ROOT/build/multi/t2/src TRACK=2 TSEL=1"
T3="ZSYM=$ROOT/build/multi/pad_t3.sym TSRC=$ROOT/build/multi/t3/src TRACK=3 TSEL=2"
NT=2; [ "$N" = racer_3tracks ] && NT=3
{
echo "t1_drive env $T1 python3 tests/drive_test.py"
echo "t1_arrow env $T1 TRACK=1 python3 tests/arrow_test.py"
echo "t1_copy env $T1 python3 tests/copy_check.py"
echo "t1_again_drive env $T1 TSEL=$NT python3 tests/drive_test.py"
echo "mem python3 tests/multi_mem_check.py $N"
echo "unpack python3 tests/unpack_time.py $ROOT/build/$N.tap $ROOT/build/$N.sym"
echo "t2_track env $T2 QUICK=${QUICK-1} python3 tests/track2_test.py"
echo "t2_arrow env $T2 python3 tests/arrow_test.py"
if [ $NT = 3 ]; then
echo "t3_track env $T3 QUICK=${QUICK-1} python3 tests/track2_test.py"
echo "t3_arrow env $T3 python3 tests/arrow_test.py"
fi
} | xargs -P "${JOBS:-4}" -L 1 bash -c 'n=$0; "$@" > build/multi/logs/$n.log 2>&1; echo "$n: $(grep -c "^PASS" build/multi/logs/$n.log) pass, $(grep -c "^FAIL" build/multi/logs/$n.log) fail - $(grep -E "^RESULT|Traceback|Error" build/multi/logs/$n.log | tail -1)"' | sort
echo "FAILS:"; grep -H "^FAIL" $L/*.log | sed 's|.*/logs/||' | cut -c1-230
