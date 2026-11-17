"""
Módulo: modelo.nodo
Descripción: Representa un nodo (vértice) en el grafo dirigido de la red de alcantarillado
de Ciudad Bicentenario.

Un Nodo corresponde a una de las siguientes entidades de la infraestructura:
- FUENTE (Source): Alcantarilla receptora donde ingresa la escorrentía pluvial de la cuenca.
- INTERMEDIO (Manhole): Pozo de inspección para convergencia, inspección y tránsito de flujo.
- SUMIDERO (Sink): Punto de entrega o descarga final del sistema (ej. PTAR de Punta Canoa).

Diseñado con rigor de ingeniería de software: validaciones tempranas (fail-fast), contrato
formal de conexiones para recorridos (BFS/DFS), soporte para balance de masa y conservación de caudales.
"""

from typing import List, Optional, Any

# Constantes canónicas para tipos de nodo
FUENTE = "FUENTE"          # Punto de entrada de escorrentía pluvial (S / Source)
SUMIDERO = "SUMIDERO"      # Punto de descarga final (T / Sink / PTAR Punta Canoa)
INTERMEDIO = "INTERMEDIO"  # Pozo de inspección ordinario (Manhole)


class Nodo:
    """
    Vértice de la red de alcantarillado.
    
    Almacena los atributos físicos e hidrológicos del pozo/alcantarilla,
    su lista de adyacencia local (tuberías entrantes y salientes) y las
    variables de estado dinámicas durante la simulación temporal.
    """

    def __init__(
        self,
        id_nodo: Any,
        tipo: str = INTERMEDIO,
        x: Optional[float] = None,
        y: Optional[float] = None,
        area_ha: float = 0.0,
        coef_escorrentia: float = 0.0,
        caudal_sanitario: float = 0.0
    ):
        """
        Inicializa y valida un nodo de la red.

        :param id_nodo: Identificador único (str o int no vacío), ej. "1", "Q", "31".
        :param tipo: Tipo de nodo ("FUENTE", "SUMIDERO", "INTERMEDIO" o sinónimos válidos del dataset).
        :param x: Coordenada cartesiana X para visualización en GUI (None si no está disponible).
        :param y: Coordenada cartesiana Y para visualización en GUI (None si no está disponible).
        :param area_ha: Área de la cuenca de drenaje tributaria en hectáreas (ha >= 0).
        :param coef_escorrentia: Coeficiente C del método racional (0.0 <= C <= 1.0).
        :param caudal_sanitario: Caudal base en tiempo seco en m³/s (opcional, >= 0).
        :raises ValueError: Si algún parámetro de entrada no cumple con el dominio válido.
        """
        # 1. Validación de identificador único
        if id_nodo is None or str(id_nodo).strip() == "":
            raise ValueError("El nodo requiere un identificador no vacío.")
        self.id = str(id_nodo).strip()

        # 2. Validación y normalización estricta del tipo de nodo
        self.tipo = self._validar_y_normalizar_tipo(tipo)

        # 3. Validación de parámetros hidrológicos (Método Racional: Q = 0.00278 * C * I * A)
        if area_ha < 0:
            raise ValueError(f"El área de drenaje no puede ser negativa (recibido: {area_ha}).")
        if not (0.0 <= coef_escorrentia <= 1.0):
            raise ValueError(
                f"El coeficiente de escorrentía C debe estar en el rango [0.0, 1.0] (recibido: {coef_escorrentia})."
            )
        if caudal_sanitario < 0:
            raise ValueError(f"El caudal sanitario no puede ser negativo (recibido: {caudal_sanitario}).")

        self.area_ha = float(area_ha)
        self.coef_escorrentia = float(coef_escorrentia)
        self.caudal_sanitario = float(caudal_sanitario)

        # 4. Coordenadas para interfaz gráfica (None indica sin coordenadas / layout automático)
        self.x = float(x) if x is not None else None
        self.y = float(y) if y is not None else None

        # 5. Lista de adyacencia local (Conexiones del grafo dirigido)
        self.salidas: List[Any] = []   # Tuberías que parten de este nodo (aristas u -> v)
        self.entradas: List[Any] = []  # Tuberías que descargan en este nodo (aristas v -> u)

        # 6. Variables de estado dinámicas durante la simulación temporal
        self.caudal_lluvia_actual: float = 0.0    # Caudal pluvial generado por lluvia (m³/s)
        self.caudal_entradas_actual: float = 0.0  # Caudal recibido desde tuberías aguas arriba (m³/s)
        self.caudal_total_entrada: float = 0.0    # Balance total de entrada: lluvia + sanitario + tuberías (m³/s)
        self.caudal_salida_actual: float = 0.0    # Caudal evacuado hacia tuberías aguas abajo (m³/s)
        self.volumen_almacenado: float = 0.0      # Agua acumulada temporalmente en pozo por sobrecarga (m³)
        self.sobrecargado: bool = False           # Bandera indicadora de sobrecarga o inundación

    @staticmethod
    def _validar_y_normalizar_tipo(tipo: Any) -> str:
        """
        Valida que el tipo sea conocido y lo normaliza a las constantes canónicas.
        Rechaza explícitamente valores desconocidos para evitar errores silenciosos en la carga de archivos.
        """
        if tipo is None:
            raise ValueError("El tipo de nodo no puede ser nulo.")

        t = str(tipo).strip().upper()

        if t in (FUENTE, "SOURCE", "S", "ALCANTARILLA"):
            return FUENTE
        if t in (SUMIDERO, "SINK", "T", "PTAR", "DESCARGA"):
            return SUMIDERO
        if t in (INTERMEDIO, "POZO", "MANHOLE", "INSPECCION"):
            return INTERMEDIO

        raise ValueError(
            f"Tipo de nodo desconocido: '{tipo}'. "
            f"Valores permitidos: '{FUENTE}' (o 'SOURCE'/'S'), "
            f"'{SUMIDERO}' (o 'SINK'/'T'), '{INTERMEDIO}' (o 'POZO'/'MANHOLE')."
        )

    # =========================================================================
    # Consultas de tipo y grado
    # =========================================================================

    def es_fuente(self) -> bool:
        """Indica si el nodo es un punto de entrada de escorrentía (Source)."""
        return self.tipo == FUENTE

    def es_sumidero(self) -> bool:
        """Indica si el nodo es un punto de descarga final (Sink / PTAR)."""
        return self.tipo == SUMIDERO

    def es_intermedio(self) -> bool:
        """Indica si el nodo es un pozo de inspección intermedio (Manhole)."""
        return self.tipo == INTERMEDIO

    def grado_salida(self) -> int:
        """Número de tuberías que salen de este nodo."""
        return len(self.salidas)

    def grado_entrada(self) -> int:
        """Número de tuberías que descargan en este nodo."""
        return len(self.entradas)

    # =========================================================================
    # Manejo de adyacencias (Topología del Grafo)
    # =========================================================================

    def agregar_salida(self, tuberia: Any) -> None:
        """
        Registra una tubería que tiene como origen este nodo.
        Previene duplicados en caso de lecturas repetidas de aristas.
        """
        if tuberia not in self.salidas:
            self.salidas.append(tuberia)

    def agregar_entrada(self, tuberia: Any) -> None:
        """
        Registra una tubería que tiene como destino este nodo.
        Previene duplicados en caso de lecturas repetidas de aristas.
        """
        if tuberia not in self.entradas:
            self.entradas.append(tuberia)

    def vecinos(self) -> List[Any]:
        """
        Retorna los nodos destino alcanzables directamente desde este nodo (para BFS y DFS).
        Contrato formal: el objeto Tuberia debe definir el atributo `destino` (instancia de Nodo).
        """
        return [t.destino for t in self.salidas]

    # =========================================================================
    # Dinámica Hidrológica y Simulación Temporal
    # =========================================================================

    def caudal_lluvia(self, intensidad_mm_h: float) -> float:
        """
        Estima y guarda el caudal de escorrentía generado por precipitación según el Método Racional:
            Q = 0.00278 * C * I * A  (m³/s)

        :param intensidad_mm_h: Intensidad de lluvia I en mm/h.
        :return: Caudal de escorrentía en m³/s.
        """
        if intensidad_mm_h < 0:
            raise ValueError(f"La intensidad de lluvia no puede ser negativa (recibido: {intensidad_mm_h}).")

        self.caudal_lluvia_actual = 0.00278 * self.coef_escorrentia * float(intensidad_mm_h) * self.area_ha
        return self.caudal_lluvia_actual

    def actualizar_balance_caudales(self, caudal_entradas_tuberias: float = 0.0) -> float:
        """
        Actualiza el balance de masa de caudales que ingresan al pozo en el instante actual:
            Q_total = Q_lluvia + Q_sanitario + Q_entradas_tuberias

        :param caudal_entradas_tuberias: Caudal total recibido de tuberías que descargan en el nodo (m³/s).
        :return: Caudal total de entrada en m³/s.
        """
        if caudal_entradas_tuberias < 0:
            raise ValueError("El caudal recibido de tuberías no puede ser negativo.")

        self.caudal_entradas_actual = float(caudal_entradas_tuberias)
        self.caudal_total_entrada = (
            self.caudal_lluvia_actual + self.caudal_sanitario + self.caudal_entradas_actual
        )
        return self.caudal_total_entrada

    @property
    def caudal_acumulado(self) -> float:
        """Propiedad de conveniencia para consultar el caudal total que confluye en el pozo (m³/s)."""
        return self.caudal_total_entrada

    @caudal_acumulado.setter
    def caudal_acumulado(self, valor: float) -> None:
        self.caudal_total_entrada = max(0.0, float(valor))

    def reiniciar(self) -> None:
        """Restablece los estados dinámicos del nodo al inicio de una simulación."""
        self.caudal_lluvia_actual = 0.0
        self.caudal_entradas_actual = 0.0
        self.caudal_total_entrada = 0.0
        self.caudal_salida_actual = 0.0
        self.volumen_almacenado = 0.0
        self.sobrecargado = False

    # =========================================================================
    # Métodos especiales (Representación y Hash)
    # =========================================================================

    def __repr__(self) -> str:
        coords = f"({self.x}, {self.y})" if (self.x is not None and self.y is not None) else "sin coords"
        return (
            f"Nodo(id={self.id!r}, tipo={self.tipo!r}, coords={coords}, "
            f"entradas={self.grado_entrada()}, salidas={self.grado_salida()})"
        )

    def __str__(self) -> str:
        return f"Nodo '{self.id}' ({self.tipo})"

    def __eq__(self, otro: Any) -> bool:
        """Permite comparar nodos por su identificador único (con otro Nodo o directamente con un str)."""
        if isinstance(otro, Nodo):
            return self.id == otro.id
        if isinstance(otro, str):
            return self.id == otro
        return False

    def __hash__(self) -> int:
        """Permite usar el nodo como clave en tablas hash, diccionarios o conjuntos."""
        return hash(self.id)
