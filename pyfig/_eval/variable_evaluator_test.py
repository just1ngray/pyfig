import pytest

from .variable_evaluator import VariableEvaluator


def test__given_empty_variable_evaluator__when_evaluate__then_raises_key_error():
    evaluator = VariableEvaluator()
    with pytest.raises(KeyError):
        evaluator.evaluate("anything")

def test__given_variable_evaluator__when_evaluate_unknown__then_raises_key_error():
    evaluator = VariableEvaluator(foo="bar")
    with pytest.raises(KeyError):
        evaluator.evaluate("unknown")

def test__given_variable_evaluator__when_evaluate_known__then_returns_that_value():
    evaluator = VariableEvaluator(foo="bar")
    assert evaluator.evaluate("foo") == "bar"

def test__given_large_variable_evaluator__when_evaluate_known__then_returns_that_value():
    evaluator = VariableEvaluator(one=1, two="two", three=.14)
    assert evaluator.evaluate("three") == .14
