from __future__ import annotations

from .models import Scenario, Consequence, SocraticPrompt


class SocraticReflectionEngine:
    """Generates Socratic reflection prompts.

    The engine does not lecture. It helps the user discover the experiential
    pattern behind the consequence.
    """

    def generate(self, scenario: Scenario, consequence: Consequence) -> list[SocraticPrompt]:
        prompts = []

        if consequence.counterfactual_best_option:
            prompts.append(SocraticPrompt(
                question=(
                    f"Che cosa rendeva l'opzione {consequence.counterfactual_best_option} meno rischiosa "
                    f"dell'opzione {consequence.selected_option}?"
                ),
                target_pattern="counterfactual_comparison",
                purpose="Make the user compare chosen and safer path."
            ))

        for pattern in consequence.missed_patterns[:2]:
            prompts.append(SocraticPrompt(
                question=self._question_for_pattern(pattern),
                target_pattern=pattern,
                purpose="Transform missed pattern into transferable experience."
            ))

        if not prompts:
            prompts.append(SocraticPrompt(
                question="Quale principio potresti riutilizzare in un dominio diverso?",
                target_pattern="transfer",
                purpose="Support transfer learning."
            ))

        return prompts

    def _question_for_pattern(self, pattern: str) -> str:
        mapping = {
            "avoid_bottleneck": "Quale segnale precoce indicava che la soluzione più vicina poteva diventare la più pericolosa?",
            "distributed_flow": "Come avresti potuto preservare più percorsi invece di concentrare il rischio?",
            "time_critical_action": "Quale informazione era sufficiente per agire senza aspettare certezza completa?",
            "avoid_projection": "Quale tua interpretazione hai proiettato sull'altro senza verificarla?",
            "respect_processing_time": "Quando una pausa è informazione e quando è solo assenza di informazione?",
            "explicit_bridge": "Quale frase minima avrebbe trasformato l'ambiguità in coordinamento?",
            "operationalize_ambiguity": "Quale termine astratto doveva essere trasformato in criteri osservabili?",
            "define_evidence": "Che evidenza avrebbe reso verificabile l'obbligo?",
            "prevent_schema_gap": "Dove due gruppi usavano la stessa parola ma due schemi diversi?",
        }
        return mapping.get(pattern, f"Quale pattern operativo era nascosto in {pattern}?")
