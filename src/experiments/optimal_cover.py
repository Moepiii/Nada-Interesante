def get_optimal_cover_size(instance_name: str, optimal_file: str = None) -> int | None:
    """
    Busca el tamaño del cover óptimo conocido para una instancia dada.
    Retorna None si no se encuentra.
    """
    if optimal_file is None:
        optimal_file = "data/bench_graphs/optimal_covers.txt"
    try:
        with open(optimal_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"): continue
                if ":" in line:
                    name, val = line.split(":", 1)
                    if name.strip() == instance_name.strip():
                        return int(val.strip())
    except Exception:
        pass
    return None
