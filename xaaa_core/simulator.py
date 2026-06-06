from __future__ import annotations

from .models import Scenario, UserDecision, Consequence, DecisionRisk


class ConsequenceSimulator:
    """Simulates consequence and counterfactual outcome.

    This is not a physics simulator. It is a structured experiential engine:
    it turns a decision into a consequence trace and exposes hidden patterns.
    """

    def simulate(self, scenario: Scenario, decision: UserDecision) -> Consequence:
        if decision.selected_option not in scenario.decision_options:
            raise ValueError("Selected option not available in scenario.")

        risk = scenario.hidden_risks[decision.selected_option]
        risk_level = self._risk_level(risk)
        best_option = min(scenario.hidden_risks.items(), key=lambda x: x[1])[0]

        missed = []
        if risk >= 0.55:
            missed = scenario.expected_principles[:]

        return Consequence(
            selected_option=decision.selected_option,
            immediate_outcome=self._immediate(scenario.scenario_id, decision.selected_option, risk),
            delayed_outcome=self._delayed(scenario.scenario_id, decision.selected_option, risk),
            risk_score=round(risk, 4),
            risk_level=risk_level,
            missed_patterns=missed,
            counterfactual_best_option=best_option if best_option != decision.selected_option else None,
        )

    def _risk_level(self, risk: float) -> DecisionRisk:
        if risk >= 0.85:
            return DecisionRisk.CRITICAL
        if risk >= 0.65:
            return DecisionRisk.HIGH
        if risk >= 0.35:
            return DecisionRisk.MEDIUM
        return DecisionRisk.LOW

    def _immediate(self, scenario_id: str, option: str, risk: float) -> str:
        if scenario_id == "evacuation_bottleneck":
            if option == "A":
                return "Il flusso converge rapidamente verso la stessa uscita."
            if option == "B":
                return "Il flusso si distribuisce e la pressione sull'uscita principale diminuisce."
            return "La folla resta in attesa mentre la congestione aumenta."
        if scenario_id == "silent_negotiation":
            if option == "A":
                return "La controparte percepisce una concessione non richiesta."
            if option == "B":
                return "La pausa diventa spazio di elaborazione e non rottura relazionale."
            return "Il team assume accordo dove non esiste ancora commitment."
        if scenario_id == "project_contract_gap":
            if option == "B":
                return "L'ambiguità viene convertita in criteri operativi verificabili."
            return "L'ambiguità resta nascosta dietro una formula apparentemente standard."
        return "La decisione produce un esito coerente con il rischio stimato."

    def _delayed(self, scenario_id: str, option: str, risk: float) -> str:
        if risk >= 0.65:
            return "Nel tempo emerge il costo dell'assunzione implicita non verificata."
        if risk >= 0.35:
            return "L'esito resta gestibile ma richiede correzioni successive."
        return "La decisione preserva opzioni future e riduce il costo dell'errore."
