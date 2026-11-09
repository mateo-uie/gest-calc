"""Envoltorio pequeño de MediaPipe Hands para aislar la parte de visión."""

import cv2
import mediapipe as mp

import config


class RastreadorMano:
    """Detecta una mano y devuelve solo los cuatro landmarks necesarios."""

    INDICES = {
        "muneca": config.LANDMARK_WRIST,
        "pulgar": config.LANDMARK_THUMB_TIP,
        "indice": config.LANDMARK_INDEX_TIP,
        "base_medio": config.LANDMARK_MIDDLE_MCP,
    }

    def __init__(self) -> None:
        self._hands = mp.solutions.hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            model_complexity=config.MODEL_COMPLEXITY,
            min_detection_confidence=config.MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=config.MIN_TRACKING_CONFIDENCE,
        )

    def procesar(self, frame) -> dict[str, tuple[int, int]] | None:
        """Procesa una copia reducida y convierte coordenadas al frame original.

        MediaPipe devuelve posiciones normalizadas, así que reducir la imagen no
        cambia el mapeo final y ahorra trabajo sin reducir el tamaño de la GUI.
        """
        alto, ancho = frame.shape[:2]
        ancho_proceso = min(config.PROCESSING_WIDTH, ancho)
        alto_proceso = max(1, round(alto * ancho_proceso / ancho))
        reducida = cv2.resize(frame, (ancho_proceso, alto_proceso), interpolation=cv2.INTER_AREA)
        rgb = cv2.cvtColor(reducida, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        resultado = self._hands.process(rgb)
        if not resultado.multi_hand_landmarks:
            return None

        mano = resultado.multi_hand_landmarks[0]
        puntos: dict[str, tuple[int, int]] = {}
        for nombre, indice in self.INDICES.items():
            landmark = mano.landmark[indice]
            # Se limita al frame por si MediaPipe devuelve un valor apenas fuera de 0..1.
            x = min(ancho - 1, max(0, round(landmark.x * ancho)))
            y = min(alto - 1, max(0, round(landmark.y * alto)))
            puntos[nombre] = (x, y)
        return puntos

    def close(self) -> None:
        """Libera explícitamente los recursos nativos de MediaPipe."""
        self._hands.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()
