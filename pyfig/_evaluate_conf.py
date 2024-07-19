import re
from typing import Any, Optional, Collection, Union

from ._eval import AbstractEvaluator


def _find_evaluator(name: str, evaluators: Collection[AbstractEvaluator]) -> AbstractEvaluator:
    """
    Finds an evaluator by name in a collection of evaluators.

    Args:
        name:       the name of the evaluator to find
        evaluators: the collection of evaluators to search through

    Returns:
        The evaluator with the given name.

    Raises:
        ValueError if no evaluator is found or if multiple evaluators are found with the same name.
    """
    candidate: Optional[AbstractEvaluator] = None

    for evaluator in evaluators:
        if evaluator.name() == name:
            if candidate is not None:
                raise ValueError(f"Multiple evaluators found for name: '{name}'")

            candidate = evaluator

    if candidate is None:
        raise ValueError(f"No evaluator found for name: '{name}'")
    else:
        return candidate


#
# Language Implementation Note:
#
# This regular expression is designed to handle the most inner parsing of a template string first.
# For example, consider the string "${{recursive.${{nested}}}}" which contains two ${{...}} templates.
# This regular expression will match "${{nested}}" so it can be templated first. When matching the
# evaluated result, it will match "${{recursive.evaluated}}" so it can be templated next.
#
# The other approach would pass value="${{nested}}" to the evaluator="recursive". This could enable
# users to configure templates for templates. However, this behaviour is probably less intuitive in
# practice, since most template evaluators are meant to be very simple - it'd be better to take as
# input to the evaluator an evaluated result rather than a template itself. Using this approach would
# also require a more powerful language parser, like a context-free grammar.
#
# Practical Example:
#   Consider the simple evaluator: 'cap', which just capitalizes the value.
#   Suppose that the 'var' evaluator is being used to substitute the 'name' variable.
#   The configured string is "${{cap.${{var.name}}}}". The expected result is the capitalized name.
#
#   The implemented approach will first evaluate "${{var.name}}" to get the name.
#       "${{cap.${{var.name}}}}" -> "${{cap.justin}}" -> "JUSTIN"
#
#   The alternative described approach will pass the templated value to the evaluator.
#       "${{cap.${{var.name}}}}" -> "${{VAR.NAME}}" -> ?
#
# In reality this is probably an edge case nobody will ever really notice...
# If you really want to template a template, you should escape the inner template.
# And if you happen to run into issues with single '}' at the end if your 'value': add a trailing space.
#
_TEMPLATE_PATTERN = re.compile(r"""
    (?P<nonesc>^|[^\\])                     # either the beginning of the string or a non-escape character
    \$\{\{                                  # the opening template sequence '${{'
        (?P<evaluator>[A-Za-z0-9_-]*)       # the evaluator name to use
        (\.                                 # optionally, the evaluator itself might have some arguments
            (?P<value>                      # ... but the argument cannot contain unescaped '}}' or '${{' substrings
                (                               # OK state:
                    \\.                         # -> any escaped character
                    | [^$}]                     # -> regular allowed first characters (not '}' or '$')
                    | \}[^}]                    # -> '}' followed by anything but '}'
                    | \$\{?[^{]                 # -> '$' or '${' followed by anything but '{'
                )*
                (                               # OK state (but only at the end, and only if necessary for a match):
                    \}                          # -> a single trailing '}'
                    | \$\}?                     # -> a trailing '$' or '${'
                )??
            )
        )?
    \}\}                                    # the closing template sequence '}}'
""", re.VERBOSE)
"""
A regular expression pattern that matches a template string.

A template (sub)string starts with a dollar sign ($) and is wrapped in double curly braces ({{}}).
It consists of two parts:
1. The evaluator name, which is a sequence of alphanumeric characters, underscores, and hyphens.
2. The value, which is an optional sequence of characters that is separated from the evaluator name by a period.
   Note: the value can contain anything except double closing curly braces (}}).

E.g.,
    "${{foo}}" -> { "evaluator": "foo", "value": None }
    "${{foo.bar}}" -> { "evaluator": "foo", "value": "bar" }
    "some ${{eval.val}} string" -> { "evaluator": "eval", "value": "val" }

Note: if escaped - i.e., \\${{...}} - then there is no match.
"""


def _evaluate_string(string: str, evaluators: Collection[AbstractEvaluator]) -> Any:
    """
    Given a string, evaluates all templates in the string using the provided evaluators.

    Args:
        string:      the string to evaluate
        evaluators:  the collection of evaluators to use

    Returns:
        the modified string with all templates evaluated
        if the template is the entire string, then the type of the evaluator's return value is kept
    """
    # if the entire string is a template, evaluate it and keep the type
    if full_match := _TEMPLATE_PATTERN.fullmatch(string):
        evaluator = _find_evaluator(full_match.group("evaluator"), evaluators)
        return evaluator.evaluate(full_match.group("value") or "")

    def replace_substring(patmatch: re.Match) -> str:
        evaluator = _find_evaluator(patmatch.group("evaluator"), evaluators)
        value = patmatch.group("value") or ""
        replacement = str(evaluator.evaluate(value))
        return patmatch.group("nonesc") + replacement

    # otherwise, replace only the relevant substring(s)
    return re.sub(
        _TEMPLATE_PATTERN,
        replace_substring,
        string
    )


def evaluate_conf(conf: Union[list, dict], evaluators: Collection[AbstractEvaluator]) -> None:
    """
    Recursively evaluates all (present+future) templates in `conf` using the provided `evaluators`

    Substrings matching `${{evaluator.value}}` are interpolated in-place. Strings fully matching
    `${{evaluator.value}}` are replaced with the evaluator's evaluation. This is done repeatedly
    until no more templates exist, which means templates can exist within templates.

    Args:
        conf:        the configuration to search and evaluate templates
        evaluators:  the collection of evaluators to use (i.e., how to evaluate the templates)

    Returns:
        None (conf is modified in-place)
    """
    changes = 1

    while changes > 0:
        changes = 0

        if isinstance(conf, dict):
            for key, value in conf.items():
                if isinstance(value, str):
                    new = _evaluate_string(value, evaluators)
                    if new != value:
                        conf[key] = new
                        changes += 1

                elif isinstance(value, (dict, list)):
                    evaluate_conf(value, evaluators)

        elif isinstance(conf, list):
            for i, item in enumerate(conf):
                if isinstance(item, (dict, list)):
                    evaluate_conf(item, evaluators)

                elif isinstance(item, str):
                    new = _evaluate_string(item, evaluators)
                    if new != item:
                        conf[i] = new
                        changes += 1

        else:
            raise TypeError(f"Cannot evaluate conf of unknown type: {type(conf)}")
