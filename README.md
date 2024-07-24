# pyfig

A Python configuration system that's powerful enough to meet complex requirements, while
being simple enough so new contributors to your software can confidently make changes without
worrying how to get everything setup.

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

### Requirements

Strictly, only [pydantic](https://docs.pydantic.dev/latest/) is required.

To make full use of the all features, you may also need some of:
- [pyyaml](https://pyyaml.org/)
- [toml](https://pypi.org/project/toml/)
- [tomli](https://pypi.org/project/tomli/)
- [sympy](https://www.sympy.org/en/index.html)

These can be independently installed as necessary.

## Usage

1. Install pyfig
2. Create a class tree of subclasses of `Pyfig` (*). Provide all attributes, types, docs, and defaults in your `.py`'s
3. Create overriding configs that can be applied hierarchically based on your requirements
4. Load your configuration:
    - Using either the built-in 'metaconf' feature, or
    - By creating your own implementation and calling `pyfig.load_configuration(...)` appropriately

## Tutorial

There is a small tutorial ready to walk you through the features and patterns when using Pyfig.
[Click me](https://github.com/just1ngray/pyfig/tree/publish-pypi-on-tag/tutorial)
