import pytest

from ._loader import _unify_overrides, _apply_override_to_conf

class TestUnifyOverrides:
    def test__given_no_overrides__when_unify_overrides__then_returns_empty_dict(self):
        assert _unify_overrides() == {}

    def test__given_single_override_dict__when_unify_overrides__then_returns_that_dict(self):
        override = {
            "one": 1,
            "two": 2,
            "three": 3
        }
        assert _unify_overrides(override) == override

    def test__given_disjoint_dicts__when_unify_overrides__then_returns_union(self):
        first = { "a": 1 }
        second = { "b": 2, "nested": { "c": 3 } }
        unified = _unify_overrides(first, second)
        assert unified == { "a": 1, "b": 2, "nested": {"c":3} }

    def test__given_two_completely_overriding_dicts__when_unify_overrides__then_returns_first_dict(self):
        first = { "a": 1 }
        second = { "a": 100 }
        unified = _unify_overrides(first, second)
        assert unified == first

    def test__given_partial_overlapping_dicts__when_unify_overrides__then_second_with_first_as_overrides(self):
        first  = { "a": 1, "b": 2           }
        second = {         "b": 200, "c": 3 }
        unified = _unify_overrides(first, second)
        assert unified == { "a": 1, "b": 2, "c": 3 }

    def test__given_nested_dict__when_unify_overrides__then_merges_deeply(self):
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
        unified = _unify_overrides(hi, lo)
        assert unified == {
            "top": { "a": 100, "b": 2 },
            "other": "unrelated"
        }

    def test__given_nested_dict__when_unify_overrides_with_not_so_nested__then_removes_nesting(self):
        lo = {
            "top": {
                "a": 1,
                "b": 2
            },
            "other": "unrelated"
        }
        hi = { "top": "overridden" }
        unified = _unify_overrides(hi, lo)
        assert unified == {
            "top": "overridden",
            "other": "unrelated"
        }

    def test__given_array__when_unify_overrides__then_sets_atomically(self):
        lo = { "array": [1, 2, 3] }
        hi = { "array": [4, 5, 6] }
        unified = _unify_overrides(hi, lo)
        assert unified == hi

    def test__given_multiple_disjoint_dicts__when_unify_overrides__then_returns_union(self):
        first  = { "a": 1 }
        second = { "b": 2 }
        third  = { "c": 3 }
        unified = _unify_overrides(first, second, third)
        assert unified == { "a": 1, "b": 2, "c": 3 }

    def test__given_multiple_overlapping_dicts__when_unify_overrides__then_overrides_highest_to_lowest(self):
        base     = { "a": 1, "b": 2          }
        override = {         "b": 20, "c": 3 }
        top      = {         "b": 200        }
        unified = _unify_overrides(top, override, base)
        assert unified == { "a": 1, "b": 200, "c": 3 }

    def test__given_same_key_overridden_differently__when_unify_overrides__then_first_override_wins(self):
        first  = { "a": 1 }
        second = { "a": {
            "nested": "stuff"
        }}
        third  = { "a": "different type" }
        unified = _unify_overrides(first, second, third)
        assert unified == first

    def test__given_same_key_overridden_with_more_fields__when_unify_overrides__then_merges_deeply(self):
        first  = { "a": { "nested": "stuff" }}
        second = { "a": { "more": "stuff" }}
        unified = _unify_overrides(first, second)
        assert unified == { "a": {
            "nested": "stuff",
            "more": "stuff"
        }}


class TestApplyOverrideToConf:
    def test__given_empty_dict__when_override_with_stuff__then_raises_key_error(self):
        empty_dict = {}
        override = { "a": 1 }
        with pytest.raises(KeyError, match=r"Unknown key 'a' in override \(root\)"):
            _apply_override_to_conf(empty_dict, override)

    def test__given_flat_dict__when_override_with_unknown_stuff__then_raises_key_error(self):
        conf = { "a": 1 }
        override = { "b": 2 }
        with pytest.raises(KeyError, match=r"Unknown key 'b' in override \(root\)"):
            _apply_override_to_conf(conf, override)

    def test__given_single_key_dict__when_override_that_key__then_mutates_dict_with_override(self):
        conf = { "a": 1 }
        override = { "a": 100 }
        _apply_override_to_conf(conf, override)
        assert conf == { "a": 100 }

    def test__given_multi_key_dict__when_override_known_key__then_applies_that_override(self):
        conf = { "a": 1, "b": 2, "c": False }
        override = { "a": 100 }
        _apply_override_to_conf(conf, override)
        assert conf == { "a": 100, "b": 2, "c": False }

    def test__given_multi_key_dict__when_override_known_subset__then_applies_all_overrides(self):
        conf = { "a": 1, "b": 2, "c": False }
        override = { "a": 100, "c": True }
        _apply_override_to_conf(conf, override)
        assert conf == { "a": 100, "b": 2, "c": True }

    def test__given_nested_conf__when_override_nested_key_with_same_type__then_applies_that_override(self):
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

    def test__given_nested_conf__when_override_nested_key_template__then_sets_as_template(self):
        conf = {
            "top": {
                "a": 1,
                "b": 2
            },
            "level": 3
        }
        override = {
            "top": "template(self)"
        }
        _apply_override_to_conf(conf, override)
        assert conf == {
            "top": "template(self)",
            "level": 3
        }

    def test__given_nested_conf__when_override_unknown_nested_key__then_raises_key_error(self):
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
        with pytest.raises(KeyError, match=r"Unknown key 'foo' in override \(root.top\)"):
            _apply_override_to_conf(conf, override)

