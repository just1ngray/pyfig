import os
from typing import Any

from .abstract_evaluator import AbstractEvaluator, EvaluationError


class EnvironmentEvaluator(AbstractEvaluator):
    """
    A template evaluator which substitutes the value with an environment variable's value.
    """

    def name(self) -> str:
        return "env"

    def evaluate(self, value: str) -> Any:
        try:
            return os.environ[value]
        except KeyError as exc:
            raise EvaluationError(self, value) from exc
