"""Regression tests for the defects found in the audit.

Each test names the defect it guards. Reverting the corresponding fix must turn
the test red.
"""

import json
import pathlib

import pytest

from xaaa_core.config import XAAAConfig, load_config
from xaaa_core.export import export_traces, session_to_dict, trace_to_dict
from xaaa_core.memory import ExperienceMemory
from xaaa_core.models import FeedbackMode, UserDecision, WisdomTrace
from xaaa_core.orchestrator import XAAAOrchestrator
from xaaa_core.scenario_library import ScenarioLibrary
from xaaa_core.simulator import ConsequenceSimulator


# --------------------------------------------------------------------------
# Defect 1: prune() sliced the tail while protected traces sat at the head, so
# half the memory filled with the traces it was supposed to discard.
# --------------------------------------------------------------------------

def test_prune_preserves_every_high_confidence_trace():
    """10 traces at 0.95 then 10 at 0.10, max_traces=10.

    Measured before the fix: [0.95]*5 + [0.10]*5 -- five of the ten protected
    traces were dropped in favour of traces below the threshold.
    """
    mem = ExperienceMemory(max_traces=10)
    for i in range(10):
        mem.add(WisdomTrace(scenario_id=f"hi{i}", operational_rule=f"r{i}", confidence=0.95))
    for i in range(10):
        mem.add(WisdomTrace(scenario_id=f"lo{i}", operational_rule=f"r{i}", confidence=0.10))

    confidences = [t.confidence for t in mem.traces]
    assert len(mem.traces) == 10
    assert confidences == [0.95] * 10
    assert not any(c < 0.70 for c in confidences)


def test_prune_never_drops_protected_trace_while_ordinary_one_survives():
    """The pruning contract, stated generally: no low-confidence trace may
    outlive a high-confidence one while budget is contested."""
    mem = ExperienceMemory(max_traces=6)
    for i in range(4):
        mem.add(WisdomTrace(scenario_id=f"hi{i}", confidence=0.90))
    for i in range(20):
        mem.add(WisdomTrace(scenario_id=f"lo{i}", confidence=0.20))

    protected = [t for t in mem.traces if t.confidence >= 0.70]
    assert len(mem.traces) == 6
    assert len(protected) == 4, "all four protected traces must survive"
    assert len(mem.traces) - len(protected) == 2, "remaining budget goes to recency"
    # And the ordinary survivors are the most recent ones, not arbitrary.
    assert [t.scenario_id for t in mem.traces if t.confidence < 0.70] == ["lo18", "lo19"]


def test_preserve_high_confidence_can_be_switched_off():
    mem = ExperienceMemory(max_traces=4, preserve_high_confidence=False)
    for i in range(4):
        mem.add(WisdomTrace(scenario_id=f"hi{i}", confidence=0.95))
    for i in range(4):
        mem.add(WisdomTrace(scenario_id=f"lo{i}", confidence=0.10))
    assert [t.confidence for t in mem.traces] == [0.10] * 4


# --------------------------------------------------------------------------
# Defect 2: dedup keyed on (scenario_id, operational_rule) collapsed every
# session on a scenario into one entry.
# --------------------------------------------------------------------------

def test_distinct_sessions_on_same_scenario_are_not_deduplicated():
    """120 sessions on evacuation_bottleneck/A, max_traces=100.

    Measured before the fix: 20 traces retained -- the first 101 collapsed to 1,
    discarding 100 distinct trace_ids, timestamps and user rationales.
    """
    xaaa = XAAAOrchestrator()
    assert xaaa.memory.max_traces == 100
    for i in range(120):
        xaaa.run_session(UserDecision("evacuation_bottleneck", "A", f"rationale {i}"))

    assert len(xaaa.memory.traces) == 100
    assert len({t.trace_id for t in xaaa.memory.traces}) == 100


def test_same_trace_reinserted_is_still_deduplicated():
    """Dedup must still collapse a genuine re-insert of the same trace."""
    mem = ExperienceMemory(max_traces=3)
    trace = WisdomTrace(scenario_id="s", operational_rule="r", confidence=0.5)
    for _ in range(10):
        mem.traces.append(trace)
    mem.prune()
    assert len(mem.traces) == 1


# --------------------------------------------------------------------------
# Defect 3: missed_patterns marked every principle missed above a threshold,
# so two different mistakes produced identical reports.
# --------------------------------------------------------------------------

def test_missed_patterns_distinguish_which_principle_was_violated():
    """Before the fix, options A (0.88) and C (0.65) both reported all three
    principles as missed."""
    lib, sim = ScenarioLibrary(), ConsequenceSimulator()
    scenario = lib.get("evacuation_bottleneck")

    a = sim.simulate(scenario, UserDecision("evacuation_bottleneck", "A", "x"))
    c = sim.simulate(scenario, UserDecision("evacuation_bottleneck", "C", "x"))

    assert a.missed_patterns == ["avoid_bottleneck", "distributed_flow"]
    assert c.missed_patterns == ["time_critical_action"]
    assert a.missed_patterns != c.missed_patterns


@pytest.mark.parametrize("scenario_id", ["evacuation_bottleneck", "silent_negotiation", "project_contract_gap"])
def test_missed_patterns_are_always_declared_principles(scenario_id):
    lib, sim = ScenarioLibrary(), ConsequenceSimulator()
    scenario = lib.get(scenario_id)
    for option in scenario.decision_options:
        consequence = sim.simulate(scenario, UserDecision(scenario_id, option, "x"))
        assert set(consequence.missed_patterns) <= set(scenario.expected_principles)


def test_safest_option_violates_nothing():
    lib, sim = ScenarioLibrary(), ConsequenceSimulator()
    for scenario in lib.all():
        best = min(scenario.hidden_risks.items(), key=lambda kv: kv[1])[0]
        consequence = sim.simulate(scenario, UserDecision(scenario.scenario_id, best, "x"))
        assert consequence.missed_patterns == []


def test_socratic_questions_target_only_violated_principles():
    xaaa = XAAAOrchestrator()
    result = xaaa.run_session(UserDecision("evacuation_bottleneck", "C", "wait for info"))
    targeted = {p.target_pattern for p in result.prompts}
    assert "time_critical_action" in targeted
    assert "avoid_bottleneck" not in targeted


# --------------------------------------------------------------------------
# Defect 4: the user's rationale was stored and never read.
# --------------------------------------------------------------------------

def test_rationale_changes_the_socratic_prompts():
    """Before the fix these two sessions produced identical prompts."""
    panic = XAAAOrchestrator().run_session(
        UserDecision("evacuation_bottleneck", "A", "I panicked and guessed")
    )
    careful = XAAAOrchestrator().run_session(
        UserDecision("evacuation_bottleneck", "A", "Careful analysis of throughput")
    )

    panic_q = [p.question for p in panic.prompts]
    careful_q = [p.question for p in careful.prompts]
    assert panic_q != careful_q
    assert any("I panicked and guessed" in q for q in panic_q)
    assert any("Careful analysis of throughput" in q for q in careful_q)
    assert not any("I panicked" in q for q in careful_q)


def test_empty_rationale_adds_no_prompt():
    result = XAAAOrchestrator().run_session(UserDecision("evacuation_bottleneck", "A", "   "))
    assert not any(p.target_pattern == "rationale_review" for p in result.prompts)


# --------------------------------------------------------------------------
# Defect 5: Scenario.experience_patterns was read by no code at all.
# --------------------------------------------------------------------------

def test_experience_patterns_reach_the_wisdom_trace_and_the_export():
    result = XAAAOrchestrator().run_session(
        UserDecision("evacuation_bottleneck", "A", "closest exit")
    )
    assert result.wisdom_trace.experience_patterns == [
        "crowd_convergence_failure",
        "single_exit_overload",
        "distributed_routing",
    ]
    assert trace_to_dict(result.wisdom_trace)["experience_patterns"]


# --------------------------------------------------------------------------
# Defect 6: project_contract_gap options A (0.76) and C (0.58) returned
# byte-identical outcomes despite landing in different risk bands.
# --------------------------------------------------------------------------

def test_project_contract_gap_a_and_c_are_distinguishable():
    lib, sim = ScenarioLibrary(), ConsequenceSimulator()
    scenario = lib.get("project_contract_gap")
    a = sim.simulate(scenario, UserDecision("project_contract_gap", "A", "x"))
    c = sim.simulate(scenario, UserDecision("project_contract_gap", "C", "x"))

    assert a.risk_level.value == "HIGH"
    assert c.risk_level.value == "MEDIUM"
    assert a.immediate_outcome != c.immediate_outcome
    assert a.missed_patterns != c.missed_patterns


def test_simulator_still_rejects_an_option_outside_the_scenario():
    lib, sim = ScenarioLibrary(), ConsequenceSimulator()
    with pytest.raises(ValueError):
        sim.simulate(lib.get("evacuation_bottleneck"), UserDecision("evacuation_bottleneck", "Z", "x"))


def test_library_still_rejects_an_unknown_scenario():
    with pytest.raises(KeyError):
        ScenarioLibrary().get("no_such_scenario")


def test_simulation_feedback_mode_is_gone():
    assert not hasattr(FeedbackMode, "SIMULATION")
    assert {m.value for m in FeedbackMode} == {
        "narrative", "socratic", "counterfactual", "sensory",
    }


# --------------------------------------------------------------------------
# Defect 7: transfer_candidates() was correct but called by nothing.
# --------------------------------------------------------------------------

def test_transfer_candidates_are_retrieved_into_the_session_result():
    xaaa = XAAAOrchestrator()
    first = xaaa.run_session(UserDecision("evacuation_bottleneck", "C", "wait"))
    assert first.transfer_candidates == [], "nothing prior on the first session"

    second = xaaa.run_session(UserDecision("evacuation_bottleneck", "A", "closest"))
    ids = [t.trace_id for t in second.transfer_candidates]
    assert ids == [first.wisdom_trace.trace_id]
    assert second.wisdom_trace.trace_id not in ids, "must not retrieve its own trace"


def test_transfer_candidates_do_not_cross_unrelated_domains():
    xaaa = XAAAOrchestrator()
    xaaa.run_session(UserDecision("project_contract_gap", "A", "standard"))
    result = xaaa.run_session(UserDecision("evacuation_bottleneck", "A", "closest"))
    assert result.transfer_candidates == []
    assert xaaa.memory.transfer_candidates("crisis_management")
    assert xaaa.memory.transfer_candidates("no_such_domain") == []


# --------------------------------------------------------------------------
# Defect 8: FR-08 export had no implementation anywhere in the repo.
# --------------------------------------------------------------------------

def test_trace_export_includes_confidence_and_round_trips_as_json(tmp_path):
    xaaa = XAAAOrchestrator()
    result = xaaa.run_session(UserDecision("evacuation_bottleneck", "A", "closest exit"))

    as_dict = trace_to_dict(result.wisdom_trace)
    assert as_dict["confidence"] == 0.72
    assert as_dict["scenario_id"] == "evacuation_bottleneck"
    assert as_dict["trace_id"] and as_dict["created_at"]

    path = export_traces(xaaa.memory.traces, tmp_path / "traces.json")
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert len(payload) == len(xaaa.memory.traces)
    assert payload[0]["operational_rule"] == result.wisdom_trace.operational_rule


def test_session_export_is_json_serialisable():
    result = XAAAOrchestrator().run_session(
        UserDecision("evacuation_bottleneck", "A", "closest exit")
    )
    encoded = json.dumps(session_to_dict(result), ensure_ascii=False)
    assert "evacuation_bottleneck" in encoded
    assert '"risk_level": "CRITICAL"' in encoded


# --------------------------------------------------------------------------
# Defect 9: config/default.yaml was decorative -- no yaml import anywhere.
# --------------------------------------------------------------------------

def test_shipped_config_is_actually_loaded():
    cfg = load_config()
    assert cfg.max_traces == 100
    assert cfg.preserve_high_confidence is True
    assert [m.value for m in cfg.feedback_modes] == [
        "narrative", "counterfactual", "socratic", "sensory",
    ]


def test_changing_max_traces_in_config_changes_memory_behaviour(tmp_path):
    """The load-bearing test for the config: a different file, different runtime."""
    path = tmp_path / "custom.yaml"
    path.write_text(
        "xaaa:\n"
        "  scenario_mode: simulated\n"
        "  memory:\n"
        "    max_traces: 5\n"
        "    preserve_high_confidence: true\n"
        "  feedback:\n"
        "    modes:\n"
        "      - narrative\n"
        "      - socratic\n",
        encoding="utf-8",
    )
    xaaa = XAAAOrchestrator(config=load_config(path))
    assert xaaa.memory.max_traces == 5

    for i in range(40):
        xaaa.run_session(UserDecision("evacuation_bottleneck", "A", f"r{i}"))
    assert len(xaaa.memory.traces) == 5

    result = xaaa.run_session(UserDecision("evacuation_bottleneck", "A", "last"))
    assert [m.value for m in result.feedback_modes] == ["narrative", "socratic"]


def test_config_rejects_an_unknown_feedback_mode(tmp_path):
    path = tmp_path / "bad.yaml"
    path.write_text("xaaa:\n  feedback:\n    modes:\n      - telepathy\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Unknown feedback mode"):
        load_config(path)


def test_config_rejects_a_non_simulated_scenario_mode(tmp_path):
    """safety.no_real_emergency_command, enforced rather than declared."""
    path = tmp_path / "live.yaml"
    path.write_text("xaaa:\n  scenario_mode: live\n", encoding="utf-8")
    with pytest.raises(ValueError, match="simulated"):
        load_config(path)


def test_config_falls_back_to_defaults_when_file_is_absent(tmp_path):
    cfg = load_config(tmp_path / "does_not_exist.yaml")
    assert cfg.max_traces == 100
    assert cfg.scenario_mode == "simulated"


# --------------------------------------------------------------------------
# Defect 10: the HTML storyboard displayed "HIGH 0.88" while the engine
# classifies 0.88 as CRITICAL.
# --------------------------------------------------------------------------

def test_storyboard_risk_label_matches_the_engine():
    """The storyboard is hand-written, so it can drift. This pins the one number
    it shares with the engine, and checks it is labelled as pre-scripted."""
    html = (
        pathlib.Path(__file__).resolve().parent.parent
        / "web"
        / "XAAA_Experiential_Wisdom_Demo.html"
    ).read_text(encoding="utf-8")

    scenario = ScenarioLibrary().get("evacuation_bottleneck")
    consequence = ConsequenceSimulator().simulate(
        scenario, UserDecision("evacuation_bottleneck", "A", "closest exit")
    )
    assert consequence.risk_score == 0.88
    expected = f"{consequence.risk_level.value} 0.88"

    assert expected in html, f"storyboard must display {expected!r}"
    assert "HIGH 0.88" not in html
    assert "Storyboard pre-scritto" in html, "storyboard must be labelled as such"


def test_expert_review_flag_follows_the_safety_config():
    xaaa = XAAAOrchestrator()
    critical = xaaa.run_session(UserDecision("evacuation_bottleneck", "A", "closest"))
    safe = xaaa.run_session(UserDecision("evacuation_bottleneck", "B", "distribute"))
    assert critical.requires_expert_review is True
    assert safe.requires_expert_review is False

    off = XAAAOrchestrator(
        config=XAAAConfig(safety={"high_risk_domains_require_expert_review": False})
    )
    assert off.run_session(
        UserDecision("evacuation_bottleneck", "A", "closest")
    ).requires_expert_review is False
