from typing import Type, List, Union, Dict, Set
from unittest.mock import Mock

import pytest
from pydantic import BaseModel, ConfigDict, ValidationError

from ._loader import _apply_model_config_recursively, _is_generic_type


@pytest.mark.parametrize("t", [
    List[int],
    Union[int, str],
    Dict[str, int],
    Type[BaseModel],
    Set[bool],
])
def test__given_generic_type__when_is_generic_type__then_returns_true(t: Type):
    assert _is_generic_type(t)


@pytest.mark.parametrize("o", [
    True,
    42,
    3.14,
    Mock,
    Mock(),
])
def test__given_non_generic__when_is_generic_type__then_returns_false(o: object):
    assert not _is_generic_type(o)


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


def test__given_nested_with_defaults__when_apply_model_config__then_doesnt_change_default():
    class NestedModel(BaseModel):
        nested: bool = True

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
    kwargs = { "n": {"dne": "dne does not exist"} }

    top_model = TopModel(**kwargs)
    assert top_model.n.nested == True

    with pytest.raises(ValidationError):
        ModifiedTopModel(**kwargs)
