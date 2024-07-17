# pyfig

A Python configuration system that's powerful enough to meet complex requirements, while
being simple enough so new contributors can confidently make changes without worrying how
to get everything setup.

## Features

- 🏆 Heiarchical overrides
- ✅ Validation powered by [pydantic](https://docs.pydantic.dev/latest/)
- ✏️ Extensible templating for variables
- 🚀 Type-annotated configuration classes
- 🔎 Document your config using docstrings
- 📦 Package config files with your application, and configure how to combine the configs

Note: pyfig does not inherently support changes to the config at runtime.

## Installation

```shell
pip install git+https://github.com/just1ngray/pyfig.git
```

### Requirements

Strictly, only [pydantic](https://docs.pydantic.dev/latest/) is required.

To make full use of the 'meta configuration' feature, you may also need some of:
- [pyyaml](https://pyyaml.org/)
- [toml](https://pypi.org/project/toml/)
- [tomli](https://pypi.org/project/tomli/)

These can be independently installed as necessary.

## Usage

See the [example](./example) directory in this repository for an example of using pyfig.

```yaml
evaluators:
  pyfig.VariableEvaluator:
    protocol: https
    host: production.example.com
    port: ""
  pyfig.EnvironmentEvaluator: {}

configs:
  - example/configs/special_mode.yml
  - example/configs/do_health_check.json
  - example/configs/prod.yaml

overrides:
  name: "Production Application"
```

A [metaconf.yaml](./example/metaconf.yaml) defines how to create the application config.
It assumes a base default configuration tree specified in [config.py](./example/config.py),
and then applies overrides to it as specified in [metaconf.yaml](./example/metaconf.yaml).
After applying overrides, templates are evaluated given the meta configuration's
`evaluators` section, which defines how to handle `${{template}}` style strings.

This config turns the example default config:

```yaml
name: My Application
version: 0.1.0
log_level: DEBUG
modules:
  health_monitor:
    enabled: false
    interval_seconds: 30
  important_task:
    enabled: true
    resource: "http://localhost:8080/api"
    api_key: "${{env.EXAMPLE_API_KEY}}"
    params:
      timeout: 10
      retries: 3
```

into a config ready for use by the application:

```yaml
name: Production Application
version: 0.1.0
log_level: INFO
modules:
  health_monitor:
    enabled: true
    interval_seconds: 30
  important_task:
    enabled: true
    resource: "https://production.example.com/important_task"
    api_key: mocked api key
    params:
      timeout: 60
      retries: 100
```

## How it Works

At its core, there are five levels to pyfig:

1. Deserializing configuration overrides from files is handled by other libraries (json, yaml, etc.)
2. Combine overrides by merging them in priority order
3. Apply the (combined) overrides to the default config
4. Evaluate string templates
5. Convert & validate into a pydantic class tree for use by the application

Basically, you give pyfig a class tree (with defaults), and a bunch of overriding dictionaries, and it
will create your application's configuration by giving you back a pydantic-based class tree.

Overrides are applied in priority order. A high priority override will always take prescedence over a
low priority one. Combining all the overrides at once makes it easier later when we apply & template
the config.

Templates are string-based variables which allow you to separate config structure from contents. There
are two modes:
1. When a value contains a template substring, only the substring is replaced.
    ```yaml
    endpoint: http://${{var.host}}/api
    ```
    will use the [VariableEvaluator](./pyfig/_eval/variable_evaluator.py) to look for the value of `host`.
    If `host` is defined as `localhost:8080`, then the config will evaluate to:
    ```yaml
    endpoint: http://localhost:8080/api
    ```
2. When a value is exactly one template string, the value itself is replaced.
    ```yaml
    endpoint: "${{var.endpoint}}"
    ```
    Could turn into something like:
    ```yaml
    endpoint:
      host: localhost
      port: 8080
    ```

Additionally, templates are evaluated recursively. This means that templates themselves can contain templates:
```yaml
# default value includes a template
endpoint: ${{var.endpoint}}

# which could be intermediately evaluated as
endpoint:
  host: ${{var.cluster}}
  port: 80

# and then finally, perhaps
endpoint:
  host: 255.255.255.255
  port: 80
```

## Metaconf

[Metaconf](./pyfig/_metaconf.py)
