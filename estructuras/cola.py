from typing import Any, Optional, Iterator
from collections import deque


class Cola:

    def __init__(self):
        self._elementos: deque = deque()

    def encolar(self, valor: Any) -> None:
        self._elementos.append(valor)

    def desencolar(self) -> Any:
        if self.esta_vacia():
            raise IndexError("No se puede desencolar de una cola vacía.")
        return self._elementos.popleft()

    def ver_frente(self) -> Any:
        if self.esta_vacia():
            raise IndexError("La cola está vacía.")
        return self._elementos[0]

    def esta_vacia(self) -> bool:
        return len(self._elementos) == 0

    def tamano(self) -> int:
        return len(self._elementos)

    def limpiar(self) -> None:
        self._elementos.clear()

    def __iter__(self) -> Iterator[Any]:
        return iter(self._elementos)

    def __len__(self) -> int:
        return self.tamano()

    def __repr__(self) -> str:
        return f"Cola({list(self)})"
