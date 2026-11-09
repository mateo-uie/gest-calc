"""Pruebas de hit-testing sin abrir ventana ni cámara."""

import unittest

from ui import crear_botones, find_button_at


class TestHitTesting(unittest.TestCase):
    def setUp(self) -> None:
        self.botones = crear_botones(1920, 1080)

    def test_centro_de_todos_los_botones(self) -> None:
        self.assertEqual(len(self.botones), 18)
        for boton in self.botones:
            with self.subTest(valor=boton.value):
                centro_x = boton.pos[0] + boton.width // 2
                centro_y = boton.pos[1] + boton.height // 2
                encontrado = find_button_at(self.botones, centro_x, centro_y)
                self.assertIsNotNone(encontrado)
                self.assertEqual(encontrado.value, boton.value)

    def test_puntos_fuera_del_teclado(self) -> None:
        for punto in ((0, 0), (100, 500), (1919, 1079)):
            with self.subTest(punto=punto):
                self.assertIsNone(find_button_at(self.botones, *punto))

    def test_fila_superior_tiene_botones_dobles(self) -> None:
        c, borrar = self.botones[:2]
        self.assertEqual(c.width, 2 * c.height)
        self.assertEqual(borrar.width, 2 * borrar.height)


if __name__ == "__main__":
    unittest.main()
