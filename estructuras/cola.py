from typing import Any, Iterator, Optional

class _Nodo:

    __slots__ = ("valor", "siguiente")

    def __init__(self, valor: Any):
        self.valor = valor
        self.siguiente: Optional["_Nodo"] = None


class Cola:

    def __init__(self):
        self._frente: Optional[_Nodo] = None
        self._final: Optional[_Nodo] = None
        self._tamano = 0

    def encolar(self, valor: Any) -> None:
        nuevo = _Nodo(valor)
        if self._final is None:         
            self._frente = nuevo
        else:
            self._final.siguiente = nuevo
        self._final = nuevo
        self._tamano += 1

    def desencolar(self) -> Any:
        if self.esta_vacia():
            raise IndexError("No se puede desencolar de una cola vacía.")
        nodo = self._frente
        self._frente = nodo.siguiente
        if self._frente is None:        
            self._final = None
        self._tamano -= 1
        return nodo.valor

    def ver_frente(self) -> Any:

        if self.esta_vacia():
            raise IndexError("La cola está vacía.")
        return self._frente.valor

    def esta_vacia(self) -> bool:
        return self._tamano == 0

    def tamano(self) -> int:
        return self._tamano

    def limpiar(self) -> None:
        self._frente = None
        self._final = None
        self._tamano = 0

    def __iter__(self) -> Iterator[Any]:
        actual = self._frente
        while actual is not None:
            yield actual.valor
            actual = actual.siguiente

    def __len__(self) -> int:
        return self._tamano

    def __repr__(self) -> str:
        return f"Cola({list(self)})"