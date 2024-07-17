from unittest.mock import Mock

import pytest

from just_in_pyfig._eval.abstract_evaluator import AbstractEvaluator

from .variable_evaluator import VariableEvaluator
from .evaluate_conf import _find_evaluator, _evaluate_string


def test__given_evaluators__when_find_evaluator_with_missing_evaluator__then_raises_value_error():
    variable_evaluator = VariableEvaluator(name="mock")
    with pytest.raises(ValueError):
        _find_evaluator("missing", [variable_evaluator])

def test__given_multiple_evaluators__when_ambiguous_find_evaluator__then_raises_value_error():
    with pytest.raises(ValueError):
        _find_evaluator("mock", [
            VariableEvaluator(first="mock"),
            VariableEvaluator(second="mocked")
        ])

def test__given_evaluators__when_find_evaluator__then_returns_correct_evaluator():
    variable_evaluator = VariableEvaluator(name="mock")
    mock_evaluator = Mock(spec=AbstractEvaluator)
    mock_evaluator.name.return_value = "mock"
    assert _find_evaluator("mock", [variable_evaluator, mock_evaluator]) == mock_evaluator

@pytest.mark.parametrize("string", [
    "",
    "hello, world!",
    "${unmatched brace",
    "{no dollar sign}",
    "3.14"
])
def test__given_regular_string__when_evaluate_string__then_return_unmodified_string(string: str):
    mock_evaluator = VariableEvaluator(mock="mocked")
    assert _evaluate_string(string, [mock_evaluator]) == string

def test__given_full_string_template__when_evaluate_string__then_returns_evaluated_string():
    mock_evaluator = VariableEvaluator(mock="mocked")
    assert _evaluate_string("${var.mock}", [mock_evaluator]) == "mocked"

def test__given_substring_template__when_evaluate_string__then_substitutes_substring():
    mock_evaluator = VariableEvaluator(name="tester")
    assert _evaluate_string("hello, ${var.name}!", [mock_evaluator]) == "hello, tester!"

def test__given_multiple_templates__when_evaluate_string__then_subsitutes_all_templates():
    mock_evaluator = VariableEvaluator(endpoint="localhost", port=8080, path="api")
    assert _evaluate_string("GET ${var.endpoint}:${var.port}/${var.path}", [mock_evaluator]) == "GET localhost:8080/api"

def test__given_same_template__when_evaluate_string__then_substitutes_each():
    mock_evaluator = VariableEvaluator(name="tester")
    assert _evaluate_string("${var.name} ${var.name} ${var.name}", [mock_evaluator]) == "tester tester tester"

@pytest.mark.parametrize("replacement", [
    False,
    None,
    3.14,
    17,
])
def test__given_stringable_replacement_substring__when_evaluate_string__then_replaces_into_string(replacement):
    mock_evaluator = VariableEvaluator(repl=replacement)
    assert _evaluate_string("replacement is ${var.repl}", [mock_evaluator]) == f"replacement is {replacement}"

@pytest.mark.parametrize("replacement", [
    False,
    None,
    3.14,
    17,
])
def test__given_full_non_string_replacement__when_evaluate_string__then_respects_type(replacement):
    mock_evaluator = VariableEvaluator(repl=replacement)
    assert _evaluate_string("${var.repl}", [mock_evaluator]) == replacement
