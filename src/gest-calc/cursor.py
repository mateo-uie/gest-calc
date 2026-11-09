"""Suavizado del cursor mediante una media móvil exponencial (EMA)."""

from config import CURSOR_SMOOTHING_ALPHA


class SuavizadorCursor:
    """Reduce el temblor conservando una respuesta suficientemente rápida."""

    def __init__(self, alpha: float = CURSOR_SMOOTHING_ALPHA) -> None:
        if not 0 < alpha <= 1:
            raise ValueError("alpha debe estar entre 0 (excluido) y 1")
        self.alpha = alpha
        self._posicion: tuple[float, float] | None = None

    def actualizar(self, posicion: tuple[float, float]) -> tuple[int, int]:
        if self._posicion is None:
            self._posicion = posicion
        else:
            x_anterior, y_anterior = self._posicion
            x_nuevo, y_nuevo = posicion
            self._posicion = (
                self.alpha * x_nuevo + (1 - self.alpha) * x_anterior,
                self.alpha * y_nuevo + (1 - self.alpha) * y_anterior,
            )
        return round(self._posicion[0]), round(self._posicion[1])

    def reiniciar(self) -> None:
        """Olvida la posición anterior para no saltar al reaparecer la mano."""
        self._posicion = None
