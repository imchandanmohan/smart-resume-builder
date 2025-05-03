# modules/analysis/score_component.py
from dataclasses import dataclass, field
from typing import List

@dataclass
class ScoreComponent:
    name: str
    weight: float
    raw: float          # un-scaled metric (0-100 here)
    score: float        # weight * raw/100
    notes: List[str] = field(default_factory=list)
