from typing import Any, List, Tuple

class ColaPrioridad:
 
    def __init__(self):
        self._heap: List[Tuple[float, int, Any]] = []
        self._contador: int = 0

    @staticmethod
    def _menor(a: Tuple[float, int, Any], b: Tuple[float, int, Any]) -> bool:
        # Devuelve True si a < b según la prioridad y el contador.
        return a[0] < b[0] or (a[0] == b[0] and a[1] < b[1])
    
    def _subir(self, i: int) -> None:
        # Sube el elemento en la posición i hasta que se cumpla la propiedad de montículo.
        while i > 0:
            padre = (i - 1) // 2
            if self._menor(self._heap[i], self._heap[padre]):
                self._heap[i], self._heap[padre] = self._heap[padre], self._heap[i]
                i = padre
            else:
                break

    def _bajar(self, i: int) -> None:
        # Baja el elemento en la posición i hasta que se cumpla la propiedad de montículo.
        n = len(self._heap)
        while True:
            hijo_izq = 2 * i + 1
            hijo_der = 2 * i + 2
            menor = i

            if hijo_izq < n and self._menor(self._heap[hijo_izq], self._heap[menor]):
                menor = hijo_izq
            if hijo_der < n and self._menor(self._heap[hijo_der], self._heap[menor]):
                menor = hijo_der

            if menor == i:
                break

            self._heap[i], self._heap[menor] = self._heap[menor], self._heap[i]
            i = menor

 