from typing import Type, TypeVar, Dict

from ._pyfig import Pyfig


T = TypeVar("T", bound=Pyfig)

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

    # apply overrides
    for override in overrides:
        _apply_override_to_conf(conf, override)

    # evaluate ??

    return default(**conf)
