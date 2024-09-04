import typing
from typing import Type, TypeVar, Dict, Collection, Any
from collections import deque, defaultdict

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


def _apply_model_config_generic_recursively(generic: Type, new_model_config: ConfigDict) -> Type:
    """
    Given a generic type, applies the `new_model_config` to each `BaseModel` searched recursively.

    Returns:
        a new copy of the type, but with any applicable `model_config` overrides
    """
    if not _is_generic_type(generic):
        raise TypeError(f"Expected generic type, got {generic}")

    origin = typing.get_origin(generic)
    args = typing.get_args(generic)

    modified_args = []
    for arg in args:
        if _is_generic_type(arg):
            modified_args.append(_apply_model_config_generic_recursively(arg, new_model_config))
        elif issubclass(arg, BaseModel):
            derived = _apply_model_config_recursively(arg, new_model_config)
            modified_args.append(derived)
        else:
            modified_args.append(arg)

    # In Python <= 3.8, types like 'list' are not subscriptable, and must be typed using the typing module.
    # This mapping enables us to reconstruct these types in older versions of Python
    old_python_typing_mapping: Dict[Type, Any] = {
        list: typing.List,
        tuple: typing.Tuple,
        dict: typing.Dict,
        set: typing.Set,
        frozenset: typing.FrozenSet,
        deque: typing.Deque,
        defaultdict: typing.DefaultDict,
    }
    if typing_annotation := old_python_typing_mapping.get(origin, None):
        return typing_annotation[tuple(modified_args)]

    try:
        return origin[tuple(modified_args)]
    except TypeError as exc:
        raise TypeError(f"Could not reconstruct generic type {generic}") from exc


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

        if _is_generic_type(field.annotation):
            generic = _apply_model_config_generic_recursively(field.annotation, new_model_config)
            recursive_override_annotations[name] = generic
        elif issubclass(field.annotation, BaseModel):
            recursive = _apply_model_config_recursively(field.annotation, new_model_config)
            recursive_override_annotations[name] = recursive

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
