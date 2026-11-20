# estructuras/pila.py
from typing import Any, Iterator, Optional


class _Nodo:
    __slots__ = ("valor", "siguiente")

    def __init__(self, valor: Any, siguiente: Optional["_Nodo"] = None):
        self.valor = valor
        self.siguiente = siguiente


class Pila:

    def __init__(self):
        self._tope: Optional[_Nodo] = None
        self._tamano = 0

    def apilar(self, valor: Any) -> None:
        self._tope = _Nodo(valor, self._tope)
        self._tamano += 1

    def desapilar(self) -> Any:
        if self.esta_vacia():
            raise IndexError("No se puede desapilar de una pila vacía.")
        nodo = self._tope
        self._tope = nodo.siguiente
        self._tamano -= 1
        return nodo.valor

    def ver_tope(self) -> Any:
        if self.esta_vacia():
            raise IndexError("La pila está vacía.")
        return self._tope.valor

    def esta_vacia(self) -> bool:
        return self._tamano == 0

    def tamano(self) -> int:
        return self._tamano

    def limpiar(self) -> None:
        self._tope = None
        self._tamano = 0

    def __iter__(self) -> Iterator[Any]:
        actual = self._tope
        while actual is not None:
            yield actual.valor
            actual = actual.siguiente

    def __len__(self) -> int:
        return self._tamano

    def __repr__(self) -> str:
        return f"Pila({list(self)})"