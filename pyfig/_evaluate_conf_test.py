from copy import deepcopy
from unittest.mock import Mock

import pytest

from ._eval import AbstractEvaluator, VariableEvaluator
from ._evaluate_conf import _TEMPLATE_PATTERN, _find_evaluator, _evaluate_string, evaluate_conf


@pytest.mark.parametrize("string", [
    "",
    "\\${{escaped}}",
    "$\\{{more.escaping}}",
    "${\\{more.escaping}}",
    "${{more.escaping}\\}",
    "${{inv@lid.character}}"
])
def test__given_unmatched_string__when_match_against_template_pattern__then_doesnt_match(string: str):
    patmatch = _TEMPLATE_PATTERN.search(string)
    assert patmatch is None

@pytest.mark.parametrize("string,nonesc,evaluator,value", [
    ("${{easy}}",                               "",  "easy",        None),
    ("${{easy.mode}}",                          "",  "easy",        "mode"),
    ("it's a ${{sub.string}}!",                 " ", "sub",         "string"),
    ("${{partial ${{evaluate.me}}",             " ", "evaluate",    "me"),
    ("${{evaluate.me}} nope}}",                 "",  "evaluate",    "me"),
    ("${{eval.$}}",                             "",  "eval",        "$"),
    ("${{eval.{py_string} }}",                   "",  "eval",       "{py_string} "),
    ("${{eval.${js_string} }}",                  "",  "eval",       "${js_string} "),
    ("${{recursive.repl='\\${{template\\}}'}}", "",  "recursive",   "repl='\\${{template\\}}'"),
    ("${{cap.${{var.name}}}}",                  ".", "var",         "name"),
])
def test__given_matching_string__when_match_against_template_pattern__then_matches_properly(
        string: str, nonesc: str, evaluator: str, value: str):

    patmatch = _TEMPLATE_PATTERN.search(string)
    assert patmatch is not None
    assert patmatch.group("nonesc") == nonesc
    assert patmatch.group("evaluator") == evaluator
    assert patmatch.group("value") == value

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
    "${{unmatched brace}",
    "{{no dollar sign}}",
    "3.14",
    "${single brace only}",
    "\\${{escaped}}"
])
def test__given_regular_string__when_evaluate_string__then_return_unmodified_string(string: str):
    mock_evaluator = Mock(spec=AbstractEvaluator)
    mock_evaluator.name.return_value = "mock"
    mock_evaluator.evaluate.return_value = "mocked"
    assert _evaluate_string(string, [mock_evaluator]) == string

def test__given_full_string_template__when_evaluate_string__then_returns_evaluated_string():
    mock_evaluator = VariableEvaluator(mock="mocked")
    assert _evaluate_string("${{var.mock}}", [mock_evaluator]) == "mocked"

def test__given_substring_template__when_evaluate_string__then_substitutes_substring():
    mock_evaluator = VariableEvaluator(name="tester")
    assert _evaluate_string("hello, ${{var.name}}!", [mock_evaluator]) == "hello, tester!"

def test__given_multiple_templates__when_evaluate_string__then_subsitutes_all_templates():
    mock_evaluator = VariableEvaluator(endpoint="localhost", port=8080, path="api")
    assert _evaluate_string("GET ${{var.endpoint}}:${{var.port}}/${{var.path}}", [mock_evaluator]) == "GET localhost:8080/api"

def test__given_same_template__when_evaluate_string__then_substitutes_each():
    mock_evaluator = VariableEvaluator(name="tester")
    assert _evaluate_string("${{var.name}} ${{var.name}} ${{var.name}}", [mock_evaluator]) == "tester tester tester"

@pytest.mark.parametrize("replacement", [
    False,
    None,
    3.14,
    17,
])
def test__given_stringable_replacement_substring__when_evaluate_string__then_replaces_into_string(replacement):
    mock_evaluator = VariableEvaluator(repl=replacement)
    assert _evaluate_string("replacement is ${{var.repl}}", [mock_evaluator]) == f"replacement is {replacement}"

@pytest.mark.parametrize("replacement", [
    False,
    None,
    3.14,
    17,
])
def test__given_full_non_string_replacement__when_evaluate_string__then_respects_type(replacement):
    mock_evaluator = VariableEvaluator(repl=replacement)
    assert _evaluate_string("${{var.repl}}", [mock_evaluator]) == replacement

def test__given_no_evaluation_args__when_evaluate_string__then_calls_evaluator_with_empty_string():
    mock_evaluator = Mock(spec=AbstractEvaluator)
    mock_evaluator.name.return_value = "mock"
    _evaluate_string("${{mock}}", [mock_evaluator])
    mock_evaluator.evaluate.assert_called_once_with("")

def test__given_dict_in_value__when_evaluate_string__then_calls_evaluator_with_dict():
    mock_evaluator = Mock(spec=AbstractEvaluator)
    mock_evaluator.name.return_value = "mock"
    _evaluate_string("${{mock.{} }}", [mock_evaluator])
    mock_evaluator.evaluate.assert_called_once_with("{} ")


def test__given_empty_dict__when_evaluate__then_no_error():
    conf = {}
    evaluate_conf(conf, [Mock(side_effect=Exception())])
    assert conf == {}

def test__given_dict_with_no_strings__when_evaluate_conf__then_no_changes():
    original_dict = {
        "key": 3.14,
        "key2": False,
        "key3": {
            "nested": 17
        }
    }
    mutable_copy = deepcopy(original_dict)
    evaluate_conf(mutable_copy, [Mock(side_effect=Exception())])
    assert mutable_copy == original_dict

def test__given_dict_with_one_string__when_evaluate_conf__then_replaces_string():
    conf = { "key": "hello, ${{var.name}}!" }
    evaluator = VariableEvaluator(name="tester")
    evaluate_conf(conf, [evaluator])
    assert conf == { "key": "hello, tester!" }

def test__given_dict_with_multiple_strings__when_evaluate_conf__then_replaces_each_string():
    conf = {
        "greeting": "hello, ${{var.name}}!",
        "farewell": "goodbye, ${{var.name}}!"
    }
    evaluator = VariableEvaluator(name="tester")
    evaluate_conf(conf, [evaluator])
    assert conf == {
        "greeting": "hello, tester!",
        "farewell": "goodbye, tester!"
    }

def test__given_dict_with_nested_strings__when_evaluate_conf__then_replaces_template_strings():
    conf = {
        "nested": {
            "greeting": "hello, ${{var.name}}!",
            "farewell": "goodbye, ${{var.name}}!",
            "age": "${{var.age}}"
        },
        "top": "${{mock.subtree}}"
    }
    mock_evaluator = Mock(spec=AbstractEvaluator)
    mock_evaluator.name.return_value = "mock"
    mock_evaluator.evaluate.return_value = {
        "deeply": {
            "nested": {
                "stuff": 1.0
            }
        }
    }
    variable_evaluator = VariableEvaluator(name="tester", age=99)

    evaluate_conf(conf, [mock_evaluator, variable_evaluator])
    assert conf == {
        "nested": {
            "greeting": "hello, tester!",
            "farewell": "goodbye, tester!",
            "age": 99
        },
        "top": {
            "deeply": {
                "nested": {
                    "stuff": 1.0
                }
            }
        }
    }

def test__given_recursive_evaluator__when_evaluate_conf__then_evaluates_recursively():
    evaluator = VariableEvaluator(prefix="${{var.", suffix="cool}}", cool="Wow!")
    conf = { "key": "${{var.prefix}}${{var.suffix}}" }
    evaluate_conf(conf, [evaluator])
    assert conf == { "key": "Wow!" }

def test__given_template_in_array__when_evaluate_conf__then_substitutes():
    conf = {
        "array": [
            "${{var.item1}}",
            {
                "name": "${{var.name}}",
                "age": "${{var.age}}"
            }
        ]
    }
    evaluator = VariableEvaluator(item1=True, name="tester", age=99)
    evaluate_conf(conf, [evaluator])
    assert conf == {
        "array": [
            True,
            {
                "name": "tester",
                "age": 99
            }
        ]
    }

def test__given_nested_array__when_evaluate_conf__then_subsititutes_deeply():
    conf = {
        "array": [
            [ "${{var.item1}}", "${{var.item2}}" ],
            { "array": ["${{var.deep}}"] }
        ]
    }
    evaluator = VariableEvaluator(item1=True, item2=False, deep=None)
    evaluate_conf(conf, [evaluator])
    assert conf == {
        "array": [
            [ True, False ],
            { "array": [None] }
        ]
    }

def test__given_recursive_array_templating__when_evaluate_conf__then_substitutes_properly():
    mock_evaluator = Mock(spec=AbstractEvaluator)
    mock_evaluator.name.return_value = "mock"
    mock_evaluator.evaluate.return_value = [
        "${{var.item1}}",
        { "key": "${{var.item2}}" },
        [ "${{var.item3}}" ]
    ]
    variable_evaluator = VariableEvaluator(item1=1, item2=2.0, item3=3.14)

    conf = { "array": "${{mock}}" }
    evaluate_conf(conf, [mock_evaluator, variable_evaluator])

    assert conf == {
        "array": [
            1,
            { "key": 2.0 },
            [ 3.14 ]
        ]
    }
