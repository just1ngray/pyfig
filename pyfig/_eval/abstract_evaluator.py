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

        Raises:
            EvaluationError: If the evaluation fails for some reason
        """

class EvaluationError(Exception):
    """
    A base exception type for when a string evaluation fails.
    """
    def __init__(self, evaluator: AbstractEvaluator, value: str):
        super().__init__(f"Failed to evaluate '{value}' with evaluator '{evaluator.name()}' ({type(evaluator)})")
        self._evaluator = evaluator
        self._value = value
