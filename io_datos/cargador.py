"""
Carga de los datos suministrados por el docente (RF01) y construcción del grafo (RF02).

Fuentes admitidas:
  - DataSetBicentenario.xlsx (hojas Source(s), Sink(s), Pipe(s), Drainage Basin,
    Precipitation Scenarios), o
  - una carpeta con los CSV equivalentes (Sources.csv, Sinks.csv, Pipes.csv,
    Drainage_Basin.csv, Precipitation_Scenarios.csv).

Validaciones: hojas/columnas obligatorias, tuberías duplicadas, nodos sin
conexión, valores no numéricos o fuera de rango, coherencia de Qmax con Manning
y red acíclica. Las filas de totales o notas del final de la hoja de tuberías
se ignoran con una advertencia.
"""
import csv
import math
import os
import re
from typing import Any, Dict, List, Optional, Tuple

from modelo.nodo import Nodo
from modelo.tuberia import Tuberia
from modelo.grafo import Grafo
from modelo.escenario import EscenarioLluvia, GestorEscenarios
from io_datos.layout_anexo2 import COORDENADAS_ANEXO_2

try:
    import openpyxl
    HAY_OPENPYXL = True
except ImportError:  # pragma: no cover
    HAY_OPENPYXL = False


class ErrorCargaDatos(Exception):
    """Error de validación al cargar los archivos del docente."""


# Nombre lógico -> (prefijo aceptado en el nombre de la hoja, archivo CSV)
HOJAS = {
    "fuentes": ("source", "Sources.csv"),
    "sumideros": ("sink", "Sinks.csv"),
    "tuberias": ("pipe", "Pipes.csv"),
    "cuenca": ("drainage", "Drainage_Basin.csv"),
    "escenarios": ("precip", "Precipitation_Scenarios.csv"),
}

ARCHIVO_COORDENADAS = "Coordenadas_Anexo2.csv"

# Alias de columnas (en minúsculas) de la hoja Pipe(s)
ALIAS = {
    "origen": ["from(i)", "from", "origen", "nodo_inicial"],
    "destino": ["to(i)", "to", "destino", "nodo_final"],
    "id": ["pipe", "id", "id_tuberia", "identificador"],
    "longitud": ["lenght (m)", "length (m)", "longitud (m)", "longitud"],
    "diam_m": ["⌀ (m)", "diameter (m)", "diametro (m)", "diámetro (m)", "d (m)"],
    "diam_in": ["⌀ (in)", "diameter (in)", "diametro (in)"],
    "manning": ["n", "manning"],
    "pendiente": ["s", "slope", "pendiente"],
    "qmax": ["q", "qmax", "capacidad", "capacidad_maxima"],
}


def _id(valor: Any) -> Optional[str]:
    """Normaliza un identificador de nodo/tubería a texto (1.0 -> '1')."""
    if valor is None:
        return None
    if isinstance(valor, float) and valor.is_integer():
        return str(int(valor))
    texto = str(valor).strip()
    if texto.endswith(".0") and texto[:-2].isdigit():
        texto = texto[:-2]
    return texto or None


def _num(valor: Any) -> Optional[float]:
    if valor is None or (isinstance(valor, str) and valor.strip() == ""):
        return None
    if isinstance(valor, (int, float)):
        return float(valor)
    try:
        return float(str(valor).strip().replace(",", "."))
    except ValueError:
        return None


class CargadorDatos:
    """Lee los datos del docente y construye el grafo y los escenarios."""

    def __init__(
        self,
        ruta: str,
        carpeta_csv: Optional[str] = None,
        duracion_lluvia_min: float = 60.0,
        factor_area: float = 1.0,
        areas_fuentes: Optional[Dict[str, float]] = None,
    ):
        """
        Args:
            ruta: archivo .xlsx o carpeta con los CSV.
            carpeta_csv: si se indica, se exportan allí las hojas del Excel a CSV.
            duracion_lluvia_min: duración del evento de lluvia (la guía no la
                incluye en el dataset: "será establecida por el docente").
            factor_area: factor de escala multiplicador del área total de drenaje.
            areas_fuentes: diccionario opcional {id_fuente: area_ha} para asignar
                áreas de drenaje personalizadas por alcantarilla.
        """
        if factor_area <= 0:
            raise ValueError("El factor de área debe ser mayor que cero.")
        self.ruta = ruta
        self.carpeta_csv = carpeta_csv
        self.duracion_lluvia_min = float(duracion_lluvia_min)
        self.factor_area = float(factor_area)
        self.areas_fuentes = areas_fuentes
        self.grafo = Grafo()
        self.gestor_escenarios = GestorEscenarios()
        self.advertencias: List[str] = []
        self.datos_crudos: Dict[str, List[Tuple]] = {}
        self.coef_escorrentia: float = 0.0
        self.area_total_ha: float = 0.0

    # ------------------------------------------------------------------
    # Lectura cruda (Excel o CSV)
    # ------------------------------------------------------------------
    def _es_carpeta(self) -> bool:
        return os.path.isdir(self.ruta)

    def _leer_crudo(self) -> None:
        if not os.path.exists(self.ruta):
            raise ErrorCargaDatos(f"No existe el archivo o carpeta de datos: {self.ruta}")
        if self._es_carpeta():
            for logico, (_, archivo) in HOJAS.items():
                ruta_csv = os.path.join(self.ruta, archivo)
                if not os.path.exists(ruta_csv):
                    self.datos_crudos[logico] = []
                    continue
                with open(ruta_csv, newline="", encoding="utf-8") as f:
                    self.datos_crudos[logico] = [tuple(fila) for fila in csv.reader(f)]
            return
        if not HAY_OPENPYXL:
            raise ErrorCargaDatos("Para leer el Excel se requiere 'openpyxl' (pip install openpyxl).")
        try:
            libro = openpyxl.load_workbook(self.ruta, data_only=True, read_only=True)
        except Exception as e:  # archivo corrupto o formato inválido
            raise ErrorCargaDatos(f"No se pudo abrir el Excel '{self.ruta}': {e}")
        for logico, (prefijo, _) in HOJAS.items():
            self.datos_crudos[logico] = []
            for nombre in libro.sheetnames:
                if nombre.strip().lower().startswith(prefijo):
                    self.datos_crudos[logico] = [tuple(f) for f in libro[nombre].iter_rows(values_only=True)]
                    break
        libro.close()

    def exportar_csv(self, carpeta: Optional[str] = None) -> List[str]:
        """Exporta las hojas leídas a CSV (la guía pide archivos de entrada en CSV)."""
        destino = carpeta or self.carpeta_csv
        if not destino:
            return []
        os.makedirs(destino, exist_ok=True)
        escritos = []
        for logico, (_, archivo) in HOJAS.items():
            filas = self.datos_crudos.get(logico) or []
            if not filas:
                continue
            ruta_csv = os.path.join(destino, archivo)
            with open(ruta_csv, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                for fila in filas:
                    w.writerow(["" if v is None else v for v in fila])
            escritos.append(ruta_csv)
        return escritos

    def _registros(self, logico: str) -> List[Dict[str, Any]]:
        """Primera fila no vacía = cabecera; el resto, diccionarios con claves en minúsculas."""
        filas = [f for f in self.datos_crudos.get(logico, []) if any(v not in (None, "") for v in f)]
        if not filas:
            return []
        cab = [str(c).strip().lower() if c not in (None, "") else None for c in filas[0]]
        registros = []
        for fila in filas[1:]:
            reg = {}
            for i, valor in enumerate(fila):
                if i < len(cab) and cab[i] is not None:
                    reg[cab[i]] = valor
            registros.append(reg)
        return registros

    @staticmethod
    def _col(reg: Dict[str, Any], alias: List[str]) -> Any:
        for a in alias:
            if a in reg:
                return reg[a]
        return None

    @staticmethod
    def _tiene_col(reg: Dict[str, Any], alias: List[str]) -> bool:
        return any(a in reg for a in alias)

    # ------------------------------------------------------------------
    # Construcción
    # ------------------------------------------------------------------
    def cargar_todo(self) -> Tuple[Grafo, GestorEscenarios]:
        self._leer_crudo()
        if self.carpeta_csv and not self._es_carpeta():
            self.exportar_csv()

        ids_fuentes = self._leer_ids_nodos("fuentes", obligatoria=True)
        ids_sumideros = self._leer_ids_nodos("sumideros", obligatoria=True)
        self._cargar_tuberias(ids_fuentes, ids_sumideros)
        self._asignar_cuenca(ids_fuentes)
        self._cargar_escenarios()
        self._cargar_coordenadas()
        self._validar_red()
        return self.grafo, self.gestor_escenarios

    def _leer_ids_nodos(self, logico: str, obligatoria: bool) -> List[str]:
        regs = self._registros(logico)
        if not regs and obligatoria:
            raise ErrorCargaDatos(f"Falta la hoja/archivo de {logico} o está vacía.")
        ids = []
        for reg in regs:
            valor = next(iter(reg.values()), None)  # única columna: Node(s)
            identificador = _id(valor)
            if identificador is not None and identificador not in ids:
                ids.append(identificador)
        if obligatoria and not ids:
            raise ErrorCargaDatos(f"La hoja de {logico} no contiene identificadores de nodos.")
        return ids

    def _cargar_tuberias(self, ids_fuentes: List[str], ids_sumideros: List[str]) -> None:
        regs = self._registros("tuberias")
        if not regs:
            raise ErrorCargaDatos("Falta la hoja/archivo Pipe(s) o está vacía.")

        muestra = regs[0]
        faltan = []
        for clave, alias in (("origen", ALIAS["origen"]), ("destino", ALIAS["destino"]),
                             ("id de tubería", ALIAS["id"]), ("longitud", ALIAS["longitud"]),
                             ("Manning (n)", ALIAS["manning"]), ("pendiente (S)", ALIAS["pendiente"]),
                             ("capacidad (Q)", ALIAS["qmax"])):
            if not self._tiene_col(muestra, alias):
                faltan.append(clave)
        if not (self._tiene_col(muestra, ALIAS["diam_m"]) or self._tiene_col(muestra, ALIAS["diam_in"])):
            faltan.append("diámetro")
        if faltan:
            raise ErrorCargaDatos("Hoja Pipe(s): faltan columnas obligatorias: " + ", ".join(faltan))

        filas_validas = []
        errores: List[str] = []
        ignoradas = 0
        for numero, reg in enumerate(regs, start=2):
            id_t = _id(self._col(reg, ALIAS["id"]))
            origen = _id(self._col(reg, ALIAS["origen"]))
            destino = _id(self._col(reg, ALIAS["destino"]))
            if id_t is None or origen is None or destino is None:
                ignoradas += 1  # totales, notas o fuentes al pie de la hoja
                continue
            longitud = _num(self._col(reg, ALIAS["longitud"]))
            diam = _num(self._col(reg, ALIAS["diam_m"]))
            if diam is None:
                pulg = _num(self._col(reg, ALIAS["diam_in"]))
                diam = pulg * 0.0254 if pulg is not None else None
            manning = _num(self._col(reg, ALIAS["manning"]))
            pendiente = _num(self._col(reg, ALIAS["pendiente"]))
            qmax = _num(self._col(reg, ALIAS["qmax"]))
            if None in (longitud, diam, manning, pendiente, qmax):
                errores.append(f"fila {numero} ({id_t}): hay valores vacíos o no numéricos")
                continue
            filas_validas.append((id_t, origen, destino, longitud, diam, pendiente, manning, qmax))
        if ignoradas:
            self.advertencias.append(f"Pipe(s): se ignoraron {ignoradas} filas sin identificador/nodos (totales o notas).")
        if errores:
            raise ErrorCargaDatos("Hoja Pipe(s) con datos inválidos:\n  " + "\n  ".join(errores[:15]))
        if not filas_validas:
            raise ErrorCargaDatos("La hoja Pipe(s) no contiene tuberías válidas.")

        # Nodos: fuentes, sumideros y el resto (pozos), en orden de aparición
        tipos: Dict[str, str] = {}
        for i in ids_fuentes:
            tipos[i] = Nodo.TIPO_FUENTE
        for i in ids_sumideros:
            if i in tipos:
                raise ErrorCargaDatos(f"El nodo '{i}' figura a la vez como fuente y sumidero.")
            tipos[i] = Nodo.TIPO_SUMIDERO
        orden = list(tipos.keys())
        for (_, o, d, *_r) in filas_validas:
            for n in (o, d):
                if n not in tipos:
                    tipos[n] = Nodo.TIPO_POZO
                    orden.append(n)
        for i in orden:
            self.grafo.agregar_nodo(Nodo(id_nodo=i, tipo=tipos[i]))

        for (id_t, o, d, longitud, diam, pendiente, manning, qmax) in filas_validas:
            try:
                self.grafo.agregar_tuberia(Tuberia(id_t, o, d, longitud, diam, pendiente, manning, qmax))
            except ValueError as e:
                raise ErrorCargaDatos(f"Tubería {id_t}: {e}")
            # Comprobación de coherencia con Manning (no se recalcula Qmax: solo se advierte)
            area = math.pi * diam ** 2 / 4.0
            q_teorico = (1.0 / manning) * area * (diam / 4.0) ** (2.0 / 3.0) * math.sqrt(pendiente)
            if qmax > 0 and abs(q_teorico - qmax) / qmax > 0.01:
                self.advertencias.append(
                    f"{id_t}: Qmax del archivo ({qmax:.4f}) difiere de Manning a sección llena ({q_teorico:.4f})."
                )

    def _asignar_cuenca(self, ids_fuentes: List[str]) -> None:
        """
        La hoja Drainage Basin trae un único C y un único A para toda la cuenca y no
        indica a qué alcantarilla pertenece. SUPUESTO documentado: el área total se
        reparte en partes iguales entre las alcantarillas fuente y todas usan el
        mismo coeficiente de escorrentía.
        """
        regs = self._registros("cuenca")
        if not regs:
            raise ErrorCargaDatos("Falta la hoja/archivo Drainage Basin o está vacía.")
        reg = regs[0]
        c = _num(reg.get("c", reg.get("runoff", reg.get("coeficiente"))))
        a = _num(reg.get("a", reg.get("area", reg.get("área"))))
        if c is None or a is None:
            raise ErrorCargaDatos("Drainage Basin: no se encontraron los valores de C (escorrentía) y A (hectáreas).")
        if not (0 < c <= 1):
            raise ErrorCargaDatos(f"Drainage Basin: el coeficiente C={c} debe estar en (0, 1].")
        if a <= 0:
            raise ErrorCargaDatos(f"Drainage Basin: el área A={a} ha debe ser mayor que cero.")
        self.coef_escorrentia, self.area_total_ha = c, a
        fuentes = self.grafo.obtener_fuentes()
        if not fuentes:
            raise ErrorCargaDatos("La red no tiene alcantarillas fuente donde incorporar la lluvia.")
        if self.areas_fuentes is not None:
            for nodo in fuentes:
                nodo.area_drenaje = float(self.areas_fuentes.get(nodo.id_nodo, 0.0))
                nodo.coef_escorrentia = c
            self.advertencias.append(
                f"Cuenca: áreas asignadas por configuración individual (C={c:g})."
            )
        else:
            area_efectiva = a * self.factor_area
            parte = area_efectiva / len(fuentes)
            for nodo in fuentes:
                nodo.area_drenaje = parte
                nodo.coef_escorrentia = c
            self.advertencias.append(
                f"Cuenca: A={area_efectiva:g} ha (factor={self.factor_area:g}) repartida en partes iguales "
                f"entre {len(fuentes)} fuentes ({parte:g} ha c/u), C={c:g}."
            )

    def _cargar_escenarios(self) -> None:
        regs = self._registros("escenarios")
        if not regs:
            self.advertencias.append("No hay hoja de escenarios: se usan escenarios predeterminados.")
            for nombre, i in (("Sin lluvia", 0), ("Lluvia ligera", 10), ("Lluvia moderada", 30),
                              ("Lluvia fuerte", 60), ("Lluvia extrema", 100)):
                self.gestor_escenarios.agregar_escenario(
                    EscenarioLluvia(f"{nombre} ({i} mm/h)", float(i), self.duracion_lluvia_min))
        for reg in regs:
            num = _id(reg.get("scenario", reg.get("escenario")))
            texto_i = str(reg.get("intensity", reg.get("intensidad", ""))).replace(",", ".")
            m = re.search(r"-?\d+(?:\.\d+)?", texto_i)
            if num is None or m is None:
                self.advertencias.append(f"Escenarios: fila ignorada (sin número o intensidad): {reg}")
                continue
            intensidad = float(m.group())
            cond = str(reg.get("condition", reg.get("condición", reg.get("descripcion", "")))).strip()
            nombre = f"E{num} - {cond} ({intensidad:g} mm/h)" if cond else f"E{num} ({intensidad:g} mm/h)"
            try:
                self.gestor_escenarios.agregar_escenario(
                    EscenarioLluvia(nombre, intensidad, self.duracion_lluvia_min, cond))
            except ValueError as e:
                raise ErrorCargaDatos(f"Escenario {num}: {e}")
        nombres = self.gestor_escenarios.listar_escenarios()
        if not nombres:
            raise ErrorCargaDatos("No se pudo cargar ningún escenario de lluvia.")
        self.gestor_escenarios.seleccionar_escenario(nombres[0])

    def _cargar_coordenadas(self) -> None:
        """
        Posiciones de los nodos para el dibujo. Orden de prioridad:
          1. Coordenadas_Anexo2.csv (id,x,y) junto a los datos, si existe.
          2. Posiciones del Anexo 2 incluidas en el código (io_datos/layout_anexo2.py),
             si cubren todos los nodos de la red.
          3. Si no, la GUI calcula un layout automático por capas.
        """
        carpetas = [self.ruta if self._es_carpeta() else os.path.dirname(os.path.abspath(self.ruta))]
        if self.carpeta_csv:
            carpetas.append(self.carpeta_csv)
        for carpeta in carpetas:
            ruta = os.path.join(carpeta, ARCHIVO_COORDENADAS)
            if os.path.exists(ruta):
                with open(ruta, newline="", encoding="utf-8") as f:
                    for fila in csv.DictReader(f):
                        nodo = self.grafo.obtener_nodo(_id(fila.get("id")) or "")
                        x, y = _num(fila.get("x")), _num(fila.get("y"))
                        if nodo is not None and x is not None and y is not None:
                            nodo.x, nodo.y = x, y
                return
        nodos = self.grafo.obtener_todos_los_nodos()
        if nodos and all(n.id_nodo in COORDENADAS_ANEXO_2 for n in nodos):
            for n in nodos:
                n.x, n.y = COORDENADAS_ANEXO_2[n.id_nodo]
        else:
            self.advertencias.append("Sin coordenadas para todos los nodos: el esquema se dibuja con un layout automático.")

    def _validar_red(self) -> None:
        errores = self.grafo.validar_conexiones()
        if errores:
            raise ErrorCargaDatos("\n".join(errores))
        if not self.grafo.es_aciclico():
            raise ErrorCargaDatos("La red contiene ciclos: el modelo exige un grafo dirigido acíclico.")
        for nodo in self.grafo.obtener_todos_los_nodos():
            if nodo.grado_entrada == 0 and nodo.grado_salida == 0:
                self.advertencias.append(f"El nodo {nodo.id_nodo} no está conectado a ninguna tubería.")
            if nodo.es_sumidero and nodo.grado_salida > 0:
                self.advertencias.append(f"El sumidero {nodo.id_nodo} tiene tuberías de salida.")
            if not nodo.es_sumidero and nodo.grado_salida == 0:
                self.advertencias.append(f"El nodo {nodo.id_nodo} no tiene salida y no es sumidero (el agua quedaría retenida).")
