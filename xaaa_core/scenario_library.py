from __future__ import annotations

from .models import Scenario, ScenarioDomain


class ScenarioLibrary:
    """Small scenario library for the XAAA MVP.

    XAAA does not claim to possess lived experience. It mediates structured
    experience patterns through scenarios, consequences and counterfactuals.

    PROVENANCE: every number and annotation in this library --- the ``hidden_risks``
    weights and the ``option_violations`` map --- is an author-assigned pedagogical
    weight chosen to make a teaching point legible. None of it is a measurement, an
    empirical frequency or a calibrated probability, and none of it is derived from
    any cited source. Read the risks as an ordering the author asserts, not as an
    estimate of how often something happens.
    """

    def __init__(self) -> None:
        self.scenarios = {
            "evacuation_bottleneck": Scenario(
                scenario_id="evacuation_bottleneck",
                title="Evacuazione: uscita apparentemente più vicina",
                domain=ScenarioDomain.CRISIS,
                context=(
                    "Un gruppo numeroso deve evacuare un edificio. L'uscita A è la più vicina, "
                    "ma molte persone si stanno già muovendo in quella direzione. L'uscita B è più lontana "
                    "ma ancora libera."
                ),
                decision_options={
                    "A": "Indirizzare tutti verso l'uscita A perché è la più vicina.",
                    "B": "Distribuire il flusso: gruppo 1 verso A, gruppo 2 verso B.",
                    "C": "Aspettare nuove informazioni prima di decidere."
                },
                hidden_risks={"A": 0.88, "B": 0.25, "C": 0.65},
                expected_principles=["avoid_bottleneck", "distributed_flow", "time_critical_action"],
                experience_patterns=["crowd_convergence_failure", "single_exit_overload", "distributed_routing"],
                option_violations={
                    # A funnels everyone into one exit: it concentrates flow, but it
                    # does act in time.
                    "A": ["avoid_bottleneck", "distributed_flow"],
                    "B": [],
                    # C neither concentrates nor distributes flow; it forfeits the
                    # window in which acting was still cheap.
                    "C": ["time_critical_action"],
                },
            ),
            "silent_negotiation": Scenario(
                scenario_id="silent_negotiation",
                title="Negoziazione: il silenzio dopo la proposta",
                domain=ScenarioDomain.NEGOTIATION,
                context=(
                    "Dopo una proposta economica, l'interlocutore resta in silenzio. "
                    "Il team interpreta il silenzio come rifiuto e vuole rilanciare immediatamente."
                ),
                decision_options={
                    "A": "Rilanciare subito con una concessione.",
                    "B": "Attendere e chiedere se desidera tempo per valutare.",
                    "C": "Interpretare il silenzio come accordo tacito."
                },
                hidden_risks={"A": 0.70, "B": 0.18, "C": 0.82},
                expected_principles=["avoid_projection", "respect_processing_time", "explicit_bridge"],
                experience_patterns=["silence_as_processing", "premature_concession", "schema_projection"],
                option_violations={
                    # A reads the silence as refusal and concedes before the other
                    # party has finished processing.
                    "A": ["avoid_projection", "respect_processing_time"],
                    "B": [],
                    # C reads the same silence as assent and never builds the
                    # explicit bridge that would have tested the reading.
                    "C": ["avoid_projection", "explicit_bridge"],
                },
            ),
            "project_contract_gap": Scenario(
                scenario_id="project_contract_gap",
                title="Contratto: reasonable efforts",
                domain=ScenarioDomain.PROJECT_MANAGEMENT,
                context=(
                    "In un contratto internazionale compare l'espressione 'reasonable efforts'. "
                    "Il team operativo la interpreta come obbligo forte, il team legale come standard flessibile."
                ),
                decision_options={
                    "A": "Lasciare il testo invariato perché è una formula standard.",
                    "B": "Esplicitare esempi, soglie e criteri di evidenza.",
                    "C": "Sostituirla con 'best efforts' senza confronto."
                },
                hidden_risks={"A": 0.76, "B": 0.22, "C": 0.58},
                expected_principles=["operationalize_ambiguity", "define_evidence", "prevent_schema_gap"],
                experience_patterns=["legal_operational_misalignment", "ambiguous_standard", "contract_execution_gap"],
                option_violations={
                    # A leaves the abstract standard in place and adds no evidence
                    # criteria at all.
                    "A": ["operationalize_ambiguity", "define_evidence"],
                    "B": [],
                    # C swaps one unmeasurable standard for another, unilaterally:
                    # the two teams' schemas are never reconciled.
                    "C": ["prevent_schema_gap", "define_evidence"],
                },
            ),
        }

    def get(self, scenario_id: str) -> Scenario:
        if scenario_id not in self.scenarios:
            raise KeyError(f"Unknown scenario: {scenario_id}")
        return self.scenarios[scenario_id]

    def all(self) -> list[Scenario]:
        return list(self.scenarios.values())
