Heurística especializada: Isolation Algorithm (IA)
Esta heurística parte de una proposición simple: si un nodo tiene grado 1 (es decir, incide en una sola arista), su vecino necesariamente debe estar en la cobertura para poder cubrir esa arista. Basándose en esa proposición, la heurística va escogiendo a los nodos con el menor grado, agrega a todos sus vecinos a la cobertura, y luego elimina a estos vecinos del grafo, así como las aristas donde éstos inciden. La idea es ir aislando los vértices, hasta que no queden más aristas en el grafo (de ahí su nombre: Isolation, Aislamiento). Tiene un enfoque voraz. 
Notemos que el grado de los nodos a considerar debe ser mayor a cero (no tendría sentido agregar los vecinos de un nodo aislado, ya que no tiene vecinos).
Esta heurística no garantiza que se obtenga la solución óptima, ya que al escoger nodos de grado mínimo mayores a 1, es posible que al agregar sus vecinos a la cobertura termine pasando por alto nodos que tengan una mayor cobertura. Sin embargo, obtiene soluciones buenas en buen tiempo.
Un ejemplo en pseudocódigo de la heurística sería:
mvc_isolation(G: grafo) -> C: conjunto
    C <- 0/ # conjunto vacío
    mientras |G.aristas| > 0:
        grados <- obtener_grados(G)
        nodo_min <- min(grados)
        agregar_nodos(C,nodo_min.vecinos())
        eliminar_nodos(G,nodo_min.vecinos())
    retornar C

Ahora, una mejora posible para el algoritmo está en la detección de nodos redundantes dentro de la cobertura:
Aplicando esta heurística, es posible que se terminen agregando nodos a la cobertura que cubren aristas que ya están siendo cubiertas por otros nodos en la cobertura. Así, un nodo es redundante si todos los vecinos de este nodo ya están en la cobertura.
Por tanto, luego de haber ejecutado el ciclo principal del algoritmo, podemos buscar los vecinos de los nodos de la cobertura obtenida para eliminar aquellos redundantes, optimizando la solución.
Una versión que obtiene la cobertura y elimina nodos redundantes sería:
mvc_isolation(G: grafo) -> C: conjunto
    C <- 0/ # conjunto vacío
    mientras |G.aristas| > 0:
        grados <- obtener_grados(G)
        nodo_min <- min(grados)
        agregar_nodos(C,nodo_min.vecinos())
        eliminar_nodos(G,nodo_min.vecinos())
    escanear C y eliminar nodos redundantes
    retornar C

La complejidad temporal teórica de la heurística es la siguiente: Sea G=(V,E) un grafo.
Para el peor caso, podemos imaginar un grafo en forma de camino simple, donde los nodos en los extremos son de grado 1, y los nodos internos son de grado 2.
Obtener el mínimo de los grados es O(∣V∣) (hay que recorrer todos los nodos para saber el mínimo).
Agregar un vecino a la cobertura a la vez y luego eliminarlo del grafo junto con sus dos aristas incidentes (el vecino de un extremo siempre es de grado 2) toma tiempo O(1)
Ahora, en cada paso se escogerá siempre uno de los extremos (por ser de grado 1), se eliminará a su vecino junto a sus aristas, y luego el nodo que le seguía a ese vecino pasará a ser un extremo, y así se seguirá repitiendo el proceso. Como en cada paso "salta" dos nodos en el camino, este proceso se ejecutará exactamente ∣V∣/2 veces.
Por lo tanto, la complejidad temporal para obtener la cobertura sería:
​O(|V|/2∗∣V∣)=O(∣V∣^2)
Por otro lado, si se tiene un camino simple, el escaneo y eliminación de nodos redundantes se realiza en tiempo O(∣V∣), porque cada nodo de la cobertura es de grado 2 (en este caso solo se agregan los nodos internos del camino a la cobertura), por lo que siempre se verifican 2 vecinos para cada nodo.
Finalmente, la complejidad temporal total del Isolation Algorithm es: 
O(∣V∣^2+∣V∣)=O(∣V∣^2)
Ejemplo: Sea un grafo de 10 nodos como sigue:
1-2-3-4-5-6-7-8-9-10
cover = {}
Escogemos el nodo 1 por ser de grado 1. Se agrega su vecino (el 2) a la cobertura, y se elimina del grafo.
1   3-4-5-6-7-8-9-10
cover = {2}
Ahora escogemos el 3, agregamos al 4 a la cobertura, y se elimina.
1   3   5-6-7-8-9-10
cover = {2,4}
Y así sucesivamente hasta que no queden aristas.
1   3   5   7   9
cover = {2,4,6,8,10}

Hay que resaltar, que el peor caso del Isolation Algorithm (un camino simple), es de hecho el mejor caso para agregar nodos a la cobertura, eliminar nodos del grafo junto con sus aristas, y hacer la limpieza de nodos redundantes. El peor caso para estas funciones es, de hecho, un grafo completo, donde todos los nodos son de grado ∣V∣−1.
Para agregar nodos, al escoger un nodo de grado mínimo, se escoge cualquier nodo, por lo que se deben agregar sus ∣V∣−1 vecinos a la cobertura. Esto da una complejidad de O(∣V∣)
Para eliminar nodos, se recorren los ∣V∣−1 nodos, y para cada uno se eliminan las aristas donde inciden, que está acotado por Grado(u),∀u∈MVC(G).
Como sabemos del Lema del Apretón de manos que ∑u∈G Grado(u)=2∣E∣, Grado(u) está acotado por ∣E∣. Ahora, como se eliminan los vecinos una sola vez por cada nodo de la cobertura, se tiene una complejidad total acumulada para eliminar nodos de O(∣V∣+∣E∣)
La limpieza de nodos redundantes sigue un razonamiento muy parecido al de eliminar nodos, por lo que su complejidad también es O(∣V∣+∣E∣)
Pero, como en el peor caso global del Isolation Algorithm no ocurrirá jamás el peor caso para estas funciones, éstas terminan teniendo esas complejidades de O(1), O(1) y O(∣V∣) respectivamente.
Otra cosa curiosa, es que el peor caso para agregar y eliminar nodos, y hacer la limpieza, resulta ser el mejor caso para el Isolation Algorithm.
Si se tiene un grafo completo, en la primera iteración del Isolation Algorithm se escoge un nodo cualquiera, y se agregan sus ∣V∣−1 vecinos a la cobertura, y eliminamos los mismos ∣V∣−1 nodos del grafo junto con sus aristas, que por ser un grafo completo, resultan en todas las aristas del grafo. Así que en una sola iteración se consigue la cobertura del grafo.

Implementación de la heurística
Al igual que el resto de algoritmos del proyecto, la heurística se implementó con Python.
El funcionamiento de la implementación es muy parecida a la del pseudocódigo mostrado antes:
Se crea una copia del grafo para no alterar el original.
Se itera mientras haya aristas en el grafo.
Se obtiene el nodo de menor grado, agrega a sus vecinos a la cobertura, y se eliminan del grafo, junto a sus aristas donde incide.
Luego busca nodos redundantes en la cobertura y los elimina.
Finalmente se retorna la cobertura.
Se hace uso de la librería NetworkX para trabajar con grafos. Esta librería no almacena los grafos como listas de aristas, sino mediante una estructura de Listas de Adyacencia basada en Diccionarios de Diccionarios (Dict-of-Dicts). Esto es importante para la eficiencia de la implementación del algoritmo.
Si hacemos un análisis igual al del peor caso teórico, la complejidad de la implementación seguirá siendo O(∣V∣^2):
El ciclo se seguirá ejecutando ∣V∣/2 veces.
Para obtener los grados del grafo, NetworkX usa la función degree(), la cual devuelve una vista (view object). Así, obtener el grado de un nodo específico es una operación O(1), ya que los diccionarios de Python mantienen un registro interno de su tamaño. Por otro lado, al momento de conseguir los grados del grafo, se filtran aquellos mayores a cero.
Luego, obtener los grados del grafo, filtrarlos y obtener el nodo de grado mínimo es O(∣V∣)
Agregar al vecino del nodo de grado mínimo a la cobertura y eliminarlo del grafo sigue siendo O(1)
Hacer la limpieza de los nodos redundantes de la cobertura sigue siendo O(∣V∣)
Luego, la complejidad temporal de la implementación es: 
O((∣V∣/2∗∣V∣)+∣V∣)=O(∣V∣^2)
Por otro lado, la complejidad espacial de la implementación es O(∣V∣+∣E∣), ya que hacemos una copia del grafo para no trabajar sobre la instancia original.

