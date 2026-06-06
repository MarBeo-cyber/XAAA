from __future__ import annotations

from dataclasses import dataclass, field
from .models import WisdomTrace


@dataclass
class ExperienceMemory:
    """WAAA-inspired memory pruning for experience traces."""

    max_traces: int = 100
    traces: list[WisdomTrace] = field(default_factory=list)

    def add(self, trace: WisdomTrace) -> None:
        self.traces.append(trace)
        if len(self.traces) > self.max_traces:
            self.prune()

    def prune(self) -> None:
        high = [t for t in self.traces if t.confidence >= 0.70]
        recent = self.traces[-self.max_traces // 2 :]
        seen = set()
        merged = []
        for t in high + recent:
            key = (t.scenario_id, t.operational_rule)
            if key not in seen:
                merged.append(t)
                seen.add(key)
        self.traces = merged[-self.max_traces :]

    def transfer_candidates(self, domain: str) -> list[WisdomTrace]:
        return [t for t in self.traces if domain in t.transfer_domains]
