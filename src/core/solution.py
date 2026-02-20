from __future__ import annotations
from dataclasses import dataclass
from typing import List, Set

@dataclass
class Solution:
    cover: Set[int]       # Conjunto de vértices en el cover
    in_cover: List[bool]  # Lista booleana que indica si un vértice está en el cover
    cost: int             # Costo de la solución (tamaño del cover)

    @classmethod
    
    # Crea una solución a partir de un conjunto de vértices en el cover
    def from_cover(cls, cover: Set[int], n: int) -> "Solution":
        in_cover = [False] * n
        for v in cover:
            in_cover[v] = True
        return cls(set(cover), in_cover, len(cover))

    # Crea una copia de la solución actual para modificaciones seguras
    def copy(self) -> "Solution":
        return Solution(set(self.cover), list(self.in_cover), self.cost)
