import json

from pydantic import BaseModel, ConfigDict
from pydantic_core import PydanticUndefined


class Pyfig(BaseModel):
    """
    The base class for all Pyfig configurations. It's basically just a Pydantic model that requires
    all fields to have a default value.

    See: https://docs.pydantic.dev/latest/api/base_model/ for more information on validation, serialization, etc.
    """

    model_config = ConfigDict(validate_default=True)

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs):
        """
        Validates that all fields have a default value.
        """
        for name, field in cls.model_fields.items():
            if field.get_default() == PydanticUndefined:
                raise TypeError(f"Field '{name}' of '{cls.__qualname__}' must have a default value")

        # Construct the class once to see if the defaults are valid.
        # 1. This makes defining a Pyfig class with bad defaults raise a ValidationError, rather than waiting for an
        #    instance of the class to be constructed.
        # 2. _pyfig_defaults_validated is set so we only validate the class's defaults once. This prevents issues with
        #    Derived* classes with different model config
        if not hasattr(cls, "_pyfig_defaults_validated"):
            cls()
            setattr(cls, "_pyfig_defaults_validated", True)


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
