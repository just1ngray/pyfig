# Pyfig Overview

## Define the default config

Your application's default config is defined as a class tree and is bundled inside your application for deployment.
This enables you to make changes to the default config for your application without needing to separately deploy and
sync separate configuration and software deployments. It also enables you to document in your source code the needed
config settings, their meanings, restrictions, and types. Throughout your code, you can access your config classes.

Example `myconfig.py`:
```python
from pyfig import Pyfig

class DbConfig(Pyfig):
    host: str = "localhost"
    port: int = 1234

class ApplicationRootConfig(Pyfig):
    """
    You can document your configuration classes.
    """
    db: DbConfig = DbConfig()
    api_endpoint: str = "http://localhost:8080/api/whatever"
    """
    As well as their attributes.
    """
```

`Pyfig` is a special subclass of pydantic's `BaseModel`. For now, you can assume its behaviour is similar to a
dataclass which requires that all fields have default values.

The above class tree represents a full `yaml` config that would look like:

```yaml
db:
  host: localhost
  port: 1234
api_endpoint: "http://localhost:8080/api/whatever"
```

## Create overriding config files

As your application grows in complexity and scope, its configuration requirements grow as well. The default config
might be suitable for development-mode, but not for a production deployment. For this reason, the default config
can be overridden by any number of arbitrary configuration files.

Consider the above example, a production deployment would probably prefer to target a non-local `api_endpoint`. To
override this value, we can simply use a suitable configuration format (json, yaml, toml, ini, etc.) and set only the
equivalent path in the default config.

Example `override.yaml`:
```yaml
api_endpoint: https://example.com/api/whatever
```

Now we can load the default config, but apply the `override.yaml` overrides to it. This merged config instead looks
like:

```yaml
db:
  host: localhost
  port: 1234
api_endpoint: "https://example.com/api/whatever"
```

Any number of overriding configs can be applied to the default config. Overrides are 'merged' at the lowest
dictionary level. This means that we can change `db.port` without affecting `db.host` by setting just `db.port`
and allowing `db.host` to remain as the default.

## Define the evaluators

Evaluators allow the config to resolve templates from various sources and operations, including but not limited to:

1. Hardcoded variables
2. Environment variables
3. Reading text files
4. String operations
5. Math operations
6. Etc.

> This list is not maintained as a source of truth, and is instead meant to illustrate some bare-bones functionality
> enabled by using evaluators. For more information see [Tutorial: Evaluators](./04_evaluators.md)

Templates have a basic pattern: `${{evaluator}}` or optionally `${{evaluator.args}}`. The first part describes which
evaluator should be used, and the second (optional) part delimited by a dot (`.`) is some argument(s) to pass into the
evaluator.

For example, `${{env.MY_VARIABLE}}` will be replaced with the `MY_VARIABLE` environment variable.

There are a few key things to note:

- The evaluators must be explicitly defined when loading the config
- If a template is provided by the config but no evaluator is found, an error is thrown
- Template evaluators are resolved inside-out. E.g., `${{str.upper('${{var.foo}}')}}` will evaluate `${{var.foo}}` first

## Load the config

The config can be loaded using `load_configuration(...)`. This function takes as input the root `Pyfig` configuration
subclass, the overrides to apply (as a list of dictionaries), and the list of evaluators used to resolve templates.

Pyfig does not generally take ownership of deserializing configuration overrides into dictionaries (e.g., loading a
json, yaml, etc. into a Python dictionary); this is handled by external libraries like `json` or `pyyaml`.
Pyfig also does not take (full) ownership for validating the configuration when its converted into a object tree;
this is handled by pydantic.

Pyfig is focused on overrides and evaluation, and allows external libraries to handle (de)serialization and validation.
