"""Loader for config/default.yaml.

Before this module the YAML file was decorative: nothing imported yaml and
``max_traces`` / ``feedback.modes`` were duplicated as literals in memory.py and
orchestrator.py. The values below are now the single source of truth for the
orchestrator; see config/default.yaml for which safety flags are enforced in code
and which are declarative statements of scope.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict

import yaml

from .models import FeedbackMode

#: Repo-root config shipped with the source tree.
DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "default.yaml"

#: Used when no config file is present. Mirrors config/default.yaml.
BUILTIN_DEFAULTS: Dict[str, Any] = {
    "scenario_mode": "simulated",
    "max_traces": 100,
    "preserve_high_confidence": True,
    "high_confidence_threshold": 0.70,
    "feedback_modes": ["narrative", "counterfactual", "socratic", "sensory"],
    "safety": {
        "high_risk_domains_require_expert_review": True,
        "no_real_emergency_command": True,
        "counterfactuals_are_pedagogical": True,
    },
}


@dataclass
class XAAAConfig:
    scenario_mode: str = "simulated"
    max_traces: int = 100
    preserve_high_confidence: bool = True
    high_confidence_threshold: float = 0.70
    feedback_modes: list[FeedbackMode] = field(
        default_factory=lambda: [
            FeedbackMode.NARRATIVE,
            FeedbackMode.COUNTERFACTUAL,
            FeedbackMode.SOCRATIC,
            FeedbackMode.SENSORY,
        ]
    )
    safety: Dict[str, bool] = field(default_factory=dict)

    @property
    def high_risk_requires_expert_review(self) -> bool:
        return bool(self.safety.get("high_risk_domains_require_expert_review", True))


def _resolve_path(path: str | os.PathLike[str] | None) -> Path | None:
    if path is not None:
        return Path(path)
    env = os.environ.get("XAAA_CONFIG")
    if env:
        return Path(env)
    if DEFAULT_CONFIG_PATH.is_file():
        return DEFAULT_CONFIG_PATH
    return None


def load_config(path: str | os.PathLike[str] | None = None) -> XAAAConfig:
    """Read the YAML config, falling back to BUILTIN_DEFAULTS when absent.

    Raises ValueError for a ``scenario_mode`` other than ``simulated`` and for an
    unknown feedback mode. The scenario_mode check is the code-level enforcement of
    the ``no_real_emergency_command`` safety flag: XAAA has no non-simulated mode,
    so a config asking for one is a configuration error rather than a silent no-op.
    """
    resolved = _resolve_path(path)
    if resolved is None or not resolved.is_file():
        raw: Dict[str, Any] = {}
    else:
        with resolved.open("r", encoding="utf-8") as fh:
            raw = (yaml.safe_load(fh) or {}).get("xaaa", {}) or {}

    memory = raw.get("memory", {}) or {}
    feedback = raw.get("feedback", {}) or {}
    safety = raw.get("safety", {}) or BUILTIN_DEFAULTS["safety"]

    scenario_mode = raw.get("scenario_mode", BUILTIN_DEFAULTS["scenario_mode"])
    if scenario_mode != "simulated":
        raise ValueError(
            f"Unsupported scenario_mode {scenario_mode!r}: XAAA only runs simulated "
            "scenarios (safety.no_real_emergency_command)."
        )

    mode_names = feedback.get("modes") or BUILTIN_DEFAULTS["feedback_modes"]
    modes: list[FeedbackMode] = []
    for name in mode_names:
        try:
            modes.append(FeedbackMode(name))
        except ValueError as exc:
            valid = ", ".join(m.value for m in FeedbackMode)
            raise ValueError(f"Unknown feedback mode {name!r}; valid: {valid}") from exc

    return XAAAConfig(
        scenario_mode=scenario_mode,
        max_traces=int(memory.get("max_traces", BUILTIN_DEFAULTS["max_traces"])),
        preserve_high_confidence=bool(
            memory.get(
                "preserve_high_confidence", BUILTIN_DEFAULTS["preserve_high_confidence"]
            )
        ),
        high_confidence_threshold=float(
            memory.get(
                "high_confidence_threshold",
                BUILTIN_DEFAULTS["high_confidence_threshold"],
            )
        ),
        feedback_modes=modes,
        safety=dict(safety),
    )
