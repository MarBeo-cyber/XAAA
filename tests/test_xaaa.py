from xaaa_core.models import UserDecision
from xaaa_core.orchestrator import XAAAOrchestrator
from xaaa_core.scenario_library import ScenarioLibrary
from xaaa_core.memory import ExperienceMemory
from xaaa_core.models import WisdomTrace


def test_scenario_library_contains_core_scenarios():
    lib = ScenarioLibrary()
    assert len(lib.all()) >= 3
    assert lib.get("evacuation_bottleneck").title


def test_bad_decision_generates_counterfactual():
    xaaa = XAAAOrchestrator()
    result = xaaa.run_session(UserDecision("evacuation_bottleneck", "A", "closest exit"))
    assert result.consequence.counterfactual_best_option == "B"
    assert result.consequence.risk_level.value in {"HIGH", "CRITICAL"}


def test_good_decision_low_risk():
    xaaa = XAAAOrchestrator()
    result = xaaa.run_session(UserDecision("silent_negotiation", "B", "avoid projection"))
    assert result.consequence.risk_level.value == "LOW"
    assert result.consequence.counterfactual_best_option is None


def test_socratic_prompts_are_generated():
    xaaa = XAAAOrchestrator()
    result = xaaa.run_session(UserDecision("project_contract_gap", "A", "standard wording"))
    assert len(result.prompts) >= 1
    assert result.prompts[0].question


def test_memory_pruning_keeps_size():
    mem = ExperienceMemory(max_traces=10)
    for i in range(30):
        mem.add(WisdomTrace(scenario_id=str(i), operational_rule=f"rule {i}", confidence=0.5))
    assert len(mem.traces) <= 10
