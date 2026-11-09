"""Interfaz gráfica: layout, hit-testing y feedback visual de la interacción."""

from dataclasses import dataclass

import cv2

import config


@dataclass
class Button:
    """Botón rectangular basado en la clase proporcionada en sample_main.py."""

    pos: tuple[int, int]
    width: int
    height: int
    value: str

    def contains(self, x: int, y: int) -> bool:
        """Incluye los bordes para no dejar huecos entre botones contiguos."""
        return self.pos[0] <= x <= self.pos[0] + self.width and self.pos[1] <= y <= self.pos[1] + self.height

    def draw(self, img, color: tuple[int, int, int] = config.COLOR_BUTTON) -> None:
        """Conserva dimensiones, borde, fuente y offsets del botón original."""
        escala_boton = self.height / config.BASE_BUTTON_SIZE
        esquina_opuesta = (self.pos[0] + self.width, self.pos[1] + self.height)
        cv2.rectangle(img, self.pos, esquina_opuesta, color, cv2.FILLED)
        cv2.rectangle(
            img,
            self.pos,
            esquina_opuesta,
            config.COLOR_BORDER_TEXT,
            config.BUTTON_BORDER_THICKNESS,
        )
        text_x = self.pos[0] + self.width // 2 - int(config.BUTTON_TEXT_OFFSET_X * escala_boton)
        text_y = self.pos[1] + self.height // 2 + int(config.BUTTON_TEXT_OFFSET_Y * escala_boton)
        cv2.putText(
            img,
            self.value,
            (text_x, text_y),
            cv2.FONT_HERSHEY_PLAIN,
            config.BUTTON_TEXT_SCALE * escala_boton,
            config.COLOR_BORDER_TEXT,
            max(1, round(config.BUTTON_BORDER_THICKNESS * escala_boton)),
        )


def crear_botones(width: int, height: int) -> list[Button]:
    """Reproduce el teclado del sample en el lado derecho de cualquier frame."""
    escala = height / config.REFERENCE_HEIGHT
    size = int(config.BASE_BUTTON_SIZE * escala)
    valores = [
        ["C", "<"],
        ["7", "8", "9", "/"],
        ["4", "5", "6", "*"],
        ["1", "2", "3", "-"],
        ["0", ".", "=", "+"],
    ]
    botones: list[Button] = []
    for fila, valores_fila in enumerate(valores):
        for columna, valor in enumerate(valores_fila):
            xpos = int(width - config.KEYPAD_RIGHT_MARGIN_BUTTONS * size + columna * size)
            ypos = int(height * config.KEYPAD_TOP_FRACTION + fila * size)
            if fila == 0 and columna == 1:
                # El sample desplaza '<' para que ambos botones dobles no se solapen.
                xpos += size
            ancho = config.TOP_BUTTON_WIDTH_BUTTONS * size if fila == 0 else size
            botones.append(Button((xpos, ypos), ancho, size, valor))
    return botones


def find_button_at(botones: list[Button], x: int, y: int) -> Button | None:
    """Devuelve el primer botón bajo el punto o None si está fuera del teclado."""
    for boton in botones:
        if boton.contains(x, y):
            return boton
    return None


class Interfaz:
    """Agrupa el layout y todo el dibujo para mantener main.py pequeño."""

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.escala = height / config.REFERENCE_HEIGHT
        self.size = int(config.BASE_BUTTON_SIZE * self.escala)
        self.botones = crear_botones(width, height)
        self._ultimo_activado: str | None = None
        self._instante_activacion = 0.0

    def find_button_at(self, x: int, y: int) -> Button | None:
        return find_button_at(self.botones, x, y)

    def registrar_activacion(self, valor: str, ahora: float) -> None:
        self._ultimo_activado = valor
        self._instante_activacion = ahora

    def dibujar(
        self,
        frame,
        texto: str,
        ahora: float,
        modo_dwell: bool,
        mano_detectada: bool,
        cursor: tuple[int, int] | None,
        boton_hover: Button | None,
        progreso_dwell: float,
        cerrado: bool,
        congelado: bool,
        depuracion: bool,
        razon: float | None,
        fps: float,
        landmarks: dict[str, tuple[int, int]] | None,
    ) -> None:
        """Dibuja primero la calculadora y después el feedback superpuesto."""
        self._dibujar_display(frame, texto)
        for boton in self.botones:
            color = config.COLOR_BUTTON
            if boton is boton_hover:
                color = config.COLOR_HOVER
            if (
                boton.value == self._ultimo_activado
                and ahora - self._instante_activacion <= config.PRESSED_FEEDBACK_S
            ):
                color = config.COLOR_PRESSED
            boton.draw(frame, color)

        modo = "DWELL" if modo_dwell else "PELLIZCO"
        cv2.putText(frame, f"Modo: {modo}", (config.MODE_LABEL_X, config.MODE_LABEL_Y), cv2.FONT_HERSHEY_SIMPLEX,
                    config.INFO_FONT_SCALE, config.COLOR_DEBUG, config.INFO_THICKNESS)
        if not mano_detectada:
            cv2.putText(frame, "Sin mano detectada", (config.MODE_LABEL_X, config.NO_HAND_LABEL_Y),
                        cv2.FONT_HERSHEY_SIMPLEX, config.INFO_FONT_SCALE, config.COLOR_WARNING, config.INFO_THICKNESS)

        if modo_dwell and boton_hover is not None and progreso_dwell > 0:
            centro = (boton_hover.pos[0] + boton_hover.width // 2, boton_hover.pos[1] + boton_hover.height // 2)
            radio = min(boton_hover.width, boton_hover.height) // 2 - config.DWELL_RING_EXTRA_RADIUS
            fin = config.ARC_START_DEGREES + int(config.FULL_CIRCLE_DEGREES * progreso_dwell)
            cv2.ellipse(frame, centro, (radio, radio), 0, config.ARC_START_DEGREES, fin,
                        config.COLOR_DWELL, config.DWELL_RING_THICKNESS)

        if cursor is not None:
            color_cursor = config.COLOR_CURSOR_CLOSED if cerrado else config.COLOR_CURSOR_OPEN
            if congelado:
                color_cursor = config.COLOR_CURSOR_FROZEN
            cv2.circle(frame, cursor, config.CURSOR_RADIUS, color_cursor, config.CURSOR_THICKNESS)

        if depuracion:
            self._dibujar_depuracion(frame, razon, cerrado, congelado, fps, landmarks)

    def _dibujar_display(self, frame, texto: str) -> None:
        x = int(self.width - config.KEYPAD_RIGHT_MARGIN_BUTTONS * self.size)
        y = int(self.height * config.DISPLAY_TOP_FRACTION)
        opuesta = (x + config.DISPLAY_WIDTH_BUTTONS * self.size, y + int(config.DISPLAY_HEIGHT_BUTTONS * self.size))
        cv2.rectangle(frame, (x, y), opuesta, config.COLOR_BUTTON, cv2.FILLED)
        cv2.rectangle(frame, (x, y), opuesta, config.COLOR_BORDER_TEXT, config.BUTTON_BORDER_THICKNESS)
        origen = (
            x + int(config.DISPLAY_TEXT_X_FRACTION * self.size),
            y + int(config.DISPLAY_TEXT_Y_FRACTION * self.size),
        )
        cv2.putText(frame, texto, origen, cv2.FONT_HERSHEY_PLAIN, config.BUTTON_TEXT_SCALE * self.escala,
                    config.COLOR_BORDER_TEXT, max(1, round(config.BUTTON_BORDER_THICKNESS * self.escala)))

    @staticmethod
    def _dibujar_depuracion(frame, razon, cerrado, congelado, fps, landmarks) -> None:
        estado = "CERRADO" if cerrado else "ABIERTO"
        if congelado:
            estado += " / CONGELADO"
        razon_texto = "--" if razon is None else f"{razon:.3f}"
        lineas = [
            f"Razon: {razon_texto}",
            f"Umbrales C/O/F: {config.CLOSE_RATIO:.2f} / {config.OPEN_RATIO:.2f} / {config.FREEZE_RATIO:.2f}",
            f"Estado: {estado}",
            f"FPS: {fps:.1f}",
        ]
        for indice, linea in enumerate(lineas):
            posicion = (config.DEBUG_X, config.DEBUG_Y + indice * config.DEBUG_LINE_HEIGHT)
            cv2.putText(frame, linea, posicion, cv2.FONT_HERSHEY_SIMPLEX, config.INFO_FONT_SCALE,
                        config.COLOR_DEBUG, config.INFO_THICKNESS)
        if landmarks:
            for nombre, punto in landmarks.items():
                cv2.circle(frame, punto, config.LANDMARK_RADIUS, config.COLOR_DEBUG, cv2.FILLED)
                cv2.putText(frame, nombre, (punto[0] + config.LANDMARK_RADIUS, punto[1]), cv2.FONT_HERSHEY_PLAIN,
                            config.INFO_FONT_SCALE, config.COLOR_DEBUG, 1)
