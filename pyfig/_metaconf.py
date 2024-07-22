import json
import configparser
import importlib
from typing import List, Dict, Any, Union, Type, TypeVar
from dataclasses import dataclass, field
from pathlib import Path

from ._pyfig import Pyfig
from ._eval import AbstractEvaluator
from ._loader import load_configuration


def _load_dict_from_yaml(path: Union[str, Path]) -> Dict[str, Any]:
    """
    Load a YAML file from a path.
    """
    try:
        # pylint: disable=import-outside-toplevel
        import yaml
    except ImportError:
        raise ImportError("Please install pyyaml to load YAML files.") from None

    with Path(path).open("rb") as file:
        return yaml.safe_load(file)


def _load_dict_from_json(path: Union[str, Path]) -> Dict[str, Any]:
    """
    Load a JSON file from a path.
    """
    with Path(path).open("rb") as file:
        return json.load(file)


def _load_dict_from_toml(path: Union[str, Path]) -> Dict[str, Any]:
    """
    Load a TOML file from a path.
    """
    try:
        # pylint: disable=import-outside-toplevel
        import toml
    except ImportError:
        try:
            # pylint: disable=import-outside-toplevel
            import tomli as toml
        except ImportError:
            raise ImportError("Please install toml or tomli to load TOML files.") from None

    contents = Path(path).read_text("utf-8")
    return toml.loads(contents)


def _load_dict_from_ini(path: Union[str, Path]) -> Dict[str, Any]:
    """
    Load an INI file from a path.
    """
    parser = configparser.ConfigParser()
    parser.read(path)
    return {section: dict(parser[section]) for section in parser.sections()}


def _load_dict(path: Union[str, Path]) -> Dict[str, Any]:
    path = Path(path)

    if not path.is_file():
        raise FileNotFoundError(f"Configuration file not found: {path.as_posix()}")

    return {
        "yml": _load_dict_from_yaml,
        "yaml": _load_dict_from_yaml,
        "json": _load_dict_from_json,
        "toml": _load_dict_from_toml,
        "ini": _load_dict_from_ini,
    }[path.suffix[1:]](path)


def _construct_evaluator(class_path: str, params: Dict[str, Any]):
    """
    Construct an evaluator from its name and parameters.
    """
    module_path, class_name = class_path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    evaluator_class = getattr(module, class_name, None)
    if evaluator_class is None:
        raise ImportError(f"Module exists but class {class_name} not found in {module_path}")

    if not issubclass(evaluator_class, AbstractEvaluator):
        raise TypeError(f"{evaluator_class} is not a subclass of {AbstractEvaluator.__name__}")

    return evaluator_class(**params)


T = TypeVar("T", bound=Pyfig)

@dataclass
class Metaconf:
    """
    The recommended way to use Pyfig. This 'meta configuration' specifies how the application's configuration
    is loaded.

    E.g.,
    ```
    {
        "configs": [
            "path/to/override.toml",
            "/some/other/path.json"
        ],
        "evaluators": {
            "pyfig.VariableEvaluator": {
                "foo": "bar"
            }
        },
        "overrides": {}
    }
    ```
    """

    configs: List[str] = field(default_factory=list)
    """
    A list of configuration files to load in descending priority order. Note: depending on the file format,
    additional dependencies may be required.
    """

    evaluators: List[AbstractEvaluator] = field(default_factory=list)
    """
    A list of evaluators that can be used to fill-in templated values in the configuration files.

    Recommended to always use, for their convienience. This can also be extended to meet your needs.
        - pyfig.VariableEvaluator
        - pyfig.EnvironmentEvaluator
    """

    overrides: Dict[str, Any] = field(default_factory=dict)
    """
    Highest-priority overrides applied to the configuration. This bypasses the configuration files.
    """

    @staticmethod
    def from_path(path: Union[str, Path], *, relative_to: Union[str, Path, None]=None) -> "Metaconf":
        """
        Constructs a metaconf, which is then capable of `load_config` to get your application's config.

        Args:
            path:           the path on disk to the meta configuration file
            relative_to:    if given, all relative config paths will be joined to this path

        Returns:
            A Metaconf instance
        """
        data = _load_dict(path) or {}

        overrides = data.get("overrides", {})
        evaluators: List[AbstractEvaluator] = []
        configs = data.get("configs", [])

        for evaluator, params in data.get("evaluators", {}).items():
            evaluators.append(_construct_evaluator(evaluator, params))

        if relative_to is not None:
            relative_to = Path(relative_to)
            configs = [relative_to.joinpath(cfg).as_posix() for cfg in configs]

        return Metaconf(
            evaluators=evaluators,
            overrides=overrides,
            configs=configs
        )

    def load_config(self, target: Type[T]) -> T:
        """
        Use the meta configuration to load your application's configuration.
        """
        configs = [_load_dict(config) for config in self.configs]
        return load_configuration(target, [self.overrides, *configs], self.evaluators)
