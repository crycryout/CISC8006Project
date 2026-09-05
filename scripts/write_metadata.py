#!/usr/bin/env python
"""Write/extend runs/<RUN_ID>/metadata.json as valid JSON (provenance artifact).

Usage:
  python scripts/write_metadata.py --run_id R0002 --phase start
  python scripts/write_metadata.py --run_id R0002 --phase end

start: creates the file (refuses to overwrite an existing one); end: adds
ended_at + elapsed seconds. GPU info via nvidia-smi; git commit at launch.
"""
import argparse
import json
import os
import subprocess
import time
from datetime import datetime, timezone

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def q(query):
    try:
        return subprocess.check_output(
            ["nvidia-smi", "--query-gpu=" + query, "--format=csv,noheader"],
            text=True,
        ).strip().splitlines()
    except Exception:
        return []


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--run_id", required=True)
    p.add_argument("--phase", choices=["start", "end"], required=True)
    args = p.parse_args()

    path = os.path.join(REPO_ROOT, "runs", args.run_id, "metadata.json")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    if args.phase == "start":
        if os.path.exists(path):
            raise SystemExit(f"refusing to overwrite existing {path}")
        meta = {
            "run_id": args.run_id,
            "hostname": os.uname().nodename,
            "gpus": [
                {"name": n.strip(), "driver": d.strip(), "memory_mb": int(m.strip())}
                for n, d, m in zip(q("name"), q("driver_version"), q("memory.total"))
            ],
            "git_commit": subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True
            ).strip(),
            "started_at": now,
        }
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(meta, f, indent=2)
    else:
        with open(path) as f:
            meta = json.load(f)
        started = datetime.strptime(meta["started_at"], "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=timezone.utc
        )
        meta["ended_at"] = now
        meta["elapsed_seconds"] = round(
            (datetime.now(timezone.utc) - started).total_seconds(), 1
        )
        with open(path, "w") as f:
            json.dump(meta, f, indent=2)

    print(json.dumps(json.load(open(path)), indent=2))


if __name__ == "__main__":
    main()
