from typing import List, Union, Any

import pytest

from pydantic import BaseModel
from pyfig import Pyfig, load_configuration


class ObjectConfig(BaseModel):
    index: int
    name: str

class Config(Pyfig):
    direct: List[int] = [1, 2, 3]
    objects: List[ObjectConfig] = [
        ObjectConfig(index=0, name="foo"),
        ObjectConfig(index=1, name="bar"),
    ]


def test__given_config__when_model_dump_dict__then_serializes():
    """ this test mostly exists to help illustrate the format of the config """
    assert Config().model_dump_dict() == {
        "direct": [1, 2, 3],
        "objects": [
            { "index": 0, "name": "foo" },
            { "index": 1, "name": "bar" },
        ]
    }

def test__given_new_direct_list__when_load_configuration__then_overrides_entire_list():
    direct = [1, 1, 2, 3, 5]
    assert load_configuration(Config, [{ "direct": direct }], []) == Config(direct=direct)

def test__given_new_object_list__when_load_configuration__then_overrides_entire_list():
    objects = [ObjectConfig(index=99, name="baz")]
    assert load_configuration(Config, [{ "objects": objects }], []) == Config(objects=objects)

@pytest.mark.parametrize("key", ["direct", "objects"])
@pytest.mark.parametrize("bad_index", [
    "",
    "foo",
    "True",
    False,
    "1e3",
    "3.14",
    2.718,
])
def test__given_bad_index_for_list_element_override__when_load_configuration__then_raises_valueerror(key: str, bad_index: Any):
    override = {
        key: {
            bad_index: "won't work because bad_index is not an int or int-like str"
        }
    }
    with pytest.raises(ValueError):
        load_configuration(Config, [override], [])

@pytest.mark.parametrize("key", ["direct", "objects"])
def test__given_out_of_bounds_index_for_list_element_override__when_load_configuration__then_raises_indexerror(key: str):
    default_length = len(getattr(Config(), key))
    with pytest.raises(IndexError):
        load_configuration(Config, [{ key: {default_length: "out of bounds"} }], [])

@pytest.mark.parametrize("key", ["direct", "objects"])
def test__given_negative_out_of_bounds_index_for_list_element_override__when_load_configuration__then_raises_indexerror(key: str):
    default_length = len(getattr(Config(), key))
    with pytest.raises(IndexError):
        load_configuration(Config, [{ key: {-default_length-1: "out of bounds"} }], [])

@pytest.mark.parametrize("last_index", [
    "2",
    2,
    "-1",
    -1
])
def test__given_direct_list_element_override__when_load_configuration__then_that_index_is_updated(last_index: Union[str, int]):
    override = {
        "direct": {
            last_index: 30
        }
    }
    assert load_configuration(Config, [override], []) == Config(direct=[1, 2, 30])

@pytest.mark.parametrize("last_index", [
    "1",
    1,
    "-1",
    -1
])
def test__given_object_list_element_override__when_load_configuration__then_that_index_is_updated(last_index: Union[str, int]):
    override = {
        "objects": {
            last_index: { "index": 99, "name": "baz" }
        }
    }
    assert load_configuration(Config, [override], []) == Config(objects=[
        ObjectConfig(index=0, name="foo"),
        ObjectConfig(index=99, name="baz"),
    ])

def test__given_object_list_element_override_partial__when_load_configuration__then_partially_updated():
    override = {
        "objects": {
            0: { "index": 99 }
        }
    }
    assert load_configuration(Config, [override], []) == Config(objects=[
        ObjectConfig(index=99, name="foo"),
        ObjectConfig(index=1, name="bar"),
    ])

def test__given_multiple_direct_list_element_overrides__when_load_configuration__then_all_updated():
    override = {
        "direct": {
            0: 100,
            2: 200,
        }
    }
    assert load_configuration(Config, [override], []) == Config(direct=[100, 2, 200])

def test__given_multiple_object_list_element_overrides__when_load_configuration__then_all_updated():
    override = {
        "objects": {
            0: { "index": 9 },
            1: { "name": "baz" },
        }
    }
    assert load_configuration(Config, [override], []) == Config(objects=[
        ObjectConfig(index=9, name="foo"),
        ObjectConfig(index=1, name="baz"),
    ])

def test__given_multiple_list_element_overrides__when_load_configuration__then_all_updated():
    override_low = {
        "direct": {
            0: 100,
        },
        "objects": {
            0: { "index": 100 },
            1: { "index": 1, "name": "baz" },
        }
    }
    override_high = {
        "direct": {
            0: 200,
        }
    }
    assert load_configuration(Config, [override_high, override_low], []).model_dump_dict() == {
        "direct": [200, 2, 3],
        "objects": [
            { "index": 100, "name": "foo" },
            { "index": 1, "name": "baz" },
        ]
    }
