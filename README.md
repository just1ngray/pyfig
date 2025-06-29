# pyfig

Pyfig is a configuration library for Python that makes [pydantic](docs.pydantic.dev), the popular data validation
library, suitable to be used as your application's main configuration system.

## Features

- 📂 Hierarchical overrides
- ✅ Validation powered by [pydantic](https://docs.pydantic.dev/latest/)
- 📝 Extensible templating for variables
- 🛠️ Types, defaults, validation, and docs: all in one place directly in your code

Note: pyfig does not inherently support changes to the config at runtime. This feature is not planned.

## Installation

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

## Usage

...

## Tutorial

There is a small tutorial ready to walk you through the features and patterns when using Pyfig.
[Click me](https://github.com/just1ngray/pyfig/tree/master/tutorial)
