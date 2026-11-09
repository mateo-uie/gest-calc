"""Pruebas del selector por permanencia con tiempo inyectado."""

import unittest

from dwell import SelectorDwell


class TestSelectorDwell(unittest.TestCase):
    def setUp(self) -> None:
        self.selector = SelectorDwell(tiempo_dwell=1.0)

    def test_activa_al_segundo(self) -> None:
        self.assertEqual(self.selector.actualizar("7", 10.0).progreso, 0.0)
        mitad = self.selector.actualizar("7", 10.5)
        self.assertAlmostEqual(mitad.progreso, 0.5)
        self.assertFalse(mitad.activado)
        final = self.selector.actualizar("7", 11.0)
        self.assertTrue(final.activado)

    def test_cambiar_boton_reinicia_progreso(self) -> None:
        self.selector.actualizar("7", 0.0)
        self.selector.actualizar("7", 0.8)
        cambiado = self.selector.actualizar("8", 0.9)
        self.assertEqual(cambiado.progreso, 0.0)
        self.assertFalse(cambiado.activado)

    def test_no_repite_hasta_salir(self) -> None:
        self.selector.actualizar("7", 0.0)
        self.assertTrue(self.selector.actualizar("7", 1.0).activado)
        self.assertFalse(self.selector.actualizar("7", 2.0).activado)
        self.selector.actualizar(None, 2.1)
        self.selector.actualizar("7", 3.0)
        self.assertTrue(self.selector.actualizar("7", 4.0).activado)

    def test_perdida_de_mano_reinicia(self) -> None:
        self.selector.actualizar("7", 0.0)
        self.selector.actualizar("7", 0.7)
        perdido = self.selector.actualizar(None, 0.8)
        self.assertEqual(perdido.progreso, 0.0)
        self.selector.actualizar("7", 1.0)
        self.assertFalse(self.selector.actualizar("7", 1.5).activado)


if __name__ == "__main__":
    unittest.main()
