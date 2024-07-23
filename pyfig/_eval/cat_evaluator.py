from pathlib import Path

from .abstract_evaluator import AbstractEvaluator


class CatEvaluator(AbstractEvaluator):
    """
    Cat's the contents of a file.

    Syntax: "${{cat.some/relative/path}}", optionally with an encoding: "${{cat./absolute/too:utf-8}}"
    """

    def __init__(self, *, trim: bool=True) -> None:
        """
        Whjen `trim` is `True`, the content is stripped of leading and trailing whitespace.
        """
        self._trim = trim

    def name(self) -> str:
        return "cat"

    def evaluate(self, value: str) -> str:
        parts = value.split(":")
        path = Path(parts[0])
        encoding = parts[1] if len(parts) >= 2 else "utf-8"

        content = path.read_text(encoding)
        if self._trim:
            content = content.strip()

        return content
