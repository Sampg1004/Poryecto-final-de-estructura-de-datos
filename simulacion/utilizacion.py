from typing import List, Dict, Any
from modelo.grafo import Grafo

# Escala de colores de la guía (sección 7)
COLOR_BAJA = "#2ecc71"       # 0-25 %      Verde
COLOR_MODERADA = "#f1c40f"   # >25-50 %    Amarillo
COLOR_ALTA = "#e67e22"       # >50-75 %    Naranja
COLOR_MAXIMA = "#e74c3c"     # >75-100 %   Rojo
COLOR_EXCEDIDA = "#8e1b10"   # >100 %      Rojo oscuro


def categoria_por_uso(porcentaje: float) -> str:
    """
    Clasifica la utilización según la escala de la guía. Los límites superiores
    son inclusivos: 25 % -> baja, 75 % -> alta, 100 % -> máxima; solo >100 % es excedida.
    """
    if porcentaje > 100.0:
        return "excedida"
    if porcentaje > 75.0:
        return "maxima"
    if porcentaje > 50.0:
        return "alta"
    if porcentaje > 25.0:
        return "moderada"
    return "baja"


_COLORES = {"baja": COLOR_BAJA, "moderada": COLOR_MODERADA, "alta": COLOR_ALTA,
            "maxima": COLOR_MAXIMA, "excedida": COLOR_EXCEDIDA}
_NOMBRES_COLOR = {"baja": "Verde", "moderada": "Amarillo", "alta": "Naranja",
                  "maxima": "Rojo", "excedida": "Rojo oscuro"}
_TEXTOS = {"baja": "Baja utilización", "moderada": "Utilización moderada",
           "alta": "Utilización alta", "maxima": "Cercana a la capacidad máxima",
           "excedida": "Capacidad excedida"}


def color_por_uso(porcentaje: float) -> str:
    """Color hexadecimal según el porcentaje de utilización."""
    return _COLORES[categoria_por_uso(porcentaje)]


class UtilizacionTuberia:
    """Resultado del cálculo de utilización de una tubería en un instante."""

    def __init__(self, id_tuberia: str, nodo_origen: str, nodo_destino: str,
                 caudal_transportado: float, capacidad_maxima: float,
                 porcentaje_utilizacion: float, sobrecargada: bool, tiempo: float):
        self.id_tuberia = id_tuberia
        self.nodo_origen = nodo_origen
        self.nodo_destino = nodo_destino
        self.caudal_transportado = caudal_transportado   # caudal Q_i(t) usado en la utilización
        self.capacidad_maxima = capacidad_maxima
        self.porcentaje_utilizacion = porcentaje_utilizacion
        self.sobrecargada = sobrecargada
        self.tiempo = tiempo

    def get_color_estado(self) -> str:
        return _NOMBRES_COLOR[categoria_por_uso(self.porcentaje_utilizacion)]

    def get_estado_texto(self) -> str:
        return _TEXTOS[categoria_por_uso(self.porcentaje_utilizacion)]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id_tuberia": self.id_tuberia, "nodo_origen": self.nodo_origen,
            "nodo_destino": self.nodo_destino, "caudal_transportado": self.caudal_transportado,
            "capacidad_maxima": self.capacidad_maxima,
            "porcentaje_utilizacion": self.porcentaje_utilizacion,
            "sobrecargada": self.sobrecargada, "tiempo": self.tiempo,
            "color": self.get_color_estado(), "estado": self.get_estado_texto(),
        }


def calcular_utilizacion(caudal_transportado: float, capacidad_maxima: float) -> float:
    """O_i(t) = Q_i(t) / Qmax_i x 100."""
    if capacidad_maxima <= 0:
        return 0.0
    return (caudal_transportado / capacidad_maxima) * 100.0


def calcular_utilizacion_todas_las_tuberias(grafo: Grafo, tiempo: float = 0.0) -> List[UtilizacionTuberia]:
    """
    Utilización de todas las tuberías con el caudal Q_i(t) vigente en cada una.
    Q_i(t) es el caudal demandado (puede superar Qmax); si solo se asignó
    ``caudal_transportado`` a mano, se toma el mayor de ambos.
    """
    resultados = []
    for t in grafo.obtener_todas_las_tuberias():
        q = max(t.caudal_demandado, t.caudal_transportado)
        pct = calcular_utilizacion(q, t.capacidad_maxima)
        resultados.append(UtilizacionTuberia(
            t.id_tuberia, t.nodo_origen, t.nodo_destino, q, t.capacidad_maxima,
            pct, pct > 100.0, tiempo))
    return resultados
