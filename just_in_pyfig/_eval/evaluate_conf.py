import re
from typing import Any, Iterable, Optional

from .abstract_evaluator import AbstractEvaluator


def _find_evaluator(name: str, evaluators: Iterable[AbstractEvaluator]) -> AbstractEvaluator:
    candidate: Optional[AbstractEvaluator] = None

    for evaluator in evaluators:
        if evaluator.name() == name:
            if candidate is not None:
                raise ValueError(f"Multiple evaluators found for name: '{name}'")

            candidate = evaluator

    if candidate is None:
        raise ValueError(f"No evaluator found for name: '{name}'")
    else:
        return candidate


_TEMPLATE_PATTERN = re.compile(r"\$\{(?P<evaluator>[A-Za-z0-9_-]*)\.(?P<value>[^}]*)\}")


def _evaluate_string(string: str, evaluators: Iterable[AbstractEvaluator]) -> Any:
    # if the entire string is a template, evaluate it and keep the type
    if full_match := _TEMPLATE_PATTERN.fullmatch(string):
        evaluator = _find_evaluator(full_match.group("evaluator"), evaluators)
        return evaluator.evaluate(full_match.group("value"))

    # otherwise, replace only the relevant substring(s)
    return re.sub(
        _TEMPLATE_PATTERN,
        lambda m: str(_find_evaluator(m.group("evaluator"), evaluators).evaluate(m.group("value"))),
        string
    )


def evaluate(conf: dict) -> dict:
    """
    Evaluate the configuration dictionary by replacing templated values
    """
    return conf
