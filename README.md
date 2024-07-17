# pyfig

A Python configuration system that's powerful enough to meet complex requirements, while
being simple enough so new contributors can confidently make changes without worrying how
to get everything setup.

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

...

## Metaconf

...
