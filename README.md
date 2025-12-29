# pyfig

Pyfig is a configuration library for Python that makes [pydantic](docs.pydantic.dev), the popular data validation
library, suitable to be used as your application's main configuration system.

- [pyfig](#pyfig)
  - [Installation](#installation)
  - [Features](#features)
    - [Powered by pydantic](#powered-by-pydantic)
    - [Default configuration](#default-configuration)
    - [Overrides](#overrides)
      - [List overrides](#list-overrides)
    - [Evaluators](#evaluators)
      - [Syntax](#syntax)
      - [Substitution behaviour](#substitution-behaviour)
      - [Repeated evaluation](#repeated-evaluation)
      - [Pyfig's built-in evaluators](#pyfigs-built-in-evaluators)
    - [Metaconf](#metaconf)
      - [Details](#details)
      - [Example](#example)
  - [Testing your application's configuration](#testing-your-applications-configuration)
    - [Checking the default config is loadable](#checking-the-default-config-is-loadable)
    - [Check that your overrides are OK](#check-that-your-overrides-are-ok)
    - [Commit your final configs](#commit-your-final-configs)
    - [Check for unused config sections](#check-for-unused-config-sections)

## Installation

`pyfig` has simple requirements: Python >= 3.8 and Pydantic v2.

```shell
pip install jpyfig
```

Optional dependencies that must be manually installed.

- [pyyaml](https://pyyaml.org/)
- [toml](https://pypi.org/project/toml/)
- [tomli](https://pypi.org/project/tomli/)
- [sympy](https://www.sympy.org/en/index.html)

## Features

### Powered by pydantic

Pydantic is a *powerful* data validation library that take built-in dataclasses to a whole new level. Use as many
or as few features as you like.

- type hints
- per-field validation
- entire-model validation
- secret strings
- datetime, time, and delta
- enums and literals
- pathlib paths
- serialization

For more information, see: [https://docs.pydantic.dev/latest/](https://docs.pydantic.dev/latest/) and
[https://docs.pydantic.dev/latest/concepts](https://docs.pydantic.dev/latest/concepts)

### Default configuration

Pyfig requires that the default configuration is bundled into your application as a class tree of `Pyfig` BaseModels.
The root of your config must inherit from `Pyfig`, which basically asserts that all pydantic fields have defaults.

```python
from typing import Literal, List
from pyfig import Pyfig
from pydantic import BaseModel, Field, model_validator, field_validator

class LoggingConfig(Pyfig):
    level: Literal["debug", "info", "warning", "error"] = "info"
    """logs below this level are silenced. (debug < info < warning < error)"""
    stdout: bool = True
    stderr: bool = False

    @model_validator(mode="after")
    def check_some_sink_enabled(self):
        if not self.stdout and not self.stderr:
            raise ValueError("Either stdout and or stderr logging must be enabled!")
        return self

class TaskConfig(BaseModel):
    enabled: bool = True
    interval_seconds: float = Field(default=60.0, gt=0.0)
    command: List[str]

    @field_validator("command")
    @classmethod
    def validate_command(cls, command: List[str]):
        if len(command) == 0:
            raise ValueError("command must be non-empty")
        return command

class RootConfig(Pyfig):
    """
    Root of my example application's configuration.
    """
    logging: LoggingConfig = LoggingConfig()
    tasks: List[TaskConfig] = [
        TaskConfig(command=["echo", "hello-world!"]),
        TaskConfig(command=["sqlite", "application.db", "PRAGMA wal_checkpoint(TRUNCATE);"]),
    ]

# create the config (or any subsection) easily
config = RootConfig()
```

### Overrides

Like many other configuration systems, overrides are applied at the lowest key level. E.g., in the above configuration
we can turn on `logging.stderr` by using the override:

```python
from pyfig import load_configuration

override = {
    "logging": {
        "stderr": True,
    },
}

config = load_configuration(RootConfig, [override], [])
assert config.logging.stderr is True
```

Multiple overrides can be given in descending priority order. Deserializing the overrides from files into dictionaries
is handled by external modules like `json`, `pyyaml`, `toml`, etc.

#### List overrides

Like many other configuration systems, overrides to lists are applied atomically. This means you must redefine the
entire list (continue reading for an exception)

```python
override = {
    "tasks": [
        {
            "enabled": True,
            "interval_seconds": 60.0,
            "command": [
                "sqlite",
                "application.db",
                "PRAGMA wal_checkpoint(TRUNCATE);"
            ]
        }
    ]
}
```

However, pyfig also implements a novel trick that allows for overriding a single item in a list using its index.

```python
override = {
    "tasks": {
        1: { "enabled": False }
    }
}
```

### Evaluators

Evaluators replace templates in the config with some other value. They're evaluated repeatedly, and can be extended
to implement whatever behaviour you want. They can fill-in new data, as well as mutate existing values. When calling
`load_configuration(...)`, all necessary evaluators must be provided in order to receive a valid
configuration object.

(!) Note, evaluation happens before handing-off to pydantic, so whatever you evaluate to must be a valid config.

#### Syntax

A template looks like `${{evaluator}}` or `${{evaluator.args}}`.

Exactly one evaluator class must match the evaluator by name, and that evaluator is given the (optionally present)
arguments to aid in figuring out what the replacement should be.

#### Substitution behaviour

When a template is found within a string, the evaluated template is interpolated into that string.

```yaml
example_yaml_config: Hello, ${{var.name}}!
```

would use the `VariableEvaluator` to substitute the substring only. For example, as:

```yaml
example_yaml_config: Hello, Justin!
```

When the template is the entire string, then the evaluator is granted more power. For example, you could create
an evaluator which adds your application's database connection details:

```python
pyfig.VariableEvaluator(db={
    "host": "localhost",
    "port": 1234
})
```

would substitute a simple config,

```yaml
db: ${{var.db}}
```

as:

```yaml
db:
  host: localhost
  port: 1234
```

#### Repeated evaluation

Because evaluators are resolved repeatedly, it is possible for a template to evaluate to another template.

```python
evaluators = [
    pyfig.VariableEvaluator(name="${{env.SOME_ENVIRONMENT_VARIABLE}}!"),
    pyfig.EnvironmentEvaluator()
]
```

Suppose the environment variable `SOME_ENVIRONMENT_VARIABLE` is set to `foo`. These evaluators would evaluate
`${{var.name}}` template first as `${{env.SOME_ENVIRONMENT_VARIABLE}}!` and then as `foo!`.

#### Pyfig's built-in evaluators

All evaluators are implemented in [this module](./pyfig/_eval/).

| Class Name | Evaluator Name | Purpose | Basic Syntax |
| - | - | - | - |
| VariableEvaluator | var | Replace with hardcoded values | `${{var.<variable_name>}}` |
| EnvironmentEvaluator | env | Use environment variables | `${{env.<ENVIRONMENT_VARIABLE>}}` |
| CatEvaluator | cat | Use the contents of a file | `${{cat.any/file.path}}` |
| JSONFileEvaluator | jsonfile | Extract a json file field | `${{jsonfile.access.path.to.field:/path/to/file.json}}` |
| YamlFileEvaluator | pyyaml | Extract a yaml file field | `${{pyyaml.access.path.to.field:/path/to/file.yaml}}` |
| PythonEvaluator | pyeval | `eval()` an expression with Python | `${{pyeval.1 + 1}}` |
| StringEvaluator | str | Calls a Python string method | `${{str.upper('hello')}}` |
| SympyEvaluator | sympy | Evaluates a math expression | `${{sympy.3+5}}` |

For more details about any specific evaluator, be sure to read its docstring.

### Metaconf

A `Metaconf` is Pyfig's built-in approach for loading a configuration.

It is recommended to bundle config overrides *with the application* (e.g., in the docker image) and then choose
which are combined using a separately deployed metaconf. This comes with two main benefits:

1. Fewer configuration releases since the 'goals' of a config rarely change. If you design your overrides to be
   composable, you can freely modify overrides and only need to deploy a config change when the metaconf changes.
2. Less downtime when a deployed config no longer makes sense for an updated application image. (Or vice versa)

#### Details

In this approach, you bundle your overriding configs with your application, and then tell the application
how to load the configuration using the a metaconf file. A metaconf file can be a `json`, `yaml`, `ini`, or
`toml`, and defines up to three things:

```yaml
evaluators:
  pyfig.VariableEvaluator:
    variable_name: replacement
  pyfig.EnvironmentEvaluator: {}
  your.custom.Evaluator:
    ...

configs:
  - path/to/a/config.yaml
  - /somewhere/on/your/filesystem.ini

overrides:
  specific: in-line
  overrides:
    can:
      go: here
```

The evaluators section defines which evaluators you want to use to resolve string templates (e.g., `${{eval.args}}`).
To use an evaluator, it must be defined here. You can use any Pyfig built-in evaluator, or you can implement and
use your own. The key roughly equates to an import statement: `pyfig.VariableEvaluator` means
`from pyfig import VariableEvaluator`, and the imported class is constructed with the kwargs specified in the metaconf.

The configs section defines the list of overriding configs to apply to your default config in descending priority
order. These paths can be absolute or relative.

The final section is can be used to apply top-level configuration overrides. Because the overriding configs are
generally bundled inside the application, this mechanism can be used to apply config-based hot fixes without needing
to make a full software release.

#### Example

```python
from pyfig import Pyfig, Metaconf

class MyConfig(Pyfig):
    ...

metaconf = Metaconf.from_path("path/to/metaconf.yaml")
config = metaconf.load_config(MyConfig)
```

## Testing your application's configuration

The following tests are written for [pytest](https://docs.pytest.org/en/stable/) and can be copy and pasted into
your testing suite.

### Checking the default config is loadable

```python
def test__given_no_evaluator_or_overrides__when_load_configuration__then_defaults_are_used():
    _no_validation_error = MyRootConfig()
    _via_load_configuration = load_configuration(MyRootConfig, overrides=[], evaluators=[])
```

(*) Note, you may have to pass some mock evaluators in if your default configuration assumes some evaluators are
    present. However, it is recommended to not use evaluators in your default configuration.

### Check that your overrides are OK

This includes ensuring that the overrides don't specify any non-existent fields which are usually the result of typos.

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

### Commit your final configs

It can be challenging to conceptualize how different combinations of overrides and/or evaluators will load into your
application's configuration classes. To make config changes easy to understand and review, you can commit each
loaded config to the repository so the loaded versions will be reviewed in PRs and kept in your git history.
This can be done manually and verified with a test, using a pipeline, or even pre-commit hooks.

```python
@pytest.mark.parametrize("metaconf_path", Path("...").glob("**/*.yaml"), ids=Path.as_posix)
def test__given_metaconf__when_serialized__then_is_same_as_committed_version(metaconf_path: Path):
    # some mocking may be required if you're making heavy use of environment specific evaluators
    metaconf = Metaconf.from_path(metaconf_path)
    config = metaconf.load_config()
    config_serialized = config.model_dump_json(indent=2)

    committed = Path(...).read_text("utf-8")

    assert config_serialized == committed
```

### Check for unused config sections

Pyfig can track and report about which config sections and fields were actually used at runtime. This can be handy in
finding fields that no longer do anything.

```python
import os
from pyfig import PyfigDebug
from .config import MyConfig # example

def main(config: MyConfig):
    ...

if __name__ == "__main__":
    cfg = MyConfig() # or however it's loaded

    if os.environ.get("PYFIG_DEBUG"): # or another toggle
        cfg = PyfigDebug.wrap(cfg)

    # run your code normally
    main(cfg)

    if isinstance(cfg, PyfigDebug):
        unused = set(cfg.pyfig_debug_unused())
        if len(unused) == 0:
            print("All configs were used at runtime")
        else:
            print("Unused Configurations:")
            print("- ", "\n- ".join(unused))
```
