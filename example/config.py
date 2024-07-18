import os
from enum import Enum

from pyfig import Pyfig, Metaconf


class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    ERROR = "ERROR"

class LoggingStreamConfig(Pyfig):
    enabled: bool = True
    level: LogLevel = LogLevel.INFO

class LoggingConfig(Pyfig):
    stdout: LoggingStreamConfig = LoggingStreamConfig(enabled=False)
    stderr: LoggingStreamConfig = LoggingStreamConfig(level=LogLevel.DEBUG)

class HealthMonitorConfig(Pyfig):
    enabled: bool = False
    interval_seconds: int = 30

class ImportantTaskParamsConfig(Pyfig):
    timeout: int = 10
    """Number of seconds to wait before timing out the request"""
    retries: int = 3
    """Number of times to try the request before giving up"""

class ImportantTaskConfig(Pyfig):
    enabled: bool = True
    resource: str = "http://localhost:8080/api"
    api_key: str = "${{env.EXAMPLE_API_KEY}}"
    params: ImportantTaskParamsConfig = ImportantTaskParamsConfig()

class ModulesConfig(Pyfig):
    health_monitor: HealthMonitorConfig = HealthMonitorConfig()
    important_task: ImportantTaskConfig = ImportantTaskConfig()

class ApplicationConfig(Pyfig):
    """
    The configuration for the application.
    """
    name: str = "My Application"
    version: str = "0.1.0"
    logging: LoggingConfig = LoggingConfig()
    modules: ModulesConfig = ModulesConfig()


def get_config() -> ApplicationConfig:
    # for the purpose of this example, set the EXAMPLE_API_KEY environment variable programmatically
    if not os.environ.get("EXAMPLE_API_KEY"):
        os.environ["EXAMPLE_API_KEY"] = "mocked api key"

    loader = Metaconf.from_path("example/metaconf.yaml")
    return loader.load_config(ApplicationConfig)


if __name__ == "__main__":
    print("----[ Default Config ]----")
    print(ApplicationConfig().model_dump_json(indent=4))

    print("----[ Metaconf Constructed ]----")
    print(get_config().model_dump_json(indent=4))
