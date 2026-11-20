from typing import Optional

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

        self.velocidad_referencia = self._velocidad_manning_llena()

        self.caudal_demandado: float = 0.0
        self.caudal_transportado: float = 0.0
        self.excseso: float = 0.0
        self.velocidad: float = 0.0
        self.porcentaje_utilizacion: float = 0.0
        self.sobrecargada: bool = False
        self.tiempo_transito: float = 0.0

