from typing import Dict, Any


def _list_element_override_with_error_messaging(src: list, index: Any, override: Any):
    try:
        if type(index) == str:
            index_validated = int(index)
        elif type(index) == int:
            index_validated = index
        else:
            raise ValueError()

        current = src[index_validated]
    except ValueError:
        raise ValueError(f"Error applying override to index in list. '{index}' is not an integer")
    except IndexError:
        raise IndexError(
            f"Error applying override to out of bounds index {index}. List is only {len(src)} elements long"
        )

    # overriding a list element at a nested dict level
    if isinstance(current, dict):
        src[index_validated] = unify_overrides(override, current)

    # overriding a list element with another list element override
    # (we can't just call unify_overrides because it doesn't support lists)
    elif isinstance(current, list) and isinstance(override, dict):
        for sub_override_idx, sub_override_val in override.items():
            _list_element_override_with_error_messaging(current, sub_override_idx, sub_override_val)

    # atomic list element override
    else:
        src[index_validated] = override


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
