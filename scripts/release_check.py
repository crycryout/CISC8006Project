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
from src.run_store import spent,numerical_source
from src.approvals import ceiling,authorized


def secret_scan():
    patterns={"private_key":re.compile(rb"-----BEGIN (?:[A-Z]+ )?PRIVATE KEY-----"),
              "github_token":re.compile(rb"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),
              "github_fine_grained_token":re.compile(rb"\bgithub_pat_[A-Za-z0-9_]{40,}\b"),
              "openai_key":re.compile(rb"\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{20,}\b"),
              "huggingface_token":re.compile(rb"\bhf_[A-Za-z0-9]{30,}\b"),
              "google_api_key":re.compile(rb"\bAIza[A-Za-z0-9_-]{35}\b"),
              "aws_access_key":re.compile(rb"\bAKIA[0-9A-Z]{16}\b")}
    assignment=re.compile(rb'''(?im)\b(?:password|passwd|api_key|api_secret|access_token|secret_key)\b["']?\s*[:=]\s*["']?([A-Za-z0-9_./+\-=]{12,})''')
    placeholders=(b"placeholder",b"example",b"dummy",b"your_",b"change_me",b"changeme",b"replace",b"test_")
    def credential_assignments(data):
        return sum(not any(marker in value.lower() for marker in placeholders)
                   for value in assignment.findall(data))
    findings=[]
    paths=subprocess.check_output(["git","ls-files","-z"],cwd=ROOT).decode().split("\0")
    for rel in filter(None,paths):
        path=ROOT/rel
        if not path.is_file(): continue
        data=path.read_bytes()
        for label,pattern in patterns.items():
            count=len(pattern.findall(data))
            if count: findings.append(dict(path=rel,pattern=label,count=count))
        count=credential_assignments(data)
        if count: findings.append(dict(path=rel,pattern="literal_credential_assignment",count=count))
        if Path(rel).name==".env": findings.append(dict(path=rel,pattern="tracked_dotenv",count=1))
    history=subprocess.check_output(["git","log","--all","-p","--format=commit:%H"],cwd=ROOT)
    for label,pattern in patterns.items():
        count=len(pattern.findall(history))
        if count: findings.append(dict(path="git history",pattern=label,count=count))
    count=credential_assignments(history)
    if count: findings.append(dict(path="git history",pattern="literal_credential_assignment",count=count))
    out=dict(scanned_at=now(),tool="project regex scanner-v2 / Python "+sys.version.split()[0],scope="tracked files and all local Git historical diffs; known key families, literal credentials and tracked .env; not a proof that every possible secret is absent",finding_details_redacted=True,findings=findings,status="pass" if not findings else "needs_review")
    write_json(ROOT/"environment/verification/secret_scan.json",out)
    return out


def manifest(kind):
    paths=subprocess.check_output(["git","ls-files","-z"],cwd=ROOT).decode().split("\0")
    artifacts=[]
    for rel in sorted(filter(None,paths)):
        excluded={"submission/release_manifest.json","submission/technical_final_manifest.json"}
        if kind=="review_candidate_not_final_freeze": excluded.add("submission/candidate_manifest.json")
        if rel in excluded: continue
        path=ROOT/rel
        if path.is_file(): artifacts.append(dict(path=rel,sha256=file_hash(path),bytes=path.stat().st_size))
    return dict(created_at=now(),state=kind,artifact_commit="record after commit in external receipt or immutable annotated tag; no self reference",assets_in_git="weights/raw text excluded; token/NLL traces included",artifacts=artifacts)


def main():
    p=argparse.ArgumentParser(); p.add_argument("--candidate",action="store_true",help="write review snapshot; never treat pending gates as final")
    p.add_argument("--technical",action="store_true",help="seal measured scientific delivery; report real human course activities separately")
    a=p.parse_args(); missing=[]
    completion=json.loads((ROOT/"results/completion.json").read_text()) if (ROOT/"results/completion.json").exists() else {}
    core_ready=all(completion.get(stage,{}).get("state")=="complete" for stage in ("reproduction","pilots","improvement")) and len(completion.get("ablations",{}))==2 and all(value.get("state")=="complete" for value in completion["ablations"].values())
    required=["TASK_STATUS.md","AI_USAGE.md","CONTRIBUTIONS.md","LICENSES.md","SECURITY.md","data/assets_manifest.json","experiments/registry.jsonl","results/build_provenance.json","audit/peer_audit/README.md"]
    required.extend(["report/report.md","report/report.pdf","presentation/defense.pptx","tables/scientific_summary.csv","tables/improvement_book_selections.csv","results/raw_artifact_index.csv","environment/verification/scientific-raw-reconstruction.json","environment/verification/reference-error-distributions.json","environment/verification/deliverable-verification.json"] if core_ready else ["report/report_draft.pdf","presentation/defense_draft.pptx"])
    for rel in required:
        if not (ROOT/rel).is_file(): missing.append(rel)
    clean_path=ROOT/"environment/verification/clean-checkout.json"
    if clean_path.exists():
        clean=json.loads(clean_path.read_text())
        if clean.get("status")!="pass" or clean.get("assets_manifest_sha256")!=file_hash(ROOT/"data/assets_manifest.json"):
            missing.append("clean checkout status / asset contract")
        for rel,digest in clean.get("installation_files_sha256",{}).items():
            if file_hash(ROOT/rel)!=digest: missing.append("clean checkout installation source changed: "+rel)
        for artifact in clean.get("logs",[]):
            if not (ROOT/artifact["path"]).is_file() or file_hash(ROOT/artifact["path"])!=artifact["sha256"]:
                missing.append("clean checkout receipt checksum: "+artifact["path"])
    demo_path=ROOT/"presentation/demo_recording_manifest.json"
    if demo_path.exists():
        demo=json.loads(demo_path.read_text())
        if demo.get("exit_code")!=0 or demo.get("demo_script_sha256")!=file_hash(ROOT/"scripts/demo.sh"):
            missing.append("successful recording of current demo script")
        if demo.get("diagnostic_result_sha256")!=file_hash(ROOT/"runs/D-S1-20261008/result.json"):
            missing.append("demo diagnostic changed since recording")
        for key,rel in [("demo_evidence_sha256","scripts/demo_evidence.py"),("recorder_sha256","scripts/record_demo.py")]:
            if demo.get(key)!=file_hash(ROOT/rel): missing.append("recording source changed: "+rel)
        if core_ready and demo.get("scientific_complete") is not True: missing.append("recording of completed scientific evidence")
        for artifact in demo.get("paired_results",[]):
            if file_hash(ROOT/artifact["path"])!=artifact["sha256"]: missing.append("demo paired result changed: "+artifact["path"])
        for artifact in demo.get("artifacts",[]):
            path=Path(artifact["path"])
            if path.is_absolute() or ".." in path.parts or not (ROOT/path).is_file() or file_hash(ROOT/path)!=artifact["sha256"]:
                missing.append("demo artifact checksum: "+str(path))
    scan=secret_scan()
    if scan["status"]!="pass": missing.append("secret scan review")
    limit=ceiling()
    if limit is not None and spent()>limit: missing.append("GPU ceiling exceeded")
    pending=[]
    for stage in ("reproduction","pilots","improvement"):
        if completion.get(stage,{}).get("state")!="complete": pending.append(stage)
    for key,row in json.loads((ROOT/"docs/approval_decisions.json").read_text()).items():
        if not authorized(row): pending.append("actual decision: "+key)
    decision=json.loads((ROOT/"docs/budget_decision.json").read_text())
    if not authorized(decision): pending.append("actual feasible budget / exemption decision")
    selected=json.loads((ROOT/"docs/approval_decisions.json").read_text())["selected_improvement"].get("method")
    selected_decision=json.loads((ROOT/"docs/approval_decisions.json").read_text())["selected_improvement"]
    if selected:
        evidence=ROOT/selected_decision.get("selection_evidence","")
        if not evidence.is_file() or file_hash(evidence)!=selected_decision.get("selection_evidence_sha256"):
            pending.append("recorded pilot selection evidence checksum")
    prefix={"h1_adaptive_sink":"h1_","h2_sink_selection":"h2_"}.get(selected)
    controls={k:v for k,v in completion.get("ablations",{}).items() if prefix and k.startswith(prefix)}
    if prefix is None or len(controls)!=2 or any(v.get("state")!="complete" for v in controls.values()):
        pending.append("selected method core ablations / controls")
    if core_ready:
        check_path=ROOT/"environment/verification/deliverable-verification.json"
        if check_path.is_file():
            check=json.loads(check_path.read_text())
            if check.get("status")!="pass" or check.get("verification_script_sha256")!=file_hash(ROOT/"scripts/verify_deliverables.py") or check.get("deck_slides")!=12:
                missing.append("current measured report/deck verification")
            for artifact in check.get("artifacts",[])+check.get("embedded_figures",[]):
                if file_hash(ROOT/artifact["path"])!=artifact["sha256"]:
                    missing.append("verified deliverable changed: "+artifact["path"])
            for row in check.get("comparisons",[]):
                if row.get("metrics_match") is not True or row.get("summary_sha256")!=file_hash(ROOT/"results"/row["stage"]/"summary.json"):
                    missing.append("verified report/deck metrics changed: "+row["stage"])
        reference_path=ROOT/"environment/verification/reference-error-distributions.json"
        if reference_path.is_file():
            reference=json.loads(reference_path.read_text())
            if reference.get("status")!="pass" or reference.get("script_sha256")!=file_hash(ROOT/"scripts/record_reference_errors.py") or reference.get("reference_fixture_sha256")!=file_hash(ROOT/"tests/test_position_reference.py") or len(reference.get("cases",[]))!=6:
                missing.append("current preset-tolerance reference error distributions")
            if reference.get("errors_sha256")!=file_hash(ROOT/reference["artifact_path"]/"errors.json"):
                missing.append("reference error-distribution raw artifact checksum")
        audit_path=ROOT/"environment/verification/scientific-raw-reconstruction.json"
        if audit_path.is_file():
            audit=json.loads(audit_path.read_text())
            if audit.get("status")!="pass" or audit.get("audit_script_sha256")!=file_hash(ROOT/"scripts/audit_scientific_results.py") or audit.get("input_manifest_sha256")!=file_hash(ROOT/"results/final_input_manifest.json"):
                missing.append("current raw-statistics reconstruction receipt")
            expected={"reproduction","improvement","pilots/h1_adaptive_sink","pilots/h2_sink_selection",*("ablations/"+name for name in completion["ablations"])}
            if {row["stage"] for row in audit.get("stages",[])}!=expected:
                missing.append("complete raw-statistics reconstruction stage set")
            for row in audit.get("stages",[]):
                paired_path=ROOT/row.get("paired_result_path","results/"+row["stage"]+"/paired_result.json")
                if row["status"]!="pass" or row["paired_result_sha256"]!=file_hash(paired_path):
                    missing.append("raw-statistics reconstruction differs: "+row["stage"])
                for raw in row["raw_files"]:
                    if file_hash(ROOT/raw["path"])!=raw["sha256"]: missing.append("audited raw array checksum: "+raw["path"])
        provenance=json.loads((ROOT/"results/build_provenance.json").read_text())
        if provenance.get("builder_sha256")!=file_hash(ROOT/"scripts/build_results.py") or provenance.get("input_manifest_sha256")!=file_hash(ROOT/"results/final_input_manifest.json"):
            missing.append("current result/table/figure builder and input manifest")
        for artifact in provenance["artifacts"]:
            if not (ROOT/artifact["path"]).is_file() or file_hash(ROOT/artifact["path"])!=artifact["sha256"]:
                missing.append("result/table/figure provenance checksum: "+artifact["path"])
        numeric=numerical_source()[0]
        inputs=json.loads((ROOT/"results/final_input_manifest.json").read_text())
        for group in [inputs["reproduction"],inputs["pilots"],inputs["improvement"],*inputs["ablations"].values()]:
            for value in group.values():
                if not isinstance(value,list): continue
                for rel in value:
                    result=json.loads((ROOT/rel).read_text())
                    if result["contract"]["numerical_source_sha256"]!=numeric:
                        missing.append("current inference source differs from frozen run: "+rel)
        delivery=json.loads((ROOT/"submission/deliverables_manifest.json").read_text())
        if delivery.get("state")!="scientific_complete_owner_authorized" or delivery.get("input_manifest_sha256")!=file_hash(ROOT/"results/final_input_manifest.json") or delivery.get("builder_sha256")!=file_hash(ROOT/"scripts/build_deliverables.py"):
            missing.append("complete deliverables manifest / input contract")
        for artifact in delivery.get("artifacts",[]):
            if not (ROOT/artifact["path"]).is_file() or file_hash(ROOT/artifact["path"])!=artifact["sha256"]:
                missing.append("report/deck checksum: "+artifact["path"])
    for rel in ["audit/peer_audit/signed_review.md","CONTRIBUTIONS_verified.md"]:
        if not (ROOT/rel).exists(): pending.append("human evidence: "+rel)
    for rel in ["environment/verification/clean-checkout.json","presentation/demo_recording_manifest.json"]:
        if not (ROOT/rel).exists(): pending.append("technical evidence: "+rel)
    scientific_pending=[item for item in pending if not item.startswith("human evidence:")]
    technical_ready=not(missing or scientific_pending)
    output=dict(checked_at=now(),engineering_missing=missing,scientific_human_pending=pending,technical_scientific_ready=technical_ready,final_ready=not(missing or pending),spent_or_reserved_gpu_hours=spent(),ceiling_gpu_hours=limit)
    write_json(ROOT/"submission/release_check.json",output)
    if a.candidate and not missing:
        write_json(ROOT/"submission/candidate_manifest.json",manifest("review_candidate_not_final_freeze"))
    elif a.technical and technical_ready:
        value=manifest("owner_authorized_scientific_delivery_human_course_activities_separately_recorded")
        value.update(scope="scientific_and_engineering",human_activities_pending=[item for item in pending if item.startswith("human evidence:")])
        write_json(ROOT/"submission/technical_final_manifest.json",value)
        write_json(ROOT/"submission/release_manifest.json",value)
    elif not(missing or pending): write_json(ROOT/"submission/release_manifest.json",manifest("final_freeze_candidate_for_actual_tag"))
    print(json.dumps(output,indent=2))
    return 0 if (a.candidate and not missing) or (a.technical and technical_ready) else (0 if output["final_ready"] else 2)


if __name__=="__main__": sys.exit(main())
