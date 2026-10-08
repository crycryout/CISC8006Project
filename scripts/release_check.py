#!/usr/bin/env python3
"""Engineering readiness and real human/scientific gates; no false final release."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.io_utils import file_hash, now, write_json
from src.run_store import spent
from src.approvals import ceiling


def secret_scan():
    patterns={"private_key":re.compile(rb"-----BEGIN (?:[A-Z]+ )?PRIVATE KEY-----"),
              "github_token":re.compile(rb"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),
              "github_fine_grained_token":re.compile(rb"\bgithub_pat_[A-Za-z0-9_]{40,}\b"),
              "aws_access_key":re.compile(rb"\bAKIA[0-9A-Z]{16}\b")}
    findings=[]
    paths=subprocess.check_output(["git","ls-files","-z"],cwd=ROOT).decode().split("\0")
    for rel in filter(None,paths):
        path=ROOT/rel
        if not path.is_file(): continue
        data=path.read_bytes()
        for label,pattern in patterns.items():
            count=len(pattern.findall(data))
            if count: findings.append(dict(path=rel,pattern=label,count=count))
        if Path(rel).name==".env": findings.append(dict(path=rel,pattern="tracked_dotenv",count=1))
    history=subprocess.check_output(["git","log","--all","-p","--format=commit:%H"],cwd=ROOT)
    for label,pattern in patterns.items():
        count=len(pattern.findall(history))
        if count: findings.append(dict(path="git history",pattern=label,count=count))
    out=dict(scanned_at=now(),tool="project regex scanner-v1 / Python "+sys.version.split()[0],scope="tracked files and all local Git historical diffs",finding_details_redacted=True,findings=findings,status="pass" if not findings else "needs_review")
    write_json(ROOT/"environment/verification/secret_scan.json",out)
    return out


def manifest(kind):
    paths=subprocess.check_output(["git","ls-files","-z"],cwd=ROOT).decode().split("\0")
    artifacts=[]
    for rel in sorted(filter(None,paths)):
        if rel in {"submission/release_manifest.json","submission/candidate_manifest.json"}: continue
        path=ROOT/rel
        if path.is_file(): artifacts.append(dict(path=rel,sha256=file_hash(path),bytes=path.stat().st_size))
    return dict(created_at=now(),state=kind,artifact_commit="record after commit in external receipt or immutable annotated tag; no self reference",assets_in_git="weights/raw text excluded; token/NLL traces included",artifacts=artifacts)


def main():
    p=argparse.ArgumentParser(); p.add_argument("--candidate",action="store_true",help="write review snapshot; never treat pending gates as final")
    a=p.parse_args(); missing=[]
    required=["TASK_STATUS.md","AI_USAGE.md","CONTRIBUTIONS.md","LICENSES.md","SECURITY.md","data/assets_manifest.json","experiments/registry.jsonl","results/build_provenance.json","report/report_draft.pdf","presentation/defense_draft.pptx","audit/peer_audit/README.md"]
    for rel in required:
        if not (ROOT/rel).is_file(): missing.append(rel)
    clean_path=ROOT/"environment/verification/clean-checkout.json"
    if clean_path.exists():
        clean=json.loads(clean_path.read_text())
        if clean.get("status")!="pass" or clean.get("assets_manifest_sha256")!=file_hash(ROOT/"data/assets_manifest.json"):
            missing.append("clean checkout status / asset contract")
        for rel,digest in clean.get("installation_files_sha256",{}).items():
            if file_hash(ROOT/rel)!=digest: missing.append("clean checkout installation source changed: "+rel)
    demo_path=ROOT/"presentation/demo_recording_manifest.json"
    if demo_path.exists():
        demo=json.loads(demo_path.read_text())
        if demo.get("exit_code")!=0 or demo.get("demo_script_sha256")!=file_hash(ROOT/"scripts/demo.sh"):
            missing.append("successful recording of current demo script")
        if demo.get("diagnostic_result_sha256")!=file_hash(ROOT/"runs/D-S1-20261008/result.json"):
            missing.append("demo diagnostic changed since recording")
        for artifact in demo.get("artifacts",[]):
            path=Path(artifact["path"])
            if path.is_absolute() or ".." in path.parts or not (ROOT/path).is_file() or file_hash(ROOT/path)!=artifact["sha256"]:
                missing.append("demo artifact checksum: "+str(path))
    scan=secret_scan()
    if scan["status"]!="pass": missing.append("secret scan review")
    if spent()>ceiling(): missing.append("GPU ceiling exceeded")
    completion=json.loads((ROOT/"results/completion.json").read_text()) if (ROOT/"results/completion.json").exists() else {}
    pending=[]
    for stage in ("reproduction","pilots","improvement"):
        if completion.get(stage,{}).get("state")!="complete": pending.append(stage)
    for key,row in json.loads((ROOT/"docs/approval_decisions.json").read_text()).items():
        if row.get("status")!="approved" or not row.get("reviewer") or not row.get("evidence"): pending.append("actual decision: "+key)
    decision=json.loads((ROOT/"docs/budget_decision.json").read_text())
    if decision.get("status")!="approved" or not decision.get("reviewer") or not decision.get("evidence"): pending.append("actual feasible budget / exemption decision")
    selected=json.loads((ROOT/"docs/approval_decisions.json").read_text())["selected_improvement"].get("method")
    prefix={"h1_adaptive_sink":"h1_","h2_sink_selection":"h2_"}.get(selected)
    controls={k:v for k,v in completion.get("ablations",{}).items() if prefix and k.startswith(prefix)}
    if prefix is None or len(controls)!=2 or any(v.get("state")!="complete" for v in controls.values()):
        pending.append("selected method core ablations / controls")
    for rel in ["audit/peer_audit/signed_review.md","CONTRIBUTIONS_verified.md"]:
        if not (ROOT/rel).exists(): pending.append("human evidence: "+rel)
    for rel in ["environment/verification/clean-checkout.json","presentation/demo_recording_manifest.json"]:
        if not (ROOT/rel).exists(): pending.append("technical evidence: "+rel)
    output=dict(checked_at=now(),engineering_missing=missing,scientific_human_pending=pending,final_ready=not(missing or pending),spent_or_reserved_gpu_hours=spent(),ceiling_gpu_hours=ceiling())
    write_json(ROOT/"submission/release_check.json",output)
    if a.candidate and not missing:
        write_json(ROOT/"submission/candidate_manifest.json",manifest("review_candidate_not_final_freeze"))
    elif not(missing or pending): write_json(ROOT/"submission/release_manifest.json",manifest("final_freeze_candidate_for_actual_tag"))
    print(json.dumps(output,indent=2))
    return 0 if a.candidate and not missing else (0 if output["final_ready"] else 2)


if __name__=="__main__": sys.exit(main())
