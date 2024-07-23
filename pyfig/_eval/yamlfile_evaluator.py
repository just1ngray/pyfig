from pathlib import Path
from typing import Any

from .abstract_evaluator import AbstractEvaluator


class YamlFileEvaluator(AbstractEvaluator):
    """
    An evaluator that reads a field from a yaml file.

    Syntax: "${{pyyaml.access.path.to.field:/path/to/file.yaml}}"
    """

    def __init__(self) -> None:
        try:
            import yaml
        except ImportError as exc:
            raise ImportError("The pyyaml module is required to use the pyyaml evaluator") from exc

        self._yaml = yaml

    def name(self) -> str:
        return "pyyaml"

    def evaluate(self, value: str) -> Any:
        colon = value.rfind(":")
        if colon == -1:
            raise ValueError("Invalid syntax for yaml file evaluator. Should follow '<access.path>.</disk/path.yaml>'")

        accessor = value[:colon]
        diskpath = value[colon + 1:]

        with Path(diskpath).open("rb") as file:
            yamldata = self._yaml.safe_load(file)

        for key in accessor.split("."):
            if isinstance(yamldata, list):
                try:
                    key = int(key)
                except ValueError as exc:
                    raise KeyError("Array index cannot be referenced by a string") from exc

                yamldata = yamldata[key]
            elif isinstance(yamldata, dict):
                yamldata = yamldata[key]
            else:
                raise KeyError("Unknown json data type. Expected dict or list.")

        return yamldata
