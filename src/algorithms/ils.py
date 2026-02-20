from __future__ import annotations
from typing import Any, Dict, Optional, Set, List
import random
import time
import networkx as nx
from ..core.api import Result
from ..core.evaluator import Evaluator
from ..core.solution import Solution
from .utils import _edge_key, _add_greedy_cover_vertices, _initial_cover
from .local_search import improve_cover

def _can_remove(instance: nx.Graph, cover: Set[int], v: int) -> bool:
    """
    Verifica si al remover v la solución sigue siendo factible.
    Si algún vecino de v no está en el cover, remover v dejaría una 
    arista descubierta y haría la solución infactible.
    """
    for nbr in instance.neighbors(v):
        if nbr not in cover:
            return False
    return True


def _repair_cover(instance: nx.Graph, cover: Set[int], rng: random.Random) -> None:
    """
    Repara un cover (posiblemente infactible) agregando vértices.
    Para cada arista descubierta, agrega un extremo (mayor grado o aleatorio).
    """
    # Conjunto de aristas no cubiertas
    uncovered = {_edge_key(u, v) for u, v in instance.edges() if u != v and u not in cover and v not in cover}

    # Agregamos vértices al cover hasta cubrir todas las aristas
    _add_greedy_cover_vertices(instance, uncovered, cover, rng)


def _perturb(instance: nx.Graph, cover: Set[int], k: int, rng: random.Random) -> Set[int]:
    """
    Paso de perturbación para ILS:
    1) Remueve k vértices aleatorios del cover actual (diversificación).
    2) Repara la solución para restaurar factibilidad.
    """
    # Si el cover está vacío, no hay nada que remover
    if not cover:
        return set(cover)
    
    # Aseguramos que k no sea mayor al tamaño del cover
    k = min(k, len(cover))

    # Inicializamos el nuevo cover como una copia del actual
    new_cover = set(cover)

    # 1) Removemos k vértices aleatorios
    removed = rng.sample(list(new_cover), k)
    for v in removed:
        new_cover.discard(v)

    # 2) Reparamos el cover para asegurar factibilidad
    _repair_cover(instance, new_cover, rng)
    return new_cover

def hash_cover(cov: Set[int]) -> int:
    """
    Genera un hash inmutable para un cover dado.
    """
    return hash(frozenset(cov))

def solve(
    instance: nx.Graph,
    seed: Optional[int] = None,
    params: Optional[Dict[str, Any]] = None,
) -> Result:
    """
    Búsqueda Local Iterada (ILS) para Vertex Cover.

    Pipeline:
    1) Construir una solución inicial voraz.
    2) Aplicar búsqueda local (eliminar vértices redundantes).
    3) Repetir: perturbar -> reparar -> búsqueda local, evitando ciclos con memoria.
    4) Mantener la mejor solución encontrada.

    Parámetros opcionales:
        - max_iter: máximo de iteraciones de ILS.
        - time_limit: límite de tiempo en segundos.
        - perturb_fraction: fracción de la solución a remover en la perturbación.
        - perturb_min: mínimo de vértices a remover.
        - accept_equal_prob: probabilidad de aceptar soluciones de igual calidad.
        - memoria_tam: tamaño de la memoria de soluciones recientes (default: 10).
    """
    if params is None:
        params = {}
    rng = random.Random(seed)
    n = instance.number_of_nodes()
    max_iter = int(params.get("max_iter", 1000))
    time_limit = params.get("time_limit", None)
    perturb_fraction = float(params.get("perturb_fraction", 0.1))
    perturb_min = int(params.get("perturb_min", 1))
    accept_equal_prob = float(params.get("accept_equal_prob", 0.05))
    memoria_tam = int(params.get("memoria_tam", 10))

    # 1) Solución inicial voraz
    cover = _initial_cover(instance, rng)

    # 2) Búsqueda local para llegar a un óptimo local
    local_params = params.get("local_search_params", params)
    cover = improve_cover(instance, cover, seed=seed, params=local_params)

    # Guardamos la mejor solución encontrada
    best_cover = set(cover)
    best_cost = len(best_cover)

    # Memoria para evitar ciclos
    memoria: List[int] = []

    # Agregamos a la memoria la solución inicial
    memoria.append(hash_cover(cover))

    # Iniciar el cronómetro justo antes del bucle principal
    start_time = time.time()

    # 3) Bucle principal de ILS
    for _ in range(max_iter):
        # Si se alcanza el límite de tiempo, terminamos
        if time_limit is not None and (time.time() - start_time) >= float(time_limit):
            break

        # Aplicamos la perturbación
        k = max(perturb_min, int(max(1, round(perturb_fraction * max(1, len(cover))))))
        candidato = _perturb(instance, cover, k, rng)

        # Aplicamos búsqueda local al candidato encontrado
        candidato = improve_cover(instance, candidato, seed=seed, params=local_params)

        # Guardamos costo y hash del candidato
        candidato_cost = len(candidato)
        candidato_hash = hash_cover(candidato)

        # Evitar ciclos: si la solución ya está en memoria, aplicamos perturbación fuerte
        if candidato_hash in memoria:
            # Perturbación fuerte: remover la mitad del cover
            k_fuerte = max(1, len(candidato) // 2)
            candidato = _perturb(instance, candidato, k_fuerte, rng)
            candidato = improve_cover(instance, candidato, seed=seed, params=local_params)
            candidato_cost = len(candidato)
            candidato_hash = hash_cover(candidato)

        # 4) Criterio de aceptación
        # Si el candidato es mejor, lo aceptamos como la nueva solución
        if candidato_cost < best_cost:
            best_cover = set(candidato)
            best_cost = candidato_cost
            cover = candidato
        # Si es igual, lo aceptamos con cierta probabilidad
        else:
            if candidato_cost <= len(cover) or rng.random() < accept_equal_prob:
                cover = candidato

        # Actualizamos la memoria
        memoria.append(candidato_hash)

        # Si la memoria excede su tamaño, removemos la solución más antigua
        if len(memoria) > memoria_tam:
            memoria.pop(0)

    # Construimos la solución final
    sol = Solution.from_cover(best_cover, n)
    evaluacion = Evaluator(instance).evaluate(sol)
    return Result(
        solution=sol,
        cost=evaluacion.cost,
        feasible=evaluacion.feasible,
        meta={
            "metodo": "ils",
            "max_iter": max_iter,
            "time_limit": time_limit,
            "perturb_fraction": perturb_fraction,
            "perturb_min": perturb_min,
            "accept_equal_prob": accept_equal_prob,
            "memoria_tam": memoria_tam,
        },
    )
