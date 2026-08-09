"""Serialisation of XAAA structures (FR-08).

Plain dict / JSON export of the objects the engine already produces. This is the
whole of the export surface: there is no network client, no TAAA or NOAH bridge
and no privacy or anonymisation layer here. Writing a file that another module
could read is all that is claimed.

The shape emitted by ``trace_to_dict`` is the one documented in docs/API_SPEC.md.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, Iterable, List

from .models import ExperienceSessionResult, UserDecision, WisdomTrace


def trace_to_dict(trace: WisdomTrace) -> Dict[str, Any]:
    """Serialise a WisdomTrace, including its confidence and provenance fields."""
    return asdict(trace)


def traces_to_dicts(traces: Iterable[WisdomTrace]) -> List[Dict[str, Any]]:
    return [trace_to_dict(t) for t in traces]


def decision_to_dict(decision: UserDecision) -> Dict[str, Any]:
    return asdict(decision)


def session_to_dict(result: ExperienceSessionResult) -> Dict[str, Any]:
    """Serialise a full session result.

    Enum members are emitted as their string values; the scenario is reduced to
    its identifier and title so the export carries the session, not the library.
    """
    return {
        "scenario_id": result.scenario.scenario_id,
        "scenario_title": result.scenario.title,
        "domain": result.scenario.domain.value,
        "decision": decision_to_dict(result.decision),
        "consequence": {
            "selected_option": result.consequence.selected_option,
            "immediate_outcome": result.consequence.immediate_outcome,
            "delayed_outcome": result.consequence.delayed_outcome,
            "risk_score": result.consequence.risk_score,
            "risk_level": result.consequence.risk_level.value,
            "missed_patterns": list(result.consequence.missed_patterns),
            "counterfactual_best_option": result.consequence.counterfactual_best_option,
        },
        "prompts": [asdict(p) for p in result.prompts],
        "wisdom_trace": trace_to_dict(result.wisdom_trace),
        "feedback_modes": [m.value for m in result.feedback_modes],
        "transfer_candidates": traces_to_dicts(result.transfer_candidates),
        "requires_expert_review": result.requires_expert_review,
    }


def export_traces(traces: Iterable[WisdomTrace], path: str | Path) -> Path:
    """Write traces to ``path`` as a UTF-8 JSON array. Returns the path written."""
    target = Path(path)
    if target.parent != Path(""):
        target.parent.mkdir(parents=True, exist_ok=True)
    payload = traces_to_dicts(traces)
    target.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return target
