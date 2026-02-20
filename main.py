from __future__ import annotations
import argparse
import json
import os
import networkx as nx
from typing import Any, Dict, Iterable, Optional
from src.core.graph_io import load_edgelist
from src.algorithms import exact, heuristic, local_search, ils, gls, better_exact
from src.experiments.run_benchmark import run
from src.experiments.optimal_cover import get_optimal_cover_size

# Mapeo de nombres de algoritmos a sus funciones correspondientes
ALGORITHMS = {
    "exact": exact.solve,
    "better_exact": better_exact.solve,
    "heuristic": heuristic.solve,
    "local_search": local_search.solve,
    "ils": ils.solve,
    "gls": gls.solve,
}

# Función para parsear parámetros JSON
# La usamos para convertir la cadena JSON pasada como argumento en un diccionario para
# pasar los parámetros a los algoritmos
def _parse_params(params_raw) -> Optional[Dict[str, Any]]:
    if not params_raw:
        return None
    if os.path.isfile(params_raw):
        with open(params_raw, "r", encoding="utf-8") as f:
            return json.load(f)
    return json.loads(params_raw)

# Función para iterar sobre instancias en un archivo o directorio
# La usamos para cargar las instancias de grafos desde archivos edgelist
def _iter_instances(path: str) -> Iterable[tuple[str, nx.Graph]]:
    if os.path.isdir(path):
        for name in sorted(os.listdir(path)):
            if name.startswith("."):
                continue
            full = os.path.join(path, name)
            if os.path.isfile(full):
                yield name, load_edgelist(full)
    else:
        yield os.path.basename(path), load_edgelist(path)


def main() -> None:
    # Configuración del parser de argumentos
    parser = argparse.ArgumentParser(description="Vertex Cover runner")

    # Argumento para seleccionar el algoritmo a usar
    parser.add_argument("--algo", required=True, choices=sorted(ALGORITHMS.keys()))

    # Argumento para especificar el archivo o directorio de instancias
    parser.add_argument(
        "--input",
        default="data/sample.edgelist",
        help="Archivo o directorio de instancias",
    )

    # Argumento para parámetros adicionales en formato JSON
    parser.add_argument(
        "--params",
        type=str,
        default="config/default_params.json",
        help=(
            "JSON con hiperparámetros o ruta a JSON. "
            "Ej: '{\"seed\": 42, \"max_iter\": 1000,\"num_runs\": 10 }' o config/default_params.json"
        ),
    )

    # Argunmento para activar modo verbose
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Imprime las soluciones completas en la salida",
    )

    # Parseo de argumentos
    args = parser.parse_args()
    algorithm = ALGORITHMS[args.algo]

    params = _parse_params(args.params)
    # Si el flag --verbose está presente, forzar verbose=True en params
    if args.verbose:
        if params is None:
            params = {"verbose": True}
        else:
            params = dict(params)
            params["verbose"] = True
    seed = None
    if params and "seed" in params:
        seed = params["seed"]

    # Iteración sobre las instancias y ejecución del algoritmo seleccionado
    instances = list(_iter_instances(args.input))
    names = [name for name, _ in instances]
    graphs = [graph for _, graph in instances]

    def make_json_serializable(obj):
        # Convierte sets a listas y aplica recursivamente a dicts y listas
        if isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, dict):
            return {k: make_json_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [make_json_serializable(x) for x in obj]
        elif hasattr(obj, 'to_dict'):
            return make_json_serializable(obj.to_dict())
        elif hasattr(obj, '__dict__'):
            return make_json_serializable(dict(obj.__dict__))
        else:
            return obj


    for name, result in zip(names, run(algorithm, graphs, seed=seed, params=params)):
        meta = make_json_serializable(result.meta)
        optimal = get_optimal_cover_size(name)
        output = {
            "instance": name,             # Nombre de la instancia
            "algo": args.algo,            # Algoritmo usado
            "cost": result.cost,          # Costo de la solución
            "feasible": result.feasible,  # Si la solución es factible
            "meta": meta,                 # Metadatos adicionales serializables
        }
        if optimal is not None:
            output["optimal"] = optimal
            output["gap"] = result.cost - optimal
        if args.verbose:
            # Imprime la solución completa (cover, in_cover, etc.)
            output["solution"] = make_json_serializable(result.solution)
        print(json.dumps(output, ensure_ascii=False))


if __name__ == "__main__":
    main()
