from __future__ import annotations
from typing import Any, Dict, Optional, Set, List, Callable
import random
import time
import networkx as nx
from ..core.api import Result
from ..core.evaluator import Evaluator
from ..core.solution import Solution
from .utils import _edge_key, _initial_cover


def guided_cost(
	cover: Set[int],
	edge_keys: List[tuple[int, int]],
	penalties: Dict[tuple[int, int], int],
	lambda_penalty: float
) -> float:
	"""
	Calcula el costo guiado de un cover : tamaño + penalización por aristas descubiertas.
	"""
	penalty_sum = 0
	# Para cada arista, si no está en el cover, sumamos su penalización
	for e in edge_keys:
		u, v = e
		if u not in cover and v not in cover:
			penalty_sum += penalties[e]
	return len(cover) + lambda_penalty * penalty_sum

def _guided_local_search(
	instance: nx.Graph,
	cover: Set[int],
	edge_keys: List[tuple[int, int]],
	penalties: Dict[tuple[int, int], int],
	lambda_penalty: float,
	rng: random.Random,
) -> Set[int]:
	"""
	Búsqueda local guiada por penalizaciones: elimina vértices si mejora el costo penalizado.
	"""
	improved = True
	current_cover = set(cover)
	
    # Mientras se encuentre mejora
	while improved:
		improved = False
		vertices = list(current_cover)
		# Mezclamos el orden de los vértices para diversificar la búsqueda
		rng.shuffle(vertices)
		
        # Para cada vértice en el cover actual
		for v in vertices:
			if v in current_cover:
				# Intentar remover v
				candidate = set(current_cover)
				candidate.remove(v)
				# Verificar factibilidad
				is_feasible = True
				for u, w in edge_keys:
					if u not in candidate and w not in candidate:
						is_feasible = False
						break
				# Solo aceptar si es factible y mejora el costo penalizado
				if is_feasible and guided_cost(candidate, edge_keys, penalties, lambda_penalty) < guided_cost(current_cover, edge_keys, penalties, lambda_penalty):
					current_cover = candidate
					improved = True
					break
	return current_cover

def solve(
	instance: nx.Graph,
	seed: Optional[int] = None,
	params: Optional[Dict[str, Any]] = None,
) -> Result:
	"""
	Búsqueda Local Guiada (GLS) para Vertex Cover.

	Pipeline:
	1) Construir una solución inicial voraz.
	2) Inicializar penalizaciones pi=0 para cada arista.
	3) Repetir:
		a) Definir función objetivo guiada (costo + penalizaciones).
		b) Ejecutar búsqueda local guiada por penalizaciones.
		c) Actualizar penalizaciones en las aristas más frecuentemente descubiertas.
	4) Retornar la mejor solución encontrada.

	Parámetros opcionales:
		- max_iter: máximo de iteraciones de GLS.
		- time_limit: límite de tiempo en segundos.
		- lambda_penalty: peso de la penalización (lambda en la fórmula).
	"""
	if params is None:
		params = {}
	rng = random.Random(seed)
	n = instance.number_of_nodes()
	max_iter = int(params.get("max_iter", 1000))
	time_limit = params.get("time_limit", None)
	lambda_penalty = float(params.get("lambda_penalty", 0.3))


	# 1) Solución inicial voraz
	cover = _initial_cover(instance, rng)
	best_cover = set(cover)
	best_cost = len(best_cover)

	# 2) Penalizaciones iniciales (pi=0 para cada arista)
	edge_list = [e for e in instance.edges() if e[0] != e[1]]
	edge_keys = [_edge_key(u, v) for u, v in edge_list]
	penalties = {e: 0 for e in edge_keys}

	# Iniciamos el tiempo
	start_time = time.time()

	# 3) Bucle principal de GLS
	for it in range(max_iter):
		# Si se alcanza el límite de tiempo, terminamos
		if time_limit is not None and (time.time() - start_time) >= float(time_limit):
			break

		# Búsqueda local guiada por penalizaciones
		cover = _guided_local_search(instance, set(cover), edge_keys, penalties, lambda_penalty, rng)

		# Actualizamos penalizaciones: identificar aristas descubiertas
		uncovered = [_edge_key(u, v) for u, v in instance.edges() if u != v and u not in cover and v not in cover]

		# Si hay aristas descubiertas, aumentamos sus penalizaciones
		if uncovered:
			for e in uncovered:
				penalties[e] += 1

		# Actualizamos la mejor solución encontrada
		if len(cover) < best_cost:
			best_cover = set(cover)
			best_cost = len(cover)

    # Construimos el resultado final
	sol = Solution.from_cover(best_cover, n)
	evaluacion = Evaluator(instance).evaluate(sol)
	return Result(
		solution=sol,
		cost=evaluacion.cost,
		feasible=evaluacion.feasible,
		meta={
			"metodo": "gls",
			"max_iter": max_iter,
			"time_limit": time_limit,
			"lambda_penalty": lambda_penalty,
		},
	)
