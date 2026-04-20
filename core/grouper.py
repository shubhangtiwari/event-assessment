"""Form balanced groups from scored participants using snake-draft on score.

This runs on every dashboard view / submission, so it has to be fast — but
with only dozens of participants it's effectively instantaneous.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Any

from core.config import DEFAULT_GROUP_SIZE, GROUPING_SEED


@dataclass
class Participant:
    respondent_id: str
    name: str
    email: str
    role: str
    score: int
    level: str


@dataclass
class Group:
    number: int
    members: list[Participant] = field(default_factory=list)

    @property
    def avg_score(self) -> float:
        return sum(m.score for m in self.members) / len(self.members) if self.members else 0.0

    @property
    def level_mix(self) -> dict[str, int]:
        mix: dict[str, int] = {}
        for m in self.members:
            mix[m.level] = mix.get(m.level, 0) + 1
        return mix

    def as_dict(self) -> dict[str, Any]:
        return {
            "number":    self.number,
            "size":      len(self.members),
            "avg_score": round(self.avg_score, 1),
            "level_mix": self.level_mix,
            "members":   [m.__dict__ for m in self.members],
        }


def form_balanced_groups(
    participants: list[Participant],
    group_size: int = DEFAULT_GROUP_SIZE,
    seed: int = GROUPING_SEED,
) -> list[Group]:
    if not participants:
        return []

    rng = random.Random(seed)
    ordered = list(participants)
    # Stable tie-break: sort by score desc then by deterministic random jitter
    # seeded by respondent_id.
    jitter = {p.respondent_id: rng.random() for p in ordered}
    ordered.sort(key=lambda p: (p.score, jitter[p.respondent_id]), reverse=True)

    n = len(ordered)
    n_groups = max(1, math.ceil(n / group_size))
    groups = [Group(number=i + 1) for i in range(n_groups)]

    # Snake draft.
    for i, p in enumerate(ordered):
        round_idx = i // n_groups
        pos = i % n_groups
        target = pos if round_idx % 2 == 0 else n_groups - 1 - pos
        groups[target].members.append(p)

    # Sort each group's members so Advanced appears first.
    level_order = {"Advanced": 0, "Intermediate": 1, "Beginner": 2}
    for g in groups:
        g.members.sort(key=lambda m: (level_order.get(m.level, 99), -m.score))

    return groups
