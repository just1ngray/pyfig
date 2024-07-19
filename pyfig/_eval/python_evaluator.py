from typing import Any

from .abstract_evaluator import AbstractEvaluator


class PythonEvaluator(AbstractEvaluator):
    """
    A template evaluator which evaluates a Python expression.
    This is especially powerful when used with other nested templates.

    It should be used with caution as it can execute arbitrary code.
    """

    def name(self) -> str:
        return "pyeval"

    def evaluate(self, value: str) -> Any:
        # pylint: disable=eval-used
        return eval(value, {}, {})
