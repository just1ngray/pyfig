from typing import Type, TypeVar, Dict, Iterable, Collection

from ._pyfig import Pyfig
from ._override import unify_overrides, apply_overrides
from ._eval import evaluate_conf, AbstractEvaluator


T = TypeVar("T", bound=Pyfig)


def load_configuration(default: Type[T], overrides: Iterable[Dict], evaluators: Collection[AbstractEvaluator]) -> T:
    """
    TODO
    """
    conf = default().model_dump() # TODO: consider using 'serialize_as_any' kwarg
    unified_overrides = unify_overrides(*list(overrides))
    apply_overrides(conf, unified_overrides)
    evaluate_conf(conf, evaluators)
    return default(**conf)
