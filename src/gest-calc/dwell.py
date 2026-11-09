"""Selección accesible por permanencia del cursor sobre un botón."""

from dataclasses import dataclass

from config import DWELL_TIME_S


@dataclass(frozen=True)
class ResultadoDwell:
    progreso: float
    activado: bool


class SelectorDwell:
    """Activa una vez y exige salir antes de repetir sobre el mismo botón."""

    def __init__(self, tiempo_dwell: float = DWELL_TIME_S) -> None:
        self.tiempo_dwell = tiempo_dwell
        self._boton_actual: str | None = None
        self._inicio: float | None = None
        self._bloqueado = False

    def actualizar(self, boton: str | None, ahora: float) -> ResultadoDwell:
        if boton is None:
            self.reiniciar()
            return ResultadoDwell(0.0, False)

        if boton != self._boton_actual:
            self._boton_actual = boton
            self._inicio = ahora
            self._bloqueado = False
            return ResultadoDwell(0.0, False)

        if self._bloqueado:
            return ResultadoDwell(1.0, False)

        # _inicio solo puede ser None en la primera observación del botón.
        if self._inicio is None:
            self._inicio = ahora
        progreso = min(1.0, max(0.0, (ahora - self._inicio) / self.tiempo_dwell))
        if progreso >= 1.0:
            self._bloqueado = True
            return ResultadoDwell(1.0, True)
        return ResultadoDwell(progreso, False)

    def reiniciar(self) -> None:
        """La pérdida de mano y la salida de botones permiten otra activación."""
        self._boton_actual = None
        self._inicio = None
        self._bloqueado = False
