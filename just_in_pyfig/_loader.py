from typing import Type, TypeVar, Dict, Iterable

from ._pyfig import Pyfig
from ._override import unify_overrides, apply_overrides


T = TypeVar("T", bound=Pyfig)


def load_configuration(default: Type[T], overrides: Iterable[Dict]) -> T:
    """
    TODO
    """
    conf = default().model_dump() # TODO: consider using 'serialize_as_any' kwarg
    unified_overrides = unify_overrides(*list(overrides))
    apply_overrides(conf, unified_overrides)

    # evaluate ??

    return default(**conf)
