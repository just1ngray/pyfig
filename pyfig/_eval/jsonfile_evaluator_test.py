from json import JSONDecodeError
from pathlib import Path
from typing import Any

import pytest

from .jsonfile_evaluator import JSONFileEvaluator


def test__given_no_colon__when_json_evaluated__then_raises_value_error():
    evaluator = JSONFileEvaluator()
    with pytest.raises(ValueError):
        evaluator.evaluate("badvalue")

def test__given_missing_file__when_json_evaluated__then_raises_file_not_found_error():
    evaluator = JSONFileEvaluator()
    with pytest.raises(FileNotFoundError):
        evaluator.evaluate("access.path:/path/to/file/that_does_not_exist.json")

def test__given_malformatted_json__when_json_evaluated__then_raises_json_decode_error(pytestdir: Path):
    path = pytestdir / "malformatted.json"
    path.write_text("badjson: missing quotes")

    evaluator = JSONFileEvaluator()
    with pytest.raises(JSONDecodeError):
        evaluator.evaluate(f"badjson:{path.as_posix()}")

@pytest.mark.parametrize("key", [
    "missing",
    "key.not_recursive",
    "other.data.its_an_array"
])
def test__given_missing_json_key__when_json_evaluated__then_raises_key_error(key: str, pytestdir: Path):
    path = pytestdir / "missing.json"
    path.write_text('{ "key": "value", "other": { "data": [1, 2, 3] } }')

    evaluator = JSONFileEvaluator()
    with pytest.raises(KeyError):
        evaluator.evaluate(f"{key}:{path.as_posix()}")

def test__given_json_array__when_json_evaluated_with_bad_index__then_raises_index_error(pytestdir: Path):
    path = pytestdir / "array.json"
    path.write_text('[1, 2, 3]')

    evaluator = JSONFileEvaluator()
    with pytest.raises(IndexError):
        evaluator.evaluate(f"100:{path.as_posix()}")

@pytest.mark.parametrize("accessor,expected", [
    ("key", "value"),
    ("other.data.0", 1),
    ("other.data.1", { "deeply": "nested" }),
    ("other.data.1.deeply", "nested" ),
    ("other.data.2", 3)
])
def test__given_valid_json__when_json_evaluated__then_extracts_properly(accessor: str, expected: Any, pytestdir: Path):
    path = pytestdir / "valid.json"
    path.write_text('''{
        "key": "value",
        "other": {
            "data": [
                1,
                { "deeply": "nested" },
                3
            ]
        }
    }''')

    assert JSONFileEvaluator().evaluate(f"{accessor}:{path.as_posix()}") == expected
