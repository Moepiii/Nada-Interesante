from __future__ import annotations
import networkx as nx
from dataclasses import dataclass
from typing import Any, Dict, Optional, Protocol
from .solution import Solution

@dataclass
class Result:
    solution: Solution
    cost: int
    feasible: bool
    meta: Dict[str, Any]

class Algorithm(Protocol):
    def solve(
        self,
        instance: nx.Graph,
        seed: Optional[int] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Result:
        ...
