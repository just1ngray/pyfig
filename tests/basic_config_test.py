from typing import List
from enum import Enum

import pytest
from pydantic import BaseModel, ValidationError
from pyfig import Pyfig, load_configuration


class HttpMethod(Enum):
    GET = "GET"
    PUT = "PUT"
    POST = "POST"
    DELETE = "DELETE"

class EndpointConfig(BaseModel):
    path: str
    method: HttpMethod
    enabled: bool = True

class NestedMappingConfig(Pyfig):
    something: str = "else"

class AllBasicTypesConfig(Pyfig):
    string: str = "string type"
    integer: int = 3
    floating: float = 0.14
    boolean: bool = False
    nested_object: NestedMappingConfig = NestedMappingConfig()

class BasicConfig(Pyfig):
    list_of_strings: List[str] = [
        "foo",
        "bar",
        "baz",
    ]
    list_of_objects: List[EndpointConfig] = [
        EndpointConfig(method=HttpMethod.GET, path="/"),
        EndpointConfig(method=HttpMethod.POST, path="/page"),
    ]
    all_types: AllBasicTypesConfig = AllBasicTypesConfig()


def test__given_basic_config__when_dump_to_dict__then_serializes_to_dict():
    config = BasicConfig()
    assert config.model_dump_dict() == {
        "list_of_strings": [
            "foo",
            "bar",
            "baz"
        ],
        "list_of_objects": [
            {
                "path": "/",
                "method": "GET",
                "enabled": True
            },
            {
                "path": "/page",
                "method": "POST",
                "enabled": True
            },
        ],
        "all_types": {
            "string": "string type",
            "integer": 3,
            "floating": 0.14,
            "boolean": False,
            "nested_object": {
                "something": "else"
            }
        }
    }

def test__given_basic_pyfig_classtree__when_load_configuration__then_loads_default():
    config = load_configuration(BasicConfig, [], [])
    assert config == BasicConfig()

def test__given_str_list_override__when_load_configuration__then_overrides_entire_list():
    override = {
        "list_of_strings": [
            "overridden",
            "string list",
        ]
    }
    config = load_configuration(BasicConfig, [override], [])
    assert config == BasicConfig(list_of_strings=override["list_of_strings"])

def test__given_obj_list_override__when_load_configuration__then_overrides_entire_list():
    override = {
        "list_of_objects": [
            {
                "path": "/foo",
                "method": "PUT"
            }
        ]
    }
    config = load_configuration(BasicConfig, [override], [])
    assert config == BasicConfig(list_of_objects=[EndpointConfig(
        path="/foo",
        method=HttpMethod.PUT,
        enabled=True,
    )])

def test__given_override_value__when_load_configuration__then_overrides_at_lowest_dict_level():
    override = {
        "all_types": {
            "string": "foo",
            "nested_object": {
                "something": "new"
            }
        }
    }
    config = load_configuration(BasicConfig, [override], [])
    assert config == BasicConfig(
        all_types=AllBasicTypesConfig(
            string="foo",
            nested_object=NestedMappingConfig(something="new"),
        )
    )

def test__given_additional_keys__when_load_configuration__then_ignores():
    override = { "not": "a key" }
    config = load_configuration(BasicConfig, [override], [])
    assert config == BasicConfig()

def test__given_additional_keys__when_load_configuration_disallow_unused__then_raises():
    override = { "not": "a key" }
    with pytest.raises(ValidationError):
        load_configuration(BasicConfig, [override], [], allow_unused=False)

def test__given_multiple_overrides__when_load_configuration__then_uses_all_overrides():
    override_1 = { "list_of_strings": [ "override_1" ] }
    override_2 = { "all_types": { "integer": 2 } }
    config = load_configuration(BasicConfig, [override_1, override_2], [])
    assert config == BasicConfig(
        list_of_strings=["override_1"],
        all_types=AllBasicTypesConfig(integer=2),
    )

def test__given_conflicting_overrides__when_load_configuration__then_uses_by_priority():
    override_1 = { "all_types": { "string": "override_1" } }
    override_2 = { "all_types": { "string": "override_2" } }

    assert load_configuration(BasicConfig, [override_1, override_2], []) == BasicConfig(
        all_types=AllBasicTypesConfig(string="override_1")
    )
    assert load_configuration(BasicConfig, [override_2, override_1], []) == BasicConfig(
        all_types=AllBasicTypesConfig(string="override_2")
    )
