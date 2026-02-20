from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

import networkx as nx
from tqdm import tqdm

# Permitir ejecutar el script sin configurar PYTHONPATH
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.algorithms import heuristic, local_search, ils, gls
from src.core.graph_io import load_edgelist
from src.experiments.optimal_cover import get_optimal_cover_size
from src.experiments.run_benchmark import run

ALGORITHMS = {
    "heuristic": heuristic.solve,
    "local_search": local_search.solve,
    "ils": ils.solve,
    "gls": gls.solve,
}


def _parse_params(params_raw: str | None) -> Dict[str, Any] | None:
    if not params_raw:
        return None
    if os.path.isfile(params_raw):
        with open(params_raw, "r", encoding="utf-8") as f:
            return json.load(f)
    return json.loads(params_raw)


def _iter_instances(folder: Path) -> Iterable[Tuple[str, nx.Graph]]:
    for path in sorted(folder.glob("*.edgelist")):
        yield path.name, load_edgelist(str(path))


def _collect_results(
    params: Dict[str, Any] | None,
    instances: List[Tuple[str, nx.Graph]],
    algos: List[str],
) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    for algo_name in tqdm(algos, desc="Algoritmos", unit="algo"):
        algorithm = ALGORITHMS[algo_name]
        names = [name for name, _ in instances]
        graphs = [g for _, g in instances]
        for name, result in tqdm(
            zip(names, run(algorithm, graphs, seed=params.get("seed") if params else None, params=params)),
            desc=f"{algo_name}",
            total=len(names),
            unit="inst",
            leave=False,
        ):
            optimal = get_optimal_cover_size(name)
            gap = None if optimal is None else result.cost - optimal
            meta = result.meta or {}
            results.append(
                {
                    "instance": name,
                    "algo": algo_name,
                    "cost": result.cost,
                    "feasible": result.feasible,
                    "optimal": optimal,
                    "gap": gap,
                    "avg_time": meta.get("avg_time"),
                    "best_cost": meta.get("best_cost"),
                    "worst_cost": meta.get("worst_cost"),
                    "num_runs": meta.get("num_runs"),
                }
            )
    return results


def _write_jsonl(path: Path, rows: List[Dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ejecuta todos los algoritmos (excepto exactos) sobre el benchmark DIMACS."
    )
    parser.add_argument(
        "--bench",
        type=str,
        default="data/bench_graphs_c",
        help="Directorio con instancias .edgelist",
    )
    parser.add_argument(
        "--params",
        type=str,
        default="config/default_params.json",
        help="JSON con parámetros o ruta a JSON",
    )
    parser.add_argument(
        "--algos",
        type=str,
        default=",".join(ALGORITHMS.keys()),
        help="Lista separada por comas de algoritmos a ejecutar",
    )
    parser.add_argument(
        "--out",
        type=str,
        default="results/benchmarks.jsonl",
        help="Ruta de salida para resultados",
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["jsonl", "csv"],
        default="jsonl",
        help="Formato de salida",
    )
    args = parser.parse_args()

    bench_dir = Path(args.bench)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    params = _parse_params(args.params)
    algos = [a.strip() for a in args.algos.split(",") if a.strip()]
    for a in algos:
        if a not in ALGORITHMS:
            raise ValueError(f"Algoritmo desconocido: {a}")

    instances = list(_iter_instances(bench_dir))
    rows = _collect_results(params, instances, algos)

    if args.format == "csv":
        _write_csv(out_path, rows)
    else:
        _write_jsonl(out_path, rows)

    print(f"Resultados guardados en {out_path}")


if __name__ == "__main__":
    main()
