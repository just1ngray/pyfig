import pytest

from .environment_evaluator import EnvironmentEvaluator


def test__given_environment_evaluator__when_value_is_not_in_env__then_raises_key_error():
    evaluator = EnvironmentEvaluator()
    with pytest.raises(KeyError):
        evaluator.evaluate("this-environment-variable-shouldn't-exist")

def test__given_environment_evaluator__when_env_value_is_set__then_returns_that_value(monkeypatch: pytest.MonkeyPatch):
    env = "PYFIG_TEST"
    val = "test-value"
    monkeypatch.setenv(env, val)
    evaluator = EnvironmentEvaluator()

    assert evaluator.evaluate(env) == val
