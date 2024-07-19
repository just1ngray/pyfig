from typing import Type, TypeVar, Dict, Collection

from ._pyfig import Pyfig
from ._override import unify_overrides, apply_overrides
from ._eval import AbstractEvaluator
from ._evaluate_conf import evaluate_conf


T = TypeVar("T", bound=Pyfig)


def load_configuration(default: Type[T], overrides: Collection[Dict], evaluators: Collection[AbstractEvaluator]) -> T:
    """
    Loads the configuration into the `default` type, using `overrides`, and consulting the given `evaluators`.

    Args:
        default:    the default configuration type
        overrides:  the configuration overrides (descending priority)
        evaluators: the evaluators to consult

    Returns:
        the loaded configuration

    Raises:
        when the configuration cannot be built
    """
    conf = default().model_dump()
    unified_overrides = unify_overrides(*overrides)
    apply_overrides(conf, unified_overrides)
    evaluate_conf(conf, evaluators)
    return default(**conf)
