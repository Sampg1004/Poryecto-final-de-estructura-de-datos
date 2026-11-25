"""
Módulo de recorridos y búsqueda de caminos en la red de alcantarillado.
  - BFS (Breadth-First Search / Recorrido en Amplitud) empleando la Cola propia.
  - DFS (Depth-First Search / Recorrido en Profundidad) empleando la Pila propia.
  - Reconstrucción de caminos utilizando la Pila propia.
  - Búsqueda de caminos mínimos y secuencias de tuberías.
"""

from typing import Dict, List, Optional, Set, Tuple
from estructuras.cola import Cola
from estructuras.pila import Pila
from modelo.grafo import Grafo
from modelo.nodo import Nodo
from modelo.tuberia import Tuberia


class Recorrido:

    def __init__(self, grafo: Grafo):
        if not isinstance(grafo, Grafo):
            raise TypeError("Se esperaba una instancia válida de Grafo.")
        self.grafo = grafo

    """
     BFS: Recorrido en Amplitud (usa la Cola propia)
    """

    def bfs(self, inicio: str) -> List[str]:
        
        """Realiza un recorrido en amplitud (BFS) a partir de un nodo inicial."""

        inicio_norm = str(inicio).strip()
        if not self.grafo.existe_nodo(inicio_norm):
            raise ValueError(f"El nodo de inicio '{inicio_norm}' no existe en el grafo.")

        visitados: Set[str] = {inicio_norm}
        cola = Cola()
        cola.encolar(inicio_norm)
        orden_visita: List[str] = []

        while not cola.esta_vacia():
            actual = cola.desencolar()
            orden_visita.append(actual)

            for tuberia in self.grafo.obtener_tuberias_salientes(actual):
                destino = tuberia.nodo_destino
                if destino not in visitados:
                    visitados.add(destino)
                    cola.encolar(destino)

        return orden_visita

    def bfs_niveles(self, inicio: str) -> Dict[str, int]:
        """
        Calcula la distancia en número de tramos/saltos (niveles de profundidad BFS)
        desde el nodo inicial hasta cada uno de los nodos alcanzables.
        """
        inicio_norm = str(inicio).strip()
        if not self.grafo.existe_nodo(inicio_norm):
            raise ValueError(f"El nodo de inicio '{inicio_norm}' no existe en el grafo.")

        niveles: Dict[str, int] = {inicio_norm: 0}
        cola = Cola()
        cola.encolar(inicio_norm)

        while not cola.esta_vacia():
            actual = cola.desencolar()
            nivel_actual = niveles[actual]

            for tuberia in self.grafo.obtener_tuberias_salientes(actual):
                destino = tuberia.nodo_destino
                if destino not in niveles:
                    niveles[destino] = nivel_actual + 1
                    cola.encolar(destino)

        return niveles

    
    # DFS: Recorrido en Profundidad 

    def dfs(self, inicio: str) -> List[str]:
        """
        Realiza un recorrido en profundidad (DFS) iterativo utilizando una pila"""
        inicio_norm = str(inicio).strip()
        if not self.grafo.existe_nodo(inicio_norm):
            raise ValueError(f"El nodo de inicio '{inicio_norm}' no existe en el grafo.")

        pila = Pila()
        pila.apilar(inicio_norm)
        visitados: Set[str] = set()
        orden_visita: List[str] = []

        while not pila.esta_vacia():
            actual = pila.desapilar()
            if actual not in visitados:
                visitados.add(actual)
                orden_visita.append(actual)

                # Se apilan las tuberías en orden inverso para preservar
                # el orden natural de visita de los vecinos al desapilar
                tuberias = self.grafo.obtener_tuberias_salientes(actual)
                for tuberia in reversed(tuberias):
                    destino = tuberia.nodo_destino
                    if destino not in visitados:
                        pila.apilar(destino)

        return orden_visita

    def dfs_recursivo(self, inicio: str) -> List[str]:
        inicio_norm = str(inicio).strip()
        if not self.grafo.existe_nodo(inicio_norm):
            raise ValueError(f"El nodo de inicio '{inicio_norm}' no existe en el grafo.")

        visitados: Set[str] = set()
        orden_visita: List[str] = []

        def _dfs_visitar(nodo_id: str):
            visitados.add(nodo_id)
            orden_visita.append(nodo_id)
            for tuberia in self.grafo.obtener_tuberias_salientes(nodo_id):
                destino = tuberia.nodo_destino
                if destino not in visitados:
                    _dfs_visitar(destino)

        _dfs_visitar(inicio_norm)
        return orden_visita

    # Reconstrucción de Caminos con Pila 
    def reconstruir_camino(
        self, predecesores: Dict[str, str], destino: str, origen: str
    ) -> List[str]:
        """
        Reconstruye la secuencia de nodos desde el origen hasta el destino
        utilizando una Pila (LIFO) para invertir el rastreo hacia atrás.
        """
        if destino not in predecesores and destino != origen:
            return []

        pila = Pila()
        actual: Optional[str] = destino

        while actual is not None:
            pila.apilar(actual)
            if actual == origen:
                break
            actual = predecesores.get(actual)

        if actual != origen:
            return []

        camino: List[str] = []
        while not pila.esta_vacia():
            camino.append(pila.desapilar())

        return camino

    # -------------------------------------------------------------------------
    # Búsqueda de Caminos: Corto (BFS) y Alternativos (DFS)
    # -------------------------------------------------------------------------

    def camino_mas_corto_bfs(self, origen: str, destino: str) -> Optional[List[str]]:
        """
        Encuentra el camino dirigido con menor número de tramos entre origen y destino.
        Utiliza BFS (Cola) para explorar y la Pila para la reconstrucción del camino.
        """
        origen_norm = str(origen).strip()
        destino_norm = str(destino).strip()

        if not self.grafo.existe_nodo(origen_norm) or not self.grafo.existe_nodo(destino_norm):
            return None

        if origen_norm == destino_norm:
            return [origen_norm]

        cola = Cola()
        cola.encolar(origen_norm)
        visitados: Set[str] = {origen_norm}
        predecesores: Dict[str, str] = {}

        encontrado = False
        while not cola.esta_vacia():
            actual = cola.desencolar()
            if actual == destino_norm:
                encontrado = True
                break

            for tuberia in self.grafo.obtener_tuberias_salientes(actual):
                vecino = tuberia.nodo_destino
                if vecino not in visitados:
                    visitados.add(vecino)
                    predecesores[vecino] = actual
                    cola.encolar(vecino)

        if not encontrado and destino_norm not in predecesores:
            return None

        camino = self.reconstruir_camino(predecesores, destino_norm, origen_norm)
        return camino if camino else None

    def camino_mas_corto_tuberias_bfs(
        self, origen: str, destino: str
    ) -> Optional[List[Tuberia]]:
        """
        Encuentra la secuencia de objetos Tuberia correspondiente al camino más corto
        entre origen y destino.
        """
        camino_nodos = self.camino_mas_corto_bfs(origen, destino)
        if not camino_nodos or len(camino_nodos) < 2:
            return [] if camino_nodos else None

        tuberias_camino: List[Tuberia] = []
        for u, v in zip(camino_nodos[:-1], camino_nodos[1:]):
            encontrada = False
            for tuberia in self.grafo.obtener_tuberias_salientes(u):
                if tuberia.nodo_destino == v:
                    tuberias_camino.append(tuberia)
                    encontrada = True
                    break
            if not encontrada:
                return None

        return tuberias_camino

    def buscar_camino_dfs(self, origen: str, destino: str) -> Optional[List[str]]:
        """Encuentra un camino dirigido entre origen y destino utilizando DFS con Pila."""

        origen_norm = str(origen).strip()
        destino_norm = str(destino).strip()

        if not self.grafo.existe_nodo(origen_norm) or not self.grafo.existe_nodo(destino_norm):
            return None

        if origen_norm == destino_norm:
            return [origen_norm]

        pila = Pila()
        pila.apilar(origen_norm)
        visitados: Set[str] = set()
        predecesores: Dict[str, str] = {}

        encontrado = False
        while not pila.esta_vacia():
            actual = pila.desapilar()
            if actual == destino_norm:
                encontrado = True
                break

            if actual not in visitados:
                visitados.add(actual)
                for tuberia in reversed(self.grafo.obtener_tuberias_salientes(actual)):
                    vecino = tuberia.nodo_destino
                    if vecino not in visitados:
                        predecesores[vecino] = actual
                        pila.apilar(vecino)

        if not encontrado and destino_norm not in predecesores:
            return None

        camino = self.reconstruir_camino(predecesores, destino_norm, origen_norm)
        return camino if camino else None

    def todos_los_caminos_dfs(
        self, origen: str, destino: str, limite: int = 100
    ) -> List[List[str]]:
        """
        Encuentra todos los caminos simples posibles entre origen y destino
        mediante DFS con retroceso (backtracking), empleando la Pila propia
        para mantener la ruta actual."""
        origen_norm = str(origen).strip()
        destino_norm = str(destino).strip()

        if not self.grafo.existe_nodo(origen_norm) or not self.grafo.existe_nodo(destino_norm):
            return []

        caminos: List[List[str]] = []
        pila_camino = Pila()
        en_camino: Set[str] = set()

        def _explorar(actual: str):
            if len(caminos) >= limite:
                return

            pila_camino.apilar(actual)
            en_camino.add(actual)

            if actual == destino_norm:
                # Invertir para obtener la secuencia en orden de avance origen -> destino
                ruta = list(pila_camino)[::-1]
                caminos.append(ruta)
            else:
                for tuberia in self.grafo.obtener_tuberias_salientes(actual):
                    vecino = tuberia.nodo_destino
                    if vecino not in en_camino:
                        _explorar(vecino)

            en_camino.remove(actual)
            pila_camino.desapilar()

        _explorar(origen_norm)
        return caminos

    
