from typing import Any, Generator, TypeVar, List, Tuple

from pydantic import BaseModel


T = TypeVar("T", bound=BaseModel)

_ACCESS_COUNTER = "_pyfig_debug_access_counter"


class PyfigDebug(BaseModel):
    def __getattribute__(self, name: str) -> Any:
        if name != "__class__" and name in super().__getattribute__(_ACCESS_COUNTER):
            counter = super().__getattribute__(_ACCESS_COUNTER)
            counter[name] = counter[name] + 1

        return super().__getattribute__(name)

    def pyfig_debug_accesses(self) -> Generator[Tuple[str, int], Any, None]:
        """
        Recursive iterator over the fields and how frequently they've been accessed. Ordered to first yield
        shallower config paths before deeper ones.
        """
        field_name: str
        num_accessed: int
        for field_name, num_accessed in super().__getattribute__(_ACCESS_COUNTER).items():
            yield (field_name, num_accessed)

            value = super().__getattribute__(field_name)
            if isinstance(value, PyfigDebug):
                for sub_field_name, sub_num_accessed in value.pyfig_debug_accesses():
                    yield (f"{field_name}.{sub_field_name}", sub_num_accessed)
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if not isinstance(item, PyfigDebug):
                        continue
                    for sub_field_name, sub_num_accessed in item.pyfig_debug_accesses():
                        yield (f"{field_name}[{i}].{sub_field_name}", sub_num_accessed)

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
    def wrap(cfg: T) -> T:
        """
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
        debug_class = type(f"{cfg.__class__.__name__}PyfigDebug", (cfg.__class__, PyfigDebug), {})

        new_instance = cfg.model_copy()
        new_instance.__class__ = debug_class
        setattr(new_instance, _ACCESS_COUNTER, {})

        for fieldname in new_instance.__class__.model_fields:
            value = getattr(new_instance, fieldname)

            if isinstance(value, BaseModel):
                setattr(new_instance, fieldname, PyfigDebug.wrap(value))
            elif isinstance(value, list):
                setattr(new_instance, fieldname, [PyfigDebug.wrap(element) for element in value])

        # start tracking now
        getattr(new_instance, _ACCESS_COUNTER).update({ field: 0 for field in new_instance.__class__.model_fields })

        return new_instance
