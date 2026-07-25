import pytest

from .environment_evaluator import EnvironmentEvaluator


def test_given_default_environment_evaluator_when_evaluate_then_only_returns_env_values(monkeypatch: pytest.MonkeyPatch):
    key = "TEST_ENVIRONMENT_VARIABLE_KEY"
    value = "some-value"
    monkeypatch.setenv(key, value)

    evaluator = EnvironmentEvaluator()

    assert evaluator.evaluate(key) == value
    with pytest.raises(KeyError):
        evaluator.evaluate("ANYTHING_ELSE")

def test_given_environment_evaluator_with_default_when_evaluate_then_always_returns(monkeypatch: pytest.MonkeyPatch):
    key = "TEST_ENVIRONMENT_VARIABLE_KEY"
    value = "some-value"
    monkeypatch.setenv(key, value)

    default = "my-default"
    evaluator = EnvironmentEvaluator(default=default)

    assert evaluator.evaluate(key) == value
    assert evaluator.evaluate("ANYTHING_ELSE") == default

def test_given_environment_evaluator_with_defaults_when_evaluate_then_returns_env_or_mapped(monkeypatch: pytest.MonkeyPatch):
    key = "TEST_ENVIRONMENT_VARIABLE_KEY"
    value = "some-value"
    monkeypatch.setenv(key, value)

    defaults = {
        "EXPLICIT": "mapping",
        "WITHOUT": "plain-default",
    }
    evaluator = EnvironmentEvaluator(defaults=defaults)

    assert evaluator.evaluate(key) == value
    assert evaluator.evaluate("EXPLICIT") == defaults["EXPLICIT"]
    assert evaluator.evaluate("WITHOUT") == defaults["WITHOUT"]
    with pytest.raises(KeyError):
        evaluator.evaluate("ANYTHING_ELSE")

def test_given_environment_evaluator_with_default_and_defaults_when_evaluate_then_returns_prioritized(monkeypatch: pytest.MonkeyPatch):
    key = "TEST_ENVIRONMENT_VARIABLE_KEY"
    value = "some-value"
    monkeypatch.setenv(key, value)

    defaults = { "EXPLICIT": "mapping" }
    default = "plain-default"
    evaluator = EnvironmentEvaluator(default=default, defaults=defaults)

    assert evaluator.evaluate(key) == value
    assert evaluator.evaluate("EXPLICIT") == defaults["EXPLICIT"]
    assert evaluator.evaluate("ANYTHING_ELSE") == default


### OLD TESTS - kept only to ensure backwards compatibility       ###
### subject for future removal as they add no additional coverage ###

def test__given_default_environment_evaluator__when_value_is_not_in_env__then_raises_key_error():
    evaluator = EnvironmentEvaluator()
    with pytest.raises(KeyError):
        evaluator.evaluate("this-environment-variable-shouldn't-exist")

def test__given_environment_evaluator_with_default__when_value_is_not_in_env__then_returns_default():
    evaluator = EnvironmentEvaluator(default=13)
    assert evaluator.evaluate("this-environment-variable-shouldn't-exist") == 13

def test__given_environment_evaluator__when_env_value_is_set__then_returns_that_value(monkeypatch: pytest.MonkeyPatch):
    env = "PYFIG_TEST"
    val = "test-value"
    monkeypatch.setenv(env, val)
    evaluator = EnvironmentEvaluator()

    assert evaluator.evaluate(env) == val
