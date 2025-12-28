from typing import Any, TypeVar

from pydantic import BaseModel


T = TypeVar("T", bound=BaseModel)


_ACCESS_COUNTER = "_pyfig_debug_access_counter"


class PyfigDebug(BaseModel):
    def __getattribute__(self, name: str) -> Any:
        if name != "__class__" and name in super().__getattribute__(_ACCESS_COUNTER):
            counter = super().__getattribute__(_ACCESS_COUNTER)
            counter[name] = counter[name] + 1

        return super().__getattribute__(name)

    def pyfig_debug_accessed(self):
        field_name: str
        num_accessed: int
        for field_name, num_accessed in super().__getattribute__(_ACCESS_COUNTER).items():
            yield (field_name, num_accessed)

            value = super().__getattribute__(field_name)
            if isinstance(value, PyfigDebug):
                for sub_field_name, sub_num_accessed in value.pyfig_debug_accessed():
                    yield (f"{field_name}.{sub_field_name}", sub_num_accessed)


def pyfig_debug(cfg: T) -> T:
    debug_class = type(f"{cfg.__class__.__name__}PyfigDebug", (cfg.__class__, PyfigDebug), {})

    new_instance = cfg.model_copy()
    new_instance.__class__ = debug_class
    setattr(new_instance, _ACCESS_COUNTER, {})

    for fieldname in new_instance.__class__.model_fields:
        value = getattr(new_instance, fieldname)

        if isinstance(value, BaseModel):
            setattr(new_instance, fieldname, pyfig_debug(value))

    # start tracking now
    getattr(new_instance, _ACCESS_COUNTER).update({ field: 0 for field in new_instance.__class__.model_fields })

    return new_instance


class Nested(BaseModel):
    baz: str = "baz"

class Example(BaseModel):
    foo: str = "foo"
    bar: Nested = Nested()


ex = Example()
print(type(ex))
print(ex)
print(ex.foo)
print(ex.model_dump_json(indent=4))

print("---")

ex_debug = pyfig_debug(ex)
print(type(ex_debug))
print(list(ex_debug.pyfig_debug_accessed()))
print(ex_debug.foo)
print(list(ex_debug.pyfig_debug_accessed()))
print(ex_debug.foo)
print(list(ex_debug.pyfig_debug_accessed()))
print(ex_debug.model_dump_json(indent=4))

print("---")

print(type(ex))
print(ex)
print(ex.foo)
print(ex.model_dump_json(indent=4))

print("---")
print(list(ex_debug.pyfig_debug_accessed()))
