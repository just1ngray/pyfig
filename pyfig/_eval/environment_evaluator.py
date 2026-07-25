from __future__ import annotations

import os
from typing import Any

from .abstract_evaluator import AbstractEvaluator


class _NotSpecified:
    pass

class EnvironmentEvaluator(AbstractEvaluator):
    """
    A template evaluator which substitutes the value with an environment variable's value.
    A default evaluation can be provided in case the environment variable is not set (opt-in).

    Syntax: "${{env.VARIABLE_NAME}}"
    """
    def __init__(self, *,
        default: Any | _NotSpecified = _NotSpecified,
        defaults: dict[str, Any] | None = None,
    ):
        """
        Priority levels:
            1. If the environment variable is set, return its value
            2. If defaults has a default value for this variable name, then return it
            3. If default is specified, return it
            4. Otherwise, raise a KeyError

        Args:
            default:  the default value when the environment variable is not found
            defaults: a mapping of default values for when specific environment variables are not found
        """
        self._default = default
        self._defaults = defaults or {}

    def name(self) -> str:
        return "env"

    def evaluate(self, value: str) -> Any:
        found = os.environ.get(value, None)
        if found is not None:
            return found

        if self._defaults is not None:
            mapped = self._defaults.get(value, _NotSpecified)
            if mapped is not _NotSpecified:
                return mapped

        if self._default is not _NotSpecified:
            return self._default

        raise KeyError(f"Environment variable not found without any suitable default: {value}")
