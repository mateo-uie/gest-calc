"""Detección del pellizco con normalización, histéresis y debouncing."""

from dataclasses import dataclass
from math import hypot

import config

Punto = tuple[int, int]


@dataclass(frozen=True)
class ResultadoGesto:
    cursor: Punto
    razon: float
    cerrado: bool
    congelado: bool
    pulsacion: bool


class DetectorPellizco:
    """Convierte distancias de landmarks en eventos discretos y estables."""

    def __init__(self) -> None:
        if not config.FREEZE_RATIO > config.OPEN_RATIO > config.CLOSE_RATIO:
            raise ValueError("Se requiere FREEZE_RATIO > OPEN_RATIO > CLOSE_RATIO")
        self.reiniciar()

    @staticmethod
    def calcular_razon(muneca: Punto, pulgar: Punto, indice: Punto, base_medio: Punto) -> float:
        """Normaliza la apertura con la palma para compensar distancia a cámara."""
        distancia_dedos = hypot(pulgar[0] - indice[0], pulgar[1] - indice[1])
        tamano_palma = hypot(muneca[0] - base_medio[0], muneca[1] - base_medio[1])
        return distancia_dedos / max(tamano_palma, config.PALM_MIN_DISTANCE_PX)

    def actualizar(self, razon: float, cursor_propuesto: Punto, ahora: float) -> ResultadoGesto:
        """Actualiza un frame y emite pulsación solo en el flanco abierto-cerrado."""
        self._frames_perdidos = 0
        congelado = razon < config.FREEZE_RATIO
        if not congelado or self._cursor_congelado is None:
            self._cursor_congelado = cursor_propuesto
        cursor_usado = self._cursor_congelado

        pulsacion = False
        if self._cerrado:
            # Un umbral de apertura distinto evita oscilar cerca del cierre.
            if razon > config.OPEN_RATIO:
                self._cerrado = False
                self._frames_cierre = 0
        else:
            if razon < config.CLOSE_RATIO:
                self._frames_cierre += 1
                if self._frames_cierre >= config.CLOSE_CONFIRM_FRAMES:
                    self._cerrado = True
                    self._frames_cierre = 0
                    fuera_cooldown = (
                        self._ultima_pulsacion is None
                        or ahora - self._ultima_pulsacion >= config.PRESS_COOLDOWN_S
                    )
                    if fuera_cooldown:
                        pulsacion = True
                        self._ultima_pulsacion = ahora
            else:
                # Un frame aislado bajo el umbral no debe contar más adelante.
                self._frames_cierre = 0

        return ResultadoGesto(cursor_usado, razon, self._cerrado, congelado, pulsacion)

    def registrar_ausencia(self) -> bool:
        """Devuelve True cuando la ausencia sostenida obliga a reiniciar todo."""
        self._frames_perdidos += 1
        if self._frames_perdidos > config.HAND_LOST_FRAMES:
            self.reiniciar()
            return True
        return False

    def reiniciar(self) -> None:
        self._cerrado = False
        self._frames_cierre = 0
        self._ultima_pulsacion: float | None = None
        self._cursor_congelado: Punto | None = None
        self._frames_perdidos = 0
