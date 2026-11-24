from typing import Optional
import math

class Tuberia:
    def __init__(
        self,
        id_tuberia: str,
        nodo_origen: str,
        nodo_destino: str,
        longitud: float,
        diametro: float,
        pendiente: float,
        coeficiente_manning: float,
        capacidad_maxima: float
    ):

        if id_tuberia is None or str(id_tuberia).strip() == "":
            raise ValueError("El id de la tubería no puede ser nulo o vacío.")
        if nodo_origen is None or str(nodo_origen).strip() == "":
            raise ValueError("El nodo de origen no puede ser nulo o vacío.")
        if nodo_destino is None or str(nodo_destino).strip() == "":
            raise ValueError("El nodo de destino no puede ser nulo o vacío.")
        if longitud <= 0:
            raise ValueError("La longitud de la tubería no puede ser cero o negativa.")
        if diametro <= 0:
            raise ValueError("El diámetro de la tubería no puede ser cero o negativo.")
        if pendiente <= 0:
            raise ValueError("La pendiente de la tubería no puede ser cero o negativa.")
        if coeficiente_manning <= 0:
            raise ValueError("El coeficiente de Manning no puede ser cero o negativo.")
        if capacidad_maxima < 0:
            raise ValueError("La capacidad máxima de la tubería no puede ser negativa.")
        
        self.id_tuberia: str = str(id_tuberia).strip()
        self.nodo_origen: str = str(nodo_origen).strip()
        self.nodo_destino: str = str(nodo_destino).strip()
        self.longitud: float = float(longitud)                  
        self.diametro: float = float(diametro)                  
        self.pendiente: float = float(pendiente)                
        self.coeficiente_manning: float = float(coeficiente_manning)                
        self.capacidad_maxima: float = float(capacidad_maxima)

        # Calcula la velocidad de referencia usando la fórmula de Manning para flujo lleno.
        self.velocidad_referencia = self._velocidad_manning_llena()

        self.caudal_demandado: float = 0.0
        self.caudal_transportado: float = 0.0
        self.excseso: float = 0.0
        self.velocidad: float = 0.0
        self.porcentaje_utilizacion: float = 0.0
        self.sobrecargada: bool = False
        self.tiempo_transito: float = 0.0
    
        def _velocidad_manning_llena(self) -> float:
            radio_hidraulico = self.diametro / 4.0
            if self.pendiente <= 0:
                return 0.0
            return (1.0 / self.coeficiente_manning) * radio_hidraulico ** (2.0 / 3.0) * math.sqrt(self.pendiente)

    @property
    def tiempo_transito_referencia(self) -> float:
        # Tiempo de tránsito t_i = L_i / V_i en minutos (V_i = velocidad de referencia).
        if self.velocidad_referencia <= 0:
            return float("inf")
        return self.longitud / self.velocidad_referencia / 60.0    
        
    # Métodos para actualizar el estado de la tubería y obtener información sobre su utilización.
    def actualizar_estado(
        self,
        caudal: float,
        velocidad: Optional[float] = None,
        tiempo_transito: Optional[float] = None,
        caudal_transportado: Optional[float] = None,
    ) -> None:
        # Actualiza el estado de la tubería con los valores proporcionados.
        afluente = max(0.0, float(caudal))
        if caudal_transportado is None:
            transportado = min(afluente, self.capacidad_maxima)
        else:
            transportado = min(max(0.0, float(caudal_transportado)), self.capacidad_maxima)
        self.caudal_transportado = transportado
        self.caudal_demandado = max(afluente, transportado)
        self.exceso = max(0.0, self.caudal_demandado - self.capacidad_maxima)
        self.velocidad = self.velocidad_referencia if velocidad is None else max(0.0, float(velocidad))
        self.tiempo_transito = (
            self.tiempo_transito_referencia if tiempo_transito is None else max(0.0, float(tiempo_transito))
        )

        if self.capacidad_maxima > 0:
            self.porcentaje_utilizacion = self.caudal_demandado / self.capacidad_maxima * 100.0
        else:
            self.porcentaje_utilizacion = 0.0
        self.sobrecargada = self.porcentaje_utilizacion > 100.0
    # Método para reiniciar el estado de la tubería a valores iniciales.
    def reiniciar(self) -> None:
        self.caudal_demandado = 0.0
        self.caudal_transportado = 0.0
        self.exceso = 0.0
        self.velocidad = 0.0
        self.porcentaje_utilizacion = 0.0
        self.sobrecargada = False
        self.tiempo_transito = 0.0

    def es_critica(self, umbral: float = 100.0) -> bool:
        # True si la utilización alcanza o supera el umbral (por defecto 100 %).
        return self.porcentaje_utilizacion >= umbral

    def esta_sobrecargada(self) -> bool:
        # True si el caudal demandado supera estrictamente la capacidad máxima.
        return self.sobrecargada

    def __str__(self) -> str:
        return (
            f"Tuberia({self.id_tuberia}, {self.nodo_origen} -> {self.nodo_destino}, "
            f"Qmax={self.capacidad_maxima} m3/s, Uso={self.porcentaje_utilizacion:.1f}%)"
        )

    def __repr__(self) -> str:
        return (
            f"Tuberia(id={self.id_tuberia!r}, origen={self.nodo_origen!r}, "
            f"destino={self.nodo_destino!r}, L={self.longitud}, D={self.diametro})"
        )

    def __eq__(self, otro) -> bool:
        return isinstance(otro, Tuberia) and self.id_tuberia == otro.id_tuberia
    
    def __hash__(self) -> int:
        return hash(self.id_tuberia)

                