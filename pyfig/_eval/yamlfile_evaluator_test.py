from pathlib import Path
from typing import Any
from textwrap import dedent

import yaml
import pytest

from .yamlfile_evaluator import YamlFileEvaluator


def test__given_no_colon__when_yaml_evaluated__then_raises_value_error():
    evaluator = YamlFileEvaluator()
    with pytest.raises(ValueError):
        evaluator.evaluate("badvalue")

def test__given_missing_file__when_yaml_evaluated__then_raises_file_not_found_error():
    evaluator = YamlFileEvaluator()
    with pytest.raises(FileNotFoundError):
        evaluator.evaluate("access.path:/path/to/file/that_does_not_exist.yaml")

def test__given_malformatted_yaml__when_yaml_evaluated__then_raises_yaml_decode_error(pytestdir: Path):
    path = pytestdir / "malformatted.yaml"
    path.write_text('key: "missing trailing quote')

    evaluator = YamlFileEvaluator()
    with pytest.raises(yaml.YAMLError):
        evaluator.evaluate(f"badjson:{path.as_posix()}")

@pytest.mark.parametrize("key", [
    "missing",
    "key.not_recursive",
    "other.data.its_an_array"
])
def test__given_missing_yaml_key__when_yaml_evaluated__then_raises_key_error(key: str, pytestdir: Path):
    path = pytestdir / "missing.yaml"
    path.write_text(dedent("""\
        key: value
        other:
            data:
                - 1
                - 2
                - 3
    """))

    evaluator = YamlFileEvaluator()
    with pytest.raises(KeyError):
        evaluator.evaluate(f"{key}:{path.as_posix()}")

def test__given_yaml_array__when_yaml_evaluated_with_bad_index__then_raises_index_error(pytestdir: Path):
    path = pytestdir / "array.yaml"
    path.write_text('key: [1, 2, 3]')

    evaluator = YamlFileEvaluator()
    with pytest.raises(IndexError):
        evaluator.evaluate(f"key.100:{path.as_posix()}")

@pytest.mark.parametrize("accessor,expected", [
    ("key", "value"),
    ("other.data.0", 1),
    ("other.data.1", { "deeply": "nested" }),
    ("other.data.1.deeply", "nested" ),
    ("other.data.2", 3)
])
def test__given_valid_yaml__when_yaml_evaluated__then_extracts_properly(accessor: str, expected: Any, pytestdir: Path):
    path = pytestdir / "valid.yaml"
    path.write_text(dedent("""\
        key: value
        other:
            data:
                - 1
                - deeply: nested
                - 3
    """))

    assert YamlFileEvaluator().evaluate(f"{accessor}:{path.as_posix()}") == expected
