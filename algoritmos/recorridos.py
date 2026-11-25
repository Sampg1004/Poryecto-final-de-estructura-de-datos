"""
algoritmos/recorridos.py
Módulo de recorridos y búsqueda de caminos en la red de alcantarillado.

Implementa los algoritmos fundamentales exigidos en el proyecto final:
  - BFS (Breadth-First Search / Recorrido en Amplitud) empleando la Cola propia.
  - DFS (Depth-First Search / Recorrido en Profundidad) empleando la Pila propia.
  - Reconstrucción de caminos utilizando la Pila propia.
  - Búsqueda de caminos mínimos y secuencias de tuberías.
  - Rutas hacia puntos de descarga / sumideros (PTAR Punta Canoa).
  - Determinación de cuencas aportantes (recorrido inverso).
  - Detección y reporte de ciclos en la red (validación de DAG).
"""

from typing import Any, List, Optional
from estructuras.cola import Cola
from estructuras.pila import Pila
from estructuras.tabla_hash import TablaHash
from modelo.grafo import Grafo
from modelo.tuberia import Tuberia


class Recorrido:
    """
    Clase encargada de ejecutar algoritmos de recorrido y búsqueda de caminos
    sobre el grafo de alcantarillado, utilizando las estructuras de datos
    propias (Cola, Pila y TablaHash) según las directrices del proyecto.
    """

    def __init__(self, grafo: Grafo):
        if not isinstance(grafo, Grafo):
            raise TypeError("Se esperaba una instancia válida de Grafo.")
        self.grafo = grafo

    # -------------------------------------------------------------------------
    # BFS: Recorrido en Amplitud (usa la Cola propia)
    # -------------------------------------------------------------------------

    def bfs(self, inicio: str) -> List[str]:
        """
        Realiza un recorrido en amplitud (BFS) a partir de un nodo inicial.
        Utiliza la estructura Cola implementada en el proyecto.

        Args:
            inicio: Identificador del nodo de partida.

        Returns:
            Lista de identificadores de nodos en el orden en que fueron visitados.

        Raises:
            ValueError: Si el nodo de inicio no existe en el grafo.
        """
        inicio_norm = str(inicio).strip()
        if not self.grafo.existe_nodo(inicio_norm):
            raise ValueError(f"El nodo de inicio '{inicio_norm}' no existe en el grafo.")

        visitados = TablaHash()
        visitados.insertar(inicio_norm, True)
        cola = Cola()
        cola.encolar(inicio_norm)
        orden_visita: List[str] = []

        while not cola.esta_vacia():
            actual = cola.desencolar()
            orden_visita.append(actual)

            for tuberia in self.grafo.obtener_tuberias_salientes(actual):
                destino = tuberia.nodo_destino
                if not visitados.contiene(destino):
                    visitados.insertar(destino, True)
                    cola.encolar(destino)

        return orden_visita

    def bfs_niveles(self, inicio: str) -> TablaHash:
        """
        Calcula la distancia en número de tramos/saltos (niveles de profundidad BFS)
        desde el nodo inicial hasta cada uno de los nodos alcanzables.

        Args:
            inicio: Identificador del nodo de partida.

        Returns:
            TablaHash {id_nodo: nivel}, donde el nodo de inicio tiene nivel 0.
        """
        inicio_norm = str(inicio).strip()
        if not self.grafo.existe_nodo(inicio_norm):
            raise ValueError(f"El nodo de inicio '{inicio_norm}' no existe en el grafo.")

        niveles = TablaHash()
        niveles.insertar(inicio_norm, 0)
        cola = Cola()
        cola.encolar(inicio_norm)

        while not cola.esta_vacia():
            actual = cola.desencolar()
            nivel_actual = niveles[actual]

            for tuberia in self.grafo.obtener_tuberias_salientes(actual):
                destino = tuberia.nodo_destino
                if not niveles.contiene(destino):
                    niveles.insertar(destino, nivel_actual + 1)
                    cola.encolar(destino)

        return niveles

    # -------------------------------------------------------------------------
    # DFS: Recorrido en Profundidad (usa la Pila propia)
    # -------------------------------------------------------------------------

    def dfs(self, inicio: str) -> List[str]:
        """
        Realiza un recorrido en profundidad (DFS) iterativo utilizando la estructura
        Pila implementada en el proyecto.

        Args:
            inicio: Identificador del nodo de partida.

        Returns:
            Lista de identificadores de nodos en el orden en que fueron visitados.

        Raises:
            ValueError: Si el nodo de inicio no existe en el grafo.
        """
        inicio_norm = str(inicio).strip()
        if not self.grafo.existe_nodo(inicio_norm):
            raise ValueError(f"El nodo de inicio '{inicio_norm}' no existe en el grafo.")

        pila = Pila()
        pila.apilar(inicio_norm)
        visitados = TablaHash()
        orden_visita: List[str] = []

        while not pila.esta_vacia():
            actual = pila.desapilar()
            if not visitados.contiene(actual):
                visitados.insertar(actual, True)
                orden_visita.append(actual)

                # Se apilan las tuberías en orden inverso para preservar
                # el orden natural de visita de los vecinos al desapilar
                tuberias = self.grafo.obtener_tuberias_salientes(actual)
                for tuberia in reversed(tuberias):
                    destino = tuberia.nodo_destino
                    if not visitados.contiene(destino):
                        pila.apilar(destino)

        return orden_visita

    def dfs_recursivo(self, inicio: str) -> List[str]:
        """
        Variante recursiva de DFS para comprobación y análisis académico.
        """
        inicio_norm = str(inicio).strip()
        if not self.grafo.existe_nodo(inicio_norm):
            raise ValueError(f"El nodo de inicio '{inicio_norm}' no existe en el grafo.")

        visitados = TablaHash()
        orden_visita: List[str] = []

        def _dfs_visitar(nodo_id: str):
            visitados.insertar(nodo_id, True)
            orden_visita.append(nodo_id)
            for tuberia in self.grafo.obtener_tuberias_salientes(nodo_id):
                destino = tuberia.nodo_destino
                if not visitados.contiene(destino):
                    _dfs_visitar(destino)

        _dfs_visitar(inicio_norm)
        return orden_visita

    # -------------------------------------------------------------------------
    # Reconstrucción de Caminos con Pila (Requisito explícito del PDF)
    # -------------------------------------------------------------------------

    def reconstruir_camino(
        self, predecesores: Any, destino: str, origen: str
    ) -> List[str]:
        """
        Reconstruye la secuencia de nodos desde el origen hasta el destino
        utilizando una Pila (LIFO) para invertir el rastreo hacia atrás.

        Args:
            predecesores: TablaHash o mapeo {nodo_hijo: nodo_padre}.
            destino: Identificador del nodo final.
            origen: Identificador del nodo inicial.

        Returns:
            Lista ordenada [origen, ..., destino], o lista vacía si no hay conexión.
        """
        if destino not in predecesores and destino != origen:
            return []

        pila = Pila()
        actual: Optional[str] = destino

        while actual is not None:
            pila.apilar(actual)
            if actual == origen:
                break
            actual = predecesores[actual] if actual in predecesores else None

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

        Args:
            origen: Identificador del nodo inicial.
            destino: Identificador del nodo final.

        Returns:
            Lista con la secuencia de nodos [origen, ..., destino], o None si no hay camino.
        """
        origen_norm = str(origen).strip()
        destino_norm = str(destino).strip()

        if not self.grafo.existe_nodo(origen_norm) or not self.grafo.existe_nodo(destino_norm):
            return None

        if origen_norm == destino_norm:
            return [origen_norm]

        cola = Cola()
        cola.encolar(origen_norm)
        visitados = TablaHash()
        visitados.insertar(origen_norm, True)
        predecesores = TablaHash()

        encontrado = False
        while not cola.esta_vacia():
            actual = cola.desencolar()
            if actual == destino_norm:
                encontrado = True
                break

            for tuberia in self.grafo.obtener_tuberias_salientes(actual):
                vecino = tuberia.nodo_destino
                if not visitados.contiene(vecino):
                    visitados.insertar(vecino, True)
                    predecesores.insertar(vecino, actual)
                    cola.encolar(vecino)

        if not encontrado and not predecesores.contiene(destino_norm):
            return None

        camino = self.reconstruir_camino(predecesores, destino_norm, origen_norm)
        return camino if camino else None

    def camino_mas_corto_tuberias_bfs(
        self, origen: str, destino: str
    ) -> Optional[List[Tuberia]]:
        """
        Encuentra la secuencia de objetos Tuberia correspondiente al camino más corto
        entre origen y destino.

        Returns:
            Lista de objetos Tuberia en orden de flujo, o None si no existe camino.
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
        """
        Encuentra un camino dirigido entre origen y destino utilizando DFS con Pila.

        Returns:
            Lista con la secuencia de nodos [origen, ..., destino], o None si no hay camino.
        """
        origen_norm = str(origen).strip()
        destino_norm = str(destino).strip()

        if not self.grafo.existe_nodo(origen_norm) or not self.grafo.existe_nodo(destino_norm):
            return None

        if origen_norm == destino_norm:
            return [origen_norm]

        pila = Pila()
        pila.apilar(origen_norm)
        visitados = TablaHash()
        predecesores = TablaHash()

        encontrado = False
        while not pila.esta_vacia():
            actual = pila.desapilar()
            if actual == destino_norm:
                encontrado = True
                break

            if not visitados.contiene(actual):
                visitados.insertar(actual, True)
                for tuberia in reversed(self.grafo.obtener_tuberias_salientes(actual)):
                    vecino = tuberia.nodo_destino
                    if not visitados.contiene(vecino):
                        predecesores[vecino] = actual
                        pila.apilar(vecino)

        if not encontrado and not predecesores.contiene(destino_norm):
            return None

        camino = self.reconstruir_camino(predecesores, destino_norm, origen_norm)
        return camino if camino else None

    def todos_los_caminos_dfs(
        self, origen: str, destino: str, limite: int = 100
    ) -> List[List[str]]:
        """
        Encuentra todos los caminos simples posibles entre origen y destino
        mediante DFS iterativo con retroceso, empleando la Pila propia.

        Args:
            origen: Identificador del nodo inicial.
            destino: Identificador del nodo final.
            limite: Cantidad máxima de caminos a recolectar.

        Returns:
            Lista de caminos, donde cada camino es una lista de identificadores de nodo.
        """
        origen_norm = str(origen).strip()
        destino_norm = str(destino).strip()

        if not self.grafo.existe_nodo(origen_norm) or not self.grafo.existe_nodo(destino_norm):
            return []

        caminos: List[List[str]] = []
        pila = Pila()
        en_camino = TablaHash()
        ruta_actual: List[str] = []

        pila.apilar((origen_norm, 0))
        en_camino.insertar(origen_norm, True)
        ruta_actual.append(origen_norm)

        while not pila.esta_vacia() and len(caminos) < limite:
            u, idx = pila.desapilar()
            if u == destino_norm:
                caminos.append(list(ruta_actual))
                en_camino.eliminar(u)
                ruta_actual.pop()
                continue

            tuberias = self.grafo.obtener_tuberias_salientes(u)
            if idx < len(tuberias):
                pila.apilar((u, idx + 1))
                v = tuberias[idx].nodo_destino
                if not en_camino.contiene(v):
                    en_camino.insertar(v, True)
                    ruta_actual.append(v)
                    pila.apilar((v, 0))
            else:
                en_camino.eliminar(u)
                ruta_actual.pop()

        return caminos

    # -------------------------------------------------------------------------
    # Operaciones del Dominio del Problema (Red de Alcantarillado)
    # -------------------------------------------------------------------------

    def camino_a_sumidero(self, nodo_origen: str) -> Optional[List[str]]:
        """
        Encuentra el camino dirigido más corto desde un nodo (fuente o pozo)
        hasta el sumidero de la red (punto de entrega / PTAR de Punta Canoa).
        Satisface el requisito de presentar resultados hasta la descarga.

        Args:
            nodo_origen: Identificador del nodo inicial.

        Returns:
            Lista de nodos que llevan al sumidero, o None si no alcanza ninguno.
        """
        sumideros = self.grafo.obtener_sumideros()
        if not sumideros:
            return None

        mejor_camino: Optional[List[str]] = None
        for s in sumideros:
            camino = self.camino_mas_corto_bfs(nodo_origen, s.id_nodo)
            if camino:
                if mejor_camino is None or len(camino) < len(mejor_camino):
                    mejor_camino = camino

        return mejor_camino

    def camino_a_sumidero_tuberias(
        self, nodo_origen: str
    ) -> Optional[List[Tuberia]]:
        """
        Retorna la secuencia de objetos Tuberia desde un nodo hasta el sumidero.
        """
        camino_nodos = self.camino_a_sumidero(nodo_origen)
        if not camino_nodos or len(camino_nodos) < 2:
            return [] if camino_nodos else None

        tuberias: List[Tuberia] = []
        for u, v in zip(camino_nodos[:-1], camino_nodos[1:]):
            for t in self.grafo.obtener_tuberias_salientes(u):
                if t.nodo_destino == v:
                    tuberias.append(t)
                    break
        return tuberias

    def nodos_alcanzables(self, nodo_origen: str) -> List[str]:
        """
        Retorna todos los nodos a los que llega flujo desde el nodo origen (cuenca aguas abajo).
        """
        return self.bfs(nodo_origen)

    def cuenca_aportante(self, nodo_destino: str) -> List[str]:
        """
        Determina todos los nodos aguas arriba que aportan flujo directa o
        indirectamente hacia el nodo dado (recorrido inverso por tuberías entrantes).

        Args:
            nodo_destino: Identificador del nodo a analizar.

        Returns:
            Lista de nodos aguas arriba que descargan hacia nodo_destino.
        """
        destino_norm = str(nodo_destino).strip()
        if not self.grafo.existe_nodo(destino_norm):
            raise ValueError(f"El nodo '{destino_norm}' no existe en el grafo.")

        visitados = TablaHash()
        visitados.insertar(destino_norm, True)
        cola = Cola()
        cola.encolar(destino_norm)
        cuenca: List[str] = []

        while not cola.esta_vacia():
            actual = cola.desencolar()
            if actual != destino_norm:
                cuenca.append(actual)

            for tuberia in self.grafo.obtener_tuberias_entrantes(actual):
                origen = tuberia.nodo_origen
                if not visitados.contiene(origen):
                    visitados.insertar(origen, True)
                    cola.encolar(origen)

        return cuenca

    def detectar_ciclos(self) -> Optional[List[str]]:
        """
        Verifica si la red contiene ciclos dirigidos mediante DFS iterativo con Pila
        de 3 estados (0=No visitado, 1=En proceso, 2=Finalizado).

        Returns:
            Lista de nodos que forman el ciclo si existe uno, o None si la red es acíclica.
        """
        # Estados: 0=Blanco, 1=Gris (en pila), 2=Negro (completado)
        estado = TablaHash()
        padre = TablaHash()
        pila = Pila()

        for nodo in self.grafo.obtener_todos_los_nodos():
            inicio_id = nodo.id_nodo
            if estado.obtener(inicio_id, 0) != 0:
                continue

            estado[inicio_id] = 1
            pila.apilar((inicio_id, 0))

            while not pila.esta_vacia():
                u, idx = pila.desapilar()
                tuberias = self.grafo.obtener_tuberias_salientes(u)

                if idx < len(tuberias):
                    pila.apilar((u, idx + 1))
                    v = tuberias[idx].nodo_destino
                    est_v = estado.obtener(v, 0)
                    if est_v == 1:
                        pila_ciclo = Pila()
                        pila_ciclo.apilar(v)
                        actual = u
                        while actual != v and padre.contiene(actual):
                            pila_ciclo.apilar(actual)
                            actual = padre[actual]
                        pila_ciclo.apilar(v)
                        ciclo_encontrado: List[str] = []
                        while not pila_ciclo.esta_vacia():
                            ciclo_encontrado.append(pila_ciclo.desapilar())
                        return ciclo_encontrado
                    elif est_v == 0:
                        padre[v] = u
                        estado[v] = 1
                        pila.apilar((v, 0))
                else:
                    estado[u] = 2

        return None

    def recorrido_completo_fuentes(self, metodo: str = "bfs") -> List[str]:
        """
        Recorre toda la red a partir de todos los nodos fuente registrados,
        garantizando la cobertura de todos los ramales independientes.

        Args:
            metodo: 'bfs' para amplitud, 'dfs' para profundidad.

        Returns:
            Lista unificada de nodos visitados sin repetición.
        """
        fuentes = self.grafo.obtener_fuentes()
        visitados_global = TablaHash()
        orden_total: List[str] = []

        fn_recorrido = self.bfs if metodo.lower() == "bfs" else self.dfs

        for f in fuentes:
            if not visitados_global.contiene(f.id_nodo):
                parcial = fn_recorrido(f.id_nodo)
                for nodo_id in parcial:
                    if not visitados_global.contiene(nodo_id):
                        visitados_global.insertar(nodo_id, True)
                        orden_total.append(nodo_id)

        return orden_total

    def __repr__(self) -> str:
        return f"Recorrido(grafo={self.grafo!r})"


# Alias de clase para máxima compatibilidad
Recorridos = Recorrido


# -----------------------------------------------------------------------------
# Funciones de conveniencia a nivel de módulo
# -----------------------------------------------------------------------------

def bfs(grafo: Grafo, inicio: str) -> List[str]:
    """Ejecuta BFS sobre el grafo dado a partir del nodo inicio."""
    return Recorrido(grafo).bfs(inicio)


def dfs(grafo: Grafo, inicio: str) -> List[str]:
    """Ejecuta DFS sobre el grafo dado a partir del nodo inicio."""
    return Recorrido(grafo).dfs(inicio)


def camino_mas_corto(grafo: Grafo, origen: str, destino: str) -> Optional[List[str]]:
    """Encuentra el camino con menor número de tuberías entre origen y destino."""
    return Recorrido(grafo).camino_mas_corto_bfs(origen, destino)


def camino_a_sumidero(grafo: Grafo, origen: str) -> Optional[List[str]]:
    """Encuentra la ruta desde el nodo origen hasta el punto final / sumidero."""
    return Recorrido(grafo).camino_a_sumidero(origen)
