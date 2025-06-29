# pyfig

Pyfig is a configuration library for Python that makes [pydantic](docs.pydantic.dev), the popular data validation
library, suitable to be used as your application's main configuration system.

## Features

- 📂 Hierarchical overrides
- ✅ Validation powered by [pydantic](https://docs.pydantic.dev/latest/)
- 📝 Extensible templating for variables
- 🛠️ Types, defaults, validation, and docs: all in one place directly in your code

Note: pyfig does not inherently support changes to the config at runtime. This feature is not planned.

## Usage

### Step #1: Installation

```shell
pip install jpyfig
```

Strictly, only [pydantic](https://docs.pydantic.dev/latest/) is required. A suitable version is automatically
installed when you install pyfig.

To make full use of the all features, you may also need some of:
- [pyyaml](https://pyyaml.org/)
- [toml](https://pypi.org/project/toml/)
- [tomli](https://pypi.org/project/tomli/)
- [sympy](https://www.sympy.org/en/index.html)

These can be independently installed as necessary.

### Step #2: Define your base configuration

Your configuration is defined as a class tree.

```python
from pyfig import Pyfig

class LoggingConfig(Pyfig):
    stdout: bool = True
    stderr: bool = False
    level: str = "DEBUG"

class Config(Pyfig):
    logging: LoggingConfig = LoggingConfig()
```

Rules:

1. The root of your configuration must inherit from `Pyfig` class
2. All `Pyfig` children must provide valid defaults for all fields
3. You can basically any type annotation or composition of annotations

Your configuration can be as large or as complex as you need it to be. `Pyfig` is an extension of pydantic's
`BaseModel` class, so it supports all the advanced validation features built into that library. If you're unfamiliar
with pydantic, think of it as an advanced form of dataclasses. To get started, consider reviewing some of the following:
[Fields](https://docs.pydantic.dev/latest/concepts/fields/),
[Types](https://docs.pydantic.dev/latest/concepts/types/),
[Unions](https://docs.pydantic.dev/latest/concepts/unions/),
[Validation](https://docs.pydantic.dev/latest/concepts/validators/).

### Step #3: Develop your application

Because your config is defined as Python classes, you can import them and use them throughout your code. It's easy to
work against Pyfig configuration because:

- You don't need to make assertions that your config is valid at runtime, since this is handled when it's loaded
- No typos when accessing the configuration fields since your IDE's linter can easily discover issues as long as you
  are type-annotating your code
- Document the configuration classes and fields so you (and others) can remember what does what

### Step #4: Create overrides

Different deployments of your application may require different combinations of configuration adjustments from the
default which is defined in your Python code. Overrides can be written as Python dictionaries directly, or anything
that deserializes into a Python dictionary (json, yaml, toml, ini, etc.).

It is recommended for each override to adjust conceptual groups of configuration fields to accomplish tasks. E.g.,
adjust everything needed to run on arm64 architecture if the config supports x86 by default. Then, dependent on your
application's deployment, multiple overrides can be composed in order to create advanced behaviour from simple
overrides.

Generally speaking, overrides are merged at the lowest dictionary level. So if you have the following default config:

```yaml
string: string type
integer: 3
floating: 0.14
boolean: False
nested:
    something: else
lists:
    - foo
    - bar
```

and you override with

```yaml
nested:
    something: new
```

Then only `nested.something` will be modified (now equal to `"new"`), and all the defaults will remain in-place.

#### List overrides

Like many configuration systems, overriding a list is done atomically. Meaning you re-define the entire list.

```yaml
lists:
    - baz
```

will now give you:

```yaml
string: string type
integer: 3
floating: 0.14
boolean: False
nested:
    something: else
lists:
    - baz
```

A special syntax allows you to override just a single element by its index:

```yaml
lists:
    1: overridden
```

```yaml
...
lists:
    - foo
    - overridden
```

### Step #5: Load your configuration

Use the `load_configuration` function to apply overrides onto your default config. Serializing your overrides
into a Python dict is (by default) beyond the scope of Pyfig.

```python
from pyfig import load_configuration
from .myconfig import RootConfig

overrides = [{...}, {...}, ...]
config = load_configuration(RootConfig, overrides, [])

# pass bits of your config down to services (etc.) within your application
```

## Tutorial

There is a small tutorial ready to walk you through the features and patterns when using Pyfig.
[Click me](https://github.com/just1ngray/pyfig/tree/master/tutorial)
