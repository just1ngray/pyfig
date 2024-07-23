from pathlib import Path

from .abstract_evaluator import AbstractEvaluator


class CatEvaluator(AbstractEvaluator):
    """
    Cat's the contents of a file.

    Syntax: "${{cat.some/relative/path}}", optionally with an encoding: "${{cat./absolute/too:utf-8}}"
    """

    def name(self) -> str:
        return "cat"

    def evaluate(self, value: str) -> str:
        parts = value.split(":")
        path = Path(parts[0])
        encoding = parts[1] if len(parts) >= 2 else "utf-8"

        return path.read_text(encoding)