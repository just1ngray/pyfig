from typing import Dict


def unify_overrides(*overrides: Dict) -> Dict:
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
                unified[key] = unify_overrides(value, unified[key])
            else:
                unified[key] = value

    return unified


def apply_overrides(conf: Dict, override: Dict, trace: str="") -> None:
    """
    Using a base configuration, applies an override to it.

    The override is applied at the lowest possible dictionary-key level.

    Args:
        conf:       the base configuration
        override:   the override to apply
        trace:      the current trace of the configuration

    Returns:
        None (mutates `conf` in place)
    """
    for key, value in override.items():
        if key not in conf:
            conf[key] = value
        elif isinstance(conf[key], dict) and isinstance(value, dict):
            apply_overrides(conf[key], value, trace=f"{trace}.{key}")
        else:
            conf[key] = value
