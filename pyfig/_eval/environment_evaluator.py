import os
from typing import Any

from .abstract_evaluator import AbstractEvaluator


class EnvironmentEvaluator(AbstractEvaluator):
    """
    A template evaluator which substitutes the value with an environment variable's value.

    Syntax: "${{env.VARIABLE_NAME}}"
    """

    def name(self) -> str:
        return "env"

    def evaluate(self, value: str) -> Any:
        return os.environ[value]
