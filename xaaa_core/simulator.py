from __future__ import annotations

from .models import Scenario, UserDecision, Consequence, DecisionRisk


class ConsequenceSimulator:
    """Simulates consequence and counterfactual outcome.

    This is not a physics simulator, and it is not an analysis of the decision.
    It is a lookup: every outcome string, risk weight and violated principle is
    author-assigned scenario data, retrieved by (scenario_id, option).

    PROVENANCE: the risk-band thresholds below (0.85 / 0.65 / 0.35) are
    author-assigned pedagogical cut-points, not measured or validated boundaries.
    """

    def simulate(self, scenario: Scenario, decision: UserDecision) -> Consequence:
        if decision.selected_option not in scenario.decision_options:
            raise ValueError("Selected option not available in scenario.")

        risk = scenario.hidden_risks[decision.selected_option]
        risk_level = self._risk_level(risk)
        best_option = min(scenario.hidden_risks.items(), key=lambda x: x[1])[0]

        # Which principles this specific option violates, as annotated on the
        # scenario. Previously any option above a risk threshold was reported as
        # missing *every* principle in the scenario, which made two different
        # mistakes look identical and made the Socratic questions that follow
        # imply knowledge the engine did not have.
        missed = list(scenario.option_violations.get(decision.selected_option, []))

        return Consequence(
            selected_option=decision.selected_option,
            immediate_outcome=self._immediate(scenario.scenario_id, decision.selected_option),
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

    def _immediate(self, scenario_id: str, option: str) -> str:
        # Immediate outcomes are scripted per (scenario, option). The risk weight
        # is deliberately not an input here: it drives _delayed and the risk band.
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
            if option == "A":
                return "L'ambiguità resta nascosta dietro una formula apparentemente standard."
            if option == "B":
                return "L'ambiguità viene convertita in criteri operativi verificabili."
            return "La formula cambia ma resta astratta, e i due team non si sono confrontati."
        return "La decisione produce un esito coerente con il rischio stimato."

    def _delayed(self, scenario_id: str, option: str, risk: float) -> str:
        if risk >= 0.65:
            return "Nel tempo emerge il costo dell'assunzione implicita non verificata."
        if risk >= 0.35:
            return "L'esito resta gestibile ma richiede correzioni successive."
        return "La decisione preserva opzioni future e riduce il costo dell'errore."
