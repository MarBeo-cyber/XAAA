from __future__ import annotations

from dataclasses import dataclass, field
from .models import WisdomTrace


@dataclass
class ExperienceMemory:
    """WAAA-inspired memory pruning for experience traces.

    Pruning contract (working paper NFR-04, config ``memory.preserve_high_confidence``):
    while ``preserve_high_confidence`` is on, a trace whose confidence is at or above
    ``high_confidence_threshold`` is never dropped in favour of a lower-confidence one.
    Protected traces are released only when they alone exceed ``max_traces``, and then
    the oldest go first.

    PROVENANCE: ``max_traces`` (100) and ``high_confidence_threshold`` (0.70) are
    author-assigned pedagogical defaults, not measured or empirically derived values.
    They are declared in config/default.yaml and loaded via xaaa_core.config.
    """

    max_traces: int = 100
    traces: list[WisdomTrace] = field(default_factory=list)
    preserve_high_confidence: bool = True
    high_confidence_threshold: float = 0.70

    def add(self, trace: WisdomTrace) -> None:
        self.traces.append(trace)
        if len(self.traces) > self.max_traces:
            self.prune()

    def prune(self) -> None:
        kept = self._deduplicate(self.traces)
        if len(kept) <= self.max_traces:
            self.traces = kept
            return

        if not self.preserve_high_confidence:
            self.traces = kept[-self.max_traces :]
            return

        protected = [t for t in kept if t.confidence >= self.high_confidence_threshold]

        # More protected traces than the whole budget: keep the most recent of them.
        # This is the only case in which a high-confidence trace is discarded.
        if len(protected) >= self.max_traces:
            self.traces = protected[-self.max_traces :]
            return

        ordinary = [t for t in kept if t.confidence < self.high_confidence_threshold]
        budget = self.max_traces - len(protected)
        keep_ids = {t.trace_id for t in protected}
        keep_ids |= {t.trace_id for t in ordinary[-budget:]}
        # Rebuild from ``kept`` so surviving traces stay in insertion order.
        self.traces = [t for t in kept if t.trace_id in keep_ids]

    @staticmethod
    def _deduplicate(traces: list[WisdomTrace]) -> list[WisdomTrace]:
        """Drop re-inserts of the *same* trace, keyed on ``trace_id``.

        The previous key was ``(scenario_id, operational_rule)``. Because
        WisdomTraceBuilder emits one fixed rule per scenario per risk band, that key
        collapsed every session on a scenario into a single surviving entry and
        discarded the distinct ``trace_id`` and ``created_at`` of real sessions.
        Trace identity is ``trace_id``; two sessions are never the same experience.
        """
        seen: set[str] = set()
        out: list[WisdomTrace] = []
        for t in traces:
            if t.trace_id not in seen:
                seen.add(t.trace_id)
                out.append(t)
        return out

    def transfer_candidates(
        self, domain: str, exclude_trace_id: str | None = None
    ) -> list[WisdomTrace]:
        """L6 retrieval: stored traces that declare ``domain`` as a transfer domain.

        ``exclude_trace_id`` lets a caller drop the trace produced by the session it
        is currently running, so the result is *prior* experience only.
        """
        return [
            t
            for t in self.traces
            if domain in t.transfer_domains and t.trace_id != exclude_trace_id
        ]
