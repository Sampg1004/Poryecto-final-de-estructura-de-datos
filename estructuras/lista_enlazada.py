class NodoLista:

    def __init__(self, dato):
        self.dato = dato
        self.siguiente = None


class ListaEnlazada:

    def __init__(self):
        self.limpiar()

    def limpiar(self) -> None:
        self.cabeza = None
        self.cola = None
        self.tamano = 0

    def esta_vacia(self) -> bool:
        return self.tamano == 0

    def __len__(self) -> int:
        return self.tamano

    def agregar_al_inicio(self, dato) -> bool:
        nuevo = NodoLista(dato)
        if self.esta_vacia():
            self.cabeza = nuevo
            self.cola = nuevo
        else:
            nuevo.siguiente = self.cabeza
            self.cabeza = nuevo
        self.tamano += 1
        return True

    def agregar_al_final(self, dato) -> bool:
        nuevo = NodoLista(dato)
        if self.esta_vacia():
            self.cabeza = nuevo
        else:
            self.cola.siguiente = nuevo
        self.cola = nuevo
        self.tamano += 1
        return True

    def ver_primero(self):
        if self.esta_vacia():
            raise IndexError("La lista está vacía.")
        return self.cabeza.dato

    def ver_ultimo(self):
        if self.esta_vacia():
            raise IndexError("La lista está vacía.")
        return self.cola.dato

    def obtener(self, indice: int):
        if indice < 0 or indice >= self.tamano:
            raise IndexError(f"Índice fuera de rango: {indice}")
        actual = self.cabeza
        for _ in range(indice):
            actual = actual.siguiente
        return actual.dato

    def buscar(self, condicion):
        actual = self.cabeza
        while actual is not None:
            if condicion(actual.dato):
                return actual.dato
            actual = actual.siguiente
        return None

    def eliminar(self, condicion) -> bool:
        """Elimina el primer dato que cumpla condicion"""
        anterior = None
        actual = self.cabeza
        while actual is not None:
            if condicion(actual.dato):
                if anterior is None:             
                    self.cabeza = actual.siguiente
                else:
                    anterior.siguiente = actual.siguiente
                if actual is self.cola:          
                    self.cola = anterior
                self.tamano -= 1
                return True
            anterior = actual
            actual = actual.siguiente
        return False

    # recorre la lista y devuelve un iterador sobre los datos como si fuera un ciclo for
    def __iter__(self):
        actual = self.cabeza
        while actual is not None:
            yield actual.dato
            actual = actual.siguiente