# API Specification

## UserDecision

```json
{
  "scenario_id": "evacuation_bottleneck",
  "selected_option": "A",
  "rationale": "The closest exit seems fastest."
}
```

## WisdomTrace

```json
{
  "scenario_id": "evacuation_bottleneck",
  "learned_pattern": "The largest cost often emerges from implicit assumptions.",
  "operational_rule": "The closest path is not always the safest: evaluate future congestion.",
  "transfer_domains": ["crisis_management", "network_routing"]
}
```
