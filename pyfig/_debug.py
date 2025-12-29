from typing import Any, Generator, TypeVar, List, Tuple, Union

from pydantic import BaseModel


T = TypeVar("T", bound=BaseModel)

_ACCEPTED_INPUT_TYPES = (BaseModel, list, dict)
W = TypeVar("W", BaseModel, list, dict)

_ACCESS_COUNTER = "_pyfig_debug_access_counter"


class PyfigDebug(BaseModel):
    def __getattribute__(self, name: str) -> Any:
        if name != "__class__" and name in super().__getattribute__(_ACCESS_COUNTER):
            counter = super().__getattribute__(_ACCESS_COUNTER)
            counter[name] = counter[name] + 1

        return super().__getattribute__(name)

    @staticmethod
    def _pyfig_debug_accesses(cfg: Union["PyfigDebug", list, dict]) -> Generator[Tuple[List[str], int], Any, None]:
        accepted = (PyfigDebug, list, dict)

        if isinstance(cfg, PyfigDebug):
            for field_name, num_accessed in getattr(cfg, _ACCESS_COUNTER).items():
                yield ([field_name], num_accessed)

                value = super(BaseModel, cfg).__getattribute__(field_name)
                if isinstance(value, accepted):
                    for sub_paths, sub_num_accessed in PyfigDebug._pyfig_debug_accesses(value):
                        yield ([field_name, *sub_paths], sub_num_accessed)
            return

        elif isinstance(cfg, list):
            for i, item in enumerate(cfg):
                if isinstance(item, accepted):
                    for sub_paths, num in PyfigDebug._pyfig_debug_accesses(item):
                        yield ([f"[{i}]", *sub_paths], num)

        elif isinstance(cfg, dict):
            for k, v in cfg.items():
                if isinstance(v, accepted):
                    for sub_paths, num in PyfigDebug._pyfig_debug_accesses(v):
                        yield ([f"[{repr(k)}]", *sub_paths], num)

        elif isinstance(cfg, accepted):
            raise NotImplementedError()

        else:
            raise TypeError()


    def pyfig_debug_accesses(self) -> Generator[Tuple[str, int], Any, None]:
        """
        Recursive iterator over the fields and how frequently they've been accessed. Ordered to first yield
        shallower config paths before deeper ones.
        """
        for path, num in PyfigDebug._pyfig_debug_accesses(self):
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
        return super().__getattribute__(_ACCESS_COUNTER)[field]

    @staticmethod
    def _wrap(cfg: Union[BaseModel, list]):
        if isinstance(cfg, BaseModel):
            debug_class = type(f"{cfg.__class__.__name__}PyfigDebug", (cfg.__class__, PyfigDebug), {})

            new_instance = cfg.model_copy()
            new_instance.__class__ = debug_class
            setattr(new_instance, _ACCESS_COUNTER, { field: 0 for field in new_instance.__class__.model_fields })

            for fieldname in new_instance.__class__.model_fields:
                value = super(BaseModel, new_instance).__getattribute__(fieldname)
                if isinstance(value, _ACCEPTED_INPUT_TYPES):
                    setattr(new_instance, fieldname, PyfigDebug._wrap(value))

            return new_instance

        elif isinstance(cfg, list):
            wrapped = []
            for item in cfg:
                if isinstance(item, _ACCEPTED_INPUT_TYPES):
                    wrapped.append(PyfigDebug._wrap(item))
                else:
                    wrapped.append(item)
            return wrapped

        elif isinstance(cfg, dict):
            wrapped = {}
            for k, v in cfg.items():
                if isinstance(v, _ACCEPTED_INPUT_TYPES):
                    wrapped[k] = PyfigDebug._wrap(v)
                else:
                    wrapped[k] = v
            return wrapped

        elif isinstance(cfg, _ACCEPTED_INPUT_TYPES):
            raise NotImplementedError()

        else:
            raise TypeError()

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
        return PyfigDebug._wrap(cfg)
