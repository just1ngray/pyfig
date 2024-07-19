import json
from pathlib import Path
from typing import Any

from .abstract_evaluator import AbstractEvaluator


class JSONFileEvaluator(AbstractEvaluator):
    """
    An evaluator that reads a field from a JSON file.

    Syntax: "${{jsonfile.access.path.to.field:/path/to/file.json}}"
    """

    def name(self) -> str:
        return "jsonfile"

    def evaluate(self, value: str) -> Any:
        colon = value.rfind(":")
        if colon == -1:
            raise ValueError("Invalid syntax for JSON file evaluator. Should follow '<access.path>.</disk/path.json>'")

        accessor = value[:colon]
        diskpath = value[colon + 1:]

        with Path(diskpath).open("rb") as jsonfile:
            jsondata = json.load(jsonfile)

        for key in accessor.split("."):
            if isinstance(jsondata, list):
                try:
                    key = int(key)
                except ValueError as exc:
                    raise KeyError("Array index cannot be referenced by a string") from exc

                jsondata = jsondata[key]
            elif isinstance(jsondata, dict):
                jsondata = jsondata[key]
            else:
                raise KeyError("Unknown json data type. Expected dict or list.")

        return jsondata
