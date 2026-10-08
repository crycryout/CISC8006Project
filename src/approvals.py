"""Read real decisions; never infer approval from an existing artifact."""
import json
from pathlib import Path


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
