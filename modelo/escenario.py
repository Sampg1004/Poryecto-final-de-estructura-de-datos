from typing import List, Optional, Dict
from dataclasses import dataclass, field

@dataclass
class EscenarioLluvia:

    nombre: str
    intensidad_mm_h: float
    duracion_min: float
    descripcion: str = ""

    def __post_init__(self):
        if self.intensidad_mm_h < 0:
            raise ValueError("La intensidad de lluvia no puede ser negativa.")
        if self.duracion_min <= 0:
            raise ValueError("La duración debe ser mayor a cero.")

    def caudal_por_area(
        self,
        area_drenaje_ha: float,
        coef_escorrentia: float,
    ) -> float:
        return 0.00278 * coef_escorrentia * self.intensidad_mm_h * area_drenaje_ha

    def __str__(self) -> str:
        return (
            f"Escenario({self.nombre}, I={self.intensidad_mm_h} mm/h, "
            f"dur={self.duracion_min} min)"
        )

class GestorEscenarios:

    def __init__(self):
        self.escenarios: Dict[str, EscenarioLluvia] = {}
        self.escenario_activo: Optional[EscenarioLluvia] = None

    def agregar_escenario(self, escenario: EscenarioLluvia) -> None:
        if not isinstance(escenario, EscenarioLluvia):
            raise TypeError("Se esperaba una instancia de EscenarioLluvia.")
        if escenario.nombre in self.escenarios:
            raise ValueError(
                f"Ya existe un escenario con nombre '{escenario.nombre}'."
            )
        self.escenarios[escenario.nombre] = escenario

    def obtener_escenario(self, nombre: str) -> Optional[EscenarioLluvia]:
        return self.escenarios.get(nombre)

    def existe_escenario(self, nombre: str) -> bool:
        return nombre in self.escenarios

    def listar_escenarios(self) -> List[str]:
        return list(self.escenarios.keys())

    def seleccionar_escenario(self, nombre: str) -> bool:
        escenario = self.obtener_escenario(nombre)
        if escenario is None:
            return False
        self.escenario_activo = escenario
        return True

    def obtener_activo(self) -> Optional[EscenarioLluvia]:
        return self.escenario_activo

    def cantidad(self) -> int:
        return len(self.escenarios)