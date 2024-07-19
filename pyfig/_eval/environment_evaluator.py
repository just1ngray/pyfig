import os
from typing import Any, Union

from .abstract_evaluator import AbstractEvaluator


class _NotSpecified:
    pass

class EnvironmentEvaluator(AbstractEvaluator):
    """
    A template evaluator which substitutes the value with an environment variable's value.
    A default evaluation can be provided in case the environment variable is not set (opt-in).

    Syntax: "${{env.VARIABLE_NAME}}"
    """
    def __init__(self, *, default: Union[Any, _NotSpecified] = _NotSpecified):
        self._default = default

    def name(self) -> str:
        return "env"

    def evaluate(self, value: str) -> Any:
        if self._default is _NotSpecified:
            return os.environ[value]

        return os.environ.get(value, self._default)
