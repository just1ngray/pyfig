# Default Config

Your default configuration is created as a tree of special Python classes.

The "root" of your configuration must be a `Pyfig` subclass.

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
    api_endpoint: str = "https://example.com/api/whatever"
    """
    As well as their attributes.
    """
```

A `Pyfig` is a [pydantic](https://docs.pydantic.dev/latest/) `BaseModel` which requires that all attributes
have default values. If you specify a `Pyfig` without default values, your program will raise an error upon
loading your configuration type. For basic usage, no advanced knowledge of pydantic is required.

It is recommended that most of your configuration classes are subclasses of `Pyfig`, since this enables these
classes to be loaded directly by pyfig. However, under some circumstances it can be beneficial to use a common
config structure with different default values throughout your config.

In this case you can create a subclass of `BaseModel`, not provide defaults for all attributes, and construct
instances as part of another context-aware `Pyfig` configuration object.

```python
from pyfig import Pyfig
from pydantic import BaseModel

class TaskConfig(BaseModel):
    task: str
    period_seconds: int = 60

class RootConfiguration(Pyfig):
    tasks: List[TaskConfig] = [
        TaskConfig(task="cleanup"), # default period_seconds
        TaskConfig(
            task="monitor",
            period_seconds=15
        )
    ]
    ...
```

In the above example it may not make sense to create "duplicated" configuration classes for each task
(`CleanupTaskConfig`, `MonitorTaskConfig`, ...) because they all follow the same structure. And assume that
we would never want to load a config rooted at a single `TaskConfig`, then we can define the structure of
the `TaskConfig` with a `BaseModel`, and then provide defaults within another `Pyfig` class.
