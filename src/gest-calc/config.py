"""Configuración central de la calculadora gestual.

Cada valor ajustable está aquí para que durante la defensa se pueda explicar y
calibrar sin buscar números repartidos por el programa.
"""

# --- Cámara y procesamiento ---
CAMERA_INDEX = 0  # Dispositivo que abre OpenCV; Docker mapea CAM a /dev/video0.
CAMERA_WIDTH = 1920  # Resolución solicitada; la cámara puede entregar otra.
CAMERA_HEIGHT = 1080
PROCESSING_WIDTH = 640  # Copia pequeña enviada a MediaPipe para mejorar los FPS.
MODEL_COMPLEXITY = 0  # Modelo ligero: suficiente para una mano y menor latencia.
MIN_DETECTION_CONFIDENCE = 0.7  # Más alto reduce detecciones falsas iniciales.
MIN_TRACKING_CONFIDENCE = 0.6  # Equilibrio entre continuidad y falsos positivos.
LANDMARK_WRIST = 0  # Muñeca: extremo inferior usado para medir la palma.
LANDMARK_THUMB_TIP = 4  # Punta del pulgar.
LANDMARK_INDEX_TIP = 8  # Punta del índice.
LANDMARK_MIDDLE_MCP = 9  # Base del dedo corazón: extremo superior de la palma.

# --- Cursor y gesto de pellizco ---
CURSOR_SMOOTHING_ALPHA = 0.4  # Peso de la medida nueva en el filtro EMA.
CLOSE_RATIO = 0.22  # Por debajo, pulgar e índice se consideran cerrados.
OPEN_RATIO = 0.38  # Por encima, se vuelve a considerar abierto (histéresis).
FREEZE_RATIO = 0.45  # Por debajo, el cursor se congela antes del cierre.
CLOSE_CONFIRM_FRAMES = 2  # Frames cerrados requeridos para filtrar ruido aislado.
PRESS_COOLDOWN_S = 0.4  # Pausa mínima entre dos eventos de pulsación.
HAND_LOST_FRAMES = 5  # Ausencias toleradas antes de reiniciar gesto y cursor.
PALM_MIN_DISTANCE_PX = 1.0  # Evita dividir por cero con landmarks degenerados.

# --- Selección dwell ---
DWELL_TIME_S = 1.0  # Tiempo inmóvil sobre un botón antes de activarlo.

# --- Calculadora y aspecto heredado del sample ---
MAX_DISPLAY_CHARS = 12  # Cabe con margen usando la tipografía del sample.
RESULT_SIGNIFICANT_DIGITS = 10  # Precisión legible sin largas colas decimales.
REFERENCE_HEIGHT = 1080  # Altura usada por el sample para calcular toda la escala.
BASE_BUTTON_SIZE = 100  # Tamaño de botón a la resolución de referencia.
KEYPAD_RIGHT_MARGIN_BUTTONS = 6  # Desplaza el teclado un botón a la izquierda respecto al sample.
KEYPAD_TOP_FRACTION = 0.15
DISPLAY_TOP_FRACTION = 0.05
DISPLAY_HEIGHT_BUTTONS = 1.2
DISPLAY_WIDTH_BUTTONS = 4
TOP_BUTTON_WIDTH_BUTTONS = 2
BUTTON_BORDER_THICKNESS = 3
BUTTON_TEXT_SCALE = 3.0
BUTTON_TEXT_OFFSET_X = 15
BUTTON_TEXT_OFFSET_Y = 15
DISPLAY_TEXT_X_FRACTION = 0.1
DISPLAY_TEXT_Y_FRACTION = 0.75

# Colores BGR: se conserva el gris del sample y se añaden estados distinguibles.
COLOR_BUTTON = (225, 225, 225)
COLOR_BORDER_TEXT = (50, 50, 50)
COLOR_HOVER = (190, 225, 255)
COLOR_PRESSED = (90, 210, 120)
COLOR_CURSOR_OPEN = (255, 170, 0)
COLOR_CURSOR_CLOSED = (0, 80, 255)
COLOR_CURSOR_FROZEN = (0, 220, 255)
COLOR_DEBUG = (40, 255, 40)
COLOR_WARNING = (40, 40, 255)
COLOR_DWELL = (255, 100, 255)
PRESSED_FEEDBACK_S = 0.25  # Duración del color verde tras una activación.
CURSOR_RADIUS = 12
CURSOR_THICKNESS = 3
DWELL_RING_EXTRA_RADIUS = 9
DWELL_RING_THICKNESS = 5
FULL_CIRCLE_DEGREES = 360
ARC_START_DEGREES = -90  # El progreso dwell comienza arriba, como un reloj.

# --- Textos, depuración y ventana ---
WINDOW_NAME = "Calculadora gestual"
MODE_LABEL_X = 20
MODE_LABEL_Y = 40
NO_HAND_LABEL_Y = 85
INFO_FONT_SCALE = 0.8
INFO_THICKNESS = 2
DEBUG_X = 20
DEBUG_Y = 130
DEBUG_LINE_HEIGHT = 28
LANDMARK_RADIUS = 6
FPS_SMOOTHING_ALPHA = 0.15  # Suaviza el valor de FPS para que se pueda leer.
WAIT_KEY_MS = 1
KEY_ESCAPE = 27
