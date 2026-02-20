from __future__ import annotations
from typing import Any, Dict, Optional, Set, Tuple
import random
import networkx as nx
from ..core.api import Result
from ..core.evaluator import Evaluator
from ..core.solution import Solution
from .utils import _initial_cover, _get_any_edge


def _maximal_matching_lower_bound(graph: nx.Graph) -> int:
    """
    Calcula una cota inferior para el tamaño del Minimum Vertex Cover
    usando el tamaño de un matching maximal.
    """
    # Tamaño de un matching maximal es cota inferior válida para MVC
    matching = nx.algorithms.matching.maximal_matching(graph)
    return len(matching)


def _reduce_graph(graph: nx.Graph, cover: Set[int]) -> None:
    """
    Reduce el grafo aplicando reglas simples:
    - Remover nodos aislados.
    - Regla de grado 1: si un nodo u tiene grado 1, incluir su vecino v en el cover.
    Modifica el grafo y el cover in-place, es decir, los cambia directamente.
    """
    changed = True
    # Mientras se puedan aplicar reducciones
    while changed:
        changed = False
        # Remover nodos aislados
        isolated = [v for v in graph.nodes() if graph.degree(v) == 0]
        # Si hay nodos aislados, los removemos
        if isolated:
            graph.remove_nodes_from(isolated)
            changed = True

        # Regla de grado 1: si u tiene grado 1, incluir su vecino v
        # Para cada nodo en el grafo    
        for u in list(graph.nodes()):
            # Si u tiene grado 1
            if graph.degree(u) == 1:
                # Obtenemos su único vecino v
                v = next(iter(graph.neighbors(u)))
                # Agregamos v al cover y removemos v del grafo
                cover.add(v)
                graph.remove_node(v)
                changed = True
                break


def _branch_and_bound(graph: nx.Graph, cover: Set[int], best_cover: Set[int]) -> Set[int]:
    """
    Algoritmo exacto de branching con poda para Minimum Vertex Cover.
    Usa reglas de reducción y cotas inferiores para podar ramas:
    - Si el grafo no tiene aristas, el cover mínimo es el conjunto actual.
    - Si el tamaño del cover actual es mayor o igual al mejor encontrado, se poda.
    - Si la cota inferior (matching maximal) más el tamaño del cover actual
      es mayor o igual al mejor encontrado, se poda.
    """
    # Iniciamos aplicando reducciones
    _reduce_graph(graph, cover)

    # Caso base: si no hay aristas, devolvemos el cover actual
    edge = _get_any_edge(graph)
    if edge is None:
        return set(cover)

    # Si el cover actual ya es peor que el mejor, podamos
    if len(cover) >= len(best_cover):
        return best_cover

    # Aplicamos cota inferior para podamos
    lb = _maximal_matching_lower_bound(graph)

    # Si cover + lb >= mejor solución, podamos
    if len(cover) + lb >= len(best_cover):
        return best_cover

    # Extraemos una arista para ramificar
    u, v = edge

    # Rama 1: usando u
    # Hacemos una copia del grafo sin el nodo u
    g_u = graph.copy()
    g_u.remove_node(u)
    # Hacemos una copia del cover y agregamos u
    cover_u = set(cover)
    cover_u.add(u)
    # Resolvemos recursivamente el subproblema
    sol_u = _branch_and_bound(g_u, cover_u, best_cover)

    # Si la solución de la rama 1 es mejor, actualizamos best_cover
    if len(sol_u) < len(best_cover):
        best_cover = sol_u

    # Rama 2: usando v
    # Hacemos una copia del grafo sin el nodo v
    g_v = graph.copy()
    g_v.remove_node(v)
    # Hacemos una copia del cover y agregamos v
    cover_v = set(cover)
    cover_v.add(v)
    # Resolvemos recursivamente el subproblema
    sol_v = _branch_and_bound(g_v, cover_v, best_cover)

    # Si la solución de la rama 2 es mejor, actualizamos best_cover
    if len(sol_v) < len(best_cover):
        best_cover = sol_v

    return best_cover


def solve(
    instance: nx.Graph,
    seed: Optional[int] = None,
    params: Optional[Dict[str, Any]] = None,
) -> Result:
    n = instance.number_of_nodes()

    # Extraemos semilla para el generador aleatorio
    rng_seed = params.get("seed", seed) if params else seed
    rng = random.Random(rng_seed)

    # Obtenemos una solución inicial usando heurística voraz
    initial_cover = _initial_cover(instance, rng)
    best_cover = set(initial_cover)

    cover = set()
    # Ejecutamos el branch-and-bound
    best_cover = _branch_and_bound(instance.copy(), cover, best_cover)

    # Construimos el objeto Result
    sol = Solution.from_cover(best_cover, n)
    evaluation = Evaluator(instance).evaluate(sol)
    return Result(
        solution=sol,
        cost=evaluation.cost,
        feasible=evaluation.feasible,
        meta={"method": "better_exact", "note": "branch-and-bound"},
    )
