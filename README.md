# XAAA v1.0 - eXperiential Autopoietic Adaptive Agent

The **XAAA** fills the gap between SAAA and TAAA in the autopoietic ontology.

It transforms structured knowledge into operational wisdom through mediated experience:

```text
SAAA -> knowledge and learning biography
XAAA -> mediated experience, consequence, counterfactual, wisdom trace
TAAA -> inter-schema cognitive translation
NOAH -> collective coordination
```

## Core idea

The machine does not possess lived experience. It mediates aggregated and structured experience patterns through scenarios, consequences, counterfactuals and Socratic reflection.

## What the code actually is

This repository is the MVP of that idea, and it is deliberately modest: a **deterministic, rule-based scenario engine** of roughly 500 lines. Everything it produces is looked up, not inferred.

- Three hand-written scenarios, each with author-assigned risk weights per option.
- Consequences are scripted strings selected by `(scenario_id, option)`; the "simulator" runs no model and no physics.
- The counterfactual is `min()` over those same author-assigned risk weights.
- Socratic questions come from a **fixed question bank** keyed on principle name, plus one prompt that quotes the user's own rationale back at them. The engine does not parse or interpret the rationale.
- The wisdom trace is one of a handful of pre-written operational rules, chosen by risk band.
- There is no randomness, no machine learning, no external model call and no network I/O.

Every risk weight, confidence value and threshold in the code is an **author-assigned pedagogical constant**, not a measurement, a calibrated probability or a value derived from the literature. Each one carries a `PROVENANCE:` note at its definition. Read them as an ordering the author asserts, so a teaching point becomes legible — not as an estimate of how often something happens in the world.

## Included

- Scenario Library (3 scenarios, hand-authored)
- Consequence Simulator (scripted outcome lookup by scenario and option)
- Counterfactual Engine (lowest author-assigned risk among the options)
- Socratic Reflection Engine (fixed question bank + rationale echo)
- Wisdom Trace Builder (pre-written rules selected by risk band)
- Experience Memory with WAAA-style pruning and transfer-domain retrieval
- JSON export of traces and sessions (`xaaa_core/export.py`)
- YAML configuration (`config/default.yaml`, loaded by `xaaa_core/config.py`)
- CLI demo
- A pre-scripted HTML storyboard in `web/` (see the note below)
- Tests

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[test]"
python examples/run_demo.py
pytest -q
```

## Configuration

`config/default.yaml` is read at startup by `xaaa_core/config.py`. It sets memory
sizing (`max_traces`, `preserve_high_confidence`, `high_confidence_threshold`) and
the emitted `feedback.modes` list. The file documents, per key, which code enforces
it; `scenario_mode` is validated and any value other than `simulated` raises.

## The HTML demo is a storyboard

`web/XAAA_Experiential_Wisdom_Demo.html` is a **hand-written, pre-scripted animation**. It contains no `fetch`, calls nothing in `xaaa_core/`, and its numbers are typed into the HTML. It illustrates the intended sensory feel of the loop; it is not a view onto the engine, and its output is not evidence that the engine produced anything. The `sensory` feedback mode is delivered only there — the Python engine emits text.

## Safety boundary

XAAA is a training and reflection architecture. It does not replace professional judgment in emergencies, medical practice, legal advice or operational command. Counterfactuals are pedagogical comparisons of author-assigned weights and are never evidence of causality.
