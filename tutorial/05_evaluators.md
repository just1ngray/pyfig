# Evaluators

Evaluators replace templates in the config with some other value. They're evaluated recursively, and can be extended
to implement whatever behaviour you want. They can fill-in new data, as well as mutate existing values. When calling
`load_configuration(...)`, all necessary evaluators must be provided in order to receive a valid
configuration object.

## Syntax

A template looks like `${{evaluator}}` or `${{evaluator.args}}`.

Exactly one evaluator class must match the evaluator by name, and that evaluator is given the (optionally present)
arguments to aid in figuring out what the replacement should be.

## Substitution behaviour

When a template is found within a string, the evaluated template is interpolated into the string.

```yaml
example_yaml_config: Hello, ${{var.name}}!
```

would use the `VariableEvaluator` to substitute the substring only. For example, as:

```yaml
example_yaml_config: Hello, World!
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

## Repeated evaluation

Because evaluators are resolved repeatedly, it is possible for a template to evaluate to another template.

```python
evaluators = [
    pyfig.VariableEvaluator(name="${{env.SOME_ENVIRONMENT_VARIABLE}}!"),
    pyfig.EnvironmentEvaluator()
]
```

Suppose the environment variable `SOME_ENVIRONMENT_VARIABLE` is set to `foo`. These evaluators would evaluate
`${{var.name}}` template first as `${{env.SOME_ENVIRONMENT_VARIABLE}}!` and then as `foo!`.

## Pyfig's built-in evaluators

All evaluators are implemented in [this module](../pyfig/_eval/).

| Class Name | Evaluator Name | Purpose | Basic Syntax |
| - | - | - | - |
| VariableEvaluator | var | Replace with hardcoded values | `${{var.<variable_name>}}` |
| EnvironmentEvaluator | env | Use environment variables | `${{env.<ENVIRONMENT_VARIABLE>}}` |
| CatEvaluator | cat | Use the contents of a file | `${{cat.any/file.path}}` |
| JSONFileEvaluator | jsonfile | Extract a json file field | `${{jsonfile.access.path.to.field:/path/to/file.json}}` |
| YamlFileEvaluator | pyyaml | Extract a yaml file field | `${{pyyaml.access.path.to.field:/path/to/file.yaml}}` |
| PythonEvaluator | pyeval | `eval()` an expression with Python | `${{pyeval:1 + 1}}` |
| StringEvaluator | str | Calls a Python string method | `${{str.upper('hello')}}` |
| SympyEvaluator | sympy | Evaluates a math expression | `${{sympy.3+5}}` |

For more details about any specific evaluator, be sure to read its docstring.
