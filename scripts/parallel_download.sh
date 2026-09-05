#!/usr/bin/env bash
# Parallel ranged download for hosts with slow single-stream throughput.
# Usage: parallel_download.sh <url> <outfile> <expected_sha256> [nstreams]
set -uo pipefail
URL="$1"; OUT="$2"; SHA="$3"; N="${4:-32}"
TMP="${OUT}.parts"; mkdir -p "$TMP"

SIZE=$(curl -sIL "$URL" | tr -d '\r' | grep -i '^content-length:' | tail -1 | awk '{print $2}')
[ -n "$SIZE" ] || { echo "no content-length"; exit 1; }
CHUNK=$(( (SIZE + N - 1) / N ))
echo "size=$SIZE streams=$N chunk=$CHUNK"

for i in $(seq 0 $((N-1))); do
  s=$((i * CHUNK)); e=$(( s + CHUNK - 1 )); [ $e -ge $SIZE ] && e=$((SIZE-1))
  [ $s -ge $SIZE ] && break
  ( for attempt in 1 2 3 4 5; do
      curl -sL --retry 3 -r "$s-$e" -o "$TMP/part_$i" "$URL" && break || sleep 2
    done ) &
done
wait
echo "parts done: $(ls "$TMP" | wc -l)"

> "$OUT"
cat $(for i in $(seq 0 $((N-1))); do [ -f "$TMP/part_$i" ] && echo "$TMP/part_$i"; done) > "$OUT"
GOT=$(sha256sum "$OUT" | awk '{print $1}')
ACT=$(stat -c%s "$OUT")
echo "downloaded=$ACT sha=$GOT"
if [ "$GOT" = "$SHA" ] && [ "$ACT" = "$SIZE" ]; then echo "VERIFY_OK"; rm -rf "$TMP"; else echo "VERIFY_FAIL"; exit 2; fi
