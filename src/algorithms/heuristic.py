from __future__ import annotations
from typing import Any, Dict, Optional
import networkx as nx
from ..core.api import Result
from ..core.evaluator import Evaluator
from ..core.solution import Solution

def _remove_redundant(graph: nx.Graph, cover: set[int]) -> set[int]:
    """
    Elimina nodos redundantes de la cobertura
    Un nodo es redundante si todos sus vecinos estan en la cobertura
    """
    # Hacemos una copia para no modificar el cover original mientras iteramos
    refined_cover = cover.copy()
    # Para cada nodo en la cobertura
    for node in list(refined_cover):
        # Si todos sus vecinos están en la cobertura, lo removemos
        if all(neighbor in refined_cover for neighbor in graph.neighbors(node)):
            refined_cover.remove(node)
    return refined_cover

def _mvc_isolation(graph: nx.Graph) -> set[int]:
    """
    Implementación del algoritmo de aislamiento
    Busca nodos con grado minimo, agrega a sus vecinos a la cobertura, y los elimina del grafo
    Más eficiente y mejores resultados que Max Degree (por lo menos para instancias DIMACS)
    """
    # Hacemos una copia del grafo para no modificar el original
    g_copy = graph.copy()
    cover = set()
    # Mientras queden aristas en el grafo
    while g_copy.number_of_edges() > 0:
        # Encontrar el nodo de grado mínimo
        min_node, _ = min(  # el _ es porque degree() devuelve tuplas (el nodo y su grado). Y ahora solo nos interesa el nodo
            (node_degree for node_degree in g_copy.degree() if node_degree[1] > 0),
            key=lambda x: x[1]
        )

        # Agregamos sus vecinos a la cobertura y los eliminamos del grafo
        neighbors = list(g_copy.neighbors(min_node))
        cover.update(neighbors)
        g_copy.remove_nodes_from(neighbors)
    
    # Finalmente, removemos nodos redundantes de la cobertura
    cover = _remove_redundant(graph, cover)
    return cover

def solve(
    instance: nx.Graph,
    seed: Optional[int] = None,
    params: Optional[Dict[str, Any]] = None,
) -> Result:

    # Ejecutamos nuestra heuristica para obtener una cobertura
    raw_cover = _mvc_isolation(instance)

    # Convertimos la cobertura obtenida a una solucion
    n = instance.number_of_nodes()
    sol = Solution.from_cover(raw_cover, n)

    # Evaluamos la solucion
    evaluator = Evaluator(instance)
    evaluation = evaluator.evaluate(sol)

    # Empaquetamos el resultado
    return Result(
        solution=sol,
        cost=evaluation.cost,
        feasible=evaluation.feasible,
        meta={
            "method": "Isolation",
            "note": "Heurística basada en la eliminación de vecinos de los nodos de menor grado"
        },
    )
