from __future__ import annotations
from typing import Any, Dict, Optional, Set, Tuple
import random
import time
import networkx as nx
from ..core.api import Result
from ..core.evaluator import Evaluator
from ..core.solution import Solution
from .utils import _edge_key


def _get_dscore(
    v: int,
    cover: Set[int],
    graph: nx.Graph,
    edge_weights: Dict[Tuple[int, int], int],
) -> int:
    """
    Calcula el dscore: cambio en el peso total de aristas cubiertas
    si el estado del vértice 'v' se invierte.
    """
    score = 0
    for neighbor in graph.neighbors(v):
        edge = _edge_key(v, neighbor)
        weight = edge_weights.get(edge, 1)
        if v in cover:
            if neighbor not in cover:
                score -= weight
        else:
            if neighbor not in cover:
                score += weight
    return score


def _greedy_initial_cover(graph: nx.Graph) -> Set[int]:
    """Construcción inicial ávida usando mayor grado."""
    current_cover: Set[int] = set()
    temp_graph = graph.copy()
    while temp_graph.number_of_edges() > 0:
        v = max(temp_graph.nodes(), key=lambda n: nx.degree(temp_graph, n))
        current_cover.add(v)
        temp_graph.remove_node(v)
    return current_cover


def improve_cover(
    instance: nx.Graph,
    cover: Set[int],
    seed: Optional[int] = None,
    params: Optional[Dict[str, Any]] = None,
) -> Set[int]:
    """
    Aplica la búsqueda local sobre un cover inicial y devuelve el mejor cover hallado.
    """
    params = params or {}
    max_iter = int(params.get("max_iter", params.get("max_steps", 20000)))
    time_limit = params.get("time_limit", 5.0)
    rho = float(params.get("rho", 0.5))
    rng = random.Random(seed)

    # Inicialización de pesos de aristas a 1
    edge_weights: Dict[Tuple[int, int], int] = {
        _edge_key(u, v): 1 for u, v in instance.edges()
    }

    current_cover = set(cover)
    best_cover = set(current_cover)

    # Intentamos mejorar reduciendo el tamaño objetivo
    if current_cover:
        v_remove = max(
            current_cover,
            key=lambda x: _get_dscore(x, current_cover, instance, edge_weights),
        )
        current_cover.remove(v_remove)

    # Lista dinámica de aristas no cubiertas para eficiencia
    uncovered_edges = [
        _edge_key(u, v)
        for u, v in instance.edges()
        if u not in current_cover and v not in current_cover
    ]

    # --- Ciclo de Búsqueda Local ---
    start_time = time.perf_counter()
    for step in range(max_iter):
        if time_limit is not None and (time.perf_counter() - start_time) >= float(time_limit):
            break
        if not uncovered_edges:
            if len(current_cover) < len(best_cover):
                best_cover = set(current_cover)

            if not current_cover:
                continue

            v_rem = max(
                current_cover,
                key=lambda x: _get_dscore(x, current_cover, instance, edge_weights),
            )
            current_cover.remove(v_rem)
            uncovered_edges = [
                _edge_key(v_rem, n)
                for n in instance.neighbors(v_rem)
                if n not in current_cover
            ]
            continue

        # Two-stage exchange: añadir un vértice y luego remover otro
        target_edge = rng.choice(uncovered_edges)
        v_add = max(
            target_edge,
            key=lambda x: _get_dscore(x, current_cover, instance, edge_weights),
        )
        current_cover.add(v_add)

        # Actualizar aristas no cubiertas tras adición
        uncovered_edges = [e for e in uncovered_edges if v_add not in e]

        if not current_cover:
            continue

        v_rem = max(
            current_cover,
            key=lambda x: _get_dscore(x, current_cover, instance, edge_weights),
        )
        current_cover.remove(v_rem)

        # Añadir nuevas aristas descubiertas por la eliminación
        for n in instance.neighbors(v_rem):
            if n not in current_cover:
                edge = _edge_key(v_rem, n)
                if edge not in uncovered_edges:
                    uncovered_edges.append(edge)

        # Actualización de pesos (Penalización de aristas no cubiertas)
        for u, v in uncovered_edges:
            edge = _edge_key(u, v)
            edge_weights[edge] += 1

        # Olvido periódico
        if step % 500 == 0:
            for e in edge_weights:
                edge_weights[e] = max(1, int(edge_weights[e] * rho))

    return best_cover


def solve(
    instance: nx.Graph,
    seed: Optional[int] = None,
    params: Optional[Dict[str, Any]] = None,
) -> Result:
    params = params or {}
    max_iter = int(params.get("max_iter", params.get("max_steps", 20000)))
    time_limit = params.get("time_limit", 5.0)
    rho = float(params.get("rho", 0.5))

    # --- FASE 1: Construcción Inicial Ávida ---
    current_cover = _greedy_initial_cover(instance)
    initial_size = len(current_cover)

    # --- FASE 2: Búsqueda Local ---
    best_cover = improve_cover(instance, current_cover, seed=seed, params=params)

    n = instance.number_of_nodes()
    sol = Solution.from_cover(best_cover, n)
    evaluation = Evaluator(instance).evaluate(sol)
    return Result(
        solution=sol,
        cost=evaluation.cost,
        feasible=evaluation.feasible,
        meta={
            "metodo": "local_search",
            "method": "local_search",
            "initial_size": initial_size,
            "best_size": len(best_cover),
            "max_iter": max_iter,
            "time_limit": time_limit,
            "rho": rho,
            "seed": seed,
        },
    )
