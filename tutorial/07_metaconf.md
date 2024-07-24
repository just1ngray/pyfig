# Metaconf

A `Metaconf` is Pyfig's built-in approach for loading a configuration.

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
To use an evaluator, it must be defined here. You can use any Pyfig built-in evaluator, or by providing your own. The
key roughly equates to an import statement: `pyfig.VariableEvaluator` means `from pyfig import VariableEvaluator`.

The configs section defines the list of overriding configs to apply to your default config in descending priority
order. These paths can be absolute or relative.

The final section is can be used to apply top-level configuration overrides. Because the overriding configs are
generally bundled inside the application, this mechanism can be used to apply config-based hot fixes without needing
to make a full software release.

```python
from pyfig import Pyfig, Metaconf

class MyConfig(Pyfig):
    ...

metaconf = Metaconf.from_path("path/to/metaconf.yaml")
config = metaconf.load_config(MyConfig)
```
