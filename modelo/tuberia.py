class Tuberia:


    def __init__(
        self,
        id_tuberia: str,
        nodo_origen: str,
        nodo_destino: str,
        longitud: float,
        diametro: float,
        pendiente: float,
        rugosidad: float,
        capacidad_maxima: float
    )-> None:
        self.id_tuberia: str = str(id_tuberia)
        self.nodo_origen: str = str(nodo_origen)
        self.nodo_destino: str = str(nodo_destino)
        self.longitud: float = float(longitud)                  
        self.diametro: float = float(diametro)                  
        self.pendiente: float = float(pendiente)                
        self.rugosidad: float = float(rugosidad)                
        self.capacidad_maxima: float = float(capacidad_maxima) 
