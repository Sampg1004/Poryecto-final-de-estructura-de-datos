from typing import List, Optional, Dict, Any
from modelo.grafo import Grafo
from modelo.nodo import Nodo
from modelo.tuberia import Tuberia

class BuscadorRed:

    def __init__(self, grafo: Grafo):
        self.grafo = grafo

    def buscar_nodo_por_id(self, id_nodo: str) -> Optional[Nodo]:

        return self.grafo.obtener_nodo(id_nodo)

    def existe_nodo(self, id_nodo: str) -> bool:
        return self.grafo.existe_nodo(id_nodo)

    def listar_todos_los_nodos(self) -> List[Nodo]:
        return self.grafo.obtener_todos_los_nodos()

    def listar_fuentes(self) -> List[Nodo]:

        return self.grafo.obtener_fuentes()

    def listar_sumideros(self) -> List[Nodo]:

        return self.grafo.obtener_sumideros()

    def listar_pozos(self) -> List[Nodo]:

        return self.grafo.obtener_pozos()

    def nodos_por_tipo(self, tipo: str) -> List[Nodo]:
        return self.grafo.obtener_nodos_por_tipo(tipo)

    def obtener_atributos_nodo(self, id_nodo: str) -> Optional[Dict[str, Any]]:

        nodo = self.buscar_nodo_por_id(id_nodo)
        if nodo is None:
            return None
        return {
            "id_nodo": nodo.id_nodo,
            "tipo": nodo.tipo,
            "x": nodo.x,
            "y": nodo.y,
            "area_drenaje": nodo.area_drenaje,
            "coef_escorrentia": nodo.coef_escorrentia,
            "caudal_sanitario": nodo.caudal_sanitario,
            "capacidad_almacenamiento": nodo.capacidad_almacenamiento,
            "caudal_lluvia": nodo.caudal_lluvia,
            "caudal_total_entrada": nodo.caudal_total_entrada,
            "caudal_salida": nodo.caudal_salida,
            "volumen_almacenado": nodo.volumen_almacenado,
            "sobrecargado": nodo.sobrecargado,
            "grado_entrada": nodo.grado_entrada,
            "grado_salida": nodo.grado_salida,
        }


    def buscar_tuberia_por_id(self, id_tuberia: str) -> Optional[Tuberia]:

        return self.grafo.obtener_tuberia(id_tuberia)

    def existe_tuberia(self, id_tuberia: str) -> bool:
        return self.grafo.existe_tuberia(id_tuberia)

    def listar_todas_las_tuberias(self) -> List[Tuberia]:
        return self.grafo.obtener_todas_las_tuberias()

    def tuberias_salientes_de(self, id_nodo: str) -> List[Tuberia]:
        return self.grafo.obtener_tuberias_salientes(id_nodo)

    def tuberias_entrantes_de(self, id_nodo: str) -> List[Tuberia]:
        return self.grafo.obtener_tuberias_entrantes(id_nodo)

    def obtener_atributos_tuberia(self, id_tuberia: str) -> Optional[Dict[str, Any]]:
  
        tuberia = self.buscar_tuberia_por_id(id_tuberia)
        if tuberia is None:
            return None
        return {
            "id_tuberia": tuberia.id_tuberia,
            "nodo_origen": tuberia.nodo_origen,
            "nodo_destino": tuberia.nodo_destino,
            "longitud": tuberia.longitud,
            "diametro": tuberia.diametro,
            "pendiente": tuberia.pendiente,
            "coeficiente_manning": tuberia.coeficiente_manning,
            "capacidad_maxima": tuberia.capacidad_maxima,
            "caudal_transportado": tuberia.caudal_transportado,
            "velocidad": tuberia.velocidad,
            "porcentaje_utilizacion": tuberia.porcentaje_utilizacion,
            "sobrecargada": tuberia.sobrecargada,
            "tiempo_transito": tuberia.tiempo_tránsito,
        }

    def tuberias_conectando(self, id_origen: str, id_destino: str) -> List[Tuberia]:
        """Retorna tuberías que van de origen a destino."""
        resultado = []
        for t in self.grafo.obtener_tuberias_salientes(id_origen):
            if t.nodo_destino == id_destino:
                resultado.append(t)
        return resultado

    def resumen_red(self) -> Dict[str, Any]:
        """Retorna un resumen estadístico de la red."""
        nodos = self.listar_todos_los_nodos()
        tuberias = self.listar_todas_las_tuberias()
        return {
            "total_nodos": len(nodos),
            "total_fuentes": len(self.listar_fuentes()),
            "total_pozos": len(self.listar_pozos()),
            "total_sumideros": len(self.listar_sumideros()),
            "total_tuberias": len(tuberias),
            "nodos": [n.id_nodo for n in nodos],
            "tuberias": [t.id_tuberia for t in tuberias],
        }
