"""Bucle principal: une cámara, seguimiento, interacción, cálculo e interfaz."""

import time

import cv2

import config
from calculator import Calculadora
from cursor import SuavizadorCursor
from dwell import SelectorDwell
from gestures import DetectorPellizco
from hand_tracker import RastreadorMano
from ui import Interfaz


def punto_medio(a: tuple[int, int], b: tuple[int, int]) -> tuple[float, float]:
    """El punto medio hace que el puntero coincida visualmente con el pellizco."""
    return (a[0] + b[0]) / 2, (a[1] + b[1]) / 2


def actualizar_fps(fps_anterior: float, instante_anterior: float, ahora: float) -> float:
    intervalo = ahora - instante_anterior
    if intervalo <= 0:
        return fps_anterior
    fps_instantaneo = 1.0 / intervalo
    if fps_anterior == 0:
        return fps_instantaneo
    alpha = config.FPS_SMOOTHING_ALPHA
    return alpha * fps_instantaneo + (1 - alpha) * fps_anterior


def ejecutar() -> int:
    """Ejecuta la aplicación y devuelve un código apto para la línea de comandos."""
    camara = cv2.VideoCapture(config.CAMERA_INDEX)
    if not camara.isOpened():
        print(f"Error: no se pudo abrir la cámara con índice {config.CAMERA_INDEX}.")
        return 1

    camara.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAMERA_WIDTH)
    camara.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAMERA_HEIGHT)
    correcto, frame = camara.read()
    if not correcto or frame is None:
        print("Error: la cámara se abrió, pero no se pudo leer el primer frame.")
        camara.release()
        return 1

    alto, ancho = frame.shape[:2]
    interfaz = Interfaz(ancho, alto)
    calculadora = Calculadora(config.MAX_DISPLAY_CHARS)
    suavizador = SuavizadorCursor()
    detector = DetectorPellizco()
    selector_dwell = SelectorDwell()
    modo_dwell = False
    mostrar_depuracion = False
    fps = 0.0
    instante_anterior = time.monotonic()

    try:
        with RastreadorMano() as rastreador:
            while correcto and frame is not None:
                ahora = time.monotonic()
                fps = actualizar_fps(fps, instante_anterior, ahora)
                instante_anterior = ahora

                # Se espeja antes de MediaPipe y del dibujo: gesto y feedback usan
                # el mismo sistema de coordenadas y el texto nunca queda invertido.
                frame = cv2.flip(frame, 1)
                landmarks = rastreador.procesar(frame)
                cursor = None
                boton_hover = None
                razon = None
                cerrado = False
                congelado = False
                progreso_dwell = 0.0

                if landmarks is not None:
                    medio = punto_medio(landmarks["pulgar"], landmarks["indice"])
                    razon = detector.calcular_razon(
                        landmarks["muneca"], landmarks["pulgar"], landmarks["indice"], landmarks["base_medio"]
                    )

                    if modo_dwell:
                        # Dwell ignora por completo el pellizco y nunca congela.
                        cursor = suavizador.actualizar(medio)
                        boton_hover = interfaz.find_button_at(*cursor)
                        valor_hover = boton_hover.value if boton_hover else None
                        resultado_dwell = selector_dwell.actualizar(valor_hover, ahora)
                        progreso_dwell = resultado_dwell.progreso
                        if resultado_dwell.activado and boton_hover is not None:
                            calculadora.pulsar(boton_hover.value)
                            interfaz.registrar_activacion(boton_hover.value, ahora)
                    else:
                        # No se alimenta el EMA durante la congelación: así tampoco
                        # acumula movimiento oculto que causaría un salto al abrir.
                        if razon >= config.FREEZE_RATIO:
                            cursor_propuesto = suavizador.actualizar(medio)
                        else:
                            cursor_propuesto = (round(medio[0]), round(medio[1]))
                        resultado = detector.actualizar(razon, cursor_propuesto, ahora)
                        cursor = resultado.cursor
                        cerrado = resultado.cerrado
                        congelado = resultado.congelado
                        boton_hover = interfaz.find_button_at(*cursor)
                        if resultado.pulsacion and boton_hover is not None:
                            calculadora.pulsar(boton_hover.value)
                            interfaz.registrar_activacion(boton_hover.value, ahora)
                else:
                    selector_dwell.actualizar(None, ahora)
                    if detector.registrar_ausencia():
                        suavizador.reiniciar()

                interfaz.dibujar(
                    frame, calculadora.texto, ahora, modo_dwell, landmarks is not None,
                    cursor, boton_hover, progreso_dwell, cerrado, congelado,
                    mostrar_depuracion, razon, fps, landmarks,
                )
                cv2.imshow(config.WINDOW_NAME, frame)
                tecla = cv2.waitKey(config.WAIT_KEY_MS) & 0xFF
                if tecla in (ord("q"), config.KEY_ESCAPE):
                    break
                if tecla == ord("d"):
                    modo_dwell = not modo_dwell
                    # Cambiar de técnica cancela selecciones parciales para evitar
                    # que una acción comenzada en un modo termine en el otro.
                    detector.reiniciar()
                    selector_dwell.reiniciar()
                    suavizador.reiniciar()
                elif tecla == ord("h"):
                    mostrar_depuracion = not mostrar_depuracion

                correcto, frame = camara.read()
                if not correcto:
                    print("Error: se perdió la lectura de la cámara; cerrando limpiamente.")
    finally:
        camara.release()
        cv2.destroyAllWindows()
    return 0


if __name__ == "__main__":
    raise SystemExit(ejecutar())
