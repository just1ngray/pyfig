import typing
from typing import Type, TypeVar, Dict, Collection, Any

from pydantic import BaseModel, ConfigDict

from ._pyfig import Pyfig
from ._override import unify_overrides, apply_overrides
from ._eval import AbstractEvaluator
from ._evaluate_conf import evaluate_conf


def _is_generic_type(t: Any) -> bool:
    """
    Checks if a given object is a generic type.

    Returns:
        true if the object is a generic type, false otherwise
    """
    return hasattr(t, "__origin__") and t.__origin__ is not None


def _apply_model_config_recursively(model: Type[BaseModel], new_model_config: ConfigDict) -> Type[BaseModel]:
    """
    Creates a distinct class tree which mirrors `model`, but with a particular `model_config`
    applied to each (sub)class.

    If a model already has a config, then the `new_model_config` will be applied as override(s).
    """
    recursive_override_annotations = {}
    for name, field in model.model_fields.items():
        if field.annotation is None:
            continue

        if issubclass(field.annotation, BaseModel):
            recursive = _apply_model_config_recursively(field.annotation, new_model_config)
            recursive_override_annotations[name] = recursive

        elif typing.get_origin(field.annotation) in [typing.Union, typing.List, typing.Tuple, typing.Dict]:
            raise NotImplementedError()


    class DerivedModel(model):
        model_config = {**model.model_config, **new_model_config} # type: ignore
        __annotations__ = recursive_override_annotations

    return DerivedModel


T = TypeVar("T", bound=Pyfig)


def load_configuration(
    default: Type[T],
    overrides: Collection[Dict],
    evaluators: Collection[AbstractEvaluator],
    *,
    allow_unused: bool=True
) -> T:
    """
    Loads the configuration into the `default` type, using `overrides`, and consulting the given `evaluators`.

    Args:
        default:        the default configuration type
        overrides:      the configuration overrides (descending priority)
        evaluators:     the evaluators to consult
        allow_unused:   true if fields in overriding dictionaries can be unused if they are not required;
                        false means that unused override fields will raise validation errors

    Returns:
        the loaded configuration

    Raises:
        when the configuration cannot be built
    """
    conf = default().model_dump()
    unified_overrides = unify_overrides(*overrides)
    apply_overrides(conf, unified_overrides)
    evaluate_conf(conf, evaluators)

    if not allow_unused:
        default = _apply_model_config_recursively(default, ConfigDict(extra="forbid")) # type: ignore

    return default(**conf)
