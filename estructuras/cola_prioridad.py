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

    def insertar(self, valor: Any, prioridad: float) -> None:
         # Inserta un valor. Menor prioridad = sale primero (O(log n)).
         self._heap.append((prioridad, self._contador, valor))
         self._contador += 1
         self._subir(len(self._heap) - 1)
 
    def extraer_minimo(self) -> Tuple[float, Any]:
         # Retira y retorna (prioridad, valor) del elemento con menor prioridad (O(log n)).
         if self.esta_vacia():
             raise IndexError("No se puede extraer de una cola de prioridad vacía.")
         heap = self._heap
         raiz = heap[0]
         ultimo = heap.pop()
         if heap:                      # si quedan elementos, el último pasa a la raíz y baja
             heap[0] = ultimo
             self._bajar(0)
         return raiz[0], raiz[2]
 
    def ver_minimo(self) -> Tuple[float, Any]:
         # Retorna (prioridad, valor) del menor sin retirarlo (O(1)).
         if self.esta_vacia():
             raise IndexError("La cola de prioridad está vacía.")
         return self._heap[0][0], self._heap[0][2]
 
    def esta_vacia(self) -> bool:
         return len(self._heap) == 0
 
    def tamano(self) -> int:
         return len(self._heap)
 
    def limpiar(self) -> None:
         self._heap.clear()
         self._contador = 0
 
    def __len__(self) -> int:
         return self.tamano()
 
    def __repr__(self) -> str:
         return f"ColaPrioridad(tamano={self.tamano()})"