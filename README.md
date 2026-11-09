# Calculadora basada en gestos

Aplicación de cálculo controlada mediante gestos de una mano frente a la cámara. Permite seleccionar los botones con un pellizco o mediante permanencia (*dwell*) como alternativa accesible.

El sistema operativo empleado para el desarrollo es **Debian GNU/Linux 13 (Trixie)**. La aplicación se ejecuta mediante Docker con Python 3.12, OpenCV 4.11 y MediaPipe 0.10.21 usando la API clásica `mp.solutions.hands`.

## Ejecución con Docker

```bash
make build                 # Construye la imagen con las versiones fijadas
make camtest               # Comprueba el acceso a la cámara y la ventana
make run                   # Ejecuta con /dev/video0
make run CAM=/dev/video2   # Mapea otra cámara del host a /dev/video0
make shell                 # Abre una consola dentro del contenedor
make test                  # Ejecuta las pruebas sin cámara ni pantalla
```

Para mostrar la ventana de OpenCV, el contenedor necesita acceder al entorno gráfico del equipo. El `Makefile` configura automáticamente este acceso y también conecta la cámara indicada.

## Uso

1. Coloque una mano abierta frente a la cámara, con la palma visible y dentro del encuadre.
2. Mueva el punto medio entre pulgar e índice hasta el botón deseado. El botón cambia de color al quedar bajo el cursor.
3. Acerque pulgar e índice para pellizcar. El cursor se congela antes del cierre para que el movimiento de los dedos no seleccione un botón vecino.
4. Abra claramente los dedos antes de volver a pulsar.

Teclas:

- `d`: alterna entre **PELLIZCO** y **DWELL**.
- En **DWELL**, mantenga el cursor sobre un botón durante un segundo; el anillo muestra el progreso. El pellizco se ignora.
- `h`: muestra u oculta razón de pellizco, umbrales, estado, FPS y landmarks.
- `q` o `Esc`: sale.

## Estructura

- `src/gest-calc/main.py`: bucle principal y coordinación de módulos.
- `src/gest-calc/config.py`: todas las constantes y umbrales ajustables.
- `src/gest-calc/hand_tracker.py`: adapta `mp.solutions.hands` y devuelve cuatro landmarks.
- `src/gest-calc/cursor.py`: filtro EMA que reduce el temblor.
- `src/gest-calc/gestures.py`: razón normalizada, histéresis, debouncing, cooldown y congelación.
- `src/gest-calc/dwell.py`: selección por permanencia con tiempo inyectado.
- `src/gest-calc/ui.py`: botones, layout, hit-testing y feedback visual.
- `src/gest-calc/calculator.py`: estado y reglas aritméticas sin visión ni GUI.
- `src/gest-calc/tests/`: pruebas `unittest` con datos sintéticos.

## Cambios respecto al material inicial

Se mantienen sin cambios `webcam_test.py`, `sample_main.py`, `Dockerfile` y `requirements.txt`. La aplicación se ha dividido en módulos nuevos para separar la visión, los gestos, la interfaz y la lógica de cálculo, lo que simplifica su comprensión y permite probar cada parte sin cámara. La interfaz conserva la distribución, las proporciones y el estilo visual de `sample_main.py`.

En el `Makefile`, la receta `run` se ha actualizado para ejecutar `main.py` y se ha añadido la receta `test`, que permite ejecutar las pruebas dentro del contenedor sin cámara ni pantalla.

## Ajuste de los gestos

Pulse `h` y observe la razón normalizada mientras abre y cierra los dedos. Los parámetros principales están en `config.py`:

- `CLOSE_RATIO`: súbalo si cuesta cerrar; bájelo si hay cierres falsos.
- `OPEN_RATIO`: súbalo si se rearma demasiado pronto; bájelo si exige abrir demasiado.
- `FREEZE_RATIO`: súbalo para congelar antes; bájelo si el cursor se queda congelado con demasiada facilidad.
- Debe mantenerse siempre `FREEZE_RATIO > OPEN_RATIO > CLOSE_RATIO`.
- `CLOSE_CONFIRM_FRAMES` filtra cierres breves; más frames dan estabilidad pero añaden latencia.
- `CURSOR_SMOOTHING_ALPHA`: más alto responde antes y tiembla más; más bajo suaviza más y retrasa.
- `DWELL_TIME_S`: tiempo necesario en el modo accesible.


## Limitaciones conocidas

- Se sigue una sola mano y no se distingue entre izquierda y derecha.
- MediaPipe puede perder la mano con poca luz, oclusión, fondo complejo o si sale del encuadre.
- Los umbrales iniciales son orientativos y pueden requerir ajuste para la cámara y el usuario.
- La selección dwell exige mantener el cursor estable y puede ser lenta para usuarios sin dificultad motora.
- El display limita la expresión a 12 caracteres; un resultado que no cabe muestra `Error`.
- Las operaciones usan aritmética de punto flotante, por lo que conservan sus limitaciones de precisión habituales.
