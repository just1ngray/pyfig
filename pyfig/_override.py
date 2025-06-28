from typing import Dict, Any


def _list_element_override_with_error_messaging(src: list, index: Any, override: Any):
    try:
        src[int(index)] = override
    except ValueError:
        raise ValueError(f"Error applying override to index in list. '{index}' is not an integer")
    except IndexError:
        raise IndexError(
            f"Error applying override to out of bounds index {index}. List is only {len(src)} elements long"
        )


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
            # recursive override at lower dict level
            if key in unified and isinstance(value, dict) and isinstance(unified[key], dict):
                unified[key] = unify_overrides(value, unified[key])
                continue

            # override a list element: if we are targeting a list with an override like { "n": X }, then index n
            # should be assigned X
            if key in unified and isinstance(unified[key], list) and isinstance(value, dict):
                for element_idx, element_override in value.items():
                    _list_element_override_with_error_messaging(unified[key], element_idx, element_override)
                continue

            # plain assignment
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
        elif isinstance(conf[key], list) and isinstance(value, dict):
            for idx, override_element in value.items():
                _list_element_override_with_error_messaging(conf[key], idx, override_element)
        else:
            conf[key] = value
