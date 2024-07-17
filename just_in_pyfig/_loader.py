from typing import Type, TypeVar, Dict

from ._pyfig import Pyfig


T = TypeVar("T", bound=Pyfig)

def _unify_overrides(*overrides: Dict) -> Dict:
    """
    Configuration overrides are unified by merging them together at a dictionary-key level. This means that if a key
    is present in multiple overrides, the last one will take precedence. Overrides are always performed at the lowest
    dictionary level possible.

    Args:
        overrides: descending order of precedence

    Returns:
        the unified override dictionary
    """
    unified = {}

    for override in reversed(overrides):
        for key, value in override.items():
            if key in unified and isinstance(value, dict) and isinstance(unified[key], dict):
                unified[key] = _unify_overrides(value, unified[key])
            else:
                unified[key] = value

    return unified


def _apply_override_to_conf(conf: Dict, override: Dict, trace: str="") -> Dict:
    for key, value in override.items():
        if key not in conf:
            # TODO: consider logging a warning instead depending on some argument
            raise KeyError(f"Unknown key '{key}' in override ({trace or 'root'})")

        if isinstance(value, dict):
            _apply_override_to_conf(conf[key], value, trace=f"{trace}.{key}")
        else:
            conf[key] = value

    return conf


def load_configuration(default: Type[T], *overrides: Dict) -> T:
    # find the default configuration
    conf = default().model_dump() # TODO: consider using 'serialize_as_any' kwarg

    # unify the overrides into a single dict, with the first one taking precedence
    unified_overrides = _unify_overrides(*overrides)

    # apply overrides
    _apply_override_to_conf(conf, unified_overrides)

    # evaluate ??

    return default(**conf)
