from typing import Type, List, Union, Dict, Set, Tuple, Literal
from unittest.mock import Mock
from copy import deepcopy

import pytest
from pydantic import BaseModel, ConfigDict, ValidationError

from ._pyfig import Pyfig
from ._loader import load_configuration, _apply_model_config_recursively, _apply_model_config_generic_recursively, \
                     _is_generic_type, _issubclass_safe


@pytest.mark.parametrize("t", [
    List[int],
    Union[int, str],
    Dict[str, int],
    Type[BaseModel],
    Set[bool],
    Literal["foo"],
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


def test__given_b_subclass_of_a__when_issubclass_safe__then_returns_true():
    class A:
        pass

    class B(A):
        pass

    assert _issubclass_safe(B, A)


def test__given_b_not_subclass_of_a__when_issubclass_safe__then_returns_false():
    class A:
        pass

    class B:
        pass

    assert not _issubclass_safe(B, A)


def test__given_not_a_class__when_issubclass_safe__then_returns_false():
    class A:
        pass

    assert not _issubclass_safe(A(), A)


def test__given_not_a_generic__when_apply_model_config_generic_recursively__then_raises_type_error():
    with pytest.raises(TypeError):
        _apply_model_config_generic_recursively(int, ConfigDict())


@pytest.mark.parametrize("Generic", [
    List,
    Set,
    Dict,
    List[int],
    Set[str],
    Dict[int, float],
    Union[int, List[str]],
    Dict[Tuple[int, int], Dict[str, List[int]]],
])
def test__given_simple_generic__when_apply_model_config_generic_recursively__then_returns_same(Generic: Type):
    cfg = ConfigDict(extra="forbid")
    ModifiedGeneric = _apply_model_config_generic_recursively(Generic, cfg)

    assert ModifiedGeneric == Generic


def test__given_list_of_base_model__when_apply_model_config_generic_recursively__then_model_config_set_as_copy():
    class SimpleModel(BaseModel):
        foo: int
        bar: str

    Generic = List[SimpleModel]
    cfg = ConfigDict(extra="forbid")
    ModifiedGeneric = _apply_model_config_generic_recursively(Generic, cfg)

    assert Generic == List[SimpleModel]
    assert Generic.__args__[0].model_config == ConfigDict()
    assert ModifiedGeneric.__args__[0].model_config == cfg


def test__given_complex_recursive_generic__when_apply_model_config_generic_recursively__then_adjusts_copy_deeply():
    class SomeModel(BaseModel):
        pass

    Generic = Union[
        SomeModel,
        List[SomeModel],
        Dict[str, SomeModel],
        Tuple[SomeModel, str, Tuple[SomeModel, SomeModel]],
    ]

    cfg = ConfigDict(extra="forbid")
    ModifiedGeneric = _apply_model_config_generic_recursively(Generic, cfg)

    assert Generic == Union[
        SomeModel,
        List[SomeModel],
        Dict[str, SomeModel],
        Tuple[SomeModel, str, Tuple[SomeModel, SomeModel]],
    ]

    # SomeModel
    assert Generic.__args__[0].model_config == ConfigDict()
    assert ModifiedGeneric.__args__[0].model_config == cfg

    # list[SomeModel]
    assert Generic.__args__[1].__args__[0].model_config == ConfigDict()
    assert ModifiedGeneric.__args__[1].__args__[0].model_config == cfg

    # dict[str, SomeModel]
    assert Generic.__args__[2].__args__[1].model_config == ConfigDict()
    assert ModifiedGeneric.__args__[2].__args__[1].model_config == cfg

    # tuple[SomeModel, str, Tuple[SomeModel, SomeModel]]
    for some_model in [
        Generic.__args__[3].__args__[0],
        Generic.__args__[3].__args__[2].__args__[0],
        Generic.__args__[3].__args__[2].__args__[1]
    ]:
        assert some_model.model_config == ConfigDict()
    for modified_some_model in [
        ModifiedGeneric.__args__[3].__args__[0],
        ModifiedGeneric.__args__[3].__args__[2].__args__[0],
        ModifiedGeneric.__args__[3].__args__[2].__args__[1]
    ]:
        assert modified_some_model.model_config == cfg


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
            "dne": "<< this field does not exist"
        }
    }
    _dne_field_is_ignored = TopModel(**kwargs)
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
    assert top_model.n.nested is True

    with pytest.raises(ValidationError):
        ModifiedTopModel(**kwargs)


def test__given_config_class_tree__when_load_configuration_without_allow_unused__then_raises_when_unused_fields():
    class LoggingConfig(Pyfig):
        level: str = "INFO"
        file: Union[Literal["stdout"], Literal["stderr"]] = "stdout"

    class GenericConfigurableService(BaseModel):
        name: str
        enabled: bool = True

    class MainConfig(Pyfig):
        services: List[GenericConfigurableService] = [
            GenericConfigurableService(name="important_job"),
            GenericConfigurableService(name="health"),
        ]
        logging: LoggingConfig = LoggingConfig()

    override_all_used = {
        "services": [
            { "name": "some-name" }
        ],
        "logging": { "level": "DEBUG" }
    }
    override_with_extra = deepcopy(override_all_used)
    override_with_extra["services"][0]["bad-field"] = True

    _normal_behaviour_ignores_extra = load_configuration(MainConfig, [override_with_extra], [], allow_unused=True)
    with pytest.raises(ValidationError):
        _unused_field_raises = load_configuration(MainConfig, [override_with_extra], [], allow_unused=False)
    _still_loaded_when_no_extra = load_configuration(MainConfig, [override_all_used], [], allow_unused=False)
    _normal_behaviour_preserved = load_configuration(MainConfig, [override_with_extra], [], allow_unused=True)
