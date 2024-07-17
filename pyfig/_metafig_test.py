import textwrap
from pathlib import Path

import pytest

from ._eval import AbstractEvaluator
from ._metafig import _load_dict, _construct_evaluator


@pytest.mark.parametrize("ext", ["yaml", "yml"])
def test__given_yaml__when_load_dict__then_dict_is_loaded(pytestdir: Path, ext: str):
    path = pytestdir / f"test.{ext}"
    path.write_text(textwrap.dedent("""\
        types:
            string: Hello
            integer: 1
            float: 2.718
            boolean: true
            nothing: null
            array:
                - 1
                - 2
                - obj: mapping
    """), encoding="utf-8")

    result = _load_dict(path)

    assert result == {
        "types": {
            "string": "Hello",
            "integer": 1,
            "float": 2.718,
            "boolean": True,
            "nothing": None,
            "array": [1, 2, {"obj": "mapping"}]
        }
    }

def test__given_json__when_load_dict__then_dict_is_loaded(pytestdir: Path):
    path = pytestdir / "test.json"
    path.write_text(textwrap.dedent("""\
    {
        "types": {
            "string": "Hello",
            "integer": 1,
            "float": 2.718,
            "boolean": true,
            "nothing": null,
            "array": [ 1, 2, { "obj": "mapping" } ]
        }
    }
    """), encoding="utf-8")

    result = _load_dict(path)

    assert result == {
        "types": {
            "string": "Hello",
            "integer": 1,
            "float": 2.718,
            "boolean": True,
            "nothing": None,
            "array": [1, 2, {"obj": "mapping"}]
        }
    }

def test__given_toml__when_load_dict__then_dict_is_loaded(pytestdir: Path):
    path = pytestdir / "test.toml"
    path.write_text(textwrap.dedent("""\
        [types]
        string = "Hello"
        integer = 1
        float = 2.718
        boolean = true
        array = [1, 2, 3]
    """), encoding="utf-8")

    result = _load_dict(path)

    assert result == {
        "types": {
            "string": "Hello",
            "integer": 1,
            "float": 2.718,
            "boolean": True,
            "array": [1, 2, 3]
        }
    }


def test__given_ini__when_load_dict__then_dict_is_loaded(pytestdir: Path):
    path = pytestdir / "test.ini"
    path.write_text(textwrap.dedent("""\
        [types]
        string = Hello
        integer = 1
        float = 2.718
        boolean = true
        nothing =

        array_0 = 1
        array_1 = 2
        array_2_obj = mapping

    """), encoding="utf-8")

    result = _load_dict(path)

    assert result == {
        "types": {
            "string": "Hello",
            "integer": "1",
            "float": "2.718",
            "boolean": "true",
            "nothing": "",
            "array_0": "1",
            "array_1": "2",
            "array_2_obj": "mapping"
        }
    }

class MockEvaluator(AbstractEvaluator):
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def evaluate(self, value):
        return value

    def name(self):
        return "mock"

def test__given_class_path_and_params__when_construct_evaluator__then_evaluator_is_constructed():
    kwargs = {"param": "value", "other": 1}
    result = _construct_evaluator("pyfig._metafig_test.MockEvaluator", kwargs)
    assert isinstance(result, MockEvaluator)
    assert result.kwargs == kwargs

def test__given_missing_module__when_construct_evaluator__then_raises_module_not_found_error():
    with pytest.raises(ModuleNotFoundError):
        _construct_evaluator("pyfig._module_does_not.Exist", {})

def test__given_missing_class_in_known_module__when_construct_evaluator__then_raises_import_error():
    with pytest.raises(ImportError):
        _construct_evaluator("pyfig._metafig_test.ClassDoesNotExist", {})
