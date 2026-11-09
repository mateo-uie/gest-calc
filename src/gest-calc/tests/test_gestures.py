"""Pruebas sintéticas del detector de pellizco."""

import unittest

import config
from gestures import DetectorPellizco


class TestDetectorPellizco(unittest.TestCase):
    def setUp(self) -> None:
        self.detector = DetectorPellizco()

    def cerrar(self, inicio: float = 0.0):
        resultado = None
        for frame in range(config.CLOSE_CONFIRM_FRAMES):
            resultado = self.detector.actualizar(0.1, (100 + frame, 100), inicio + frame * 0.01)
        return resultado

    def test_razon_normalizada(self) -> None:
        razon = self.detector.calcular_razon((0, 0), (0, 10), (10, 10), (0, 20))
        self.assertAlmostEqual(razon, 0.5)

    def test_histéresis_mantiene_cerrado_hasta_open_ratio(self) -> None:
        self.assertTrue(self.cerrar().cerrado)
        intermedio = (config.CLOSE_RATIO + config.OPEN_RATIO) / 2
        self.assertTrue(self.detector.actualizar(intermedio, (10, 10), 0.2).cerrado)
        self.assertFalse(self.detector.actualizar(config.OPEN_RATIO + 0.01, (10, 10), 0.3).cerrado)

    def test_mantener_cerrado_emite_una_sola_pulsacion(self) -> None:
        eventos = [self.cerrar().pulsacion]
        eventos.extend(self.detector.actualizar(0.1, (20, 20), t).pulsacion for t in (0.2, 0.3, 0.4))
        self.assertEqual(eventos.count(True), 1)

    def test_debounce_ignora_un_frame_bajo(self) -> None:
        primero = self.detector.actualizar(0.1, (10, 10), 0.0)
        segundo = self.detector.actualizar(config.CLOSE_RATIO + 0.01, (10, 10), 0.1)
        self.assertFalse(primero.pulsacion)
        self.assertFalse(segundo.pulsacion)
        self.assertFalse(segundo.cerrado)

    def test_cooldown_bloquea_segundo_evento(self) -> None:
        self.assertTrue(self.cerrar(0.0).pulsacion)
        self.detector.actualizar(config.OPEN_RATIO + 0.1, (0, 0), 0.1)
        self.assertFalse(self.cerrar(0.2).pulsacion)
        self.detector.actualizar(config.OPEN_RATIO + 0.1, (0, 0), 0.5)
        self.assertTrue(self.cerrar(0.6).pulsacion)

    def test_cursor_se_congela_antes_del_pellizco(self) -> None:
        libre = self.detector.actualizar(config.FREEZE_RATIO + 0.1, (100, 100), 0.0)
        congelado = self.detector.actualizar(config.FREEZE_RATIO - 0.01, (200, 200), 0.1)
        self.assertEqual(libre.cursor, (100, 100))
        self.assertEqual(congelado.cursor, (100, 100))
        self.assertTrue(congelado.congelado)

    def test_perdida_sostenida_reinicia_estado_y_cooldown(self) -> None:
        self.cerrar()
        for _ in range(config.HAND_LOST_FRAMES):
            self.assertFalse(self.detector.registrar_ausencia())
        self.assertTrue(self.detector.registrar_ausencia())
        # Tras el reset puede pulsar incluso con un tiempo anterior al cooldown previo.
        self.assertTrue(self.cerrar(0.1).pulsacion)


if __name__ == "__main__":
    unittest.main()
