# Functional Requirements

Status reflects what is implemented in this repository, verified by the test suite.

| ID | Requirement | Status |
|---|---|---|
| FR-01 | Provide scenario-based experiential sessions from a hand-authored library | Implemented |
| FR-02 | Capture user decision and rationale, and use the rationale in reflection | Implemented |
| FR-03 | Return scripted immediate and delayed consequences per (scenario, option) | Implemented |
| FR-04 | Generate counterfactual comparison (lowest author-assigned risk option) | Implemented |
| FR-05 | Generate Socratic prompts from a fixed question bank keyed on principle | Implemented |
| FR-06 | Convert experience into a Wisdom Trace with transfer domains | Implemented |
| FR-07 | Maintain Experience Memory with pruning that preserves high-confidence traces | Implemented |
| FR-08 | Serialise traces and sessions to dict/JSON (`xaaa_core/export.py`) | Implemented |
| FR-09 | Retrieve prior traces sharing a transfer domain (L6 retrieval) | Implemented |

## Not implemented

These were previously listed as requirements without an implementation. They are
recorded here as intent, not as delivered behaviour.

| ID | Requirement | Note |
|---|---|---|
| FR-N1 | Transport traces *to* TAAA and NOAH | `export.py` writes a JSON file. There is no client, transport, bridge or receiving endpoint of any kind in this repository. |
| FR-N2 | Sensory/intuitive feedback from the engine | The engine emits text. `web/XAAA_Experiential_Wisdom_Demo.html` is a pre-scripted storyboard with hardcoded values; it does not call the engine. |
| FR-N3 | Anonymisation / consent gating on export | No consent model and no anonymisation exist in this codebase. `docs/SAFETY.md` states the intent. |
| FR-N4 | Generalisability verification of a wisdom rule | Rules are selected from a fixed per-scenario bank by risk band. Nothing verifies that a rule transfers. |

## Non-functional

| ID | Requirement | Status |
|---|---|---|
| NFR-04 | Pruning preserves traces with confidence >= 0.70 | Implemented and tested. Previously stated in three documents and false in code; see `docs/ERRATA.md`. |
