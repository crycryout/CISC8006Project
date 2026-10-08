#!/usr/bin/env python3
"""Record the actual bounded terminal demo, with an optional video replay."""
import argparse
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.io_utils import file_hash, now, write_json


def render_video(events, duration, path, commit):
    from PIL import Image, ImageDraw, ImageFont
    encoder = shutil.which("ffmpeg")
    if encoder is None:
        raise RuntimeError("ffmpeg is required for --video")
    font = ImageFont.truetype("DejaVuSansMono.ttf", 19)
    command = [encoder, "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo",
               "-pixel_format", "rgb24", "-video_size", "1600x900", "-framerate", "2",
               "-i", "-", "-an", "-c:v", "libx264", "-preset", "veryfast",
               "-crf", "24", "-pix_fmt", "yuv420p", str(path)]
    with subprocess.Popen(command, stdin=subprocess.PIPE) as process:
        for frame in range(max(1, math.ceil(duration * 2))):
            stamp = frame / 2
            screen = Image.new("RGB", (1600, 900), "#101827")
            draw = ImageDraw.Draw(screen)
            draw.text((28, 24), "CISC8006 actual terminal demo | source " + commit[:12], font=font, fill="#70d7ff")
            draw.text((28, 54), "Recorded diagnostic and fixtures; formal scientific results pending", font=font, fill="#ffd580")
            current = "".join(event[2] for event in events if event[0] <= stamp)
            lines = current.replace("\r", "").splitlines()[-31:]
            for index, line in enumerate(lines):
                draw.text((28, 102 + index * 24), line[:128], font=font, fill="#e8edf6")
            draw.text((28, 860), f"Recorded session time {stamp:.1f}s / {duration:.1f}s", font=font, fill="#94a3b8")
            process.stdin.write(screen.tobytes())
        process.stdin.close()
        if process.wait() != 0:
            raise RuntimeError("video encoder failed")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="presentation/demo_recording")
    parser.add_argument("--video", action="store_true")
    args = parser.parse_args()
    directory = ROOT / args.out
    directory.mkdir(parents=True, exist_ok=False)
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT).decode().strip()
    dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT))
    command = ["bash", "scripts/demo.sh"]
    started_at = now()
    events = [[0.0, "o", "$ " + " ".join(command) + "\r\n"]]
    started = time.monotonic()
    with subprocess.Popen(command, cwd=ROOT, env=dict(os.environ, CUDA_VISIBLE_DEVICES=""),
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1) as process:
        for line in process.stdout:
            print(line, end="", flush=True)
            events.append([time.monotonic() - started, "o", line.replace("\n", "\r\n")])
        exit_code = process.wait()
    duration = time.monotonic() - started
    events.append([duration, "o", f"\r\nProcess exit code: {exit_code}\r\n"])
    # Keep the final output visible for two seconds in the faithful replay.
    cast = directory / "session.cast"
    with cast.open("x") as stream:
        header = dict(version=2, width=128, height=40, timestamp=int(time.time() - duration),
                      duration=duration + 2, command=" ".join(command), title="CISC8006 bounded terminal demo")
        stream.write(json.dumps(header) + "\n")
        for event in events:
            stream.write(json.dumps(event) + "\n")
    (directory / "stdout.log").write_text("".join(event[2] for event in events))
    if args.video:
        render_video(events, duration + 2, directory / "session.mp4", commit)
    files = [dict(path=str(path.relative_to(ROOT)), sha256=file_hash(path), bytes=path.stat().st_size)
             for path in sorted(directory.iterdir()) if path.is_file()]
    write_json(ROOT / "presentation/demo_recording_manifest.json",
               dict(recorded_at=started_at, artifact_kind="actual_agent_terminal_session_and_video_replay",
                    source_commit=commit, git_dirty_at_launch=dirty, command=command, exit_code=exit_code,
                    runtime_seconds=duration, demo_script_sha256=file_hash(ROOT / "scripts/demo.sh"),
                    diagnostic_result_sha256=file_hash(ROOT / "runs/D-S1-20261008/result.json"),
                    human_rehearsal="pending; this is not a member defense or peer review", artifacts=files))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
