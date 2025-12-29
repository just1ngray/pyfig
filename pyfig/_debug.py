import gc
import weakref
from typing import Any, Generator, TypeVar, List, Tuple, Dict

from pydantic import BaseModel


T = TypeVar("T", bound=BaseModel)

class _IdentityWrapper:
    def __init__(self, obj):
        self.obj = weakref.ref(obj)

        if _gc_callback_access_counter not in gc.callbacks:
            gc.callbacks.append(_gc_callback_access_counter)

    def __hash__(self) -> int:
        return id(self.obj)

    def __eq__(self, other) -> bool:
        return isinstance(other, _IdentityWrapper) and self.obj == other.obj

_ACCESS_COUNTER: Dict[_IdentityWrapper, Dict[str, int]] = {}

def _gc_callback_access_counter(phase, info):
    for idw in _ACCESS_COUNTER.copy().keys():
        if idw.obj() is None:
            _ACCESS_COUNTER.pop(idw)

class PyfigDebug(BaseModel):
    """
    A wrapper class that tracks field use in your configuration.

    This aims to be helpful in identifying config sections that were never used, or are no longer used. They can be
    removed at the discretion of the maintainer.

    Main entrypoint to this feature is via `PyfigDebug.wrap()` static method.

    See:
        `PyfigDebug.wrap()`
    """

    def __getattribute__(self, name: str) -> Any:
        if not name.startswith("__") and name in _ACCESS_COUNTER[_IdentityWrapper(self)]:
            _ACCESS_COUNTER[_IdentityWrapper(self)][name] = _ACCESS_COUNTER[_IdentityWrapper(self)][name] + 1

        return super(BaseModel, self).__getattribute__(name)

    def pyfig_debug_accesses(self) -> Generator[Tuple[str, int], Any, None]:
        """
        Recursive iterator over the fields and how frequently they've been accessed. Ordered to first yield
        shallower config paths before deeper ones.
        """
        for path, num in _pyfig_debug_accesses(self):
            formatted_path = path[0]
            for p in path[1:]:
                if p[0] == "[":
                    formatted_path += p
                else:
                    formatted_path += f".{p}"

            yield (formatted_path, num)

    def pyfig_debug_unused(self) -> Generator[str, Any, None]:
        """
        Reports the highest level path(s) that have not been accessed.

        Note: deeper paths cannot be accessed without their parent being accessed at least once!
        """
        reported: List[str] = []

        for path, n in self.pyfig_debug_accesses():
            if n > 0:
                continue

            if not any(path.startswith(r) for r in reported):
                reported.append(path)
                yield path

    def pyfig_debug_field_accesses(self, field: str) -> int:
        """
        Gets the number of times a specific field has been accessed.

        Args:
            field: the field name to check

        Returns:
            the number of times that the given field has been accessed

        Raises:
            KeyError if the provided field name is not tracked
        """
        return _ACCESS_COUNTER[_IdentityWrapper(self)][field]

    @staticmethod
    def wrap(cfg: T) -> T:
        """
        !! WARNING !! This feature is experimental and may not work properly for configs with untested edge cases.

        Copies a Pyfig and injects behaviour to track the number of times each field is accessed.

        Usage:
            >>> config: Pyfig = load_configuration()
            >>> config = PyfigDebug.wrap(config) if os.environ.get("DEBUG") else config
            >>> # run your app normally
            >>> # ...
            >>> # check how often each field has or hasn't been used
            >>> if isinstance(config, PyfigDebug):
            ...     for path, n in config.pyfig_debug_accesses():
            ...         print(f"{path} accessed {n} times")

        Args:
            cfg: the config to debug

        Returns:
            a subclass tree of cfg instance which should be usable in the same ways as the original `cfg` arg,
            but with additional tracking behaviour that allows you to later check how often each field is used.
        """
        return _wrap(cfg)


def _pyfig_debug_accesses(cfg) -> Generator[Tuple[List[str], int], Any, None]:
    """
    Walks through a config recursively (incl. through selected types of collections) and yields a mapping
    between config paths to the number of times each field has been accessed.
    """
    if isinstance(cfg, PyfigDebug):
        for field_name, num_accessed in _ACCESS_COUNTER[_IdentityWrapper(cfg)].items():
            yield ([field_name], num_accessed)

            value = super(BaseModel, cfg).__getattribute__(field_name)
            for sub_paths, sub_num_accessed in _pyfig_debug_accesses(value):
                yield ([field_name, *sub_paths], sub_num_accessed)

    elif isinstance(cfg, (list, tuple)):
        for i, item in enumerate(cfg):
            for sub_paths, num in _pyfig_debug_accesses(item):
                yield ([f"[{i}]", *sub_paths], num)

    elif isinstance(cfg, dict):
        for k, v in cfg.items():
            for sub_paths, num in _pyfig_debug_accesses(v):
                yield ([f"[{repr(k)}]", *sub_paths], num)


def _wrap(cfg):
    """
    Recursive conversion into the PyfigDebug type.
    """
    if isinstance(cfg, BaseModel):
        debug_class = type(f"{cfg.__class__.__name__}PyfigDebug", (cfg.__class__, PyfigDebug), {})

        new_instance = cfg.model_copy()
        new_instance.__class__ = debug_class
        _ACCESS_COUNTER[_IdentityWrapper(new_instance)] = { field: 0 for field in new_instance.__class__.model_fields }

        for fieldname in new_instance.__class__.model_fields:
            value = super(BaseModel, new_instance).__getattribute__(fieldname)
            setattr(new_instance, fieldname, _wrap(value))

        return new_instance

    elif isinstance(cfg, list):
        return [_wrap(item) for item in cfg]

    elif isinstance(cfg, tuple):
        return tuple(_wrap(item) for item in cfg)

    elif isinstance(cfg, dict):
        return {k: _wrap(v) for k, v in cfg.items()}

    else:
        return cfg
