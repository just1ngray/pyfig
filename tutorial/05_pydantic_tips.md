# Pydantic Tips

## Differences from dataclasses

Dataclasses are built-in since Python 3.7 and includes simple initialization, representation, and comparison methods.
However, it does not have built-in validation, and does not enforce type annotations. Special care must be taken when
working with reference-type default values, or all instances that don't provide a default will use the same reference.

```python
from typing import List
from dataclasses import dataclass, field

@dataclass
class Person:
    name: str
    age: int
    fav_foods: List[str] = field(default_factory=list)
```

Pydantic's `BaseModel` is more strict, and more powerful, should you choose to use its full features.

```python
from typing import List
from pydantic import BaseModel, Field, constr, conint, validator

class Person(BaseModel):
    name: constr(min_length=1, max_length=255)         # name length between [1, 255]
    age: conint(ge=0, le=150)                          # age between [0, 150]
    fav_foods: List[constr(min_length=1)] = ["yogurt"] # by default, everyone likes yogurt
```

Even without validation, pydantic also supports recursive dictionary spreading (e.g., `Person(**dictionary)`) and
serialization into a Python or JSON dictionary `.model_dump(mode="python"|"json")`. Json serialization will serialize
all types into json-compatible objects (e.g., `pathlib.Path` becomes a `str`).

## Secret Strings

For convienience, you may wish to use pyfig to load credentials/keys/tokens into your application. However, you
don't want to accidentally leak your secrets when you dump or print your application's config. For this, you can
use pydantic's built-in `SecretBytes` or `SecretStr` classes. When printed, these objects do not expose their
underlying secrets.

## Datetime, time, and delta

Pydantic supports many date & time types out of the box. In general these values are provided as an int, float, or
string, and then parsed into the specified datetime/date/time/timedelta object. Please reference the pydantic docs
for specific parsing information.

## Enums

If a specific list of valid choices is applicable to your situation, an enum is probably the way to go. Define a
plain Python enum, and just use it in your configuration classes.

## Paths

Pydantic can handle `pathlib.Path` objects fine, but if you want to require that there is an existing file or
directory at the path, then you should opt to use `FilePath` or `DirectoryPath` respectively.

## Serializing your config

To serialize your config (to a plain JSON-supported object), you should use `.model_dump(mode="json")` to create
a dictionary of json-serializable types. Then, using your preferred dictionary serialization implementation, you
can dump that serializable dictionary. E.g.,

```python
import yaml # pyyaml library
cfg_yaml = yaml.safe_dump(cfg.model_dump(mode="json"))
```

If you want to serialize to a JSON string, you can use `.model_dump_json()` directly.
