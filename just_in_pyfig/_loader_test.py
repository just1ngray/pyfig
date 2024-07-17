import pytest

from ._loader import _apply_override_to_conf


def test__given_empty_dict__when_override_with_stuff__then_raises_key_error():
    empty_dict = {}
    override = { "a": 1 }
    with pytest.raises(KeyError):
        _apply_override_to_conf(empty_dict, override)

def test__given_dict_with_stuff__when_override_with_unknown_stuff__then_raises_key_error():
    conf = { "a": 1 }
    override = { "b": 2 }
    with pytest.raises(KeyError):
        _apply_override_to_conf(conf, override)

def test__given_single_key_dict__when_override_that_key__then_mutates_dict_with_override():
    conf = { "a": 1 }
    override = { "a": 100 }
    _apply_override_to_conf(conf, override)
    assert conf == { "a": 100 }

def test__given_multi_key_dict__when_override_known_key__then_applies_that_override():
    conf = { "a": 1, "b": 2, "c": False }
    override = { "a": 100 }
    _apply_override_to_conf(conf, override)
    assert conf == { "a": 100, "b": 2, "c": False }

def test__given_multi_key_dict__when_override_known_subset__then_applies_all_overrides():
    conf = { "a": 1, "b": 2, "c": False }
    override = { "a": 100, "c": True }
    _apply_override_to_conf(conf, override)
    assert conf == { "a": 100, "b": 2, "c": True }

def test__given_nested_conf__when_override_nested_key_with_same_type__then_applies_that_override():
    conf = {
        "top": {
            "a": 1,
            "b": 2
        },
        "level": 3
    }
    override = {
        "top": {
            "a": 100
        }
    }
    _apply_override_to_conf(conf, override)
    assert conf == {
        "top": {
            "a": 100,
            "b": 2
        },
        "level": 3
    }

def test__given_nested_conf__when_override_nested_key_template__then_sets_as_template():
    conf = {
        "top": {
            "a": 1,
            "b": 2
        },
        "level": 3
    }
    override = {
        "top": "template()"
    }
    _apply_override_to_conf(conf, override)
    assert conf == {
        "top": "template()",
        "level": 3
    }
