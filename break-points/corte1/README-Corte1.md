# CI5652-DisenoDeAlgoritmosII-Proyecto

## Problema escogido: Vertex Cover
El problema de *Vertex Cover* consiste en encontrar un conjunto mínimo de vértices en un grafo tal que cada arista tenga al menos uno de sus extremos en ese conjunto.

## Árbol del proyecto (resumen)
Proyecto:
- [README.md](README.md): descripción general del proyecto.
- [TODO.md](TODO.md): lista de tareas pendientes.
- [main.py](main.py): entrypoint para ejecutar algoritmos por consola.
- [requirements.txt](requirements.txt): dependencias (NetworkX).
- [config/default_params.json](config/default_params.json): parámetros por defecto (incluye seed).
- [data/sample.edgelist](data/sample.edgelist): instancia de prueba en formato edgelist.
- src/
	- [src/core/api.py](src/core/api.py): `Result` e interfaz `Algorithm`.
	- [src/core/solution.py](src/core/solution.py): estructura `Solution` y helper `from_cover`.
	- [src/core/evaluator.py](src/core/evaluator.py): verificación de factibilidad y costo.
	- [src/core/graph_io.py](src/core/graph_io.py): carga/normalización de grafos.
	- [src/algorithms/exact.py](src/algorithms/exact.py): placeholder del algoritmo exacto.
	- [src/algorithms/heuristic.py](src/algorithms/heuristic.py): placeholder de heurística.
	- [src/algorithms/local_search.py](src/algorithms/local_search.py): placeholder de búsqueda local.
	- [src/algorithms/ils.py](src/algorithms/ils.py): placeholder ILS.
	- [src/experiments/run_benchmark.py](src/experiments/run_benchmark.py): helper para medir tiempo y ejecutar lotes.
- data/: carpeta para instancias.
- tests/: carpeta reservada para pruebas.
- tex/: archivos del informe en LaTeX.

## Flujo básico de ejecución
1. El usuario ejecuta main.py con `--algo` y opcionalmente `--input` y `--params`.
2. Se carga el grafo (edgelist).
3. Cada algoritmo construye `cover`, se transforma a `Solution` y se evalúa.
4. El resultado se imprime como JSON por consola.