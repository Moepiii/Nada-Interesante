from __future__ import annotations
from typing import Any, Dict, Optional, Set
import networkx as nx
from ..core.api import Result
from ..core.evaluator import Evaluator
from ..core.solution import Solution
from .utils import _get_any_edge


def _branch_and_reduce(graph: nx.Graph) -> Set[int]:
    """
    Algoritmo exacto de branching para Minimum Vertex Cover.

    Idea principal:
    - Si el grafo no tiene aristas, el cover mínimo es el conjunto vacío.
    - Si hay una arista (u, v), cualquier cover válido debe incluir u o v.
        Por eso se ramifica en dos casos: incluir u o incluir v.
    - Se resuelve recursivamente cada rama y se elige la solución de menor tamaño.

    Nota: esta versión no aplica reglas de reducción adicionales ni poda,
    por lo que su complejidad es exponencial en el peor caso.
    """
    # Caso base: si no hay aristas, el cover es vacío
    edge = _get_any_edge(graph)
    if edge is None:
        return set()

    # Extraemos la arista anterior
    u, v = edge

    # Hacemos una rama por cada opción: tomar u o tomar v
    # Rama 1: usando u
    # Hacemos una copia del grafo sin el nodo u
    g_u = graph.copy()
    g_u.remove_node(u)
    # Resolvemos recursivamente el subproblema
    sol_u = _branch_and_reduce(g_u)
    # Agregamos u al cover resultante
    sol_u.add(u)

    # Rama 2: usando v
    # Hacemos una copia del grafo sin el nodo v
    g_v = graph.copy()
    g_v.remove_node(v)
    # Resolvemos recursivamente el subproblema
    sol_v = _branch_and_reduce(g_v)
    # Agregamos v al cover resultante
    sol_v.add(v)

    # Devolvemos la mejor solución entre ambas ramas
    return sol_u if len(sol_u) <= len(sol_v) else sol_v


def solve(
    instance: nx.Graph,
    seed: Optional[int] = None,
    params: Optional[Dict[str, Any]] = None,
) -> Result:
    n = instance.number_of_nodes()

    # Ejecutamos el algoritmo de branching
    cover = _branch_and_reduce(instance.copy())

    sol = Solution.from_cover(cover, n)
    evaluation = Evaluator(instance).evaluate(sol)
    return Result(
        solution=sol,
        cost=evaluation.cost,
        feasible=evaluation.feasible,
        meta={"method": "exact", "note": "branching"},
    )
