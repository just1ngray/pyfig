# Testing your Configuration

There are a few recommended automated tests which can be dropped into your test suite. Typically, this test file
can go anywhere near your class tree definition module(s).

## Default Config is Loadable

Even if your config includes advanced environment-specific evaluators (like reading environment variables), it's still
important to test that your default config can be loaded independently.

Example using [pytest](https://docs.pytest.org/en/stable/):

```python
def test__given_no_evaluator_or_overrides__when_load_configuration__then_defaults_are_used():
    _no_validation_error = MyRootConfig()
    _via_load_configuration = load_configuration(MyRootConfig, overrides=[], evaluators=[])
```

Note: you may have to pass in some (mock) evaluators to make your default config class loadable using
`load_configuration`. This can happen if your default config assumes some evaluator(s) are present.

```python
from unittest.mock import Mock
some_mock_evaluator = VariableEvaluator(**{
    "any-key.works.here because dict expansion": "mock replacement"
})
some_mock_evaluator.name = Mock(return_value="yaml") # e.g., you are mocking the YamlFileEvaluator
```

## Overriding Configs Override Real Fields

An overriding config should be kept up to date with the application. Inevitably, application changes will be made at
some point which cause existing override files to no longer override real fields. Typically, overrides to imaginary
fields are ignored (See: `load_configuration(...)`'s `allow_unused` kwarg.). However, if we are more strict in testing,
we can catch these outdated configuration files before releasing.

Example using [pytest](https://docs.pytest.org/en/stable/):

```python
@pytest.mark.parametrize("overriding_path", Path("...").glob("**/*.yaml"), ids=Path.as_posix)
def test__given_overriding_config__when_disallow_unused__then_config_is_loaded(overriding_path: Path):
    overriding_dict = yaml.safe_load(overriding_path.read_text("utf-8"))
    _no_validation_error = load_configuration(
        default=MyRootConfig,
        overrides=[overriding_dict],
        evaluators=[],
        allow_unused=False # this is the important bit - default is True, which allows unused fields to exist
    )
```

Similar to above (Default Config is Loadable), you may need to construct some mock evaluator(s) to ensure that
overrides work to create a loadable config using `load_configuration`.
