import json

from pydantic import BaseModel


class Pyfig(BaseModel):
    """
    The base class for all Pyfig configurations. It's basically just a Pydantic model that requires
    all fields to have a default value.

    See: https://docs.pydantic.dev/latest/api/base_model/ for more information on validation, serialization, etc.
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


    def model_dump_dict(self) -> dict:
        """
        Dumps the model as a dictionary.

        Performs the same serialization to json-supported types as `model_dump_json`. This means:
            - Enums become their value
            - Path becomes a string
            - None becomes null
            - Etc.

        Returns:
            the data as a dictionary
        """
        plain_json = self.model_dump_json()
        plain_dict = json.loads(plain_json)
        return plain_dict
