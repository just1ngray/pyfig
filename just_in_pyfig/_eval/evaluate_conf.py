import re
from typing import Any, Optional, Collection, Union

from .abstract_evaluator import AbstractEvaluator


def _find_evaluator(name: str, evaluators: Collection[AbstractEvaluator]) -> AbstractEvaluator:
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


_TEMPLATE_PATTERN = re.compile(r"\$\{(?P<evaluator>[A-Za-z0-9_-]*)(\.(?P<value>[^}]*))?\}")


def _evaluate_string(string: str, evaluators: Collection[AbstractEvaluator]) -> Any:
    # if the entire string is a template, evaluate it and keep the type
    if full_match := _TEMPLATE_PATTERN.fullmatch(string):
        evaluator = _find_evaluator(full_match.group("evaluator"), evaluators)
        return evaluator.evaluate(full_match.group("value") or "")

    # otherwise, replace only the relevant substring(s)
    return re.sub(
        _TEMPLATE_PATTERN,
        lambda m: str(_find_evaluator(m.group("evaluator"), evaluators).evaluate(m.group("value") or "")),
        string
    )


def evaluate_conf(conf: Union[list, dict], evaluators: Collection[AbstractEvaluator]) -> None:
    changes = 1

    while changes > 0:
        changes = 0

        if isinstance(conf, dict):
            for key, value in conf.items():
                if isinstance(value, str):
                    new = _evaluate_string(value, evaluators)
                    if new != value:
                        conf[key] = new
                        changes += 1

                elif isinstance(value, (dict, list)):
                    evaluate_conf(value, evaluators)

        elif isinstance(conf, list):
            for i, item in enumerate(conf):
                if isinstance(item, (dict, list)):
                    evaluate_conf(item, evaluators)

                elif isinstance(item, str):
                    new = _evaluate_string(item, evaluators)
                    if new != item:
                        conf[i] = new
                        changes += 1

        else:
            raise TypeError(f"Cannot evaluate conf of unknown type: {type(conf)}")
