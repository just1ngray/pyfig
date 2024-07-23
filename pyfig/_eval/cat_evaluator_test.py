from pathlib import Path

import pytest

from .cat_evaluator import CatEvaluator


def test__given_missing_file__when_cat_evaluated__then_raises_file_not_found_exception(pytestdir: Path):
    dne = pytestdir / "dne.txt"
    cat_evaluator = CatEvaluator()

    with pytest.raises(FileNotFoundError):
        cat_evaluator.evaluate(dne.as_posix())

def test__given_file_with_content__when_cat_evaluated__then_returns_file_content(pytestdir: Path):
    content = "Hello, World!"
    file = pytestdir / "file.txt"
    file.write_text(content, "utf-8")
    cat_evaluator = CatEvaluator()

    result = cat_evaluator.evaluate(file.as_posix())

    assert result == content

def test__given_utf8_encoded_file__when_evaluated_as_ascii__then_raises_decode_error(pytestdir: Path):
    content = "To the moon! 🚀"
    file = pytestdir / "file.txt"
    file.write_text(content, "utf-8")
    cat_evaluator = CatEvaluator()

    with pytest.raises(UnicodeDecodeError):
        cat_evaluator.evaluate(f"{file.as_posix()}:ascii")

def test__given_file_with_whitespace__when_trim_evaluated__then_returns_content_without_whitespace(pytestdir: Path):
    content = "Hello, World!"
    file = pytestdir / "file.txt"
    file.write_text(f"     {content}\n   \n\n", "utf-8")
    cat_evaluator = CatEvaluator(trim=True)

    result = cat_evaluator.evaluate(file.as_posix())

    assert result == content


def test__given_file_with_whitespace__when_evaluated_witout_trim__then_returns_content_raw(pytestdir: Path):
    content = "     Hello, World!\n   \n\n"
    file = pytestdir / "file.txt"
    file.write_text(content, "utf-8")
    cat_evaluator = CatEvaluator(trim=False)

    result = cat_evaluator.evaluate(file.as_posix())

    assert result == content
