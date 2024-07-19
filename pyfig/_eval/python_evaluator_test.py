import pytest

from .python_evaluator import PythonEvaluator


@pytest.mark.parametrize("value, exp", [
    ("0", 0),
    ("int(1)", 1),
    ("1 + 1", 2),
    ("round(22/7, 2)", 3.14),
    ('"hello" + " " + "world!"', 'hello world!'),
    ('"too excited!!!!!!!!!!".rstrip("!")', "too excited"),
    ("bool(42)", True),
    ["[i**2 for i in range(4)]", [0, 1, 4, 9]],
    ("[1, 2, 3][1]", 2),
])
def test__given_proper_python_syntax_variable__when_evaluate_with_python_evaluator__then_returns_output(value, exp):
    evaluator = PythonEvaluator(danger="accepted")
    assert evaluator.evaluate(value) == exp

def test__given_no_args_python_evaluator__when_instantiate__then_raises_error():
    with pytest.raises(RuntimeError):
        PythonEvaluator()

    with pytest.raises(RuntimeError):
        PythonEvaluator(danger="bad_value")
