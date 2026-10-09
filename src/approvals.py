"""Read real decisions and explicit owner overrides without inventing reviews."""
import json
import math
from pathlib import Path


def budget_decision():
    return json.loads((Path(__file__).resolve().parents[1]/"docs/budget_decision.json").read_text())


def authorized(decision):
    return (decision.get("status") in {"approved","waived_by_user","authorized_by_user"}
            and bool(decision.get("reviewer")) and bool(decision.get("evidence")))


def ceiling():
    decision=budget_decision()
    if not authorized(decision): return 20.0
    value=decision.get("approved_ceiling_gpu_hours")
    if value is None and decision.get("unlimited_resources") is True and decision.get("status")=="authorized_by_user": return None
    if type(value) not in {int,float} or not math.isfinite(value) or value<=0: raise ValueError("invalid actually approved GPU ceiling")
    return float(value)


def single_pass_allowed(scope="reproduction"):
    decision=budget_decision()
    return authorized(decision) and decision.get("deterministic_single_pass_exemption") is True and scope in decision.get("exemption_scope",[])


def require_approval(phase,method=None):
    decisions=json.loads((Path(__file__).resolve().parents[1]/"docs/approval_decisions.json").read_text())
    keys={"reproduction":["reproduction_v2"],"pilot":["reproduction_v2","pilots_h1_h2"],
          "improvement":["reproduction_v2","pilots_h1_h2","selected_improvement"],
          "ablation":["reproduction_v2","pilots_h1_h2","selected_improvement"]}.get(phase,[])
    for key in keys:
        value=decisions[key]
        if not authorized(value):
            raise ValueError(f"scientific decision pending: {key}; see docs/protocol_amendments.md")
    selected=decisions["selected_improvement"].get("method")
    if phase in {"improvement","ablation"} and selected not in {"h1_adaptive_sink","h2_sink_selection"}:
        raise ValueError("selection pending: complete registered pilots and apply the frozen selection rule")
    if phase=="improvement" and selected!=method:
        raise ValueError("method differs from recorded selection")
    if keys:
        value=budget_decision()
        if not authorized(value): raise ValueError("measured full plan requires an actual feasible budget decision")
