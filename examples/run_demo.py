from xaaa_core.models import UserDecision
from xaaa_core.orchestrator import XAAAOrchestrator

xaaa = XAAAOrchestrator()

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
print("socratic prompt:", result.prompts[0].question)
print("wisdom rule:", result.wisdom_trace.operational_rule)
print("memory traces:", len(xaaa.memory.traces))
