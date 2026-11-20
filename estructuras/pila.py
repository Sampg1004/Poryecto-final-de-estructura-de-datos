from typing import Any, Optional, Iterator


class Pila:

    def __init__(self):
        self._elementos: list = []

    def apilar(self, valor: Any) -> None:
        self._elementos.append(valor)

    def desapilar(self) -> Any:
        if self.esta_vacia():
            raise IndexError("No se puede desapilar de una pila vacía.")
        return self._elementos.pop()

    def ver_tope(self) -> Any:
        if self.esta_vacia():
            raise IndexError("La pila está vacía.")
        return self._elementos[-1]

    def esta_vacia(self) -> bool:
        return len(self._elementos) == 0

    def tamano(self) -> int:
        return len(self._elementos)

    def limpiar(self) -> None:
        self._elementos.clear()

    def __iter__(self) -> Iterator[Any]:
        return iter(reversed(self._elementos))

    def __len__(self) -> int:
        return self.tamano()

    def __repr__(self) -> str:
        return f"Pila({list(self)})"
