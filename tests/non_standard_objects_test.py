from pathlib import Path
from enum import Enum
from typing import Any

from pydantic import SecretStr, ConfigDict
from pydantic_core import core_schema
from pyfig import Pyfig, load_configuration


class CustomObject:
    def __init__(self, value: Any):
        self.value = value

    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type, _handler):
        return core_schema.no_info_before_validator_function(
            lambda v: v if isinstance(v, cls) else cls(v),
            core_schema.any_schema(),
            serialization=core_schema.plain_serializer_function_ser_schema(lambda v: v.value),
        )

class AnEnum(Enum):
    VARIANT_1 = "VARIANT_1"
    VARIANT_2 = "VARIANT_2"

class Config(Pyfig):
    enumeration: AnEnum = AnEnum.VARIANT_1
    path: Path = Path("example.txt")
    password: SecretStr = SecretStr("foo")
    custom: CustomObject = CustomObject("custom object!")


def test__given_config__when_model_dump_json__then_serializes_appropriately():
    assert Config().model_dump_json(indent=4) == """{
    "enumeration": "VARIANT_1",
    "path": "example.txt",
    "password": "**********",
    "custom": "custom object!"
}"""

def test__given_no_overrides__when_load_configuration__then_all_defaults():
    config = load_configuration(Config, [], [])
    assert config.enumeration == AnEnum.VARIANT_1
    assert config.path == Path("example.txt")
    assert config.password == SecretStr("foo")
    assert config.custom.value == "custom object!"

def test__given_enum_override__when_load_configuration__then_finds_variant():
    config = load_configuration(Config, [{ "enumeration": "VARIANT_1" }], [])
    assert config.enumeration == AnEnum.VARIANT_1
    config = load_configuration(Config, [{ "enumeration": "VARIANT_2" }], [])
    assert config.enumeration == AnEnum.VARIANT_2

def test__given_path_override__when_load_configuration__then_converts_str_to_path():
    config = load_configuration(Config, [{ "path": "overridden.txt" }], [])
    assert config.path == Path("overridden.txt")

def test__given_password_override__when_load_configuration__then_converts_to_secretstr():
    config = load_configuration(Config, [{ "password": "admin" }], [])
    assert config.password == SecretStr("admin")

def test__given_custom_override__when_load_configuration__then_constructs_custom_instance():
    config = load_configuration(Config, [{ "custom": 1234 }], [])
    assert isinstance(config.custom, CustomObject)
    assert config.custom.value == 1234
