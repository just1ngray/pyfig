from typing import Optional, Any, List, Dict
from pathlib import Path
from enum import Enum

import pytest
from pydantic import ValidationError, ConfigDict

from ._pyfig import Pyfig


def test__given_config_without_default__when_instantiating__then_raise_error():
    with pytest.raises(TypeError):
        class _MyConfig(Pyfig):
            no_default_value: int

def test__given_pyfig_with_standard_types__when_model_dump_dict__then_returns_serialized_dict():
    class RecursiveConfig(Pyfig):
        important: str = "stuff"

    class MyConfig(Pyfig):
        integer: int = 1
        string: str = "hello"
        boolean: bool = True
        array: List[int] = [1, 2, 3]
        dictionary: Dict[str, str] = {"a": "b"}
        recursive: RecursiveConfig = RecursiveConfig()

    conf = MyConfig()
    assert conf.model_dump_dict() == {
        "integer": 1,
        "string": "hello",
        "boolean": True,
        "array": [1, 2, 3],
        "dictionary": {"a": "b"},
        "recursive": {"important": "stuff"}
    }

def test__given_pyfig_with_non_standard_types__when_model_dump_dict__then_return_serialized_dict():
    class SomeEnum(Enum):
        VARIANT1 = "variant1"
        VARIANT2 = "variant2"

    class MyConfig(Pyfig):
        path: Path = Path("/some/path")
        none: Optional[Any] = None
        enumeration: SomeEnum = SomeEnum.VARIANT1

    conf = MyConfig()
    assert conf.model_dump_dict() == {
        "path": "/some/path",
        "none": None,
        "enumeration": "variant1"
    }

def test__given_invalid_default__when_defining_pyfig_class__then_raises_error():
    with pytest.raises(ValidationError):
        class _MyConfig(Pyfig):
            bad_default_value: int = "not an integer"

def test__given_invalid_default__when_defining_pyfig_class_with_config__then_raises_error():
    with pytest.raises(ValidationError):
        class _MyConfig(Pyfig):
            model_config = ConfigDict(frozen=True)
            bad_default_value: int = "not an integer"

def test__given_model_config_validate_default_false__when_defining_pyfig_class__then_no_error():
    class _MyConfig(Pyfig):
        model_config = ConfigDict(validate_default=False)
        bad_default_value: int = "not an integer"
