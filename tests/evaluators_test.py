from typing import Any
import pytest

from pyfig import Pyfig, load_configuration, VariableEvaluator, EnvironmentEvaluator, AbstractEvaluator


class Config(Pyfig):
    user_pass: str = "${{var.user_pass}}"


def test__given_config__when_construct_directly__then_loads_properly():
    config = Config()
    assert config.user_pass == "${{var.user_pass}}"

def test__given_no_evaluator__when_load_configuration__then_raises_valueerror():
    with pytest.raises(ValueError):
        load_configuration(Config, [], [])

def test__given_var_evaluator_hit__when_load_configuration__then_loads_config():
    config = load_configuration(Config, [], [VariableEvaluator(user_pass="foo:bar")])
    assert config.user_pass == "foo:bar"

def test__given_var_evaluator_miss__when_load_configuration__then_raises_keyerror():
    with pytest.raises(KeyError):
        load_configuration(Config, [], [VariableEvaluator()])

def test__given_multi_layer_evaluator_stack__when_load_configuration__then_loads_config(monkeypatch: pytest.MonkeyPatch):
    var = VariableEvaluator(user_pass="${{env.USERNAME}}:${{env.PASSWORD}}")
    env = EnvironmentEvaluator()
    monkeypatch.setenv("USERNAME", "email@example.com")
    monkeypatch.setenv("PASSWORD", "qwerty123!")

    config = load_configuration(Config, [], [var, env])

    assert config.user_pass == "email@example.com:qwerty123!"

def test__given_custom_evaluator__when_load_configuration__then_loads_config():
    class MyCustomEvaluator(AbstractEvaluator):
        def name(self) -> str:
            return "var"

        def evaluate(self, _value: str) -> Any:
            return "mocked"

    config = load_configuration(Config, [], [MyCustomEvaluator()])
    assert config.user_pass == "mocked"
