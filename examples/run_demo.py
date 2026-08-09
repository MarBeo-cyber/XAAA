"""README quickstart. Run two sessions so L6 transfer retrieval has something to find."""

from xaaa_core.export import export_traces, session_to_dict
from xaaa_core.models import UserDecision
from xaaa_core.orchestrator import XAAAOrchestrator

xaaa = XAAAOrchestrator()

# An earlier session on the same scenario with a different option, so the session
# below has prior experience in memory sharing a transfer domain. Note that C and A
# are reported as violating different principles.
first = xaaa.run_session(UserDecision(
    scenario_id="evacuation_bottleneck",
    selected_option="C",
    rationale="Volevo più informazioni prima di muovere le persone.",
))
print("earlier session: option C violated", first.consequence.missed_patterns)
print()

decision = UserDecision(
    scenario_id="evacuation_bottleneck",
    selected_option="A",
    rationale="L'uscita A è più vicina e quindi sembra la scelta più rapida."
)

result = xaaa.run_session(decision)

print("XAAA experiential session")
print("------------------------")
print("scenario:", result.scenario.title)
print("decision:", result.decision.selected_option)
print("risk:", result.consequence.risk_level.value, result.consequence.risk_score)
print("immediate:", result.consequence.immediate_outcome)
print("delayed:", result.consequence.delayed_outcome)
print("counterfactual:", result.consequence.counterfactual_best_option)
print("principles violated by this option:", result.consequence.missed_patterns)
print("socratic prompt:", result.prompts[0].question)
print("rationale prompt:", result.prompts[-1].question)
print("wisdom rule:", result.wisdom_trace.operational_rule)
print("experience patterns:", result.wisdom_trace.experience_patterns)
print("feedback modes (from config):", [m.value for m in result.feedback_modes])
print("requires expert review:", result.requires_expert_review)
print("memory traces:", len(xaaa.memory.traces))

print()
print("L6 transfer retrieval")
print("---------------------")
print("prior traces sharing a transfer domain:", len(result.transfer_candidates))
for prior in result.transfer_candidates:
    print("-", prior.scenario_id, "|", prior.operational_rule)
print("crisis_management candidates in memory:",
      len(xaaa.memory.transfer_candidates("crisis_management")))

print()
print("Export (FR-08)")
print("--------------")
written = export_traces(xaaa.memory.traces, "xaaa_traces.json")
print("wrote", len(xaaa.memory.traces), "traces to", written)
print("session keys:", sorted(session_to_dict(result)))
