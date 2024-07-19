import re
import ast
from typing import Any

from .abstract_evaluator import AbstractEvaluator


class StringEvaluator(AbstractEvaluator):
    """
    A template evaluator which is able to perform Python string method operations.

    Syntax: "${{str.method(args)}}", "${{str.upper('to upper')}}"
    """

    def __init__(self) -> None:
        self._pattern = re.compile(r"^(?P<method>[^(]+)\((?P<string>.*)\)$")

    def name(self) -> str:
        return "str"

    def evaluate(self, value: str) -> Any:
        patmatch = self._pattern.search(value)
        if patmatch is None:
            raise ValueError(f"Invalid string format: {value}")

        method = patmatch.group("method")
        string = patmatch.group("string")
        args = ast.literal_eval(f"({string})")
        if not isinstance(args, tuple):
            args = (args,)

        return getattr(str, method)(*args)
