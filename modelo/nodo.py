
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
        raise ValueError(f"Tipo de nodo no válido: {tipo!r}")

    @property
    def tipo(self) -> str:
        return self._tipo

    @tipo.setter
    def tipo(self, valor: str):
        self._tipo = self._sinonimo(valor)

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
        
        area_drenaje = float(area_drenaje)
        coef_escorrentia = float(coef_escorrentia)
        caudal_sanitario = float(caudal_sanitario)
        capacidad_almacenamiento = float(capacidad_almacenamiento)
        # Validaciones de entrada
        if id_nodo is None or str(id_nodo).strip() == "":
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
        self.id_nodo = str(id_nodo).strip()
        self.tipo = tipo
        self.x = x
        self.y = y
        self.area_drenaje = area_drenaje
        self.coef_escorrentia = coef_escorrentia
        self.caudal_sanitario = caudal_sanitario
        self.capacidad_almacenamiento = capacidad_almacenamiento

        self.tuberias_entrantes: List = []
        self.tuberias_salientes: List = []
        self.caudal_lluvia = 0.0
        self.caudal_tuberias_entrantes = 0.0
        self.caudal_total_entrada = 0.0
        self.caudal_salida = 0.0
        self.volumen_almacenado = 0.0
        self.sobrecargado = False

    @property
    def es_fuente(self) -> bool:
        return self.tipo == self.TIPO_FUENTE

    @property
    def es_sumidero(self) -> bool:
        return self.tipo == self.TIPO_SUMIDERO

    @property
    def es_pozo(self) -> bool:
        return self.tipo == self.TIPO_POZO

    
    def agregar_tuberia_saliente(self, tuberia) -> None:
        if tuberia not in self.tuberias_salientes:
            self.tuberias_salientes.append(tuberia)

    def agregar_tuberia_entrante(self, tuberia) -> None:
        if tuberia not in self.tuberias_entrantes:
            self.tuberias_entrantes.append(tuberia)
    
    def obtener_vecinos(self) -> List[str]:
        vecinos = []
        for tuberia in self.tuberias_salientes:
            if tuberia.nodo_destino not in vecinos:
                vecinos.append(tuberia.nodo_destino)
        return vecinos

    @property
    def grado_entrada(self) -> int:
        return len(self.tuberias_entrantes)

    @property
    def grado_salida(self) -> int:
        return len(self.tuberias_salientes)
    
    def calcular_caudal_lluvia(self, intensidad_mm_h: float) -> float:
        intensidad_mm_h = float(intensidad_mm_h)
        if intensidad_mm_h < 0:
            raise ValueError("La intensidad de lluvia no puede ser negativa.")
        self.caudal_lluvia = (
            0.00278 * self.coef_escorrentia * intensidad_mm_h * self.area_drenaje
        )
        return self.caudal_lluvia
    
    def actualizar_caudal_total_entrada(self, caudal_de_tuberias: float = 0.0) -> float:
        self.caudal_tuberias_entrantes = max(0.0, float(caudal_de_tuberias))
        self.caudal_total_entrada = (
            self.caudal_lluvia + self.caudal_sanitario + self.caudal_tuberias_entrantes
        )
        return self.caudal_total_entrada
    
    def reiniciar_simulacion(self) -> None:
        self.caudal_lluvia = 0.0
        self.caudal_tuberias_entrantes = 0.0
        self.caudal_total_entrada = 0.0
        self.caudal_salida = 0.0
        self.volumen_almacenado = 0.0
        self.sobrecargado = False

    def __str__(self) -> str:
        return f"Nodo({self.id_nodo}, {self.tipo})"

    def __repr__(self) -> str:
        return (
            f"Nodo(id={self.id_nodo!r}, tipo={self.tipo!r}, "
            f"A={self.area_drenaje}ha, C={self.coef_escorrentia})"
        )

    def __eq__(self, otro) -> bool:
        return isinstance(otro, Nodo) and self.id_nodo == otro.id_nodo

    def __hash__(self) -> int:
        return hash(self.id_nodo)