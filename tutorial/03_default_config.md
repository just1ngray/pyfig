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
loading your configuration subclass. For basic usage, no advanced knowledge of pydantic is required.

It is recommended that most of your configuration classes are subclasses of `Pyfig`, since this enables these
classes to be loaded directly by pyfig.
