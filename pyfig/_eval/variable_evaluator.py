from typing import Any

from .abstract_evaluator import AbstractEvaluator, EvaluationError


class VariableEvaluator(AbstractEvaluator):
    """
    A simple evaluator which enables variable interpolation for values known at initialization time.

    Syntax: "${{var.known_variable}}"
    """
    def __init__(self, **variables: Any):
        self._variables = variables

    def name(self) -> str:
        return "var"

    def evaluate(self, value: str) -> Any:
        try:
            return self._variables[value]
        except KeyError as exc:
            raise EvaluationError(self, value) from exc
