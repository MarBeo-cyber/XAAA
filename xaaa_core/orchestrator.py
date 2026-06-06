from __future__ import annotations

from .models import UserDecision, ExperienceSessionResult, FeedbackMode
from .scenario_library import ScenarioLibrary
from .simulator import ConsequenceSimulator
from .socratic import SocraticReflectionEngine
from .wisdom import WisdomTraceBuilder
from .memory import ExperienceMemory


class XAAAOrchestrator:
    """Integrated XAAA loop.

    Scenario -> decision -> consequence -> counterfactual -> Socratic reflection
    -> wisdom trace -> experience memory.
    """

    def __init__(self) -> None:
        self.library = ScenarioLibrary()
        self.simulator = ConsequenceSimulator()
        self.socratic = SocraticReflectionEngine()
        self.wisdom = WisdomTraceBuilder()
        self.memory = ExperienceMemory()

    def run_session(self, decision: UserDecision) -> ExperienceSessionResult:
        scenario = self.library.get(decision.scenario_id)
        consequence = self.simulator.simulate(scenario, decision)
        prompts = self.socratic.generate(scenario, consequence)
        trace = self.wisdom.build(scenario, consequence)
        self.memory.add(trace)

        modes = [FeedbackMode.NARRATIVE, FeedbackMode.COUNTERFACTUAL, FeedbackMode.SOCRATIC, FeedbackMode.SENSORY]

        return ExperienceSessionResult(
            scenario=scenario,
            decision=decision,
            consequence=consequence,
            prompts=prompts,
            wisdom_trace=trace,
            feedback_modes=modes,
        )
