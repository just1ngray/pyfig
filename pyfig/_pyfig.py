import json

from pydantic import BaseModel, ValidationError
from pydantic_core import PydanticUndefined


class Pyfig(BaseModel):
    """
    The base class for all Pyfig configurations. It's basically just a Pydantic model that requires
    all fields to have a default value.

    See: https://docs.pydantic.dev/latest/api/base_model/ for more information on validation, serialization, etc.
    """

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs):
        """
        Validates that all fields have a valid default value
        """
        kwargs = {}

        for name, field in cls.model_fields.items():
            default = field.get_default()
            if default == PydanticUndefined:
                raise TypeError(f"Field '{name}' of '{cls.__qualname__}' must have a default value")

            kwargs[name] = default

        # FIXME: when we are using load_configuration(allow_unused=False), the defaults are no longer valid somehow
        if cls.model_config.get("extra", None) == "forbid":
            return

        # try constructing the class with each of the default values to ensure they are valid
        #
        # pydantic can validate defaults on instance __init__, but this elevates the check to the definition
        # of the config itself
        try:
            cls(**kwargs)
        except ValidationError as e:
            raise TypeError("All default values must be valid") from e


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
