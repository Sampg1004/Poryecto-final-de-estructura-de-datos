from typing import List, Dict, Tuple, Optional
from modelo.grafo import Grafo
from modelo.tuberia import Tuberia
from simulacion.utilizacion import categoria_por_uso


class AnalizadorCriticas:
    """
    Identifica y clasifica las tuberías críticas según su porcentaje de utilización.

    Una tubería es crítica cuando alcanza o supera su capacidad máxima de transporte.
    También se clasifican las que están cercanas a la capacidad máxima.
    """

    # Umbrales de clasificación (coherentes con la escala de colores del PDF)
    UMBRAL_BAJA = 25.0
    UMBRAL_MODERADA = 50.0
    UMBRAL_ALTA = 75.0
    UMBRAL_MAXIMA = 100.0

    @staticmethod
    def obtener_tuberias_criticas(
        grafo: Grafo,
        umbral_sobrecarga: float = 100.0,
    ) -> List[Tuberia]:
        """
        Retorna las tuberías cuyo porcentaje de utilización supera o iguala el umbral.
        Ordenadas de mayor a menor porcentaje de utilización.
        """
        criticas = []
        for tuberia in grafo.obtener_todas_las_tuberias():
            if tuberia.porcentaje_utilizacion >= umbral_sobrecarga:
                criticas.append(tuberia)
        criticas.sort(key=lambda t: t.porcentaje_utilizacion, reverse=True)
        return criticas

    @staticmethod
    def obtener_tuberias_sobrecargadas(grafo: Grafo) -> List[Tuberia]:
        """Retorna tuberías con uso > 100% (capacidad excedida)."""
        return [
            t for t in grafo.obtener_todas_las_tuberias() if t.esta_sobrecargada()
        ]

    @staticmethod
    def clasificar_por_utilizacion(
        grafo: Grafo,
    ) -> Dict[str, List[Tuberia]]:
        """
        Clasifica todas las tuberías según su porcentaje de utilización:
        - baja: 0-25%  | moderada: >25-50%  | alta: >50-75%
        - maxima: >75-100%  | excedida: >100%
        (límites superiores inclusivos, como en la escala de la guía)
        """
        clasificacion = {"baja": [], "moderada": [], "alta": [], "maxima": [], "excedida": []}
        for tuberia in grafo.obtener_todas_las_tuberias():
            clasificacion[categoria_por_uso(tuberia.porcentaje_utilizacion)].append(tuberia)
        return clasificacion

    @staticmethod
    def obtener_top_n_criticas(
        grafo: Grafo,
        n: int = 10,
    ) -> List[Tuberia]:
        """Retorna las N tuberías con mayor porcentaje de utilización."""
        tuberias = sorted(
            grafo.obtener_todas_las_tuberias(),
            key=lambda t: t.porcentaje_utilizacion,
            reverse=True,
        )
        return tuberias[:n]

    @staticmethod
    def reporte_criticas(grafo: Grafo) -> str:
        """Genera un reporte de texto con las tuberías críticas."""
        lineas = []
        lineas.append("=" * 60)
        lineas.append("REPORTE DE TUBERÍAS CRÍTICAS")
        lineas.append("=" * 60)

        sobrecargadas = AnalizadorCriticas.obtener_tuberias_sobrecargadas(grafo)
        lineas.append(f"\nTuberías sobrecargadas (>100%): {len(sobrecargadas)}")
        for t in sobrecargadas:
            lineas.append(
                f"  - {t.id_tuberia}: {t.nodo_origen} -> {t.nodo_destino} | "
                f"Uso: {t.porcentaje_utilizacion:.2f}% | Q: {t.caudal_transportado:.4f} m³/s | "
                f"Qmax: {t.capacidad_maxima:.4f} m³/s"
            )

        criticas = AnalizadorCriticas.obtener_top_n_criticas(grafo, 10)
        lineas.append(f"\nTop 10 tuberías con mayor utilización:")
        for i, t in enumerate(criticas, 1):
            estado = "SOBRECARGADA" if t.esta_sobrecargada() else "Crítica"
            lineas.append(
                f"  {i:2d}. {t.id_tuberia}: {t.nodo_origen} -> {t.nodo_destino} | "
                f"{estado} | Uso: {t.porcentaje_utilizacion:.2f}%"
            )

        clasificacion = AnalizadorCriticas.clasificar_por_utilizacion(grafo)
        lineas.append("\nDistribución por rango de utilización:")
        for rango, lista in clasificacion.items():
            lineas.append(f"  - {rango.capitalize()}: {len(lista)} tuberías")

        lineas.append("=" * 60)
        return "\n".join(lineas)
