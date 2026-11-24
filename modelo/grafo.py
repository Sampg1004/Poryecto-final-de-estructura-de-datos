from typing import List, Optional, Set

from estructuras.tabla_hash import TablaHash
from estructuras.cola import Cola
from modelo.nodo import Nodo
from modelo.tuberia import Tuberia

class Grafo:
        # Red de alcantarillado como grafo dirigido.
        #
        # Vértices = alcantarillas / pozos de inspección / sumideros (Nodo).
        # Aristas  = tuberías dirigidas (Tuberia).

    def __init__(self):
        self.nodos = TablaHash()
        self.tuberias = TablaHash()
        self.adyacencia = TablaHash()           # id_nodo -> [Tuberia salientes]
        self.adyacencia_inversa = TablaHash()   # id_nodo -> [Tuberia entrantes]
        self._orden_nodos: List[str] = []
        self._orden_tuberias: List[str] = []

    # Nodos
    def agregar_nodo(self, nodo: Nodo) -> None:
        if not isinstance(nodo, Nodo):
            raise TypeError("Se esperaba una instancia de Nodo.")
        if self.nodos.contiene(nodo.id_nodo):
            raise ValueError(f"Ya existe un nodo con id '{nodo.id_nodo}'.")
        self.nodos.insertar(nodo.id_nodo, nodo)
        self.adyacencia.insertar(nodo.id_nodo, [])
        self.adyacencia_inversa.insertar(nodo.id_nodo, [])
        self._orden_nodos.append(nodo.id_nodo)

    def obtener_nodo(self, id_nodo: str) -> Optional[Nodo]:
        return self.nodos.obtener(id_nodo)

    def existe_nodo(self, id_nodo: str) -> bool:
        return self.nodos.contiene(id_nodo)

    def obtener_todos_los_nodos(self) -> List[Nodo]:
        return [self.nodos.obtener(i) for i in self._orden_nodos]

    def obtener_nodos_por_tipo(self, tipo: str) -> List[Nodo]:
        return [n for n in self.obtener_todos_los_nodos() if n.tipo == tipo]

    def obtener_fuentes(self) -> List[Nodo]:
        return self.obtener_nodos_por_tipo(Nodo.TIPO_FUENTE)

    def obtener_sumideros(self) -> List[Nodo]:
        return self.obtener_nodos_por_tipo(Nodo.TIPO_SUMIDERO)

    def obtener_pozos(self) -> List[Nodo]:
        return self.obtener_nodos_por_tipo(Nodo.TIPO_POZO)

    def cantidad_nodos(self) -> int:
        return len(self._orden_nodos)

    # Tuberías
    def agregar_tuberia(self, tuberia: Tuberia) -> None:
        if not isinstance(tuberia, Tuberia):
            raise TypeError("Se esperaba una instancia de Tuberia.")
        if self.tuberias.contiene(tuberia.id_tuberia):
            raise ValueError(f"Ya existe una tubería con id '{tuberia.id_tuberia}'.")
        if not self.existe_nodo(tuberia.nodo_origen):
            raise ValueError(f"El nodo origen '{tuberia.nodo_origen}' no existe en el grafo.")
        if not self.existe_nodo(tuberia.nodo_destino):
            raise ValueError(f"El nodo destino '{tuberia.nodo_destino}' no existe en el grafo.")

        self.tuberias.insertar(tuberia.id_tuberia, tuberia)
        self._orden_tuberias.append(tuberia.id_tuberia)
        self.adyacencia.obtener(tuberia.nodo_origen).append(tuberia)
        self.adyacencia_inversa.obtener(tuberia.nodo_destino).append(tuberia)
        self.nodos.obtener(tuberia.nodo_origen).agregar_tuberia_saliente(tuberia)
        self.nodos.obtener(tuberia.nodo_destino).agregar_tuberia_entrante(tuberia)

    def obtener_tuberia(self, id_tuberia: str) -> Optional[Tuberia]:
        return self.tuberias.obtener(id_tuberia)

    def existe_tuberia(self, id_tuberia: str) -> bool:
        return self.tuberias.contiene(id_tuberia)

    def obtener_todas_las_tuberias(self) -> List[Tuberia]:
        return [self.tuberias.obtener(i) for i in self._orden_tuberias]

    def obtener_tuberias_salientes(self, id_nodo: str) -> List[Tuberia]:
        return list(self.adyacencia.obtener(id_nodo, []))

    def obtener_tuberias_entrantes(self, id_nodo: str) -> List[Tuberia]:
        return list(self.adyacencia_inversa.obtener(id_nodo, []))

    def cantidad_tuberias(self) -> int:
        return len(self._orden_tuberias)

    # Consultas
    def obtener_vecinos(self, id_nodo: str) -> List[Nodo]:
        vecinos: List[Nodo] = []
        for tuberia in self.obtener_tuberias_salientes(id_nodo):
            vecino = self.nodos.obtener(tuberia.nodo_destino)
            if vecino not in vecinos:
                vecinos.append(vecino)
        return vecinos

    def grado_entrada(self, id_nodo: str) -> int:
        return len(self.adyacencia_inversa.obtener(id_nodo, []))

    def grado_salida(self, id_nodo: str) -> int:
        return len(self.adyacencia.obtener(id_nodo, []))

    def camino_existe(self, origen: str, destino: str) -> bool:
        # Existe un camino dirigido origen -> destino (BFS con la Cola propia).
        if not self.existe_nodo(origen) or not self.existe_nodo(destino):
            return False
        visitados: Set[str] = {origen}
        cola = Cola()
        cola.encolar(origen)
        while not cola.esta_vacia():
            actual = cola.desencolar()
            if actual == destino:
                return True
            for tuberia in self.obtener_tuberias_salientes(actual):
                if tuberia.nodo_destino not in visitados:
                    visitados.add(tuberia.nodo_destino)
                    cola.encolar(tuberia.nodo_destino)
        return False

    def orden_topologico(self) -> Optional[List[str]]:
        # Orden topológico (algoritmo de Kahn con la Cola propia).
        # Devuelve None si el grafo tiene ciclos.
        grados = {i: self.grado_entrada(i) for i in self._orden_nodos}
        cola = Cola()
        for i in self._orden_nodos:
            if grados[i] == 0:
                cola.encolar(i)
        orden: List[str] = []
        while not cola.esta_vacia():
            actual = cola.desencolar()
            orden.append(actual)
            for tuberia in self.obtener_tuberias_salientes(actual):
                grados[tuberia.nodo_destino] -= 1
                if grados[tuberia.nodo_destino] == 0:
                    cola.encolar(tuberia.nodo_destino)
        return orden if len(orden) == len(self._orden_nodos) else None

    def es_aciclico(self) -> bool:
        return self.orden_topologico() is not None

    def validar_conexiones(self) -> List[str]:
        # Mensajes de error si alguna tubería apunta a nodos inexistentes.
        errores = []
        for tuberia in self.obtener_todas_las_tuberias():
            if not self.existe_nodo(tuberia.nodo_origen):
                errores.append(f"Tubería {tuberia.id_tuberia}: nodo origen '{tuberia.nodo_origen}' no existe.")
            if not self.existe_nodo(tuberia.nodo_destino):
                errores.append(f"Tubería {tuberia.id_tuberia}: nodo destino '{tuberia.nodo_destino}' no existe.")
        return errores

    def reiniciar_estado(self) -> None:
        for nodo in self.obtener_todos_los_nodos():
            nodo.reiniciar_simulacion()
        for tuberia in self.obtener_todas_las_tuberias():
            tuberia.reiniciar()

    def __str__(self) -> str:
        return f"Grafo(nodos={self.cantidad_nodos()}, tuberias={self.cantidad_tuberias()})"

    __repr__ = __str__
