from __future__ import annotations
from typing import Any
import networkx as nx

# Normaliza los nodos del grafo para que sean enteros consecutivos desde 0
# para facilitar el manejo interno
def normalize_nodes(graph: nx.Graph) -> nx.Graph:
    # Crear un mapeo de nodos originales a enteros consecutivos
    mapping = {node: i for i, node in enumerate(graph.nodes())}
    # Retornar un nuevo grafo con los nodos renombrados
    return nx.relabel_nodes(graph, mapping, copy=True)

# Carga un grafo desde un archivo de edgelist y normaliza sus nodos
def load_edgelist(path: str, nodetype: Any = int, comment: str = "#") -> nx.Graph:
    graph = nx.read_edgelist(path, nodetype=nodetype, comments=comment)
    return normalize_nodes(graph)
