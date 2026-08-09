from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone
from uuid import uuid4
from typing import Dict, List, Optional


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class DecisionRisk(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ScenarioDomain(str, Enum):
    CRISIS = "crisis"
    NEGOTIATION = "negotiation"
    MEDICAL_COMMUNICATION = "medical_communication"
    PROJECT_MANAGEMENT = "project_management"
    LEARNING = "learning"


class FeedbackMode(str, Enum):
    NARRATIVE = "narrative"
    SOCRATIC = "socratic"
    COUNTERFACTUAL = "counterfactual"
    SENSORY = "sensory"


@dataclass
class Scenario:
    scenario_id: str
    title: str
    domain: ScenarioDomain
    context: str
    decision_options: Dict[str, str]
    hidden_risks: Dict[str, float]
    expected_principles: List[str]
    experience_patterns: List[str] = field(default_factory=list)
    #: Per-option map of which ``expected_principles`` that option actually
    #: violates. Author-assigned pedagogical annotation, not an inference: the
    #: engine performs no analysis of the option text.
    option_violations: Dict[str, List[str]] = field(default_factory=dict)


@dataclass
class UserDecision:
    scenario_id: str
    selected_option: str
    rationale: str
    timestamp: str = field(default_factory=utc_now)


@dataclass
class Consequence:
    selected_option: str
    immediate_outcome: str
    delayed_outcome: str
    risk_score: float
    risk_level: DecisionRisk
    missed_patterns: List[str]
    counterfactual_best_option: Optional[str] = None


@dataclass
class SocraticPrompt:
    question: str
    target_pattern: str
    purpose: str


@dataclass
class WisdomTrace:
    trace_id: str = field(default_factory=lambda: str(uuid4()))
    scenario_id: str = ""
    learned_pattern: str = ""
    operational_rule: str = ""
    transfer_domains: List[str] = field(default_factory=list)
    confidence: float = 0.0
    created_at: str = field(default_factory=utc_now)
    #: Experience-pattern names the originating scenario mediates.
    experience_patterns: List[str] = field(default_factory=list)


@dataclass
class ExperienceSessionResult:
    scenario: Scenario
    decision: UserDecision
    consequence: Consequence
    prompts: List[SocraticPrompt]
    wisdom_trace: WisdomTrace
    feedback_modes: List[FeedbackMode]
    #: Prior traces in Experience Memory that share a transfer domain with this
    #: session's trace (L6 retrieval).
    transfer_candidates: List[WisdomTrace] = field(default_factory=list)
    #: Set when config safety.high_risk_domains_require_expert_review is on and
    #: the consequence lands in a HIGH or CRITICAL band.
    requires_expert_review: bool = False
