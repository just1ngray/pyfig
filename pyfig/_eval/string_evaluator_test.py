import pytest

from .string_evaluator import StringEvaluator


def test__given_string_evaluator__when_unknown__then_raises_attribute_error():
    evaluator = StringEvaluator()
    with pytest.raises(AttributeError):
        evaluator.evaluate("not_a_method('hello')")

@pytest.mark.parametrize("value", [
    "unbalanced(",
    "()",
    "()method",
    "method)",
])
def test__given_string_evaluator__when_unknown_format__then_raises_value_error(value: str):
    evaluator = StringEvaluator()
    with pytest.raises(ValueError):
        evaluator.evaluate(value)

def test__given_string_evaluator__when_upper__then_returns_uppercase_string():
    assert StringEvaluator().evaluate("upper('hello')") == "HELLO"

def test__given_string_evaluator__when_rjust__then_returns_justified_string():
    assert StringEvaluator().evaluate("rjust('hello', 10)") == "     hello"

def test__given_string_evaluator__when_split__then_returns_elements_array():
    assert StringEvaluator().evaluate("split('hello world', ' ')") == ["hello", "world"]

def test__given_string_evaluator__when_join__then_returns_joined_strings():
    assert StringEvaluator().evaluate("join('_', ['hello', 'world'])") == "hello_world"

def test__given_string_evaluator__when_isnumeric__then_returns_bool_result():
    assert StringEvaluator().evaluate("isnumeric('92')") is True
    assert StringEvaluator().evaluate("isnumeric('no')") is False
