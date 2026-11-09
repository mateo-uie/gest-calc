"""Estado y reglas de una calculadora básica, sin dependencias gráficas."""

import math

import config


class Calculadora:
    """Procesa botones y conserva la expresión que se muestra en pantalla.

    La clase no conoce OpenCV ni MediaPipe. Esta separación permite probar todas
    las reglas con datos sintéticos y reutilizar la lógica con otra interfaz.
    """

    OPERADORES = "+-*/"
    CARACTERES_PERMITIDOS = set("0123456789.+-*/")

    def __init__(self, max_caracteres: int) -> None:
        self.max_caracteres = max_caracteres
        self.texto = ""
        self.resultado_reciente = False

    def pulsar(self, valor: str) -> str:
        """Aplica un botón y devuelve el texto que debe mostrar el display."""
        if valor == "C":
            self._reiniciar()
        elif valor == "<":
            self._borrar()
        elif valor.isdigit() and len(valor) == 1:
            self._agregar_digito(valor)
        elif valor == ".":
            self._agregar_decimal()
        elif valor in self.OPERADORES:
            self._agregar_operador(valor)
        elif valor == "=":
            self._evaluar()
        return self.texto

    def _reiniciar(self) -> None:
        self.texto = ""
        self.resultado_reciente = False

    def _borrar(self) -> None:
        # Error no es una expresión editable: borrar lo limpia por completo.
        self.texto = "" if self.texto == "Error" else self.texto[:-1]
        self.resultado_reciente = False

    def _hay_espacio(self, cantidad: int = 1) -> bool:
        return len(self.texto) + cantidad <= self.max_caracteres

    def _inicio_numero_actual(self) -> int:
        """Localiza el inicio del operando situado al final de la expresión."""
        inicio = 0
        for indice, caracter in enumerate(self.texto):
            if caracter in self.OPERADORES:
                # Un menos al inicio es el signo del primer número, no un separador.
                if indice == 0 and caracter == "-":
                    continue
                inicio = indice + 1
        return inicio

    def _agregar_digito(self, digito: str) -> None:
        if self.texto == "Error" or self.resultado_reciente:
            self.texto = ""
            self.resultado_reciente = False

        inicio = self._inicio_numero_actual()
        numero_actual = self.texto[inicio:]
        # Sustituir el cero evita expresiones como 007, inválidas para eval en Python.
        if numero_actual == "0":
            self.texto = self.texto[:inicio] + digito
        elif self._hay_espacio():
            self.texto += digito

    def _agregar_decimal(self) -> None:
        if self.texto == "Error":
            self.texto = ""
        if self.resultado_reciente:
            self.texto = ""
            self.resultado_reciente = False

        inicio = self._inicio_numero_actual()
        numero_actual = self.texto[inicio:]
        if "." in numero_actual:
            return

        # Es más claro mostrar 0. que un punto aislado al comenzar un operando.
        # El menos inicial pertenece al signo, pero todavía no hay cifras.
        empieza_numero = numero_actual == "" or self.texto == "-"
        prefijo = "0." if empieza_numero else "."
        if self._hay_espacio(len(prefijo)):
            self.texto += prefijo

    def _agregar_operador(self, operador: str) -> None:
        if self.texto == "Error":
            return
        self.resultado_reciente = False

        if not self.texto:
            if operador == "-" and self._hay_espacio():
                self.texto = "-"
            return

        if self.texto[-1] in self.OPERADORES:
            # Un menos aislado sigue siendo el signo inicial: no se puede cambiar
            # por un operador que la especificación prohíbe al comienzo.
            if self.texto == "-":
                return
            # Se sustituye el operador para corregir una pulsación sin borrar.
            self.texto = self.texto[:-1] + operador
        elif self._hay_espacio():
            self.texto += operador

    def _evaluar(self) -> None:
        if not self.texto or self.texto == "Error" or self.texto[-1] in self.OPERADORES:
            return

        # La lista blanca impide nombres, llamadas, espacios y cualquier sintaxis
        # ajena a la aritmética. Además, la entrada procede únicamente de botones.
        # Con builtins vacíos, eval queda limitado aquí a números y cuatro operadores.
        if any(caracter not in self.CARACTERES_PERMITIDOS for caracter in self.texto):
            self.texto = "Error"
            self.resultado_reciente = False
            return

        try:
            resultado = eval(self.texto, {"__builtins__": {}}, {})
            if not isinstance(resultado, (int, float)) or not math.isfinite(resultado):
                raise ValueError("resultado no finito")
            self.texto = self._formatear_resultado(resultado)
            if len(self.texto) > self.max_caracteres:
                raise ValueError("resultado demasiado largo")
            self.resultado_reciente = True
        except (ArithmeticError, SyntaxError, ValueError, TypeError):
            self.texto = "Error"
            self.resultado_reciente = False

    @staticmethod
    def _formatear_resultado(resultado: float | int) -> str:
        """Evita '.0' y limita los decimales a diez cifras significativas."""
        if isinstance(resultado, int) or float(resultado).is_integer():
            return str(int(resultado))
        return format(float(resultado), f".{config.RESULT_SIGNIFICANT_DIGITS}g")
