import textwrap
from pathlib import Path

import pytest

from ._metafig import _load_dict


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

