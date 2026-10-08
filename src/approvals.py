"""Read real decisions; never infer approval from an existing artifact."""
import json
import math
from pathlib import Path


def budget_decision():
    return json.loads((Path(__file__).resolve().parents[1]/"docs/budget_decision.json").read_text())


def ceiling():
    decision=budget_decision()
    if decision.get("status")!="approved" or not decision.get("reviewer") or not decision.get("evidence"): return 20.0
    value=decision.get("approved_ceiling_gpu_hours")
    if type(value) not in {int,float} or not math.isfinite(value) or value<=0: raise ValueError("invalid actually approved GPU ceiling")
    return float(value)


def single_pass_allowed(scope="reproduction"):
    decision=budget_decision()
    return decision.get("status")=="approved" and bool(decision.get("reviewer")) and bool(decision.get("evidence")) and decision.get("deterministic_single_pass_exemption") is True and scope in decision.get("exemption_scope",[])


def require_approval(phase,method=None):
    decisions=json.loads((Path(__file__).resolve().parents[1]/"docs/approval_decisions.json").read_text())
    keys={"reproduction":["reproduction_v2"],"pilot":["reproduction_v2","pilots_h1_h2"],
          "improvement":["reproduction_v2","pilots_h1_h2","selected_improvement"],
          "ablation":["reproduction_v2","pilots_h1_h2","selected_improvement"]}.get(phase,[])
    for key in keys:
        value=decisions[key]
        if value["status"]!="approved" or not value.get("reviewer") or not value.get("evidence"):
            raise ValueError(f"scientific decision pending: {key}; see docs/protocol_amendments.md")
    if phase=="improvement" and decisions["selected_improvement"]["method"]!=method:
        raise ValueError("method differs from actual team selection")
    if keys:
        value=budget_decision()
        if value.get("status")!="approved" or not value.get("reviewer") or not value.get("evidence"): raise ValueError("measured full plan requires an actual feasible budget decision")
