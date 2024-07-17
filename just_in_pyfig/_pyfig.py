from pydantic import BaseModel


class Pyfig(BaseModel):
    """
    TODO
    """

    @classmethod
    def __init_subclass__(cls, **kwargs):
        """
        Validates that all fields have a default value.
        """
        super().__init_subclass__(**kwargs)
        for name in cls.__annotations__.keys():
            if not hasattr(cls, name):
                raise TypeError(f"Field '{name}' of '{cls.__qualname__}' must have a default value")
