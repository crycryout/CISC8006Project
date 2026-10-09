#!/usr/bin/env python3
"""Render the append-only registry's real final states; preserve historical notes."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.run_store import states,spent

header="# Experiment registry\n\nMachine events: `experiments/registry.jsonl`. Historical Markdown preserved in `docs/legacy_experiment_registry.md`; legacy outputs are diagnostic only. Scientific verdicts require complete paired groups in `results/`, never an individual run row.\n\n"
header+="| Run | Phase / seed | State | Source commit | Wall seconds / device-instance hours | Artifact |\n|---|---|---|---|---|---|\n"
for r in states().values():
    seconds=r.get('runtime_seconds'); hours=r.get('gpu_hours')
    timing=(f'{seconds:.3f}' if seconds is not None else 'unknown')+' / '+(f'{hours:.6f}' if hours is not None else 'included in legacy reserve' if r['status']=='legacy_recorded' else 'pending')
    header+=f'| {r["run_id"]} | {r["phase"]} / {r.get("seed")} | {r["status"]} | `{r["git_commit"][:8]}` | {timing} | `{r["artifact_path"]}` |\n'
header+=f'\nSpent/reserved charge: {spent():.6f} device-instance hours. This includes historical0.25h plus0.02h conservative prior uninstrumented H800-fixture reserve. Full-GPU and MIG instance wall-hours are not normalized full-GPU billing or currency cost. New attempts use whole-process wall-clock timing. The user authorized resources without the old20h ceiling. Failed attempts remain visible and never enter claim inference.\n'
(ROOT/'experiment_registry.md').write_text(header)
