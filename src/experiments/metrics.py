from __future__ import annotations
from dataclasses import dataclass
from typing import Dict


@dataclass
class Metrics:
    cost: int
    feasible: bool
    time_seconds: float
    extra: Dict[str, float]
