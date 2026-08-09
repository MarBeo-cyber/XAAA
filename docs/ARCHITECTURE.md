# XAAA Architecture

## Function

XAAA is the experiential layer of the autopoietic ontology. It transforms knowledge into wisdom by exposing the user to mediated scenarios, consequences and counterfactuals.

## Six layers

The conceptual layering, with what each layer is in code. Every layer is a
deterministic lookup or a comparison over author-assigned data.

| Layer | Name | Role | In code |
|---|---|---|---|
| L1 | Experience Input | scenario, context, user decision | `scenario_library.py`, `models.UserDecision` |
| L2 | Consequence Simulation | immediate/delayed outcomes | `simulator.py` — scripted strings keyed on (scenario, option) |
| L3 | Counterfactual Engine | safer path, missed option | `simulator.py` — `min()` over author-assigned risk weights |
| L4 | Socratic Reflection | guided questions, maieutic review | `socratic.py` — fixed question bank + rationale echo |
| L5 | Wisdom Trace | operational rule, transfer domains | `wisdom.py` — pre-written rules selected by risk band |
| L6 | Experience Memory | pruning, retrieval | `memory.py` — `prune()` and `transfer_candidates()`, both called by the orchestrator |

L6's "preparation for TAAA/NOAH" is `export.py`: dict/JSON serialisation of traces
to a local file. There is no bridge, transport or receiving module for either agent
in this repository.

## Runtime

```text
Scenario -> Decision -> Consequence -> Counterfactual
         -> Socratic Reflection -> Wisdom Trace -> Experience Memory
         -> Transfer Retrieval
```

## Configuration

`config/default.yaml` is loaded by `xaaa_core/config.py` at orchestrator start-up
and supplies memory sizing and the feedback-mode list.
