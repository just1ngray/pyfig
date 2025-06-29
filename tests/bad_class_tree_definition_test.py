from pydantic import ValidationError, Field
import pytest

from pyfig import Pyfig


def test__given_no_defaults__when_define_pyfig_class__then_raises():
    with pytest.raises(TypeError):
        class MyConfig(Pyfig):
            foo: int = 1
            bar: float
            baz: str = "bar is missing a default value!"

def test__given_bad_defaults__when_define_pyfig_class__then_raises():
    with pytest.raises(ValidationError):
        class MyConfig(Pyfig):
            foo: int = 3.14

    with pytest.raises(ValidationError):
        class MyConfig(Pyfig):
            foo: int = Field(default="bar")
