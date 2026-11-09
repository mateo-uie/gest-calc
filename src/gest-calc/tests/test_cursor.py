"""Pruebas del filtro EMA del cursor."""

import unittest

from cursor import SuavizadorCursor


class TestSuavizadorCursor(unittest.TestCase):
    def test_media_exponencial_y_reinicio(self) -> None:
        cursor = SuavizadorCursor(alpha=0.5)
        self.assertEqual(cursor.actualizar((0, 0)), (0, 0))
        self.assertEqual(cursor.actualizar((10, 20)), (5, 10))
        cursor.reiniciar()
        self.assertEqual(cursor.actualizar((100, 100)), (100, 100))


if __name__ == "__main__":
    unittest.main()
