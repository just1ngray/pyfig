from abc import ABC, abstractmethod
from typing import Any


class AbstractEvaluator(ABC):
    @abstractmethod
    def name(self) -> str:
        """
        Returns the name of the evaluator this class is responsible for.
        """

    @abstractmethod
    def evaluate(self, value: str) -> Any:
        """
        Evaluates the given value and returns a replacement value.

        E.g., if the configured string is: "hello, ${{name}}!" then the 'name' evaluator is called with empty string.
        E.g., if the configured string is: "hello, ${{var.name}}!" then the 'var' evaluator is called 'name'.

        Args:
            value: The value to evaluate (does not include the evaluator name or braces from the original string)
        """
