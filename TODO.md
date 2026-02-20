# Por hacer

- [ ] Definir las reglas para los movimientos tabú (y los demás componentes necesarios) e implementar **búsqueda tabú**
- [ ] Definir un proceso de enfriado progresivo (y los demás componentes necesarios) e implementar **recocido simulado**
- [ ] Definir un método de construcción para una RCL e implementar **GRASP**
- [ ] Definir fenotipo/genotipo, así como operadores de cruce y de mutación (y demás componentes necesarios), e implementar **algoritmo genético**
- [ ] Ejecutear los algoritmos implementados sobre el benchmark escogido y comparar los **resultados** obtenidos.

# Observaciones Corte 1
- [ ] Considerar mejorar la vecindad para la búsqueda local. Aunque la intención de acortar el espacio de búsqueda es buena, la naturaleza voraz de la vecindad escogida puede provocar que la búsqueda se estanque en óptimos locales.
- [ ] Siempre que haya operaciones con parámetros configurables, probar diferentes combinaciones de dichos
parámetros (en este caso, el k para la operación k -swap).
- [ ] Medir el "gap" con respecto a la mejor solución conocida en términos de porcentajes y no de valores
absolutos (dado que el tamaño del grafo puede influir en qué tanto afecta la solución un nodo adicional al
cubrimiento).