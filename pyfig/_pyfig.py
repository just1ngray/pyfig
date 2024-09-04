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
            # if the pyfig class includes inherited fields, the default may be defined by the parent class
            found_default = False
            for pcls in [cls, *cls.__bases__]:
                if not hasattr(pcls, name):
                    found_default = True
                    break
            if not found_default:
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
