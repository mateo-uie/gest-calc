"""Pruebas de la lógica pura de la calculadora."""

import unittest

from calculator import Calculadora


class TestCalculadora(unittest.TestCase):
    def setUp(self) -> None:
        self.calc = Calculadora(max_caracteres=20)

    def escribir(self, botones: str) -> str:
        for boton in botones:
            self.calc.pulsar(boton)
        return self.calc.texto

    def test_operaciones_basicas(self) -> None:
        casos = (("2+3=", "5"), ("8-3=", "5"), ("4*3=", "12"), ("8/2=", "4"))
        for botones, esperado in casos:
            with self.subTest(botones=botones):
                self.calc.pulsar("C")
                self.assertEqual(self.escribir(botones), esperado)

    def test_expresion_encadenada_respeta_precedencia(self) -> None:
        self.assertEqual(self.escribir("2+3*4="), "14")

    def test_division_por_cero_y_recuperacion(self) -> None:
        self.assertEqual(self.escribir("1/0="), "Error")
        self.assertEqual(self.calc.pulsar("+"), "Error")
        self.assertEqual(self.calc.pulsar("7"), "7")

    def test_operadores_seguidos_se_sustituyen(self) -> None:
        self.assertEqual(self.escribir("8+*2="), "16")

    def test_ceros_a_la_izquierda(self) -> None:
        self.assertEqual(self.escribir("007"), "7")
        self.assertEqual(self.escribir("+05"), "7+5")

    def test_decimal_duplicado_se_ignora(self) -> None:
        self.assertEqual(self.escribir("1.2.3"), "1.23")

    def test_decimal_al_inicio_y_negativo(self) -> None:
        self.assertEqual(self.escribir(".5"), "0.5")
        self.calc.pulsar("C")
        self.assertEqual(self.escribir("-.5"), "-0.5")
        self.calc.pulsar("C")
        self.assertEqual(self.escribir("-3+1="), "-2")

    def test_al_principio_solo_se_admite_menos(self) -> None:
        self.assertEqual(self.escribir("+*/"), "")
        self.assertEqual(self.escribir("-+"), "-")

    def test_borrar_y_limpiar(self) -> None:
        self.assertEqual(self.escribir("123<"), "12")
        self.assertEqual(self.calc.pulsar("C"), "")
        self.escribir("1/0=")
        self.assertEqual(self.calc.pulsar("<"), "")

    def test_comportamiento_despues_de_igual(self) -> None:
        self.escribir("2+3=")
        self.assertEqual(self.escribir("+4="), "9")
        self.assertEqual(self.calc.pulsar("7"), "7")

    def test_igual_incompleto_no_hace_nada(self) -> None:
        self.assertEqual(self.calc.pulsar("="), "")
        self.escribir("2+")
        self.assertEqual(self.calc.pulsar("="), "2+")

    def test_limite_de_longitud(self) -> None:
        calc = Calculadora(max_caracteres=4)
        for boton in "12345":
            calc.pulsar(boton)
        self.assertEqual(calc.texto, "1234")


if __name__ == "__main__":
    unittest.main()
