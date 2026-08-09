# Errata

Corrections to claims made in the XAAA documents. The two `.docx` working papers
cannot be edited in this repository, so the corrections that apply to them are
listed here and the `.docx` files are left untouched.

## docs/XAAA_Working_Paper_v0_1.docx

### §12 "Struttura release GitHub" lists files that do not exist

The release tree in §12 shows these paths. None of them has ever existed in the
repository:

| Listed in §12 | Reality |
|---|---|
| `xaaa_core/counterfactual.py` | Does not exist. The counterfactual is four lines inside `simulator.py`: `min()` over `scenario.hidden_risks`. |
| `interfaces/` (whole package) | Does not exist. |
| `interfaces/saaa_bridge.py` | Does not exist. There is no SAAA integration in any form. |
| `interfaces/taaa_bridge.py` | Does not exist. There is no TAAA integration in any form. |
| `interfaces/noah_export.py` | Does not exist. `xaaa_core/export.py` (added in this branch) writes a local JSON file. It performs no anonymisation, applies no consent model and sends nothing anywhere. |
| `web/XAAA_Experiential_Demo.html` | Actual filename is `web/XAAA_Experiential_Wisdom_Demo.html`. |
| `tests/test_xaaa_core.py` | Actual filename is `tests/test_xaaa.py`. |

§12 also annotates `models.py` as containing `ExperienceMemory`; it does not, that
class lives in `memory.py`.

The release tree in §15 of *XAAA_Architettura_Tecnico_Informatica_v1_0.docx* is
accurate and needs no correction.

### NFR-04 "Preserva tracce con confidence >= 0.70 e recenti"

This was stated in the working paper (NFR-04), in `config/default.yaml`
(`preserve_high_confidence: true`) and implied by `README`, and **it was false in
code**. `ExperienceMemory.prune()` built `high + recent` and then sliced
`merged[-max_traces:]`, taking from the tail while the protected traces sat at the
head of the list.

Measured on the pre-fix code — 10 traces at confidence 0.95, then 10 at 0.10, with
`max_traces=10`:

```
surviving confidences: [0.95, 0.95, 0.95, 0.95, 0.95, 0.1, 0.1, 0.1, 0.1, 0.1]
```

Half the memory was filled with exactly the traces the rule existed to discard.
Fixed in this branch; the guarantee now holds and is covered by
`test_prune_preserves_every_high_confidence_trace`.

### FR-11 "NOAH export ... con consenso e privacy differenziale"

No consent model, no anonymisation and no differential privacy exist anywhere in
this codebase. `export.py` is plain JSON serialisation. Treat FR-11 as intent.

### FR-08 "Sensory demo" (§ requirements table)

The working paper's FR-08 credits a sensory demo with "replay, timeline, confronto
visivo scelta/controfattuale". `web/XAAA_Experiential_Wisdom_Demo.html` is a
hand-written storyboard: four JavaScript functions toggling CSS classes on a fixed
timeline, with the decision card hardcoded to "Scelta: A". It contains no `fetch`
and never calls the engine. It illustrates an intention; it demonstrates nothing.

It had also drifted from the code: it displayed `HIGH 0.88` while
`simulator.py:_risk_level` classifies 0.88 as `CRITICAL`. Corrected in this branch,
and the page now carries a banner stating that it is pre-scripted.

## Repository documents corrected in place

These were fixed directly rather than listed here:

- `README.md` — the six-component list implied more machinery than exists; the
  "HTML sensory demo" is now described as a storyboard.
- `docs/FUNCTIONAL_REQUIREMENTS.md` — FR-08's export claim now matches
  `export.py`; unimplemented requirements moved to a "Not implemented" table.
- `docs/API_SPEC.md` — retitled "Data Model". It specified no HTTP API and no
  serialisation format that any code implemented; its `WisdomTrace` example was in
  English while the engine emits Italian, and it omitted `confidence`.
- `docs/ARCHITECTURE.md` — L6 "retrieval" is now genuinely called by the
  orchestrator; each layer is annotated with what it is in code.
- `config/default.yaml` — was read by nothing. Now loaded, with per-key notes on
  which flags are enforced in code and which are declarative.

## Standing caveat on the numbers

Every risk weight, confidence value and threshold in `scenario_library.py`,
`wisdom.py` and `simulator.py` is an author-assigned pedagogical constant. None is a
measurement, a calibrated probability or a value derived from any source cited in
the working papers. Each carries a `PROVENANCE:` note at its definition.

(The audit that prompted this branch referred to a `docs/references.md`. No such
file exists in this repository; the bibliography lives in the `.docx` working
papers only.)
