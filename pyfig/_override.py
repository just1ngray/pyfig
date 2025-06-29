from typing import Dict, Any


def _list_element_override_with_error_messaging(src: list, index: Any, override: Any):
    try:
        index_validated = int(index)
        current = src[index_validated]
    except ValueError:
        raise ValueError(f"Error applying override to index in list. '{index}' is not an integer")
    except IndexError:
        raise IndexError(
            f"Error applying override to out of bounds index {index}. List is only {len(src)} elements long"
        )

    if not isinstance(current, (dict, list)):
        src[index_validated] = override
        return

    raise NotImplementedError()


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
