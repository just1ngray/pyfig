import pytest
from pydantic import BaseModel, ConfigDict, ValidationError

from ._loader import _apply_model_config_recursively


def test__given_simple_model__when_apply_model_config_recursively__then_model_config_set():
    class SimpleModel(BaseModel):
        foo: int
        bar: str

    config_dict = ConfigDict(extra="forbid")
    ModifiedSimpleModel = _apply_model_config_recursively(SimpleModel, config_dict)

    kwargs = {
        "foo": 0,
        "bar": "",
        "baz": True
    }

    _baz_arg_is_ignored = SimpleModel(**kwargs)
    with pytest.raises(ValidationError):
        _baz_arg_causes_validation_err = ModifiedSimpleModel(**kwargs)


def test__given_simple_model_with_existing_config__when_apply_new_config__then_config_is_merged():
    class SimpleModel(BaseModel):
        model_config = ConfigDict(extra="ignore", frozen=True)
        attr: bool = True

    ModifiedSimpleModel = _apply_model_config_recursively(SimpleModel, ConfigDict(extra="forbid", strict=True))

    assert SimpleModel.model_config == { "extra": "ignore", "frozen": True }
    assert ModifiedSimpleModel.model_config == { "extra": "forbid", "frozen": True, "strict": True }
