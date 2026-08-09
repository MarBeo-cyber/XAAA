# Data Model

This file was previously titled "API Specification". There is no HTTP API in this
repository and no server of any kind. What follows is the **data model** the Python
objects use, and the JSON shape `xaaa_core/export.py` actually emits.

The engine emits Italian strings. The examples below are real output, not
translations.

## UserDecision (input)

```python
from xaaa_core.models import UserDecision

UserDecision(
    scenario_id="evacuation_bottleneck",
    selected_option="A",
    rationale="L'uscita A è più vicina e quindi sembra la scelta più rapida.",
)
```

`timestamp` is filled automatically with a UTC ISO-8601 string.

## WisdomTrace

Produced by `WisdomTraceBuilder`, serialised by `xaaa_core.export.trace_to_dict`:

```json
{
  "trace_id": "3f1c9a7e-...",
  "scenario_id": "evacuation_bottleneck",
  "learned_pattern": "Il costo maggiore nasce da assunzioni implicite non testate.",
  "operational_rule": "La via più vicina non è sempre la più sicura: valuta anche la congestione futura.",
  "transfer_domains": ["crisis_management", "operations", "network_routing", "crowd_coordination"],
  "confidence": 0.72,
  "created_at": "2026-01-01T00:00:00+00:00",
  "experience_patterns": ["crowd_convergence_failure", "single_exit_overload", "distributed_routing"]
}
```

`confidence` is one of exactly two author-assigned constants (0.72 above the 0.55
risk band, 0.66 below it). It does not vary with scenario, option or risk, and it is
not a probability that the rule is correct. It exists to order traces for pruning.

## Consequence

`missed_patterns` lists the principles the **selected option** violates, taken from
the scenario's author-assigned `option_violations` map. It is not inferred.

```json
{
  "selected_option": "A",
  "immediate_outcome": "Il flusso converge rapidamente verso la stessa uscita.",
  "delayed_outcome": "Nel tempo emerge il costo dell'assunzione implicita non verificata.",
  "risk_score": 0.88,
  "risk_level": "CRITICAL",
  "missed_patterns": ["avoid_bottleneck", "distributed_flow"],
  "counterfactual_best_option": "B"
}
```

## Export functions

```python
from xaaa_core.export import trace_to_dict, traces_to_dicts, session_to_dict, export_traces

trace_to_dict(trace)                        # -> dict
traces_to_dicts(memory.traces)              # -> list[dict]
session_to_dict(result)                     # -> dict, JSON-serialisable
export_traces(memory.traces, "traces.json") # -> Path, writes a UTF-8 JSON array
```

There is no transport layer. `export_traces` writes a local file; nothing reads it
back, and no TAAA or NOAH endpoint exists in this repository.
