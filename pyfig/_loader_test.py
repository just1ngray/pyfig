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

    assert SimpleModel.model_config == ConfigDict(extra="ignore", frozen=True)
    assert ModifiedSimpleModel.model_config == ConfigDict(extra="forbid", frozen=True, strict=True)


def test__given_nested_model__when_apply_model_config__then_applies_recursively():
    class NestedModel(BaseModel):
        nested: bool

    class TopModel(BaseModel):
        n: NestedModel

    cfgdict = ConfigDict(extra="forbid")
    ModifiedTopModel = _apply_model_config_recursively(TopModel, cfgdict)

    # confirm that the original classes are unmodified
    assert NestedModel.model_config == ConfigDict()
    assert TopModel.model_config == ConfigDict()

    # confirm that the new classes have the new config
    assert ModifiedTopModel.model_config == cfgdict
    ModifiedNestedModel = ModifiedTopModel.model_fields["n"].annotation
    assert ModifiedNestedModel.model_config == cfgdict

    # confirm desired construction behaviour
    kwargs = {
        "n": {
            "nested": True,
            "dne": "dne does not exist"
        }
    }
    _no_raise = TopModel(**kwargs)
    with pytest.raises(ValidationError):
        ModifiedTopModel(**kwargs)

