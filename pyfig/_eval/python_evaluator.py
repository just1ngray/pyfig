from typing import Any

from .abstract_evaluator import AbstractEvaluator


class PythonEvaluator(AbstractEvaluator):
    """
    A template evaluator which evaluates a Python expression.
    This is especially powerful when used with other nested templates.

    It should be used with caution as it can execute arbitrary code.

    Syntax: "${{pyeval:1 + 1}}"
    """

    def __init__(self, *, danger: str = "not_accepted"):
        if danger != "accepted":
            raise RuntimeError(
                "This evaluator is dangerous because it can execute arbitrary python code. It should "
                "only be used with caution. If you understand the risks, set exactly danger='accepted'"
            )

    def name(self) -> str:
        return "pyeval"

    def evaluate(self, value: str) -> Any:
        # pylint: disable=eval-used
        return eval(value, {}, {})
