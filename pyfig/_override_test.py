import pytest

from ._override import unify_overrides, apply_overrides


def test__given_no_overrides__when_unify_overrides__then_returns_empty_dict():
    assert unify_overrides() == {}

def test__given_single_override_dict__when_unify_overrides__then_returns_that_dict():
    override = {
        "one": 1,
        "two": 2,
        "three": 3
    }
    assert unify_overrides(override) == override

def test__given_disjoint_dicts__when_unify_overrides__then_returns_union():
    first = { "a": 1 }
    second = { "b": 2, "nested": { "c": 3 } }
    unified = unify_overrides(first, second)
    assert unified == { "a": 1, "b": 2, "nested": {"c":3} }

def test__given_two_completely_overriding_dicts__when_unify_overrides__then_returns_first_dict():
    first = { "a": 1 }
    second = { "a": 100 }
    unified = unify_overrides(first, second)
    assert unified == first

def test__given_partial_overlapping_dicts__when_unify_overrides__then_second_with_first_as_overrides():
    first  = { "a": 1, "b": 2           }
    second = {         "b": 200, "c": 3 }
    unified = unify_overrides(first, second)
    assert unified == { "a": 1, "b": 2, "c": 3 }

def test__given_nested_dict__when_unify_overrides__then_merges_deeply():
    lo = {
        "top": {
            "a": 1,
            "b": 2
        },
        "other": "unrelated"
    }
    hi = {
        "top": { "a": 100, }
    }
    unified = unify_overrides(hi, lo)
    assert unified == {
        "top": { "a": 100, "b": 2 },
        "other": "unrelated"
    }

def test__given_nested_dict__when_unify_overrides_with_not_so_nested__then_removes_nesting():
    lo = {
        "top": {
            "a": 1,
            "b": 2
        },
        "other": "unrelated"
    }
    hi = { "top": "overridden" }
    unified = unify_overrides(hi, lo)
    assert unified == {
        "top": "overridden",
        "other": "unrelated"
    }

def test__given_array__when_unify_overrides__then_sets_atomically():
    lo = { "array": [1, 2, 3] }
    hi = { "array": [4, 5, 6] }
    unified = unify_overrides(hi, lo)
    assert unified == hi

def test__given_multiple_disjoint_dicts__when_unify_overrides__then_returns_union():
    first  = { "a": 1 }
    second = { "b": 2 }
    third  = { "c": 3 }
    unified = unify_overrides(first, second, third)
    assert unified == { "a": 1, "b": 2, "c": 3 }

def test__given_multiple_overlapping_dicts__when_unify_overrides__then_overrides_highest_to_lowest():
    base     = { "a": 1, "b": 2          }
    override = {         "b": 20, "c": 3 }
    top      = {         "b": 200        }
    unified = unify_overrides(top, override, base)
    assert unified == { "a": 1, "b": 200, "c": 3 }

def test__given_same_key_overridden_differently__when_unify_overrides__then_first_override_wins():
    first  = { "a": 1 }
    second = { "a": {
        "nested": "stuff"
    }}
    third  = { "a": "different type" }
    unified = unify_overrides(first, second, third)
    assert unified == first

def test__given_same_key_overridden_with_more_fields__when_unify_overrides__then_merges_deeply():
    first  = { "a": { "nested": "stuff" }}
    second = { "a": { "more": "stuff" }}
    unified = unify_overrides(first, second)
    assert unified == { "a": {
        "nested": "stuff",
        "more": "stuff"
    }}

def test__given_empty_dict__when_override_with_stuff__then_sets_anyway():
    empty_dict = {}
    override = { "a": 1 }
    apply_overrides(empty_dict, override)
    assert empty_dict == override

def test__given_flat_dict__when_override_with_unknown_stuff__then_sets_anyway():
    conf = { "a": 1 }
    override = { "b": 2 }
    apply_overrides(conf, override)
    assert conf == { "a": 1, "b": 2 }

def test__given_single_key_dict__when_override_that_key__then_mutates_dict_with_override():
    conf = { "a": 1 }
    override = { "a": 100 }
    apply_overrides(conf, override)
    assert conf == { "a": 100 }

def test__given_multi_key_dict__when_override_known_key__then_applies_that_override():
    conf = { "a": 1, "b": 2, "c": False }
    override = { "a": 100 }
    apply_overrides(conf, override)
    assert conf == { "a": 100, "b": 2, "c": False }

def test__given_multi_key_dict__when_override_known_subset__then_applies_all_overrides():
    conf = { "a": 1, "b": 2, "c": False }
    override = { "a": 100, "c": True }
    apply_overrides(conf, override)
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
    apply_overrides(conf, override)
    assert conf == {
        "top": {
            "a": 100,
            "b": 2
        },
        "level": 3
    }

def test__given_nested_conf__when_override_nested_key_different_type__then_sets():
    conf = {
        "top": {
            "a": 1,
            "b": 2
        },
        "level": 3
    }
    override = {
        "top": "different type"
    }
    apply_overrides(conf, override)
    assert conf == {
        "top": "different type",
        "level": 3
    }

def test__given_flat_conf__when_override_with_nested_dict__then_overrides_with_nested():
    conf = {
        "a": 1,
        "b": 2
    }
    override = {
        "a": {
            "nested": 100
        }
    }
    apply_overrides(conf, override)
    assert conf == {
        "a": { "nested": 100 },
        "b": 2
    }

def test__given_nested_conf__when_override_unknown_nested_key__then_sets_anyway():
    conf = {
        "top": {
            "a": 1,
            "b": 2
        },
        "level": 3
    }
    override = {
        "top": {
            "foo": 100
        }
    }
    apply_overrides(conf, override)
    assert conf == {
        "top": {
            "a": 1,
            "b": 2,
            "foo": 100
        },
        "level": 3
    }
