from typing import Any, Iterator, List, Optional, Tuple
from estructuras.lista_enlazada import ListaEnlazada


class TablaHash:

    FACTOR_MAXIMO = 0.75

    def __init__(self, capacidad_inicial: int = 11):
        if capacidad_inicial <= 0:
            raise ValueError("La capacidad inicial debe ser mayor a 0.")
        self._capacidad = capacidad_inicial
        self._cubetas = self._crear_cubetas(self._capacidad)
        self._tamano = 0

    @staticmethod
    def _crear_cubetas(cantidad: int) -> List[ListaEnlazada]:
        return [ListaEnlazada() for _ in range(cantidad)]

    @staticmethod
    def _normalizar(clave: Any) -> str:
        if clave is None:
            raise ValueError("La clave no puede ser nula.")
        cadena = str(clave).strip()
        if cadena == "":
            raise ValueError("La clave no puede ser vacía.")
        return cadena

    @staticmethod
    def _es_primo(n: int) -> bool:
        if n < 2:
            return False
        i = 2
        while i * i <= n:
            if n % i == 0:
                return False
            i += 1
        return True

    @classmethod
    def _siguiente_primo(cls, n: int) -> int:
        """Devuelve el menor número primo estrictamente mayor que n."""
        n += 1
        while not cls._es_primo(n):
            n += 1
        return n

    def _hash(self, clave: str) -> int:
        """Calcula el índice hash polinomico."""
        h = 0
        for caracter in clave:
            h = (h * 31 + ord(caracter)) % self._capacidad
        return h

    def _cubeta(self, clave: str) -> ListaEnlazada:
        """Devuelve la ListaEnlazada (cubeta) correspondiente a la clave."""
        return self._cubetas[self._hash(clave)]

    def _buscar_par(self, clave: str, cubeta: Optional[ListaEnlazada] = None) -> Optional[Tuple[str, Any]]:
        """Busca el par (clave, valor) en la cubeta correspondiente."""
        if cubeta is None:
            cubeta = self._cubeta(clave)
        return cubeta.buscar(lambda par: par[0] == clave)

    def _redimensionar(self) -> None:
        """Duplica la capacidad (al siguiente primo) y reubica todos los elementos (rehash)."""
        viejas = self._cubetas
        self._capacidad = self._siguiente_primo(self._capacidad * 2)
        self._cubetas = self._crear_cubetas(self._capacidad)
        for cubeta in viejas:
            for clave, valor in cubeta:
                self._cubeta(clave).agregar_al_final((clave, valor))


    def insertar(self, clave: Any, valor: Any) -> None:
        """
        Agrega un par (clave, valor). Lanza ValueError si la clave ya existe o es inválida."""
        clave_norm = self._normalizar(clave)
        cubeta = self._cubeta(clave_norm)
        if cubeta.buscar(lambda par: par[0] == clave_norm) is not None:
            raise ValueError(f"Clave duplicada: {clave!r}")
        cubeta.agregar_al_final((clave_norm, valor))
        self._tamano += 1
        if self.factor_carga() > self.FACTOR_MAXIMO:
            self._redimensionar()

    def actualizar(self, clave: Any, valor: Any) -> None:
        """
        Cambia el valor de una clave existente. Lanza KeyError si no existe."""
        clave_norm = self._normalizar(clave)
        cubeta = self._cubeta(clave_norm)
        if not cubeta.eliminar(lambda par: par[0] == clave_norm):
            raise KeyError(f"Clave no encontrada: {clave!r}")
        cubeta.agregar_al_final((clave_norm, valor))

    def buscar(self, clave: Any) -> Any:
        """Devuelve el valor asociado a la clave, o None si no existe o no es válida."""
        try:
            clave_norm = self._normalizar(clave)
        except ValueError:
            return None
        cubeta = self._cubeta(clave_norm)
        par = self._buscar_par(clave_norm, cubeta)
        return None if par is None else par[1]

    def contiene(self, clave: Any) -> bool:
        """Retorna True si la clave existe en la tabla, False en caso contrario."""
        try:
            clave_norm = self._normalizar(clave)
        except ValueError:
            return False
        return self._buscar_par(clave_norm) is not None

    def eliminar(self, clave: Any) -> bool:
        """Elimina la clave y su valor asociado. Devuelve True si existía, False si no."""
        try:
            clave_norm = self._normalizar(clave)
        except ValueError:
            return False
        cubeta = self._cubeta(clave_norm)
        if cubeta.eliminar(lambda par: par[0] == clave_norm):
            self._tamano -= 1
            return True
        return False

    def factor_carga(self) -> float:
        """Calcula y retorna el factor de carga actual (tamano / capacidad)."""
        return self._tamano / self._capacidad

    def items(self) -> Iterator[Tuple[str, Any]]:
        """Genera un iterador sobre todos los pares (clave, valor) almacenados."""
        for cubeta in self._cubetas:
            for par in cubeta:
                yield par

    def claves(self) -> List[str]:
        """Devuelve una lista con todas las claves almacenadas."""
        return [clave for clave, _ in self.items()]

    def valores(self) -> List[Any]:
        """Devuelve una lista con todos los valores almacenados."""
        return [valor for _, valor in self.items()]
    

    def __getitem__(self, clave: Any) -> Any:
        """
        Devuelve el valor asociado a la clave mediante tabla[clave].
        Lanza KeyError si la clave no existe o no es válida.
        """
        try:
            clave_norm = self._normalizar(clave)
        except ValueError:
            raise KeyError(f"Clave no encontrada: {clave!r}")
        cubeta = self._cubeta(clave_norm)
        par = self._buscar_par(clave_norm, cubeta)
        if par is None:
            raise KeyError(f"Clave no encontrada: {clave!r}")
        return par[1]

    def __setitem__(self, clave: Any, valor: Any) -> None:
        """
        Asigna un valor a la clave mediante tabla[clave].
        Si la clave ya existe, actualiza su valor.
        Si la clave no existe, la inserta."""
        clave_norm = self._normalizar(clave)
        cubeta = self._cubeta(clave_norm)
        existia = cubeta.eliminar(lambda par: par[0] == clave_norm)
        cubeta.agregar_al_final((clave_norm, valor))
        if not existia:
            self._tamano += 1
            if self.factor_carga() > self.FACTOR_MAXIMO:
                self._redimensionar()

    def __delitem__(self, clave: Any) -> None:
        """Elimina la clave mediante del tabla[clave]. Lanza KeyError si no existe."""
        try:
            clave_norm = self._normalizar(clave)
        except ValueError:
            raise KeyError(f"Clave no encontrada: {clave!r}")
        if not self.eliminar(clave_norm):
            raise KeyError(f"Clave no encontrada: {clave!r}")

    def __len__(self) -> int:
        return self._tamano

    def __contains__(self, clave: Any) -> bool:
        return self.contiene(clave)

    def __iter__(self) -> Iterator[str]:
        """Permite iterar sobre las claves de la tabla hash"""
        for clave, _ in self.items():
            yield clave

    def __repr__(self) -> str:
        return f"TablaHash(tamano={self._tamano}, capacidad={self._capacidad})"
