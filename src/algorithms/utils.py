from __future__ import annotations
from typing import Optional, Set
import random
import networkx as nx


def _edge_key(u: int, v: int) -> tuple[int, int]:
    """Devuelve una arista no dirigida con orden canónico."""
    return (u, v) if u < v else (v, u)


def _get_any_edge(graph: nx.Graph) -> Optional[tuple[int, int]]:
    """Devuelve cualquier arista del grafo, o None si no hay aristas."""
    for u, v in graph.edges():
        return u, v
    return None


def _add_greedy_cover_vertices(
    instance: nx.Graph,
    uncovered: Set[tuple[int, int]],
    cover: Set[int],
    rng: random.Random,
) -> None:
    """
    Dado un conjunto de aristas no cubiertas y un cover parcial,
    agrega vértices al cover usando el heurístico voraz hasta cubrir todas las aristas.
    Modifica el cover y uncovered in-place.
    """
    while uncovered:
        u, v = rng.choice(tuple(uncovered))
        du = instance.degree(u)
        dv = instance.degree(v)

        if du == dv:
            chosen = u if rng.random() < 0.5 else v
        else:
            chosen = u if du > dv else v
        cover.add(chosen)

        for nbr in instance.neighbors(chosen):
            uncovered.discard(_edge_key(chosen, nbr))


def _initial_cover(instance: nx.Graph, rng: random.Random) -> Set[int]:
    """
    Construye un cover factible usando un heurístico voraz:
    Mientras existan aristas no cubiertas, selecciona una y agrega el
    extremo de mayor grado (desempate aleatorio).
    """
    edges = {_edge_key(u, v) for u, v in instance.edges() if u != v}
    uncovered = set(edges)

    cover: Set[int] = set()

    if not uncovered:
        return cover

    _add_greedy_cover_vertices(instance, uncovered, cover, rng)

    return cover
