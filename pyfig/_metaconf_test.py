import textwrap
from pathlib import Path

import pytest

from ._pyfig import Pyfig
from ._eval import AbstractEvaluator
from ._metaconf import _load_dict, _construct_evaluator, Metaconf


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
    result = _construct_evaluator("pyfig._metaconf_test.MockEvaluator", kwargs)
    assert isinstance(result, MockEvaluator)
    assert result.kwargs == kwargs

def test__given_missing_module__when_construct_evaluator__then_raises_module_not_found_error():
    with pytest.raises(ModuleNotFoundError):
        _construct_evaluator("pyfig._module_does_not.Exist", {})

def test__given_missing_class_in_known_module__when_construct_evaluator__then_raises_import_error():
    with pytest.raises(ImportError):
        _construct_evaluator("pyfig._metaconf_test.ClassDoesNotExist", {})

class NotEvaluator:
    pass

def test__given_class_path_to_bad_class__when_construct_evaluator__then_raises_type_error():
    with pytest.raises(TypeError):
        _construct_evaluator("pyfig._metaconf_test.NotEvaluator", {})

def test__given_metaconf_config__when_metaconf_from_path__then_initialized_properly(pytestdir: Path):
    override = pytestdir.joinpath("override.yaml").as_posix()

    path = pytestdir / "metaconf.yaml"
    path.write_text(textwrap.dedent(f"""\
        evaluators:
            pyfig._metaconf_test.MockEvaluator:
                param: value
                other: 1
            pyfig.VariableEvaluator:
                name: test

        configs:
            - {override}

        overrides:
            key: value
    """), encoding="utf-8")

    metaconf = Metaconf.from_path(path)

    assert isinstance(metaconf, Metaconf)
    assert metaconf.configs == [override]
    assert metaconf.overrides == {"key": "value"}
    assert len(metaconf.evaluators) == 2
    for evaluator in metaconf.evaluators:
        assert isinstance(evaluator, AbstractEvaluator)

def test__given_missing_metaconf_path__when_metaconf_from_path__then_raises_file_not_found_error(pytestdir: Path):
    with pytest.raises(FileNotFoundError):
        Metaconf.from_path(pytestdir / "does_not_exist.yaml")

def test__given_empty_metaconf__when_metaconf_from_path__then_creates_default(pytestdir: Path):
    path = pytestdir / "empty.yaml"
    path.touch()

    metaconf = Metaconf.from_path(path)
    default = Metaconf()

    assert isinstance(metaconf, Metaconf)
    assert metaconf.evaluators == default.evaluators
    assert metaconf.configs == default.configs
    assert metaconf.overrides == default.overrides

def test__given_metaconf__when_from_path_relative_to__then_all_relative_paths_are_relative_to_relative_to(pytestdir: Path):
    relative_to = pytestdir / "rel_to"
    relative_one = pytestdir / relative_to / "relative.yaml"
    relative_two = pytestdir / relative_to / "other" / "relative" / "path.yaml"
    absolute = pytestdir / "absolute_path.yaml"

    for path in [relative_one, relative_two, absolute]:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()

    path = pytestdir / "metaconf.yaml"
    path.write_text(textwrap.dedent(f"""\
        configs:
            - relative.yaml
            - other/relative/path.yaml
            - {absolute}
    """), encoding="utf-8")

    Metaconf.from_path(path, relative_to=relative_to) # checks that files exist

def test__given_metaconf__when_load_config__then_loads_files_and_calls_load_configuration(pytestdir: Path):
    class TargetConf(Pyfig):
        a: int = 1
        b: str = "bee"
        c: float = 3.14

    override_path = pytestdir / "override.json"
    override_path.write_text('{ "a": 10 }', encoding="utf-8")
    configs = [override_path.as_posix()]

    metaconf = Metaconf(
        configs=configs,
        evaluators=[MockEvaluator()],
        overrides={ "b": "bear" }
    )

    result = metaconf.load_config(TargetConf)

    assert isinstance(result, TargetConf)
    assert result.a == 10
    assert result.b == "bear"
    assert result.c == 3.14
