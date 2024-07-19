import pytest

from .sympy_evaluator import SympyEvaluator


@pytest.mark.parametrize("expr, ans", [
    ("3+5", 8),
    ("2/3", 1),
    ("sqrt(4)", 2),
    ("2**3", 8),
    ("10*5/2", 25),
    ("10+4/2", 12), # no it's not 7 lol
    ("4!", 24),
    ("abs(-1)", 1),
    ("pi", 3),
])
def test__given_valid_int_expression__when_evaluated__then_returns_correct_int(expr: str, ans: int):
    evaluator = SympyEvaluator()
    assert evaluator.evaluate(expr) == ans

@pytest.mark.parametrize("expr, ans", [
    ("2.0/3.0", 0.667),
    ("1.0*pi", 3.141)
])
def test__given_valid_float_expression__when_evaluated__then_returns_close_float(expr: str, ans: float):
    evaluator = SympyEvaluator()
    result = evaluator.evaluate(expr)
    diff = abs(result - ans)
    assert diff < 0.001, f"{ans} !~= {result} (diff={diff})"
