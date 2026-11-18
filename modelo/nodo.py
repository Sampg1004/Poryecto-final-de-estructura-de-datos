
from typing import List, Optional


class Nodo:
    TIPO_FUENTE = "FUENTE"
    TIPO_POZO = "POZO"
    TIPO_SUMIDERO = "SUMIDERO"
    _SINONIMOS_FUENTE = ("FUENTE", "SOURCE", "S")
    _SINONIMOS_POZO = ("POZO", "MANHOLE", "INTERMEDIO")
    _SINONIMOS_SUMIDERO = ("SUMIDERO", "SINK", "T")

    @classmethod
    def _sinonimo(cls, tipo: str) -> str:
        t = str(tipo).strip().upper()
        if t in cls._SINONIMOS_FUENTE:
            return cls.TIPO_FUENTE
        if t in cls._SINONIMOS_POZO:
            return cls.TIPO_POZO
        if t in cls._SINONIMOS_SUMIDERO:
            return cls.TIPO_SUMIDERO
        raise ValueError("Tipo de nodo no válido.")

    @property
    def tipo(self) -> str:
        return self._tipo

    @tipo.setter
    def tipo(self, valor: str):
        self._tipo = self._sinonimo(valor)

    # Representa un nodo en un sistema de drenaje o alcantarillado.
    def __init__(
        self,
        id_nodo: str,
        tipo: str = "pozo",
        x: Optional[float] = None,
        y: Optional[float] = None,
        area_drenaje: float = 0.0,
        coef_escorrentia: float = 0.0,
        caudal_sanitario: float = 0.0,
        capacidad_almacenamiento: float = 0.0,
    ):
        # Validaciones de entrada
        if id_nodo is None or id_nodo == "":
            raise ValueError("El id del nodo no puede ser nulo o vacío.")
        if area_drenaje < 0:
            raise ValueError("El área de drenaje no puede ser negativa.")
        if coef_escorrentia < 0 or coef_escorrentia > 1:
            raise ValueError("El coeficiente de escorrentía debe estar entre 0 y 1.")
        if caudal_sanitario < 0:
            raise ValueError("El caudal sanitario no puede ser negativo.")
        if capacidad_almacenamiento < 0:
            raise ValueError("La capacidad de almacenamiento no puede ser negativa.")
        
        # Asignación de atributos
        self.id_nodo = id_nodo
        self.tipo = tipo
        self.x = x
        self.y = y
        self.area_drenaje = area_drenaje
        self.coef_escorrentia = coef_escorrentia
        self.caudal_sanitario = caudal_sanitario
        self.capacidad_almacenamiento = capacidad_almacenamiento

        self.tuberias_entrantes: List[str] = []
        self.tuberias_salientes: List[str] = []
        
    