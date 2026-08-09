from __future__ import annotations

from .models import (
    UserDecision,
    ExperienceSessionResult,
    DecisionRisk,
    WisdomTrace,
)
from .config import XAAAConfig, load_config
from .scenario_library import ScenarioLibrary
from .simulator import ConsequenceSimulator
from .socratic import SocraticReflectionEngine
from .wisdom import WisdomTraceBuilder
from .memory import ExperienceMemory


class XAAAOrchestrator:
    """Integrated XAAA loop.

    Scenario -> decision -> consequence -> counterfactual -> Socratic reflection
    -> wisdom trace -> experience memory -> transfer retrieval.

    Memory sizing and the emitted feedback-mode list come from config/default.yaml
    (see xaaa_core.config); they are no longer literals in this file.
    """

    def __init__(self, config: XAAAConfig | None = None) -> None:
        self.config = config or load_config()
        self.library = ScenarioLibrary()
        self.simulator = ConsequenceSimulator()
        self.socratic = SocraticReflectionEngine()
        self.wisdom = WisdomTraceBuilder()
        self.memory = ExperienceMemory(
            max_traces=self.config.max_traces,
            preserve_high_confidence=self.config.preserve_high_confidence,
            high_confidence_threshold=self.config.high_confidence_threshold,
        )

    def run_session(self, decision: UserDecision) -> ExperienceSessionResult:
        scenario = self.library.get(decision.scenario_id)
        consequence = self.simulator.simulate(scenario, decision)
        prompts = self.socratic.generate(scenario, consequence, decision)
        trace = self.wisdom.build(scenario, consequence)

        # L6 retrieval runs against memory as it stood *before* this session, so
        # the candidates are genuinely prior experience.
        candidates = self._transfer_candidates(trace)
        self.memory.add(trace)

        requires_review = (
            self.config.high_risk_requires_expert_review
            and consequence.risk_level in {DecisionRisk.HIGH, DecisionRisk.CRITICAL}
        )

        return ExperienceSessionResult(
            scenario=scenario,
            decision=decision,
            consequence=consequence,
            prompts=prompts,
            wisdom_trace=trace,
            feedback_modes=list(self.config.feedback_modes),
            transfer_candidates=candidates,
            requires_expert_review=requires_review,
        )

    def _transfer_candidates(self, trace: WisdomTrace) -> list[WisdomTrace]:
        """Prior traces sharing at least one transfer domain with ``trace``."""
        found: dict[str, WisdomTrace] = {}
        for domain in trace.transfer_domains:
            for prior in self.memory.transfer_candidates(
                domain, exclude_trace_id=trace.trace_id
            ):
                found[prior.trace_id] = prior
        return list(found.values())
