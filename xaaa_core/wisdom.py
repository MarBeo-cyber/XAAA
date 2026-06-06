from __future__ import annotations

from .models import Scenario, Consequence, WisdomTrace


class WisdomTraceBuilder:
    """Builds a transferable operational rule from an experience."""

    def build(self, scenario: Scenario, consequence: Consequence) -> WisdomTrace:
        if consequence.risk_score >= 0.55:
            learned = "Il costo maggiore nasce da assunzioni implicite non testate."
            rule = self._rule_for_scenario(scenario.scenario_id)
            confidence = 0.72
        else:
            learned = "La decisione ha preservato opzioni e ridotto costo dell'errore."
            rule = "Quando l'incertezza è alta, preserva opzioni e rendi espliciti i criteri."
            confidence = 0.66

        return WisdomTrace(
            scenario_id=scenario.scenario_id,
            learned_pattern=learned,
            operational_rule=rule,
            transfer_domains=self._transfer_domains(scenario),
            confidence=confidence,
        )

    def _rule_for_scenario(self, scenario_id: str) -> str:
        rules = {
            "evacuation_bottleneck": "La via più vicina non è sempre la più sicura: valuta anche la congestione futura.",
            "silent_negotiation": "Non tradurre il silenzio con il tuo schema prima di averlo contestualizzato.",
            "project_contract_gap": "Ogni formula ambigua va convertita in soglie, esempi ed evidenze verificabili.",
        }
        return rules.get(scenario_id, "Trasforma l'esito in una regola trasferibile.")

    def _transfer_domains(self, scenario: Scenario) -> list[str]:
        if scenario.scenario_id == "evacuation_bottleneck":
            return ["crisis_management", "operations", "network_routing", "crowd_coordination"]
        if scenario.scenario_id == "silent_negotiation":
            return ["negotiation", "cross_cultural_communication", "TAAA"]
        if scenario.scenario_id == "project_contract_gap":
            return ["legal_operations", "project_management", "vendor_management"]
        return [scenario.domain.value]
