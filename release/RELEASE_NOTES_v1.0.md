# XAAA v1.0 Release Notes

## Scope

First complete release of the XAAA module: a deterministic, rule-based scenario
and reflection engine. No randomness, no machine learning, no network I/O.

## Included

- Working paper (`docs/`, `.docx`) — see `docs/ERRATA.md` for corrections
- Scenario library (3 hand-authored scenarios)
- Consequence simulator (scripted outcomes keyed on scenario and option)
- Counterfactual engine (lowest author-assigned risk among the options)
- Socratic reflection (fixed question bank + rationale echo)
- Wisdom traces (pre-written rules selected by risk band)
- Experience memory (pruning that preserves high-confidence traces, transfer retrieval)
- JSON export of traces and sessions
- YAML configuration, loaded at start-up
- Pre-scripted HTML storyboard (`web/`) — illustrative, not engine output
- Tests

## Validation

34 automated tests pass under `pytest -q`.

## Known limitations

- No integration with SAAA, TAAA or NOAH exists. `export.py` writes a local JSON
  file; there is no transport, client or receiving endpoint.
- No consent model, anonymisation or differential privacy.
- All risk weights, confidence values and thresholds are author-assigned
  pedagogical constants, not measurements. See the `PROVENANCE:` notes in code.
- The `sensory` feedback mode is delivered only by the HTML storyboard.
