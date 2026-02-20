from __future__ import annotations
from time import perf_counter
from typing import Callable, Dict, Iterable, Optional
import networkx as nx
from ..core.api import Result

def run(
    algorithm: Callable[[nx.Graph, Optional[int], Optional[Dict]], Result],
    instances: Iterable[nx.Graph],
    seed: Optional[int] = None,
    params: Optional[Dict] = None,
) -> Iterable[Result]:
    # Extraemos cuantas corridas queremos (por defecto 1)
    n_runs = params.get("num_runs", 1) if params else 1

    for instance in instances:
        costs = []
        times = []
        solutions = []
        results = []

        # Bucle para ejecutar el algoritmo n_runs veces
        for i in range(n_runs):
            # Variamos la semilla para que cada corrida sea distinta
            current_seed = (seed + i) if seed is not None else i
            _start = perf_counter()
            res = algorithm(instance, seed=current_seed, params=params)
            _elapsed = perf_counter() - _start
            costs.append(res.cost)
            times.append(_elapsed)
            solutions.append(res.solution)
            results.append(res)

        # Agregamos los resultados de las n_runs al objeto meta
        avg_cost = sum(costs) / n_runs
        meta = {
            "costs": costs,
            "times": times,
            "avg_cost": avg_cost,
            "best_cost": min(costs),
            "worst_cost": max(costs),
            "avg_time": sum(times) / n_runs,
            "num_runs": n_runs,
            "n_nodes": instance.number_of_nodes() if hasattr(instance, 'number_of_nodes') else None,
            "n_edges": instance.number_of_edges() if hasattr(instance, 'number_of_edges') else None,
        }
        # Solo agregamos solutions si params tiene verbose True
        if params and params.get("verbose", False):
            meta["solutions"] = solutions

        # Dejamos dentro de la solucion de Result la mejor solucion obtenida
        best_idx = costs.index(min(costs))
        agg_result = Result(
            solution=solutions[best_idx],
            cost=avg_cost,
            feasible=results[best_idx].feasible,
            meta=meta
        )

        yield agg_result