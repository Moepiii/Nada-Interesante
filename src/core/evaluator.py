from __future__ import annotations
from dataclasses import dataclass
import networkx as nx
from .solution import Solution

@dataclass
class Evaluation:
    feasible: bool
    cost: int

class Evaluator:
    def __init__(self, graph: nx.Graph) -> None:
        self.graph = graph

    # Revisa si la solución es un cover válido
    def is_cover(self, sol: Solution) -> bool:
        for u, v in self.graph.edges():
            if not (sol.in_cover[u] or sol.in_cover[v]):
                return False
        return True

    # Calcula el costo de la solución
    def cost(self, sol: Solution) -> int:
        return len(sol.cover)

    # Evalúa la solución y retorna su factibilidad y costo
    def evaluate(self, sol: Solution) -> Evaluation:
        return Evaluation(self.is_cover(sol), self.cost(sol))
