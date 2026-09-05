#!/usr/bin/env bash
# Resume a parallel_download.sh job: each part_<i> keeps its range; missing
# bytes are appended. Low concurrency (CDN punishes high fan-out).
# Usage: resume_download.sh <url> <parts_dir> <total_size> <nstreams> [concurrency]
set -uo pipefail
URL="$1"; DIR="$2"; SIZE="$3"; N="$4"; C="${5:-4}"
CHUNK=$(( (SIZE + N - 1) / N ))

download_one() {
  local i=$1 s=$((i * CHUNK)) e=$(( s + CHUNK - 1 ))
  [ $e -ge $SIZE ] && e=$((SIZE-1))
  [ $s -ge $SIZE ] && return 0
  local f="$DIR/part_$i" have
  have=$( [ -f "$f" ] && stat -c%s "$f" || echo 0 )
  local want=$(( e - s + 1 ))
  while [ "$have" -lt "$want" ]; do
    curl -sL -r "$((s+have))-$e" -o - "$URL" >> "$f" || sleep 3
    have=$(stat -c%s "$f")
  done
}
export -f download_one; export URL DIR SIZE CHUNK

seq 0 $((N-1)) | xargs -P "$C" -I{} bash -c 'download_one {}'

echo "parts complete: $(ls "$DIR" | wc -l)"
TOTAL=$(du -sb "$DIR" | awk '{print $1}')
echo "bytes on disk: $TOTAL / $SIZE"
