from typing import Any

from .abstract_evaluator import AbstractEvaluator


class SympyEvaluator(AbstractEvaluator):
    """
    A template evaluator which is used to evaluate mathematical expressions using sympy.

    If all numbers are integers, the result will be rounded to the nearest integer.

    Syntax: "${{sympy.3+5}}" = 8, "${{sympy.2/3}}" = 1, "${{sympy.2.0/3.0}}" = 0.667, "${{sympy.sqrt(4)}}" = 2
    """

    def __init__(self):
        try:
            import sympy
        except ImportError as exc:
            raise ImportError("sympy is not installed. Please install it using `pip install sympy`") from exc
        self._sympy = sympy

    def name(self) -> str:
        return "sympy"

    def evaluate(self, value: str) -> Any:
        evaluated_float = self._sympy.sympify(value).evalf()
        if "." not in value:
            return round(evaluated_float)
        else:
            return evaluated_float
